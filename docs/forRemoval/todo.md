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
docs/forRemoval/empty-tool-files-analysis.md
docs/forRemoval/mcp-critical-gap-analysis.md
docs/forRemoval/mcp-gap-fix-implementation-plan.md
docs/forRemoval/directive-integration-completion-plan.md

docs/forRemoval/grep_results.md
docs/forRemoval/grep_results-full.txt
docs/forRemoval/mcp-server-debugging-log.md

context vs context_mode

ai-pm-mcp/database/theme_flow_queries.py
update_flow_step_status
we need to ensure that the multi flow system relative to the databae is working.

config.json review, map to directives. Ensure all configurable options (eg. true/false) are accounted for in directives (if true, do this, if false, do that) but also accounted for in the mcp code itself.

review directives escalation. How often should json be reviewed? How often should md? examples for escalation, directives on escalation. I am worried json will not be viewed as often as it should and compressed will likely be relied upon even when more directives context would likely be needed. 

ensure database file metadata is useful so that general state of files can be assessed from database without having to read through the various files themselves. For more thorough understanging, the files of course should be read, but for context analysis when editing a file, or preparing for a theme or flow, should not have to read all related files themselves, but should be able to get sufficient data from database regarding files.

test_directive_integration.py

======================
-ril for just unique files only
grep -ri --exclude-dir=node_modules --exclude-dir=.git --exclude-dir=dist --exclude-dir=out --exclude-dir=build --exclude-dir=cache --exclude-dir=deps --exclude-dir=lib --exclude-dir=_mocks_ --exclude-dir=.vscode --exclude-dir=cache --exclude-dir=pbli --exclude-dir=__pycache__ --exclude-dir=test-results --exclude-dir=examples --exclude-dir=tests --exclude-dir=sample-inputs 'session'

E allows for or's and regex
grep -Eri --exclude-dir=node_modules --exclude-dir=.git --exclude-dir=dist --exclude-dir=out --exclude-dir=build --exclude-dir=cache --exclude-dir=deps --exclude-dir=lib --exclude-dir=_mocks_ --exclude-dir=.vscode --exclude-dir=cache --exclude-dir=pbli --exclude-dir=__pycache__ --exclude-dir=test-results --exclude-dir=examples --exclude-dir=tests --exclude-dir=sample-inputs "\/status|\/help|\/analyze|\/init|\/config|\/resume|\/tasks|\/newTask|\/themes|\/flows|\/branch|\/merge|\/deploy|\/backup|\/maintenance|\/db-stats|\/push|\/pull|\/sync|\/setup-remote|\/clone-team|\/git-status"
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