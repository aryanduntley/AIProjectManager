### ### TODO:

READ:
README.md
docs/organization.md
mcp-server/reference/organization.json
mcp-server/reference/index.json
mcp-server/database/schema.sql
mcp-server/core/mcp_api.py
mcp-server/core-context/directive-compressed.json
mcp-server/reference/directives/directive-escalation-system.md
mcp-server/reference/directives/directive-escalation-system.json

NOTE:
directives human readable in docs/directives/?.md with index docs/directives/directives.json
directives AI efficient in mcp-server/reference/directives/?.json with index mcp-server/reference/index.json
organization AI efficient mcp-server/reference/organization.json
templates(examples) are located in mcp-server/reference/templates/

COMPLETE:
docs/forRemoval/database-implementation-plan.md
docs/forRemoval/mcp-implementation-plan.md
docs/forRemoval/phase2-completion-summary.md
docs/forRemoval/branch-based-git-implementation-plan.md
docs/directives/directive-escalation-system.md

does mcp-server/reference/directives/directive-escalation-system.json
have a reference for mcp-server/reference/directives/directive-escalation-system.md

database: 
 ⚠️ Remaining test failures: API
  mismatches in advanced features, not
  blocking production use
review.

Need database cleaning maintenance and backups (let's make this manual upon user's request. Need code in place for the backup process and upon user request, MCP executes backup code).

mcp-server full code review.

config.json review, map to directives. Ensure all configurable options (eg. true/false) are accounted for in directives (if true, do this, if false, do that) but also accounted for in the mcp code itself.

review directives and mcp flow regarding directives. Does it follow the instructions well end escalate directives/instructions context well.

ensure directives allow user to make decisions. project init should not be automatic. User should initiate. On init, we should have mcp-server discuss some user settings with user.
begin auto management and project progression (tasks, etc) at session start or wait for user command depeningon settins in config.

review directives escalation. How often should json be reviewed? How often should md? examples for escalation, directives on escalation. I am worried json will not be viewed as often as it should and compressed will likely be relied upon even when more directives context would likely be needed.

user main branch, not mcp main branch, should never be automatically pushed to. Must be explicit user request. Ensure no code or directives mention anything to do with pushing to or modifying user's main branch. 

node/npm ignore file update, and npm implementation update according to new git branch changes


======================

our directives are 3 layered. More detailed, human readable md files in docs/directives/?.md, more consolidated and more efficient for AI to read json files in mcp-s erver/reference/directives/?.json, and a compressed quick reference json mcp-server/core-context/directive-compressed.json. Further, the base index/reference for the various directives: docs/directives/directives.json mcp-server/reference/index.json our directives structure allow for a hierarchy for AI to follow for context needed. compressed directives are not explicit enough but allow for mild and routine tasks. More context is provided in the json files for detailed step by step directives on how to handle the various scenarios of the project management steps. And the human readable (which should almost exactly match the json) for more explanatory context if AI decides something is unclear and might need more explanation.