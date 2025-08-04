#!/usr/bin/env python3
"""
Git Safety Module

Provides safety checks and validations for Git workflows in AI Project Manager.
Prevents common Git workflow issues like working on main in cloned repos,
branching from wrong bases, etc.
"""

import logging
import subprocess
from pathlib import Path
from typing import Dict, Any

logger = logging.getLogger(__name__)


class GitSafetyChecker:
    """
    Provides Git workflow safety checks and validations.
    """
    
    def __init__(self, project_root: Path, ai_main_branch: str = "ai-pm-org-main"):
        self.project_root = Path(project_root)
        self.ai_main_branch = ai_main_branch
    
    def _get_current_branch(self) -> str:
        """Get the current Git branch name."""
        try:
            result = subprocess.run([
                'git', 'branch', '--show-current'
            ], cwd=self.project_root, capture_output=True, text=True)
            
            if result.returncode == 0:
                return result.stdout.strip()
            else:
                # Fallback for older Git versions or detached HEAD
                result = subprocess.run([
                    'git', 'rev-parse', '--abbrev-ref', 'HEAD'
                ], cwd=self.project_root, capture_output=True, text=True)
                
                if result.returncode == 0:
                    branch = result.stdout.strip()
                    return "detached" if branch == "HEAD" else branch
                    
        except Exception as e:
            logger.error(f"Error getting current branch: {e}")
            
        return "unknown"
    
    def _branch_exists(self, branch_name: str) -> bool:
        """Check if a branch exists locally."""
        try:
            result = subprocess.run([
                'git', 'branch', '--list', branch_name
            ], cwd=self.project_root, capture_output=True, text=True)
            return result.returncode == 0 and branch_name in result.stdout
        except Exception:
            return False
    
    def check_workflow_safety(self, repo_info: Dict[str, Any]) -> Dict[str, Any]:
        """
        Check current Git state for workflow safety issues.
        Returns warnings and recommendations based on repository type and current branch.
        """
        current_branch = self._get_current_branch()
        
        safety_check = {
            "safe": True,
            "warnings": [],
            "recommendations": [],
            "current_branch": current_branch,
            "repository_type": repo_info.get("type", "unknown")
        }
        
        # Check if working on main in cloned repo
        if (current_branch == "main" and 
            repo_info.get("type") in ["clone", "fork"] and 
            repo_info.get("has_origin", False)):
            
            safety_check["safe"] = False
            safety_check["warnings"].append({
                "type": "working_on_main_in_clone",
                "severity": "high",
                "message": "⚠️ You are working directly on 'main' in a cloned/forked repository"
            })
            
            if repo_info.get("ai_branch_exists", False):
                safety_check["recommendations"].append({
                    "action": "switch_to_ai_branch",
                    "message": f"Switch to '{self.ai_main_branch}' branch: `git checkout {self.ai_main_branch}`"
                })
                safety_check["recommendations"].append({
                    "action": "create_work_branch",
                    "message": "Then create a work branch using `/branch` command"
                })
            else:
                safety_check["recommendations"].append({
                    "action": "use_init_command",
                    "message": "Use `/init` command to set up AI project management properly"
                })
        
        # Check if trying to branch from wrong base
        if (current_branch != self.ai_main_branch and 
            current_branch != "main" and 
            repo_info.get("ai_branch_exists", False)):
            
            safety_check["warnings"].append({
                "type": "on_feature_branch",
                "severity": "medium", 
                "message": f"⚠️ You are on feature branch '{current_branch}'"
            })
            
            safety_check["recommendations"].append({
                "action": "switch_to_ai_main",
                "message": f"Switch to '{self.ai_main_branch}' before creating new branches: `git checkout {self.ai_main_branch}`"
            })
        
        # Check for GitHub CLI availability for PR operations
        if repo_info.get("is_github", False) and not repo_info.get("gh_cli_available", False):
            safety_check["warnings"].append({
                "type": "no_github_cli",
                "severity": "low",
                "message": "⚠️ GitHub CLI not available - merge operations will be limited"
            })
            
            safety_check["recommendations"].append({
                "action": "install_gh_cli",
                "message": "Install GitHub CLI for full PR functionality: https://cli.github.com/"
            })
        
        return safety_check
    
    def check_branch_ancestry(self, target_branch: str = None) -> Dict[str, Any]:
        """
        Check if current branch has proper ancestry from ai-pm-org-main.
        Prevents branching from wrong bases.
        """
        if target_branch is None:
            target_branch = self.ai_main_branch
            
        current_branch = self._get_current_branch()
        
        ancestry_check = {
            "valid": True,
            "current_branch": current_branch,
            "target_branch": target_branch,
            "message": "",
            "recommendations": []
        }
        
        try:
            # Check if target branch exists
            if not self._branch_exists(target_branch):
                ancestry_check["valid"] = False
                ancestry_check["message"] = f"Target branch '{target_branch}' does not exist"
                ancestry_check["recommendations"].append({
                    "action": "create_ai_main",
                    "message": f"Use `/init` to create '{target_branch}' branch"
                })
                return ancestry_check
            
            # If we're already on the target branch, that's fine
            if current_branch == target_branch:
                ancestry_check["message"] = f"Currently on target branch '{target_branch}'"
                return ancestry_check
            
            # Check if current branch is based on target branch
            merge_base_result = subprocess.run([
                'git', 'merge-base', 'HEAD', target_branch
            ], cwd=self.project_root, capture_output=True, text=True)
            
            target_commit_result = subprocess.run([
                'git', 'rev-parse', target_branch
            ], cwd=self.project_root, capture_output=True, text=True)
            
            if (merge_base_result.returncode == 0 and 
                target_commit_result.returncode == 0):
                
                merge_base = merge_base_result.stdout.strip()
                target_commit = target_commit_result.stdout.strip()
                
                if merge_base == target_commit:
                    ancestry_check["message"] = f"Current branch properly based on '{target_branch}'"
                else:
                    ancestry_check["valid"] = False
                    ancestry_check["message"] = f"Current branch '{current_branch}' is not directly based on '{target_branch}'"
                    ancestry_check["recommendations"].append({
                        "action": "switch_to_target",
                        "message": f"Switch to '{target_branch}': `git checkout {target_branch}`"
                    })
                    ancestry_check["recommendations"].append({
                        "action": "rebase_option",
                        "message": f"Or rebase current branch: `git rebase {target_branch}`"
                    })
            else:
                ancestry_check["valid"] = False  
                ancestry_check["message"] = "Unable to determine branch ancestry"
                
        except Exception as e:
            logger.error(f"Error checking branch ancestry: {e}")
            ancestry_check["valid"] = False
            ancestry_check["message"] = f"Error checking ancestry: {str(e)}"
            
        return ancestry_check
    
    def validate_branch_creation(self, repo_info: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validate that it's safe to create a new branch.
        Combines safety checks and ancestry validation.
        """
        validation = {
            "safe_to_create": True,
            "blocking_issues": [],
            "warnings": [],
            "recommendations": []
        }
        
        # Run safety checks
        safety_check = self.check_workflow_safety(repo_info)
        
        # Check for high-severity warnings that should block branch creation
        high_severity_warnings = [w for w in safety_check["warnings"] if w.get("severity") == "high"]
        if high_severity_warnings:
            validation["safe_to_create"] = False
            validation["blocking_issues"] = high_severity_warnings
            validation["recommendations"].extend(safety_check["recommendations"])
        else:
            # Add non-blocking warnings
            validation["warnings"] = safety_check["warnings"]
        
        # Check branch ancestry
        ancestry_check = self.check_branch_ancestry()
        if not ancestry_check["valid"]:
            # This is not necessarily blocking - we can auto-switch
            validation["warnings"].append({
                "type": "branch_ancestry",
                "severity": "medium",
                "message": ancestry_check["message"]
            })
            validation["recommendations"].extend(ancestry_check["recommendations"])
        
        return validation