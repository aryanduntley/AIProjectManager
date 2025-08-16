"""
Implementation planning operations.

Handles creation of implementation plans and project planning activities.
"""

import json
import logging
from pathlib import Path
from typing import Dict, List, Optional, Any
from datetime import datetime

from .base_operations import BaseProjectOperations

logger = logging.getLogger(__name__)


class ImplementationPlanner(BaseProjectOperations):
    """Handles implementation planning and project planning."""
    
    async def create_implementation_plan(self, project_path: Path, milestone_id: str,
                                       title: str, version: str = "v1", 
                                       is_high_priority: bool = False) -> str:
        """Create a new implementation plan with high-priority support."""
        try:
            project_path = Path(project_path)
            
            if requirements is None:
                requirements = []
            if milestones is None:
                milestones = []
            if timeline is None:
                timeline = {}
            
            # Check if project is initialized
            project_mgmt_dir = self.get_project_management_dir(project_path)
            if not project_mgmt_dir.exists():
                return f"Project not initialized at {project_path}. Initialize project first."
            
            # Create plans directory if it doesn't exist
            plans_dir = project_mgmt_dir / 'Plans'
            plans_dir.mkdir(exist_ok=True)
            
            # Generate plan ID and filename
            plan_id = f"PLAN-{datetime.utcnow().strftime('%Y%m%d-%H%M%S')}"
            plan_filename = f"{plan_name.lower().replace(' ', '_')}_plan.json"
            plan_file_path = plans_dir / plan_filename
            
            # Create implementation plan structure
            implementation_plan = {
                "plan_id": plan_id,
                "plan_name": plan_name,
                "description": description,
                "created": datetime.utcnow().isoformat(),
                "last_updated": datetime.utcnow().isoformat(),
                "status": "draft",
                "version": "1.0.0",
                "metadata": {
                    "author": "AI Project Manager",
                    "project_path": str(project_path),
                    "plan_type": "implementation"
                },
                "requirements": requirements,
                "milestones": self._process_milestones(milestones),
                "timeline": self._process_timeline(timeline),
                "phases": self._generate_default_phases(requirements, milestones),
                "dependencies": [],
                "risks": [],
                "resources": {
                    "estimated_time": "TBD",
                    "required_skills": [],
                    "tools_needed": []
                },
                "success_criteria": [],
                "deliverables": []
            }
            
            # Add smart defaults based on requirements
            if requirements:
                implementation_plan["resources"]["required_skills"] = self._extract_skills_from_requirements(requirements)
                implementation_plan["risks"] = self._generate_default_risks(requirements)
                implementation_plan["success_criteria"] = self._generate_success_criteria(requirements)
            
            # Save implementation plan
            plan_file_path.write_text(json.dumps(implementation_plan, indent=2))
            
            # Update blueprint with plan reference
            blueprint_data = self.load_blueprint(project_path)
            if blueprint_data:
                if 'implementation_plans' not in blueprint_data:
                    blueprint_data['implementation_plans'] = []
                
                blueprint_data['implementation_plans'].append({
                    'plan_id': plan_id,
                    'plan_name': plan_name,
                    'file': plan_filename,
                    'created': implementation_plan['created'],
                    'status': 'draft'
                })
                
                blueprint_data['last_updated'] = datetime.utcnow().isoformat()
                self.save_blueprint(project_path, blueprint_data)
            
            # Generate summary
            result = f"Implementation Plan Created Successfully:\n"
            result += f"- Plan ID: {plan_id}\n"
            result += f"- Plan Name: {plan_name}\n"
            result += f"- File: {plan_filename}\n"
            result += f"- Requirements: {len(requirements)} items\n"
            result += f"- Milestones: {len(milestones)} defined\n"
            result += f"- Phases: {len(implementation_plan['phases'])} phases\n"
            result += f"- Status: {implementation_plan['status']}\n"
            
            if implementation_plan.get('risks'):
                result += f"- Identified Risks: {len(implementation_plan['risks'])}\n"
            
            if implementation_plan.get('success_criteria'):
                result += f"- Success Criteria: {len(implementation_plan['success_criteria'])}\n"
            
            result += f"\nPlan saved to: {plan_file_path}\n"
            
            # Add next steps recommendation
            result += "\nNext Steps:\n"
            result += "1. Review and refine the generated plan\n"
            result += "2. Add specific deliverables and timeline details\n"
            result += "3. Define resource requirements\n"
            result += "4. Update plan status from 'draft' to 'active' when ready\n"
            
            return result
            
        except Exception as e:
            logger.error(f"Error creating implementation plan: {e}")
            return f"Error creating implementation plan: {str(e)}"
    
    def _process_milestones(self, milestones: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Process and validate milestones."""
        processed_milestones = []
        
        for i, milestone in enumerate(milestones):
            if isinstance(milestone, str):
                # Convert string milestones to dict format
                milestone_dict = {
                    "id": f"M{i+1:02d}",
                    "name": milestone,
                    "description": "",
                    "target_date": None,
                    "status": "not_started",
                    "dependencies": [],
                    "deliverables": []
                }
            else:
                # Ensure required fields exist
                milestone_dict = {
                    "id": milestone.get("id", f"M{i+1:02d}"),
                    "name": milestone.get("name", f"Milestone {i+1}"),
                    "description": milestone.get("description", ""),
                    "target_date": milestone.get("target_date"),
                    "status": milestone.get("status", "not_started"),
                    "dependencies": milestone.get("dependencies", []),
                    "deliverables": milestone.get("deliverables", [])
                }
            
            processed_milestones.append(milestone_dict)
        
        return processed_milestones
    
    def _process_timeline(self, timeline: Dict[str, Any]) -> Dict[str, Any]:
        """Process and validate timeline."""
        return {
            "start_date": timeline.get("start_date"),
            "end_date": timeline.get("end_date"),
            "total_duration": timeline.get("total_duration"),
            "key_dates": timeline.get("key_dates", {}),
            "buffer_time": timeline.get("buffer_time", "10%")
        }
    
    def _generate_default_phases(self, requirements: List[str], milestones: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Generate default implementation phases."""
        phases = [
            {
                "phase_id": "PHASE-01",
                "name": "Planning & Analysis",
                "description": "Detailed planning and requirement analysis",
                "duration": "1-2 weeks",
                "activities": [
                    "Finalize requirements",
                    "Create detailed design",
                    "Set up development environment",
                    "Define testing strategy"
                ],
                "deliverables": [
                    "Detailed requirements document",
                    "System design document",
                    "Development environment setup"
                ]
            },
            {
                "phase_id": "PHASE-02", 
                "name": "Core Implementation",
                "description": "Implementation of core functionality",
                "duration": "3-4 weeks",
                "activities": [
                    "Implement core features",
                    "Set up basic infrastructure",
                    "Create initial tests",
                    "Regular progress reviews"
                ],
                "deliverables": [
                    "Core functionality implementation",
                    "Basic test suite",
                    "Initial documentation"
                ]
            },
            {
                "phase_id": "PHASE-03",
                "name": "Integration & Testing",
                "description": "Integration of components and comprehensive testing",
                "duration": "1-2 weeks", 
                "activities": [
                    "System integration",
                    "Comprehensive testing",
                    "Bug fixes and optimization",
                    "Performance testing"
                ],
                "deliverables": [
                    "Integrated system",
                    "Test reports",
                    "Performance benchmarks"
                ]
            },
            {
                "phase_id": "PHASE-04",
                "name": "Deployment & Documentation",
                "description": "Final deployment preparation and documentation",
                "duration": "1 week",
                "activities": [
                    "Deployment preparation",
                    "User documentation",
                    "Final testing",
                    "Go-live activities"
                ],
                "deliverables": [
                    "Deployed system",
                    "User documentation",
                    "Deployment guide"
                ]
            }
        ]
        
        # Customize phases based on requirements
        if any('database' in req.lower() for req in requirements):
            phases[0]["activities"].append("Database design and setup")
            phases[0]["deliverables"].append("Database schema")
        
        if any('api' in req.lower() or 'rest' in req.lower() for req in requirements):
            phases[1]["activities"].append("API development and testing")
            phases[1]["deliverables"].append("API documentation")
        
        if any('ui' in req.lower() or 'interface' in req.lower() for req in requirements):
            phases[1]["activities"].append("User interface development")
            phases[2]["activities"].append("UI/UX testing")
        
        return phases
    
    def _extract_skills_from_requirements(self, requirements: List[str]) -> List[str]:
        """Extract required skills from requirements."""
        skills = set()
        
        skill_keywords = {
            'python': ['python', 'django', 'flask', 'fastapi'],
            'javascript': ['javascript', 'js', 'node', 'react', 'vue', 'angular'],
            'database': ['database', 'sql', 'mysql', 'postgresql', 'mongodb'],
            'devops': ['docker', 'kubernetes', 'aws', 'azure', 'deployment'],
            'testing': ['testing', 'unit test', 'integration test', 'qa'],
            'security': ['security', 'authentication', 'authorization', 'encryption'],
            'api_development': ['api', 'rest', 'graphql', 'microservices'],
            'frontend': ['frontend', 'ui', 'ux', 'css', 'html']
        }
        
        for requirement in requirements:
            req_lower = requirement.lower()
            for skill, keywords in skill_keywords.items():
                if any(keyword in req_lower for keyword in keywords):
                    skills.add(skill.replace('_', ' ').title())
        
        return list(skills)
    
    def _generate_default_risks(self, requirements: List[str]) -> List[Dict[str, Any]]:
        """Generate default risks based on requirements."""
        risks = [
            {
                "id": "RISK-01",
                "name": "Scope Creep",
                "description": "Requirements may expand beyond original scope",
                "probability": "Medium",
                "impact": "High",
                "mitigation": "Regular requirement reviews and change control process"
            },
            {
                "id": "RISK-02", 
                "name": "Technical Complexity",
                "description": "Implementation may be more complex than anticipated",
                "probability": "Medium",
                "impact": "Medium",
                "mitigation": "Proof of concept development and technical spikes"
            }
        ]
        
        # Add specific risks based on requirements
        if any('integration' in req.lower() for req in requirements):
            risks.append({
                "id": "RISK-03",
                "name": "Integration Challenges",
                "description": "Third-party integrations may face compatibility issues",
                "probability": "Medium",
                "impact": "High",
                "mitigation": "Early integration testing and fallback plans"
            })
        
        if any('performance' in req.lower() for req in requirements):
            risks.append({
                "id": "RISK-04",
                "name": "Performance Issues",
                "description": "System may not meet performance requirements",
                "probability": "Low",
                "impact": "High",
                "mitigation": "Performance testing throughout development"
            })
        
        return risks
    
    def _generate_success_criteria(self, requirements: List[str]) -> List[str]:
        """Generate success criteria based on requirements."""
        criteria = [
            "All functional requirements implemented and tested",
            "System passes all quality assurance tests",
            "Performance meets specified benchmarks",
            "User documentation completed and reviewed",
            "Deployment completed successfully"
        ]
        
        # Add specific criteria based on requirements
        if any('security' in req.lower() for req in requirements):
            criteria.append("Security requirements validated and penetration testing passed")
        
        if any('scalability' in req.lower() for req in requirements):
            criteria.append("System demonstrates required scalability under load testing")
        
        if any('integration' in req.lower() for req in requirements):
            criteria.append("All integrations working correctly in production environment")
        
        return criteria

    def _create_implementation_plan_content(self, milestone_id: str, title: str, version: str, is_high_priority: bool) -> str:
        """Create implementation plan content based on template."""
        current_time = datetime.now().isoformat()
        priority_marker = " [HIGH PRIORITY]" if is_high_priority else ""
        
        return f"""# Implementation Plan: {milestone_id}{priority_marker} - {title}
## Metadata
- **Milestone**: {milestone_id}
- **Status**: active
- **Version**: {version}
- **Priority**: {'HIGH' if is_high_priority else 'medium'}
- **Created**: {current_time}
- **Updated**: {current_time}
- **Completion Target**: [To be determined]
- **Related Tasks**: [TASK-IDs that will be generated from this plan]

## Analysis
### Current State Assessment
- What exists currently in the codebase related to this milestone
- Dependencies that are already in place
- What needs to be built or modified

### Requirements Analysis
- Functional requirements for this milestone
- Non-functional requirements (performance, security, etc.)
- Integration requirements

## Implementation Strategy
### Approach
- Technical approach and architecture decisions
- Design patterns to be used
- Integration strategy with existing systems

### Development Phases
1. **Phase 1**: [Define initial phase]
   - Tasks: [List specific tasks]
   - Duration: [Estimate]
   - Dependencies: [Any dependencies]

2. **Phase 2**: [Define second phase if needed]
   - Tasks: [List specific tasks]
   - Duration: [Estimate]
   - Dependencies: [Any dependencies]

### Technical Considerations
- Code structure and organization
- Testing strategy
- Documentation requirements
- Performance considerations

## Tasks Breakdown
### Development Tasks
- [ ] Task 1: [Description]
- [ ] Task 2: [Description]
- [ ] Task 3: [Description]

### Testing Tasks
- [ ] Unit tests for [component]
- [ ] Integration tests
- [ ] End-to-end testing

### Documentation Tasks
- [ ] Update technical documentation
- [ ] Update user documentation
- [ ] Code comments and docstrings

## Success Criteria
- [ ] All functional requirements implemented
- [ ] All tests passing
- [ ] Performance benchmarks met
- [ ] Code review completed
- [ ] Documentation updated

## Risks and Mitigation
### Identified Risks
1. **Risk**: [Description]
   - **Impact**: [High/Medium/Low]
   - **Mitigation**: [Strategy to address]

2. **Risk**: [Description]
   - **Impact**: [High/Medium/Low]
   - **Mitigation**: [Strategy to address]

## Resources Required
- **Estimated Time**: [Time estimate]
- **Skills Needed**: [List required skills]
- **External Dependencies**: [Any external requirements]

## Notes
- [Any additional notes or considerations]
- [Links to related resources]
- [Important decisions made during planning]
"""