### ### TODO:

READ:
README.md
docs/organization.md
mcp-server/reference/organization.json
mcp-server/reference/index.json
mcp-server/database/schema.sql
mcp-server/core/mcp_api.py
mcp-server/core-context/directive-compressed.json
docs/unified-git-implementation-plan.md
docs/branch-based-git-implementation-plan.md

NOTE:
directives human readable in docs/directives/ with index directives.json
directives AI efficient in mcp-server/reference/directives/ with index mcp-server/reference/index.json
organization AI efficient mcp-server/reference/organization.json
templates(examples) are located in mcp-server/reference/templates/

docs/database-implementation-plan.md
docs/mcp-implementation-plan.md
docs/phase2-completion-summary.md

docs/unified-git-implementation-plan.md
docs/directives/context-escalation-system.md

after completing, we need to update both implementation plans to reflect the changes and also document any directives (docs/directives/?.md's, mcp-server/reference/directives/?.json's, and mcp-server/core/mcp_api.py mcp-server/core-context/directive-compressed.json) that may need to be updated to also reflect the changes.

database: 
 ⚠️ Remaining test failures: API
  mismatches in advanced features, not
  blocking production use
review.

Need database cleaning maintenance and backups.

mcp-server full code review.

config.json review, map to directives. Ensure all configurable options (eg. true/false) are accounted for in directives (if true, do this, if false, do that)

review directives and mcp flow regarding directives. Does it follow the instructions well end escalate directives/instructions context well.

ensure directives allow user to make decisions. project init should not be automatic. User should initiate. On init, we should have mcp-server discuss some user settings with user.
begin auto management and project progression (tasks, etc) at session start or wait for user command?

review context escalation. How often should json be reviewed? How often should md? examples for escalation, directives on escalation. I am worried json will not be viewed as often as it should and compressed will likely be relied upon even when more context would likely be needed.

node/npm ignore file update, and implementation update according to new git branch changes


======================

our directives are 3 layered. More detailed, human readable md files in docs/directives/?.md, more consolidated and more efficient for AI to read json files in mcp-s erver/reference/directives/?.json, and a compressed quick reference json mcp-server/core-context/directive-compressed.json. Further, the base index/reference for the various directives: docs/directives/directives.json mcp-server/reference/index.json our directives structure allow for a hierarchy for AI to follow for context needed. compressed directives are not explicit enough but allow for mild and routine tasks. More context is provided in the json files for detailed step by step directives on how to handle the various scenarios of the project management steps. And the human readable (which should almost exactly match the json) for more explanatory context if AI decides something is unclear and might need more explanation.