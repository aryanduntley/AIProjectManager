"""
MCP Instance Manager - Git-like Instance Management System
Handles creation, lifecycle, and coordination of MCP instances with isolated workspaces
"""

import os
import shutil
import json
import uuid
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime, timedelta
import re

from ..database.db_manager import DatabaseManager
from ..database.git_queries import GitQueries
from .git_integration import GitIntegrationManager


class InstanceCreationResult:
    """Result of instance creation operation"""
    def __init__(self, success: bool, instance_id: str = "", message: str = "", 
                 workspace_path: str = "", metadata: Dict[str, Any] = None):
        self.success = success
        self.instance_id = instance_id
        self.message = message
        self.workspace_path = workspace_path
        self.metadata = metadata or {}


class InstanceInfo:
    """Information about an MCP instance"""
    def __init__(self, instance_data: Dict[str, Any]):
        self.instance_id = instance_data.get("instance_id", "")
        self.instance_name = instance_data.get("instance_name", "")
        self.created_from = instance_data.get("created_from", "main")
        self.created_by = instance_data.get("created_by", "")
        self.purpose = instance_data.get("purpose", "")
        self.primary_themes = instance_data.get("primary_themes", [])
        self.related_flows = instance_data.get("related_flows", [])
        self.status = instance_data.get("status", "active")
        self.workspace_path = instance_data.get("workspace_path", "")
        self.database_path = instance_data.get("database_path", "")
        self.created_at = instance_data.get("created_at", "")
        self.last_activity = instance_data.get("last_activity", "")


class InstanceStatus:
    """Status information for an instance"""
    def __init__(self, exists: bool, status: str = "", details: Dict[str, Any] = None):
        self.exists = exists
        self.status = status
        self.details = details or {}


class MCPInstanceManager:
    """
    Git-like instance management system for MCP organizational state
    Provides isolated workspaces with merge-based integration
    """
    
    def __init__(self, project_root: Path, db_manager: DatabaseManager):
        self.project_root = Path(project_root)
        self.db_manager = db_manager
        self.git_queries = GitQueries(db_manager)
        self.git_manager = GitIntegrationManager(project_root, db_manager)
        
        # Core paths
        self.main_instance_path = self.project_root / "projectManagement"
        self.instances_dir = self.project_root / ".mcp-instances"
        self.active_dir = self.instances_dir / "active"
        self.completed_dir = self.instances_dir / "completed"
        self.conflicts_dir = self.instances_dir / "conflicts"
        
        # Configuration
        self.config_file = self.instances_dir / ".mcp-config.json"
        self.merge_log_file = self.instances_dir / ".mcp-merge-log.jsonl"
        
        self._ensure_instance_directory_structure()
    
    # ============================================================================
    # INSTANCE LIFECYCLE MANAGEMENT
    # ============================================================================
    
    def create_instance(self, instance_name: str, created_by: str = "ai", 
                       purpose: str = "", themes: List[str] = None,
                       related_flows: List[str] = None,
                       expected_duration: str = "") -> InstanceCreationResult:
        """
        Create new MCP instance with isolated workspace
        Equivalent to 'git checkout -b feature/branch-name'
        """
        if themes is None:
            themes = []
        if related_flows is None:
            related_flows = []
        
        try:
            # Phase 1: Validate Main State
            main_validation = self._validate_main_instance_state()
            if not main_validation["valid"]:
                return InstanceCreationResult(
                    success=False,
                    message=f"Main instance validation failed: {main_validation['message']}"
                )
            
            # Phase 2: Generate Instance ID and Validate Naming
            instance_id = self._generate_instance_id(instance_name, created_by)
            validation_result = self._validate_instance_naming(instance_id)
            if not validation_result["valid"]:
                return InstanceCreationResult(
                    success=False,
                    message=validation_result["message"]
                )
            
            # Phase 3: Check for Existing Instance
            if self._instance_exists(instance_id):
                return InstanceCreationResult(
                    success=False,
                    message=f"Instance '{instance_id}' already exists"
                )
            
            # Phase 4: Create Instance Workspace
            workspace_result = self._create_instance_workspace(instance_id)
            if not workspace_result["success"]:
                return InstanceCreationResult(
                    success=False,
                    message=f"Workspace creation failed: {workspace_result['message']}"
                )
            
            workspace_path = workspace_result["workspace_path"]
            
            # Phase 5: Initialize Instance Database
            database_result = self._initialize_instance_database(instance_id, workspace_path)
            if not database_result["success"]:
                # Cleanup workspace on database failure
                shutil.rmtree(workspace_path, ignore_errors=True)
                return InstanceCreationResult(
                    success=False,
                    message=f"Database initialization failed: {database_result['message']}"
                )
            
            # Phase 6: Create Instance Metadata
            metadata_result = self._create_instance_metadata(
                instance_id, instance_name, "main", created_by, purpose, 
                themes, related_flows, expected_duration, workspace_path
            )
            if not metadata_result["success"]:
                # Cleanup on metadata failure
                shutil.rmtree(workspace_path, ignore_errors=True)
                return InstanceCreationResult(
                    success=False,
                    message=f"Metadata creation failed: {metadata_result['message']}"
                )
            
            # Phase 7: Register in Database
            db_success = self.git_queries.create_mcp_instance(
                instance_id=instance_id,
                instance_name=instance_name,
                created_from="main",
                created_by=created_by,
                purpose=purpose,
                primary_themes=themes,
                related_flows=related_flows,
                expected_duration=expected_duration
            )
            
            if not db_success:
                # Cleanup on database registration failure
                shutil.rmtree(workspace_path, ignore_errors=True)
                return InstanceCreationResult(
                    success=False,
                    message="Failed to register instance in database"
                )
            
            # Phase 8: Update database with workspace paths
            current_git_hash = self.git_manager.get_current_git_hash()
            self.git_queries.update_instance_status(
                instance_id=instance_id,
                status="active",
                workspace_path=str(workspace_path),
                database_path=str(database_result["database_path"]),
                git_base_hash=current_git_hash or ""
            )
            
            return InstanceCreationResult(
                success=True,
                instance_id=instance_id,
                message=f"Instance '{instance_id}' created successfully",
                workspace_path=str(workspace_path),
                metadata={
                    "instance_name": instance_name,
                    "created_by": created_by,
                    "purpose": purpose,
                    "primary_themes": themes,
                    "workspace_path": str(workspace_path),
                    "database_path": str(database_result["database_path"]),
                    "git_base_hash": current_git_hash
                }
            )
            
        except Exception as e:
            return InstanceCreationResult(
                success=False,
                message=f"Instance creation error: {str(e)}"
            )
    
    def get_active_instances(self) -> List[InstanceInfo]:
        """Get all active MCP instances"""
        try:
            active_instances_data = self.git_queries.list_active_instances()
            return [InstanceInfo(instance_data) for instance_data in active_instances_data]
        except Exception as e:
            print(f"Error getting active instances: {e}")
            return []
    
    def get_instance_status(self, instance_id: str) -> InstanceStatus:
        """Get comprehensive status of an MCP instance"""
        try:
            instance_data = self.git_queries.get_mcp_instance(instance_id)
            if not instance_data:
                return InstanceStatus(exists=False)
            
            # Check workspace existence
            workspace_path = Path(instance_data.get("workspace_path", ""))
            workspace_exists = workspace_path.exists() if workspace_path else False
            
            # Check database existence
            database_path = Path(instance_data.get("database_path", ""))
            database_exists = database_path.exists() if database_path else False
            
            return InstanceStatus(
                exists=True,
                status=instance_data["status"],
                details={
                    "instance_data": instance_data,
                    "workspace_exists": workspace_exists,
                    "database_exists": database_exists,
                    "workspace_path": str(workspace_path),
                    "database_path": str(database_path)
                }
            )
            
        except Exception as e:
            return InstanceStatus(
                exists=False,
                details={"error": f"Error checking instance status: {str(e)}"}
            )
    
    def archive_instance(self, instance_id: str) -> Dict[str, Any]:
        """Archive a completed MCP instance"""
        try:
            # Get instance information
            instance_status = self.get_instance_status(instance_id)
            if not instance_status.exists:
                return {
                    "success": False,
                    "message": f"Instance '{instance_id}' not found"
                }
            
            instance_data = instance_status.details["instance_data"]
            workspace_path = Path(instance_data.get("workspace_path", ""))
            
            # Create archive directory structure
            archive_timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            archive_name = f"{instance_id}_{archive_timestamp}"
            archive_path = self.completed_dir / archive_name
            
            # Move workspace to archive
            if workspace_path.exists():
                shutil.move(str(workspace_path), str(archive_path))
            
            # Update database status
            success = self.git_queries.archive_instance(instance_id)
            
            if success:
                return {
                    "success": True,
                    "message": f"Instance '{instance_id}' archived successfully",
                    "archive_path": str(archive_path)
                }
            else:
                return {
                    "success": False,
                    "message": f"Failed to update instance status in database"
                }
                
        except Exception as e:
            return {
                "success": False,
                "message": f"Error archiving instance: {str(e)}"
            }
    
    # ============================================================================
    # MAIN INSTANCE AUTHORITY
    # ============================================================================
    
    def is_main_instance(self) -> bool:
        """Check if current location is the main instance"""
        main_marker = self.main_instance_path / ".mcp-instance-main"
        return main_marker.exists()
    
    def get_main_instance_path(self) -> Path:
        """Get path to main instance"""
        return self.main_instance_path
    
    def validate_main_instance_authority(self) -> Dict[str, Any]:
        """Validate that this is the main instance with authority for operations"""
        if not self.is_main_instance():
            return {
                "valid": False,
                "message": "Operation requires main instance authority"
            }
        
        if not self.main_instance_path.exists():
            return {
                "valid": False,
                "message": "Main instance directory not found"
            }
        
        return {
            "valid": True,
            "message": "Main instance authority confirmed"
        }
    
    # ============================================================================
    # INSTANCE WORKSPACE MANAGEMENT
    # ============================================================================
    
    def _create_instance_workspace(self, instance_id: str) -> Dict[str, Any]:
        """Create isolated workspace for instance"""
        try:
            workspace_path = self.active_dir / instance_id
            
            # Create workspace directory
            workspace_path.mkdir(parents=True, exist_ok=False)
            
            # Copy main projectManagement to instance workspace
            instance_pm_path = workspace_path / "projectManagement"
            shutil.copytree(
                self.main_instance_path,
                instance_pm_path,
                ignore=shutil.ignore_patterns(
                    "database/backups/*",
                    "UserSettings/*",
                    ".mcp-session-*",
                    "*.tmp"
                )
            )
            
            # Remove main instance marker from copy
            main_marker = instance_pm_path / ".mcp-instance-main"
            if main_marker.exists():
                main_marker.unlink()
            
            return {
                "success": True,
                "workspace_path": workspace_path,
                "message": f"Workspace created at {workspace_path}"
            }
            
        except FileExistsError:
            return {
                "success": False,
                "message": f"Workspace for '{instance_id}' already exists"
            }
        except Exception as e:
            return {
                "success": False,
                "message": f"Workspace creation failed: {str(e)}"
            }
    
    def _initialize_instance_database(self, instance_id: str, workspace_path: Path) -> Dict[str, Any]:
        """Initialize isolated database for instance"""
        try:
            # Source and destination database paths
            main_db_path = self.main_instance_path / "project.db"
            instance_db_path = workspace_path / "projectManagement" / "project.db"
            
            if not main_db_path.exists():
                return {
                    "success": False,
                    "message": "Main database not found"
                }
            
            # Copy main database to instance workspace
            shutil.copy2(main_db_path, instance_db_path)
            
            # TODO: Initialize instance-specific database modifications
            # This could include:
            # - Adding instance identification to database
            # - Setting up instance-specific session tracking
            # - Preparing for merge conflict detection
            
            return {
                "success": True,
                "database_path": instance_db_path,
                "message": f"Instance database initialized at {instance_db_path}"
            }
            
        except Exception as e:
            return {
                "success": False,
                "message": f"Database initialization failed: {str(e)}"
            }
    
    def _create_instance_metadata(self, instance_id: str, instance_name: str,
                                 created_from: str, created_by: str, purpose: str,
                                 primary_themes: List[str], related_flows: List[str],
                                 expected_duration: str, workspace_path: Path) -> Dict[str, Any]:
        """Create instance metadata files"""
        try:
            # Create .mcp-branch-info.json
            branch_info = {
                "instanceId": instance_id,
                "createdFrom": created_from,
                "createdAt": datetime.now().isoformat(),
                "createdBy": created_by,
                "purpose": purpose,
                "primaryThemes": primary_themes,
                "relatedFlows": related_flows,
                "expectedDuration": expected_duration,
                "status": "active"
            }
            
            branch_info_path = workspace_path / ".mcp-branch-info.json"
            with open(branch_info_path, 'w') as f:
                json.dump(branch_info, f, indent=2)
            
            # Create .mcp-work-summary.md
            work_summary = self._generate_work_summary_template(
                instance_id, instance_name, purpose, primary_themes
            )
            
            work_summary_path = workspace_path / ".mcp-work-summary.md"
            with open(work_summary_path, 'w') as f:
                f.write(work_summary)
            
            return {
                "success": True,
                "message": "Instance metadata created successfully",
                "metadata_files": [str(branch_info_path), str(work_summary_path)]
            }
            
        except Exception as e:
            return {
                "success": False,
                "message": f"Metadata creation failed: {str(e)}"
            }
    
    def _generate_work_summary_template(self, instance_id: str, instance_name: str,
                                       purpose: str, themes: List[str]) -> str:
        """Generate work summary template for instance"""
        template = f"""# Work Summary: {instance_name}

## Instance Information
- **Instance ID**: {instance_id}
- **Purpose**: {purpose}
- **Primary Themes**: {', '.join(themes) if themes else 'None specified'}
- **Created**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## Work Progress

### Completed Tasks
- [ ] Initial setup and workspace preparation

### Current Focus
- Working on: [Describe current task or area of focus]

### Next Steps
- [ ] [Add specific next steps]

### Notes and Decisions
- [Add important notes, decisions, or observations during development]

### Files Modified
- [List significant files modified during this instance work]

### Integration Notes
- [Notes for merging back to main instance]
- [Potential conflicts or considerations]

---
*This summary is updated throughout the instance lifecycle to aid in merge preparation and knowledge transfer.*
"""
        return template
    
    # ============================================================================
    # INSTANCE VALIDATION AND NAMING
    # ============================================================================
    
    def _validate_main_instance_state(self) -> Dict[str, Any]:
        """Validate that main instance is in a clean, consistent state"""
        try:
            # Check main instance directory exists
            if not self.main_instance_path.exists():
                return {
                    "valid": False,
                    "message": "Main instance directory not found"
                }
            
            # Check for main instance marker
            main_marker = self.main_instance_path / ".mcp-instance-main"
            if not main_marker.exists():
                # Create main instance marker if missing
                main_marker.touch()
            
            # Check Git repository state
            git_status = self.git_manager.get_git_status()
            if git_status.get("error"):
                return {
                    "valid": False,
                    "message": f"Git repository issue: {git_status['error']}"
                }
            
            # Warn about uncommitted changes but don't block
            if git_status.get("has_uncommitted_changes"):
                return {
                    "valid": True,
                    "message": "Main instance valid (warning: uncommitted changes exist)",
                    "warnings": ["Uncommitted changes detected in main instance"]
                }
            
            return {
                "valid": True,
                "message": "Main instance state is valid"
            }
            
        except Exception as e:
            return {
                "valid": False,
                "message": f"Main instance validation error: {str(e)}"
            }
    
    def _generate_instance_id(self, instance_name: str, created_by: str) -> str:
        """
        Generate instance ID following naming convention
        Format: {theme/area}-{purpose}-{user} or {theme/area}-{purpose}
        """
        # Clean and normalize the instance name
        clean_name = re.sub(r'[^\w\-]', '-', instance_name.lower())
        clean_name = re.sub(r'-+', '-', clean_name).strip('-')
        
        # Add user suffix if provided and not already in name
        if created_by and created_by != "ai" and created_by not in clean_name:
            return f"{clean_name}-{created_by.lower()}"
        
        return clean_name
    
    def _validate_instance_naming(self, instance_id: str) -> Dict[str, Any]:
        """Validate instance ID follows naming conventions"""
        # Check basic format requirements
        if not instance_id:
            return {
                "valid": False,
                "message": "Instance ID cannot be empty"
            }
        
        if len(instance_id) < 3:
            return {
                "valid": False,
                "message": "Instance ID must be at least 3 characters long"
            }
        
        if len(instance_id) > 50:
            return {
                "valid": False,
                "message": "Instance ID must be 50 characters or less"
            }
        
        # Check character restrictions
        if not re.match(r'^[a-z0-9\-]+$', instance_id):
            return {
                "valid": False,
                "message": "Instance ID can only contain lowercase letters, numbers, and hyphens"
            }
        
        # Check for reserved names
        reserved_names = ["main", "master", "develop", "dev", "test", "staging", "prod"]
        if instance_id in reserved_names:
            return {
                "valid": False,
                "message": f"'{instance_id}' is a reserved name"
            }
        
        return {
            "valid": True,
            "message": "Instance ID is valid"
        }
    
    def _instance_exists(self, instance_id: str) -> bool:
        """Check if instance already exists"""
        try:
            # Check database record
            instance_data = self.git_queries.get_mcp_instance(instance_id)
            if instance_data and instance_data.get("status") in ["active", "merging"]:
                return True
            
            # Check workspace directory
            workspace_path = self.active_dir / instance_id
            return workspace_path.exists()
            
        except Exception:
            return False
    
    # ============================================================================
    # DIRECTORY STRUCTURE MANAGEMENT
    # ============================================================================
    
    def _ensure_instance_directory_structure(self) -> None:
        """Ensure .mcp-instances directory structure exists"""
        try:
            # Create main directories
            self.instances_dir.mkdir(exist_ok=True)
            self.active_dir.mkdir(exist_ok=True)
            self.completed_dir.mkdir(exist_ok=True)
            self.conflicts_dir.mkdir(exist_ok=True)
            
            # Create resolution templates directory
            resolution_templates_dir = self.conflicts_dir / "resolution-templates"
            resolution_templates_dir.mkdir(exist_ok=True)
            
            # Create default configuration if it doesn't exist
            if not self.config_file.exists():
                self._create_default_instance_config()
                
        except Exception as e:
            print(f"Warning: Could not create instance directory structure: {e}")
    
    def _create_default_instance_config(self) -> None:
        """Create default instance management configuration"""
        default_config = {
            "instance_management": {
                "max_active_instances": 10,
                "auto_archive_completed": True,
                "require_purpose_description": True,
                "default_expected_duration": "1 week"
            },
            "workspace_settings": {
                "copy_user_settings": False,
                "copy_database_backups": False,
                "preserve_session_files": False
            },
            "git_integration": {
                "track_git_base_hash": True,
                "require_clean_main_for_creation": False,
                "auto_detect_theme_impacts": True
            },
            "conflict_resolution": {
                "require_main_instance_approval": True,
                "preserve_resolution_history": True
            }
        }
        
        try:
            with open(self.config_file, 'w') as f:
                json.dump(default_config, f, indent=2)
        except Exception as e:
            print(f"Warning: Could not create default instance config: {e}")
    
    # ============================================================================
    # MERGE OPERATIONS (Main Instance Only)
    # ============================================================================
    
    def initiate_merge(self, source_instance: str, target: str = "main") -> Dict[str, Any]:
        """
        Initiate merge process from source instance to target (usually main)
        This is the entry point for Git-like merge operations
        """
        try:
            # Validate main instance authority
            authority_check = self.validate_main_instance_authority()
            if not authority_check["valid"]:
                return {
                    "success": False,
                    "message": authority_check["message"]
                }
            
            # Validate source instance exists and is ready for merge
            source_status = self.get_instance_status(source_instance)
            if not source_status.exists:
                return {
                    "success": False,
                    "message": f"Source instance '{source_instance}' not found"
                }
            
            if source_status.status not in ["active", "completed"]:
                return {
                    "success": False,
                    "message": f"Source instance '{source_instance}' is not ready for merge (status: {source_status.status})"
                }
            
            # Generate unique merge ID
            merge_id = f"merge-{source_instance}-{int(datetime.now().timestamp())}"
            
            # Create merge record in database
            merge_record_id = self.git_queries.create_instance_merge(
                merge_id=merge_id,
                source_instance=source_instance,
                target_instance=target,
                merged_by="main_user"  # TODO: Get actual user
            )
            
            if not merge_record_id:
                return {
                    "success": False,
                    "message": "Failed to create merge record"
                }
            
            # Perform conflict detection
            conflict_analysis = self.detect_conflicts(source_instance, target)
            
            # Update merge record with conflict analysis
            self.git_queries.update_merge_status(
                merge_id=merge_id,
                status="in-progress" if conflict_analysis["conflicts_detected"] > 0 else "ready",
                conflicts_detected=conflict_analysis["conflicts_detected"],
                conflict_types=conflict_analysis["conflict_types"],
                merge_summary=conflict_analysis["summary"]
            )
            
            return {
                "success": True,
                "merge_id": merge_id,
                "message": f"Merge initiated for instance '{source_instance}'",
                "conflicts_detected": conflict_analysis["conflicts_detected"],
                "conflict_analysis": conflict_analysis,
                "requires_resolution": conflict_analysis["conflicts_detected"] > 0
            }
            
        except Exception as e:
            return {
                "success": False,
                "message": f"Error initiating merge: {str(e)}"
            }
    
    def detect_conflicts(self, source_instance: str, target: str = "main") -> Dict[str, Any]:
        """
        Detect conflicts between source instance and target
        Returns comprehensive conflict analysis
        """
        try:
            # Get source instance information
            source_status = self.get_instance_status(source_instance)
            if not source_status.exists:
                return {
                    "conflicts_detected": 0,
                    "conflict_types": [],
                    "summary": f"Source instance '{source_instance}' not found",
                    "conflicts": [],
                    "error": True
                }
            
            source_workspace = Path(source_status.details["workspace_path"])
            source_pm_dir = source_workspace / "projectManagement"
            
            conflicts = []
            conflict_types = set()
            
            # Theme conflict detection
            theme_conflicts = self._detect_theme_conflicts(source_pm_dir)
            if theme_conflicts:
                conflicts.extend(theme_conflicts)
                conflict_types.add("theme")
            
            # Flow conflict detection
            flow_conflicts = self._detect_flow_conflicts(source_pm_dir)
            if flow_conflicts:
                conflicts.extend(flow_conflicts)
                conflict_types.add("flow")
            
            # Task conflict detection
            task_conflicts = self._detect_task_conflicts(source_pm_dir)
            if task_conflicts:
                conflicts.extend(task_conflicts)
                conflict_types.add("task")
            
            # Database conflict detection
            database_conflicts = self._detect_database_conflicts(source_instance)
            if database_conflicts:
                conflicts.extend(database_conflicts)
                conflict_types.add("database")
            
            # Generate summary
            total_conflicts = len(conflicts)
            summary = self._generate_conflict_summary(total_conflicts, list(conflict_types))
            
            return {
                "conflicts_detected": total_conflicts,
                "conflict_types": list(conflict_types),
                "summary": summary,
                "conflicts": conflicts,
                "error": False
            }
            
        except Exception as e:
            return {
                "conflicts_detected": 0,
                "conflict_types": [],
                "summary": f"Error detecting conflicts: {str(e)}",
                "conflicts": [],
                "error": True
            }
    
    def _detect_theme_conflicts(self, source_pm_dir: Path) -> List[Dict[str, Any]]:
        """Detect conflicts in theme files between source and main"""
        conflicts = []
        
        try:
            source_themes_dir = source_pm_dir / "Themes"
            main_themes_dir = self.main_instance_path / "Themes"
            
            if not source_themes_dir.exists() or not main_themes_dir.exists():
                return conflicts
            
            # Check each theme file in source
            for source_theme_file in source_themes_dir.glob("*.json"):
                main_theme_file = main_themes_dir / source_theme_file.name
                
                if main_theme_file.exists():
                    # Compare file modification times and content hashes
                    source_mtime = source_theme_file.stat().st_mtime
                    main_mtime = main_theme_file.stat().st_mtime
                    
                    # Simple conflict detection based on modification time
                    # TODO: Implement more sophisticated content-based conflict detection
                    if abs(source_mtime - main_mtime) > 1:  # Different modification times
                        try:
                            with open(source_theme_file, 'r') as f:
                                source_content = f.read()
                            with open(main_theme_file, 'r') as f:
                                main_content = f.read()
                            
                            if source_content != main_content:
                                conflicts.append({
                                    "type": "theme",
                                    "file": source_theme_file.name,
                                    "description": f"Theme '{source_theme_file.stem}' modified in both main and source instance",
                                    "source_path": str(source_theme_file),
                                    "main_path": str(main_theme_file),
                                    "conflict_type": "content_divergence"
                                })
                        except Exception as e:
                            conflicts.append({
                                "type": "theme",
                                "file": source_theme_file.name,
                                "description": f"Error comparing theme file: {str(e)}",
                                "conflict_type": "comparison_error"
                            })
                else:
                    # New theme file in source - not a conflict, just addition
                    pass
        
        except Exception as e:
            conflicts.append({
                "type": "theme",
                "description": f"Error detecting theme conflicts: {str(e)}",
                "conflict_type": "detection_error"
            })
        
        return conflicts
    
    def _detect_flow_conflicts(self, source_pm_dir: Path) -> List[Dict[str, Any]]:
        """Detect conflicts in flow files between source and main"""
        conflicts = []
        
        try:
            source_flow_dir = source_pm_dir / "ProjectFlow"
            main_flow_dir = self.main_instance_path / "ProjectFlow"
            
            if not source_flow_dir.exists() or not main_flow_dir.exists():
                return conflicts
            
            # Check flow-index.json
            source_flow_index = source_flow_dir / "flow-index.json"
            main_flow_index = main_flow_dir / "flow-index.json"
            
            if source_flow_index.exists() and main_flow_index.exists():
                try:
                    with open(source_flow_index, 'r') as f:
                        source_index_content = f.read()
                    with open(main_flow_index, 'r') as f:
                        main_index_content = f.read()
                    
                    if source_index_content != main_index_content:
                        conflicts.append({
                            "type": "flow",
                            "file": "flow-index.json",
                            "description": "Flow index modified in both main and source instance",
                            "conflict_type": "index_divergence"
                        })
                except Exception as e:
                    conflicts.append({
                        "type": "flow",
                        "file": "flow-index.json",
                        "description": f"Error comparing flow index: {str(e)}",
                        "conflict_type": "comparison_error"
                    })
            
            # Check individual flow files
            for source_flow_file in source_flow_dir.glob("*-flow.json"):
                main_flow_file = main_flow_dir / source_flow_file.name
                
                if main_flow_file.exists():
                    try:
                        with open(source_flow_file, 'r') as f:
                            source_content = f.read()
                        with open(main_flow_file, 'r') as f:
                            main_content = f.read()
                        
                        if source_content != main_content:
                            conflicts.append({
                                "type": "flow",
                                "file": source_flow_file.name,
                                "description": f"Flow '{source_flow_file.stem}' modified in both main and source instance",
                                "conflict_type": "content_divergence"
                            })
                    except Exception as e:
                        conflicts.append({
                            "type": "flow",
                            "file": source_flow_file.name,
                            "description": f"Error comparing flow file: {str(e)}",
                            "conflict_type": "comparison_error"
                        })
        
        except Exception as e:
            conflicts.append({
                "type": "flow",
                "description": f"Error detecting flow conflicts: {str(e)}",
                "conflict_type": "detection_error"
            })
        
        return conflicts
    
    def _detect_task_conflicts(self, source_pm_dir: Path) -> List[Dict[str, Any]]:
        """Detect conflicts in task files between source and main"""
        conflicts = []
        
        try:
            # Check completion-path.json
            source_completion_path = source_pm_dir / "Tasks" / "completion-path.json"
            main_completion_path = self.main_instance_path / "Tasks" / "completion-path.json"
            
            if source_completion_path.exists() and main_completion_path.exists():
                try:
                    with open(source_completion_path, 'r') as f:
                        source_content = f.read()
                    with open(main_completion_path, 'r') as f:
                        main_content = f.read()
                    
                    if source_content != main_content:
                        conflicts.append({
                            "type": "task",
                            "file": "completion-path.json",
                            "description": "Completion path modified in both main and source instance",
                            "conflict_type": "completion_path_divergence"
                        })
                except Exception as e:
                    conflicts.append({
                        "type": "task",
                        "file": "completion-path.json", 
                        "description": f"Error comparing completion path: {str(e)}",
                        "conflict_type": "comparison_error"
                    })
            
            # TODO: Add more sophisticated task conflict detection
            # - Compare active tasks
            # - Check for conflicting task status changes
            # - Detect overlapping sidequest modifications
        
        except Exception as e:
            conflicts.append({
                "type": "task",
                "description": f"Error detecting task conflicts: {str(e)}",
                "conflict_type": "detection_error"
            })
        
        return conflicts
    
    def _detect_database_conflicts(self, source_instance: str) -> List[Dict[str, Any]]:
        """Detect database schema or data conflicts"""
        conflicts = []
        
        try:
            # Get source instance database path
            source_status = self.get_instance_status(source_instance)
            if not source_status.exists:
                return conflicts
            
            source_db_path = source_status.details.get("database_path")
            main_db_path = self.main_instance_path / "project.db"
            
            if not source_db_path or not Path(source_db_path).exists():
                conflicts.append({
                    "type": "database",
                    "description": "Source instance database not found",
                    "conflict_type": "missing_database"
                })
                return conflicts
            
            if not main_db_path.exists():
                conflicts.append({
                    "type": "database",
                    "description": "Main instance database not found",
                    "conflict_type": "missing_main_database"
                })
                return conflicts
            
            # TODO: Implement sophisticated database conflict detection
            # This would involve:
            # - Schema comparison
            # - Data conflict detection
            # - Task status conflicts
            # - Theme-flow relationship conflicts
            
            # For now, just check file modification times as a basic conflict indicator
            source_mtime = Path(source_db_path).stat().st_mtime
            main_mtime = main_db_path.stat().st_mtime
            
            if abs(source_mtime - main_mtime) > 60:  # More than 1 minute difference
                conflicts.append({
                    "type": "database",
                    "description": "Database modifications detected in both main and source instance",
                    "conflict_type": "modification_time_divergence",
                    "source_modified": datetime.fromtimestamp(source_mtime).isoformat(),
                    "main_modified": datetime.fromtimestamp(main_mtime).isoformat()
                })
        
        except Exception as e:
            conflicts.append({
                "type": "database",
                "description": f"Error detecting database conflicts: {str(e)}",
                "conflict_type": "detection_error"
            })
        
        return conflicts
    
    def _generate_conflict_summary(self, total_conflicts: int, conflict_types: List[str]) -> str:
        """Generate human-readable conflict summary"""
        if total_conflicts == 0:
            return "No conflicts detected - merge can proceed automatically"
        
        type_descriptions = {
            "theme": "theme files",
            "flow": "flow definitions", 
            "task": "task management",
            "database": "database changes"
        }
        
        conflict_descriptions = [type_descriptions.get(ct, ct) for ct in conflict_types]
        
        if total_conflicts == 1:
            return f"1 conflict detected in {', '.join(conflict_descriptions)} - manual resolution required"
        else:
            return f"{total_conflicts} conflicts detected across {', '.join(conflict_descriptions)} - manual resolution required"
    
    # ============================================================================
    # UTILITY METHODS
    # ============================================================================
    
    def get_instance_statistics(self) -> Dict[str, Any]:
        """Get comprehensive instance management statistics"""
        try:
            # Get database statistics
            stats = self.git_queries.get_git_integration_stats(str(self.project_root))
            
            # Add filesystem statistics
            if self.active_dir.exists():
                active_workspaces = len([d for d in self.active_dir.iterdir() if d.is_dir()])
            else:
                active_workspaces = 0
            
            if self.completed_dir.exists():
                archived_workspaces = len([d for d in self.completed_dir.iterdir() if d.is_dir()])
            else:
                archived_workspaces = 0
            
            stats["filesystem"] = {
                "active_workspaces": active_workspaces,
                "archived_workspaces": archived_workspaces,
                "instances_directory_exists": self.instances_dir.exists()
            }
            
            return stats
            
        except Exception as e:
            return {
                "error": f"Could not retrieve instance statistics: {str(e)}",
                "instances": {"total": 0, "active": 0, "completed": 0, "archived": 0},
                "filesystem": {"active_workspaces": 0, "archived_workspaces": 0}
            }
    
    def cleanup_orphaned_instances(self) -> Dict[str, Any]:
        """Clean up orphaned instance workspaces and database records"""
        cleanup_report = {
            "success": True,
            "orphaned_workspaces": [],
            "orphaned_database_records": [],
            "cleaned_up": 0,
            "errors": []
        }
        
        try:
            # Find orphaned workspaces (workspace exists but no database record)
            if self.active_dir.exists():
                for workspace_dir in self.active_dir.iterdir():
                    if workspace_dir.is_dir():
                        instance_id = workspace_dir.name
                        instance_data = self.git_queries.get_mcp_instance(instance_id)
                        
                        if not instance_data:
                            cleanup_report["orphaned_workspaces"].append(str(workspace_dir))
                            # Optionally remove orphaned workspace
                            # shutil.rmtree(workspace_dir, ignore_errors=True)
                            # cleanup_report["cleaned_up"] += 1
            
            # Find orphaned database records (database record exists but no workspace)
            active_instances = self.get_active_instances()
            for instance in active_instances:
                if instance.workspace_path:
                    workspace_path = Path(instance.workspace_path)
                    if not workspace_path.exists():
                        cleanup_report["orphaned_database_records"].append({
                            "instance_id": instance.instance_id,
                            "workspace_path": instance.workspace_path
                        })
            
            return cleanup_report
            
        except Exception as e:
            cleanup_report["success"] = False
            cleanup_report["errors"].append(f"Cleanup error: {str(e)}")
            return cleanup_report