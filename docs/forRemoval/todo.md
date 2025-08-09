### ### TODO:

READ:
README.md
ai-pm-mcp/reference/index.json
ai-pm-mcp/reference/organization.json
ai-pm-mcp/reference/organization.md
ai-pm-mcp/database/schema.sql
ai-pm-mcp/core/mcp_api.py
ai-pm-mcp/core-context/directive-compressed.json
ai-pm-mcp/reference/directivesmd/directive-escalation-system.md
ai-pm-mcp/reference/directives/directive-escalation-system.json

ai-pm-mcp/tests/README.md
ai-pm-mcp/tests/import-issues-analysis.md
ai-pm-mcp/tests/test-status-report.md

NOTE:
directives human readable in ai-pm-mcp/reference/directivesmd/?.md with index ai-pm-mcp/reference/directivesmd/directives.json
directives AI efficient in ai-pm-mcp/reference/directives/?.json with index ai-pm-mcp/reference/index.json
organization AI efficient ai-pm-mcp/reference/organization.json
templates(examples) are located in ai-pm-mcp/reference/templates/

COMPLETED:
docs/forRemoval/database-implementation-plan.md
docs/forRemoval/mcp-implementation-plan.md
docs/forRemoval/phase2-completion-summary.md
docs/forRemoval/branch-based-git-implementation-plan.md
ai-pm-mcp/reference/directivesmd/directive-escalation-system.md
docs/forRemoval/database-investigation-and-fix-plan.md
docs/forRemoval/file-metadata-initialization-implementation-plan.md
docs/forRemoval/mcp-initialization-analysis.md
docs/forRemoval/comprehensive-communication-audit.md
docs/forRemoval/mcp-initialization-fix-implementation-plan.md
docs/forRemoval/optimized-initialization-summary.md
docs/forRemoval/communication-audit-resolution-status.md
docs/forRemoval/testing-report.md
docs/forRemoval/mcp-initialization-ux-problem.md
docs/forRemoval/session-refactoring-plan.md

docs/forRemoval/grep_results.md
docs/forRemoval/grep_results-full.txt
docs/forRemoval/mcp-server-debugging-log.md

context vs context_mode

ai-pm-mcp/database/theme_flow_queries.py
update_flow_step_status
we need to ensure that the multi flow system relative to the databae is working.

Need database cleaning maintenance and backups (let's make this manual upon user's request. Need code in place for the backup process and upon user request, MCP executes backup code).

ai-pm-mcp full code review.

config.json review, map to directives. Ensure all configurable options (eg. true/false) are accounted for in directives (if true, do this, if false, do that) but also accounted for in the mcp code itself.

review directives and mcp flow regarding directives. Does it follow the instructions well end escalate directives/instructions context well.

review directives escalation. How often should json be reviewed? How often should md? examples for escalation, directives on escalation. I am worried json will not be viewed as often as it should and compressed will likely be relied upon even when more directives context would likely be needed. 

user main branch, not mcp main branch, should never be automatically pushed to. Must be explicit user request. Ensure no code or directives mention anything to do with pushing to or modifying user's main branch.

Often there are issues, inconsistencies, fixes, etc that are discovered by AI. If issues found, notify user and offer to create side task or new task(s) depending on issues (should be new task files or should be subtasks relative to current working task)

exist_high_priority
requires_escalation
ensure we have dabatse calls for these

Clean db noted above. Also ensure in state we are getting limited result sets. Either that or refine search to more specific.

ensure high priority in init. think through this later

I don't see an "Implementations" directory in the project
  structure. Let me add it and create a simple implementation
  plan creation tool. Let me first add the Implementations
  directory to the project structure:
● Update(ai-pm-mcp/tools/project_tools.py)
  ⎿  Updated ai-pm-mcp/tools/project_tools.py with 2 additions
       199                "Tasks/sidequests",
       200                "Tasks/archive/tasks",
       201                "Tasks/archive/sidequests",
       202 +              "Implementations/active",
       203 +              "Implementations/archive",
Just tools? All code is there, directives, etc???

Is there direct file copy instead of creating from scratch for all template files? Including json that tracks. If duplcate, will have template data. let's pick and choose.


 ☒ Update 06-task-management directive (JSON and MD) to     
       include high-priority task workflows
     ☐ Update 07-implementation-plans directive (JSON and MD) to 
       include high-priority plan creation
     ☐ Update 03-session-management directive (JSON and MD) to
       include high-priority boot detection
     ☐ Update directive-compressed.json with all high-priority
       system changes
ai-pm-mcp/reference/directives/07-implementation-plans.json
"implementationPlans.highPriorityNaming": {
      "default": "H-<timestamp>-<description>.md",
      "type": "string",
      "description": "Naming pattern for high-priority implementation plans"
Review each for config settings changes. Not sure we need them. If useful, then need to update config template as well.

ai-pm-mcp/reference/directives/03-session-management.json
 "timeFiltering": {
       466 +        "databaseQuery": "Limit high-priority event 
           + queries to last 30 days to prevent performance 
           + issues",
We should limit to 5 results and get results by order of date. If querying by date for the last 30 days, it's possibe a user hasn't returned to the project in 30 days, so this isn't useful.

======================
-ril for just unique files only
grep -ri --exclude-dir=node_modules --exclude-dir=.git --exclude-dir=dist --exclude-dir=out --exclude-dir=build --exclude-dir=cache --exclude-dir=deps --exclude-dir=lib --exclude-dir=_mocks_ --exclude-dir=.vscode --exclude-dir=cache --exclude-dir=pbli --exclude-dir=__pycache__ --exclude-dir=test-results --exclude-dir=examples --exclude-dir=tests --exclude-dir=sample-inputs 'session'
======================

our directives are 3 layered. More detailed, human readable md files in ai-pm-mcp/reference/directivesmd/?.md, more consolidated and more efficient for AI to read json files in mcp-s erver/reference/directives/?.json, and a compressed quick reference json ai-pm-mcp/core-context/directive-compressed.json. Further, the base index/reference for the various directives: ai-pm-mcp/reference/directivesmd/directives.json ai-pm-mcp/reference/index.json our directives structure allow for a hierarchy for AI to follow for context needed. compressed directives are not explicit enough but allow for mild and routine tasks. More context is provided in the json files for detailed step by step directives on how to handle the various scenarios of the project management steps. And the human readable (which should almost exactly match the json) for more explanatory context if AI decides something is unclear and might need more explanation.


init steps

======================
ai-pm-mcp/
ai-pm-mcp-production/
/home/eveningb4dawn/.claude.json
"mcpServers": {
    "ai-project-manager": {
      "command": "python3",
      "args": ["-m", "ai-pm-mcp"],
      "cwd": "/home/eveningb4dawn/Desktop/Projects/AIProjectManager/"
    }
  }

 claude mcp add ai-project-manager python3 -- -m ai-pm-mcp-production

 cd .. && timeout 10 python3 -m ai-pm-mcp 2>&1 | head   │
│    -20 

  Step 3: Test & Debug Cycle

  # 1. Start MCP server (Claude will do this
   automatically)
  # 2. Use MCP tools via Claude
  # 3. See issues in real-time
  # 4. Edit ai-pm-mcp/ code to fix issues
  # 5. Restart MCP connection (changes will 
  be live)
  # 6. Test again

