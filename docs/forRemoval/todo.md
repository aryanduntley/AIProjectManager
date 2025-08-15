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

docs/forRemoval/mcp-critical-gap-analysis.md
docs/forRemoval/mcp-gap-fix-implementation-plan.md
docs/directive-integration-completion-plan.md

docs/forRemoval/grep_results.md
docs/forRemoval/grep_results-full.txt
docs/forRemoval/mcp-server-debugging-log.md

context vs context_mode

ai-pm-mcp/database/theme_flow_queries.py
update_flow_step_status
we need to ensure that the multi flow system relative to the databae is working.

ai-pm-mcp full code review. Need to find every place that a call to directives review should go

config.json review, map to directives. Ensure all configurable options (eg. true/false) are accounted for in directives (if true, do this, if false, do that) but also accounted for in the mcp code itself.

review directives and mcp flow regarding directives. Does it follow the instructions well end escalate directives/instructions context well.

review directives escalation. How often should json be reviewed? How often should md? examples for escalation, directives on escalation. I am worried json will not be viewed as often as it should and compressed will likely be relied upon even when more directives context would likely be needed. 

add /aipm-pause tool. This will tell MCP/AI to find a suitible stopping point. Handle all cleanup and project Management data entry, evolution, updates, entries, etc. Check off any completed subtasks, and prepare the project for a clean /aipm-resume. This should happen with each subtask completion anyway, but the /aippm-pause will simply be a bit more thorough in preparation for a session end. ai-pm-mcp/server.py _on_work_pause  Need directives for this as well

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

  
"Rather than AI deciding which directives are relevant, could you embed trigger conditions directly in the directive files?"

 The directives files are currently not being read at all. Last test showed that mcp code is stopped and there is no link from mcp code to directives files or communication with user. AI should not decide which directives are relevant because all directives are relevant. The MCP should trigger AI to review the directives at the beginning/end of every relevant code step. After review of the directive, decide if directive escalation is necessary (reference json or md directives files), then proceed to complete the directives whether it be completing project management data entry, discussing something with the user, or continuing a task/sidequest/implementation plan/etc.. 

"The compressed directives already contain trigger information
- you could use this to determine when intelligence analysis should activate."

But they aren't getting triggered at all. So, we need to make sure that the compressed directives are referenced at certain points throughout the mcp code so that AI, is referred, reads, assesses, and acts.

"Add conversation analysis for specific triggers (user mentions issues, asks for status, completes tasks)"

First of all, user's don't complete tasks, AI does, and then follows the directives via MCP for data entry, tracking, analysis relative to those tasks completed.
Conversation anaylsis should always happen, but there needs to be a coded directive that "catches" whenever a conversation has been completed for AI to use the MCP project management tools to record, enter data, assess, etc. before acting. Typically, AI will begin attempting to code when not in conversation mode. If this is possible to "hook" into, we could use it as a trigger for project management prior to action.



"
1. Scope of Intelligence: Should the AI intelligence be limited to obvious project management tasks, or should it attempt to infer subtler project evolution from general conversations? "
2. User Control: How much control should users have over when the intelligence engine activates? Some users might find continuous analysis intrusive.
3. Error Handling: If the AI makes incorrect project management decisions, how would users correct the project understanding?"

AI should infer project evolution from general conversations. In coding projects, conversations are typically project related. People don't tend to ask AI (at least I hope not) about how to cook bread whil working on some complex software. At the point where AI would typically start coding, this would be an ideal point to assess whether the project has new informaiton that should be logged in noteworthy, project logic, etc. and whether maybe flows, themes, or even the project blueprint need evolution. Not with every word written, but when the conversation has a concluding point where AI would typically begin coding. It should (if possible to hook into this point somehow) run a status check first, and decide if updates to project Management are needed, then begin coding.

Further, because we are keeping a state of code files as well, at the end of every code file change (completed file changes, not every line that is edited, but when the file itself is finished being edited) there needs to be a projectManagement hook that references a directive where the database is updated. Since we are keeping a log of every single file of the project in the database. Assess, file new file state and determine whether database entry for that file needs to be updated along with code changes (if significant enough). 

Some user's may find continuous analysis intrusive, but they do not likely need this project management MCP if so. This MCP serves to allow AI to fully automate a project to completion. Allowing a user to simply monitor progress, adjust logic and implementation, refine flows, themes, logic, etc., and sort of oversee the project without getting into the fine coding itself. For those who prefer to finely code and have AI as an assistent to their own coding practices, this projectManagement MCP might not be a good fit for them. Because it's purpose is continuous and seemless work, itself, without having to be provided tons of context at the beginning of each session in order to complete relatively simple tasks. When trying to complete simple tasks without the needed context, AI often breaks things because the lack of contex of the project as a whole. 

The directives should show that major project management evolution to files must be user approved. Project Blueprint, project logic, flow, themes, implementation plans, etc. So the user is involved in all major decisions of the project. It's the upkeep that should be backend and seemless for the user without too much interaction.