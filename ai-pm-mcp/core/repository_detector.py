#!/usr/bin/env python3
"""
Repository Detector Module

Handles repository analysis, user detection, GitHub CLI detection, and metadata persistence
for AI Project Manager. Extracted from GitBranchManager to reduce file size.
"""

import subprocess
import logging
import os
import datetime
import getpass
import json
from pathlib import Path
from typing import Dict, Any

from ..utils.project_paths import get_blueprint_path

logger = logging.getLogger(__name__)


class RepositoryDetector:
    """
    Handles repository analysis, user detection, and metadata persistence.
    """
    
    def __init__(self, project_root: Path, config_manager=None):
        self.project_root = Path(project_root)
        self.config_manager = config_manager
    
    def detect_user_info(self) -> Dict[str, Any]:
        """
        Detect user information from Git config, environment, and system.
        Follows detection order: Git config -> Environment -> System -> Fallback
        """
        user_info = {
            "name": None,
            "email": None,
            "source": None
        }
        
        try:
            # Try Git config user.name
            result = subprocess.run([
                'git', 'config', 'user.name'
            ], cwd=self.project_root, capture_output=True, text=True)
            
            if result.returncode == 0 and result.stdout.strip():
                user_info["name"] = result.stdout.strip()
                user_info["source"] = "git_config"
                
                # Also get email if available
                email_result = subprocess.run([
                    'git', 'config', 'user.email'
                ], cwd=self.project_root, capture_output=True, text=True)
                
                if email_result.returncode == 0 and email_result.stdout.strip():
                    user_info["email"] = email_result.stdout.strip()
                    
                return user_info
        except Exception:
            pass
        
        # Try environment variables
        try:
            env_user = os.environ.get('USER') or os.environ.get('USERNAME')
            if env_user:
                user_info["name"] = env_user
                user_info["source"] = "environment"
                return user_info
        except Exception:
            pass
        
        # Try system username
        try:
            system_user = getpass.getuser()
            if system_user:
                user_info["name"] = system_user
                user_info["source"] = "system"
                return user_info
        except Exception:
            pass
        
        # Fallback
        user_info["name"] = "ai-user"
        user_info["source"] = "fallback"
        return user_info
    
    def get_metadata_path(self) -> Path:
        """Get path to project metadata file."""
        return get_blueprint_path(self.project_root, self.config_manager) / "metadata.json"
    
    def load_metadata(self) -> Dict[str, Any]:
        """Load project metadata from file."""
        metadata_path = self.get_metadata_path()
        try:
            if metadata_path.exists():
                return json.loads(metadata_path.read_text(encoding='utf-8'))
            return {}
        except Exception as e:
            logger.error(f"Error loading metadata: {e}")
            return {}
    
    def save_metadata(self, metadata: Dict[str, Any]) -> bool:
        """Save project metadata to file."""
        metadata_path = self.get_metadata_path()
        try:
            # Ensure directory exists
            metadata_path.parent.mkdir(parents=True, exist_ok=True)
            
            metadata_path.write_text(json.dumps(metadata, indent=2), encoding='utf-8')
            return True
        except Exception as e:
            logger.error(f"Error saving metadata: {e}")
            return False
    
    def check_gh_cli_available(self) -> bool:
        """
        Check if GitHub CLI (gh) is available and authenticated.
        Stores result in metadata.json for persistence.
        """
        # Check metadata first for cached result
        metadata = self.load_metadata()
        system_info = metadata.get("system", {})
        
        # Check if we have recent data (within last hour)
        now = datetime.datetime.now(datetime.timezone.utc)
        last_check = system_info.get("gh_cli_last_check")
        
        if last_check:
            try:
                last_check_time = datetime.datetime.fromisoformat(last_check.replace('Z', '+00:00'))
                if (now - last_check_time).total_seconds() < 3600:  # 1 hour cache
                    return system_info.get("gh_cli_available", False)
            except:
                pass
        
        # Perform fresh check
        try:
            # Check if gh command exists
            result = subprocess.run([
                'gh', '--version'
            ], capture_output=True, text=True, timeout=5)
            
            if result.returncode != 0:
                gh_available = False
            else:
                # Check if authenticated
                auth_result = subprocess.run([
                    'gh', 'auth', 'status'
                ], capture_output=True, text=True, timeout=5)
                gh_available = auth_result.returncode == 0
            
            # Update metadata with results
            if "system" not in metadata:
                metadata["system"] = {}
            
            metadata["system"]["gh_cli_available"] = gh_available
            metadata["system"]["gh_cli_last_check"] = now.isoformat()
            metadata["system"]["gh_cli_version"] = result.stdout.split()[2] if result.returncode == 0 else None
            
            self.save_metadata(metadata)
            
            if gh_available:
                logger.info("GitHub CLI detected and authenticated")
            else:
                logger.info("GitHub CLI not available or not authenticated")
                
            return gh_available
            
        except (subprocess.TimeoutExpired, FileNotFoundError, Exception) as e:
            logger.debug(f"GitHub CLI not available: {e}")
            
            # Update metadata with failure
            if "system" not in metadata:
                metadata["system"] = {}
            metadata["system"]["gh_cli_available"] = False
            metadata["system"]["gh_cli_last_check"] = now.isoformat()
            self.save_metadata(metadata)
            
            return False
    
    def detect_repository_type(self) -> Dict[str, Any]:
        """
        Detect if this is a fork, clone, or original repository.
        Returns detailed repository information stored in metadata.json.
        """
        # Check metadata first for cached result
        metadata = self.load_metadata()
        repo_info = metadata.get("repository", {})
        
        # Check if we have recent data (within last 24 hours)
        now = datetime.datetime.now(datetime.timezone.utc)
        last_check = repo_info.get("last_check")
        
        if last_check:
            try:
                last_check_time = datetime.datetime.fromisoformat(last_check.replace('Z', '+00:00'))
                if (now - last_check_time).total_seconds() < 86400:  # 24 hours cache
                    return repo_info
            except:
                pass
        
        # Perform fresh analysis
        repo_info = {
            "type": "unknown",  # "original", "clone", "fork"
            "has_origin": False,
            "has_upstream": False,
            "origin_url": None,
            "upstream_url": None,
            "is_github": False,
            "gh_cli_available": self.check_gh_cli_available(),
            "current_branch": self._get_current_branch(),
            "ai_branch_exists": self._branch_exists("ai-pm-org-main"),
            "last_check": now.isoformat()
        }
        
        try:
            # Get remote information
            result = subprocess.run([
                'git', 'remote', '-v'
            ], cwd=self.project_root, capture_output=True, text=True)
            
            if result.returncode == 0:
                remotes = result.stdout.strip()
                
                # Parse remotes
                for line in remotes.split('\n'):
                    if line.strip():
                        parts = line.split('\t')
                        if len(parts) >= 2:
                            remote_name = parts[0]
                            remote_url = parts[1].split(' ')[0]
                            
                            if remote_name == "origin":
                                repo_info["has_origin"] = True
                                repo_info["origin_url"] = remote_url
                            elif remote_name == "upstream":
                                repo_info["has_upstream"] = True
                                repo_info["upstream_url"] = remote_url
                
                # Determine if GitHub
                if repo_info["origin_url"]:
                    repo_info["is_github"] = "github.com" in repo_info["origin_url"]
                
                # Determine repository type
                if repo_info["has_upstream"]:
                    repo_info["type"] = "fork"
                elif repo_info["has_origin"]:
                    if repo_info["gh_cli_available"] and repo_info["is_github"]:
                        # Use gh CLI to check if this is a fork
                        try:
                            gh_result = subprocess.run([
                                'gh', 'repo', 'view', '--json', 'isFork'
                            ], cwd=self.project_root, capture_output=True, text=True, timeout=10)
                            
                            if gh_result.returncode == 0:
                                repo_data = json.loads(gh_result.stdout)
                                if repo_data.get("isFork", False):
                                    repo_info["type"] = "fork"
                                else:
                                    repo_info["type"] = "clone"
                            else:
                                repo_info["type"] = "clone"  # Assume clone if can't determine
                        except Exception:
                            repo_info["type"] = "clone"
                    else:
                        repo_info["type"] = "clone"
                else:
                    repo_info["type"] = "original"
            
            # Store in metadata
            metadata["repository"] = repo_info
            self.save_metadata(metadata)
            
            logger.debug(f"Repository type detected: {repo_info['type']}")
            return repo_info
            
        except Exception as e:
            logger.error(f"Error detecting repository type: {e}")
            # Still save what we have
            metadata["repository"] = repo_info
            self.save_metadata(metadata)
            return repo_info
    
    def _get_current_branch(self) -> str:
        """Get the currently active branch."""
        try:
            result = subprocess.run([
                'git', 'rev-parse', '--abbrev-ref', 'HEAD'
            ], cwd=self.project_root, capture_output=True, text=True)
            
            if result.returncode == 0:
                return result.stdout.strip()
            else:
                return "unknown"
                
        except Exception as e:
            logger.error(f"Error getting current branch: {e}")
            return "unknown"
    
    def _branch_exists(self, branch_name: str) -> bool:
        """Check if a branch exists."""
        try:
            result = subprocess.run([
                'git', 'branch', '--list', branch_name
            ], cwd=self.project_root, capture_output=True, text=True)
            
            return bool(result.stdout.strip())
            
        except Exception as e:
            logger.error(f"Error checking if branch exists: {e}")
            return False