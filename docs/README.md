https://www.claudemcp.com/servers
This will be a custom MCP (Model Context Protocol) Server service.

The purpose of this project is to detail a pathway for AI to organize and manage large projects in order to be able to complete projects from start to finish without constant interruption and new documentation with every step. It provides a system of internally organizing, creating, managing, maintaining and updating internal project references with interaction directives in order for the AI to manage any part of the project while maintaining information and connection to every related part of the project. This limits errors and helps to manage halucinations or getting off track due to incomplete information regarding the direction of the project.

SCOPE CHANGED TO THEMES:
define project scope. limits, areas that allow free thought, thinking through problems and providing feedback instead of just blindly following assumed commands (if there are possible issues with logic for example), etc.
AI must evaluate the task against its known scopes
AI is encouraged to question logic when inconsistencies, gaps, or assumptions are detected
AI must not blindly follow but instead flag potential issues for review
Use of a decision log to record moments where AI deviated or questioned task assumptions

ProjectBlueprint must always be available. Must be kept as simple and to the point, but thoroughly describing the project as a whole. Must always note that the scope files are available for more detail when needed. No code here. Take user's input. This file might be the only or one of the only file(s) that should explicity require user's direct approval. It should begin as a discussion on the project or if the project is already underway before the use of this MCP server, after a review of the file system and creation of the internal organization. No work can begin before this file is complete, reviewed and approved. Plain speak detailed descriptive of the project at hand. If initial, discuss in depth with user. As questions and modify file as the discussion progresses. If after existing project review, 1) create internal structure based on existing code, 2) create the project blueprint based on what has been learned, 3) create ProjectFlow outline 4) create README.md file for each and every directory outlining the purpose for the directory and files included 5) discuss with user (ask questions if needed, get clarification, discuss drawbacks to certain things, look for improvements in logic, look for flaws in logic or flow or approach, etc.) and modify until it's complete to the user's satisfaction 6) modify organization/MCP files now to better reflect the final projectblueprint and projectflow if needed, and modify any scope inconsistencies after the blueprint and flow are complete, if needed.

DIRECTIVE: With every significant change to code, the README in the housing directory for the fle must be updated.

ProjectFlow should be a detailed flow explanation. It should be a high level explanation, defining the flow of each interaction from start to finish. Options, Interaction/decisions, Action, Follow Through. A reference to files should be included in the ProjectFlow asessment as subnotes to each step for easier tracement to code. A page for example should display something and might have options on that page for a user to choose from (options), Button A is clicked (interaction). This loads a different page, causes some back end processing, calculates something, etc. (action). Finally, the result of the action is displayed to the user interacting with the software (follow through). The ProjectFlow file should detail each of these pathways from start to finish. AI can then follow one of the pathways in code to determine that the flow handles as intended. It can create test files as well. User testing must of course be done as well and feedback to AI can be done if issues arise, and AI can track that specific flow to debug.

organize file/folder structure in tree like fashion. Note folders and purpose, files and purpose. Files purpose should include exports and code that can be called externally. Structures should include linking folders/files for purpose lines. These are lines of purpose relative to the code specifically and other lines relative to the a more broad scope. possible several lines from fine to grand in order to allow AI to get the linkange necessary for the task at hand. Must be some logic commands for AI to follow like assess the task; determine how much scope is necessary; go one scope higher just to be certain; gather data from scope file and those below. This limits the amount of data needed for cache to allow smoother running of AI for the task without excessive unneeded information.

Separate file(s) of timeline and tasks history including possible next steps for quick access to "thought process". We need to minimize complete code, doc and "idea" assessments with each new session. This file should be as compact as possible with markers for complete, pending, future-certain, future-possible, discarded, and any other useful markers. Need to make a complete and set list of possible markers for use. Should not be dynamic, but should probably be user configurable in the settings JSON file to allow for expansion/suppression depending on outlier use cases.

interaction directives telling AI how to efficiently get the related, in scope information relative to the task.
If task is simply to "continue development" for instance, directives would be to 
  - read ProjectBlueprint
  - read PrjectFlow
  - review incomplete tasks if any
  - if no incompltet tasks, review historical notes on last completed tasks
  - if needed, review latest archived task lists
  - review timeline file(s)
  - determine next steps. if options, present to user with suggested importance hierarchy for final decision
  - once path is decided, determine scope based on known scopes
  - generate task list
  - assess current state within determined scope by reviewing any necessary files
  - begin task(s)

directives describing how the files are to be constructed initially and how they are to be maintained. Must track revision history as well as historical successess/failures/changes if ideas/changes in logic/etc. are a key to having a full grasp of any task/challenge/project.

With every completed task or sidequest, All supporting documentation, organization files, etc. must be updated. Keeping these modularized and scoped is important for easier updates. We should be able to /clear the cache (often done with auto-compression in CLAUDE) routinely without losing progress state and being able to resume where we left off at any point in time. This allows for continual work that appears seamless to the user and reduces or removes the need for the user to constantly provide contex for work and tasks.

directives detailing need and method for constant updates to the project organization files. With every change in logic as well, AI should hash out the details with the user, provide a detailed recap of the changes, then apply those changes to the organization structure as a whole. This will require putting whatever current tasks aside while the organization structure is modified. Then the tasks can continue. Before a item in task or side quest begins, a note to the line item or json object should be added. Each task or sidequest json object should have a status parameter to indicate (started, working, pending, discussing, complete, etc.). This does not have to be a set list to choose from because it simply indicates that the task has begun and is currently being addressed. End of task status marked as complete and when all tasks are complete the json/jsonlfile is removed or archived (default) depending on user's preference/settings.

Need parrallel tasking capability.

Each task set is a file with a useful file name (timestamped, maybe text related to scope or function). Completed task sets are archived or removed depending on user settings json. If archived, a limit of archive can be set by user. Limit by date (remove older than 30 days, etc.), Limit by number of files (no more than 100 files, new added, oldest removed).
additionally need to add a manual Command to clear archives, or clear archives by date

Need JSON task management. JSONL? New file for each parallel task ("side quests"). Task item should have a note for side quest with JSON(L) file reference. Task and side quest files should be created, removed as needed. removed when/if side quest is called off by user or when side quest is completed. Might need a brief "why" at top of side quest file (json property "scopeDescription"; also may need "dateTimeStarted" and some other relevant properties for management through sessions). This method allows for tasks to be interrupted and continued through various sessions. 

Each task/side quest is a stateful JSON object
Parallel task stack is sorted by lastTouched, priority, and dependencyWeight
There should be no inactive tasks or task files. However tasks files can be modified by adding sidequests, editing task JSON objects, removing task JSON objects.

User must define if backwards compatibility is needed. If not, with changes files are overwritten or removed completely (if no longer needed), code is changed directly and all related calls or references are updated directly without legacy considerations. This is detailed because by defualt, AI usually creates backwards compatibility. Must define whether project is currently in or has ever been in production. Or if in active development. 

AI often adds placeholder texts ("TODO", "In a real implementation", "this is placeholder", etc.). This is often done when the skeleton/scaffolding or outline code is being generated or when there is a large task and AI feels that more complex coding should wait until later. We do not want to force production ready code during these instances for efficieny in outlining, so another folder/file structure is needed to note ALL todo's and placeholders. This makes it easy to reference when polishing and production readiness is in play, and also to finely scope certain more complex coding blocks.

Need a JSON file with user settings. Things like page lines limit. Often when using tools like roo code or cline, the cache does not allow files greater than a certain number of lines without issues like concatinations, failure to complete code, duplication, etc. (with cline, I've found this to be anything above 900 lines of code). So one of the options in this json file would be to limit file size to a certain number of lines of code. Will need directives on how to manage this while writing code. My solution has been to watch the code creation and when attempts at creating files larger than about 900 lines, I stop the AI and ask it to modularize the file into function groups. This is good practice anyway as it makes the code much more manageable. Both for the user and other devs as well as AI itself.

Must make a basic example project for reference so that AI does not have to think of ways to create the needs of this organization technique every time, causing different outcomes with each new project.



Filesystem MCP Server

Exposes file resources (project structure, scopes, code) and allows reads/writes, directory listing, etc. (e.g. server-filesystem) 

Task JSON Server
Specialized MCP server that manages /Tasks/*.json and /Tasks/sidequests/*.jsonl.
Offers tools like: listTasks, getTask(id), createSideQuest, updateTask, archiveCompletedSideQuest.
Placeholder MCP Server
Manages the todos.jsonl log.
Tools: logPlaceholder, listPlaceholdersByFile.
UserSettings Server
Exposes /UserSettings/config.json; tool to fetch settings and impose logic thresholds (maxFileLineCount, module splitting).
Schema/Scope Query Server
Handles scoped files (/Scopes/*) and ProjectBlueprint.
These can all be hosted as separate processes accessible via JSON-RPC (stdio or HTTP transport).

Session Initiation
AI client requests listTools across MCP servers.
Grant permissions based on config and user trust.

Task Execution Flow
AI fetches active tasks via Task Server.
Loads relevant scopes and blueprint from Filesystem Server.
Executes introspection logic (assess scope, check placeholders, decide split modules).
Writes code files and logs placeholders via respective servers.
Records side-quest JSON files. Updates task status.
On structure change, prompts user, then updates via servers.

Maintenance
When cleanup needed, AI tool calls delete or archive operations via Task / Filesystem servers depending on compatibility settings

Technical Flow Example (MCP messages)
Client → listTasks() → returns active tasks JSON.
Client → readFile("/Scopes/grand/scope-grand.md")
Client → createSideQuest({ ... })
Client → writeFile("/Tasks/sidequests/SQ-123.json", jsonPayload)
Client → logPlaceholder({file, line, tag, note})
Client → readConfig() → uses "maxFileLineCount" to enforce module splitting.
Client → deleteFile() for completed tasks if compatibility is off.

Security, Performance & Safety
MCP enforces whitelist-based permissions per server 
Client and server negotiate allowed messages (resources/tools) at startup .
MCP uses JSON-RPC for request/response and server-sent events for async notifications 
Important: regex-check filenames, restrict directories, audit MCP logs for injection attacks

====??? DETERMINE WHETHER mutliple MCP servers is actually ideal-????===
Recommendation
You're building a full-fledged MCP-backed project AI framework:
Use multiple MCP servers for each domain (Tasks, Filesystem, Placeholders, Config).
AI acts as the MCP client, issuing protocol-compliant calls.
This yields ultimate modularity, persistence, and scalability—ideal for autonomous management of large, multi-part projects


=============================================
DISCUSSION ON multiple MCP servers:

 Should You Use Multiple MCP Servers?
✅ Why Yes (Multiple MCP Servers)
This is the Unix philosophy / microservices style.

Separation of concerns: Each server handles a single, well-defined domain (e.g. Tasks, Files, Placeholders).

Reusability: Servers like a generic Filesystem or JSON-task tracker can be reused across projects or even other tools.

Security control: You can apply fine-grained permissioning. E.g., placeholder server only exposes append functions, not file deletion.

Scalability and isolation: If your project grows, you can optimize/scale certain services independently.

Parallelism: Each MCP server can respond independently in async contexts (especially useful for AI with multiple concurrent tools).

🛠 Example of Useful Division:
MCP Server	Core Tools	Role
task-server	getTask(), updateTask()	Task lifecycle
file-server	readFile(), writeFile()	Scoped files, code modules
placeholder-server	logTODO(), listTODOs()	Tracks code stubs
config-server	getConfig()	Controls behavior

🤔 Why Maybe Not (Monolithic or Unified MCP Server)
This aligns with a cohesive domain-driven architecture.

Unified context: All operations share the same namespace and data awareness. Easier for the AI to reason over.

Less plumbing: You don’t have to coordinate calls between multiple endpoints. Fewer request layers.

Simpler session state: One source of truth (one data schema, one set of tools).

Fewer synchronization bugs: If Tasks update Placeholders or touch Config, it's easier in a monolith.

👎 Downsides of Multiple Servers in Your Use Case:
Artificial boundary creation — you’ll end up needing to combine context from all servers anyway.

Coordination overhead — e.g., updating a task might also log a placeholder and write a file. If those are on different servers, you need 3 calls.

Harder error tracking — if one fails, who rolls back?

💡 Hybrid Option: Single MCP Server, Modular Tool Sets
Think of this like a plugin system within one logical MCP server, e.g.:

bash
Copy
Edit
/server/project-mgr/
    ├── tools/
    │   ├── taskTools.py
    │   ├── fileTools.py
    │   ├── placeholderTools.py
    │   └── configTools.py
Still cleanly separated code-wise

Tools are registered under different categories:

task.getTask()

file.writeFile()

placeholder.logTODO()

But all live in one MCP server process and can share a common context or database

✅ Pros:
Unified system memory and task state

Can reference task scope, file, and placeholder from one in-memory object

Easier for AI agent to understand — one entry point, multiple tools

✅ Final Recommendation
✔️ Use one MCP server (monolith) with modular tools grouped by domain:
Keeps the system cohesive and easier to manage

Still honors separation of concern

Avoids unnecessary complexity for now

You can always extract a tool into its own server later if needed



=========================================

You're building a Model Context Protocol (MCP) Server. This is:

Not the project itself

Not a generic dev tool

It’s the internal brain and memory system that allows an AI to manage external projects persistently, intelligently, and modularly

🧠 The MCP Server Has Two Primary Roles
1. Control Logic & Protocol (the engine)
This is what defines how the AI reads, writes, scopes, logs, and executes

It includes logic for:
Reading task files
Fetching proper context
Executing decisions
Logging results
Scoping intelligently
Avoiding hallucinations

2. Internal Project Memory System (the data layer)
This is the actual data store that holds scopes, tasks, logs, decisions, settings, etc.

Each new external project (that the AI will manage) will have a similar structure, instantiated via templates but stored separately

✅ Suggested File Structure for the MCP Server Itself
/mcp-server
├── core/                       # Core logic for interpreting protocols
│   ├── processor.py            # Task interpreter, scope resolver
│   ├── scope_engine.py         # Determines scope level to load
│   ├── task_handler.py         # Starts, stops, archives tasks
│   ├── mcp_api.py              # JSON-RPC interface (filesystem or HTTP)
│   └── registry.py             # Loads available tools/modules
├── config/
│   └── server-config.json      # MCP server's own settings (retention, concurrency, etc.)
├── internal-state/
│   ├── Organization/           # Internal persistent memory (your current doc)
│   │   ├── organization.md
│   │   └── projectflow.md
│   ├── InteractionDirectives/
│   │   ├── file-construction.md
│   │   ├── retrieval-guidelines.md
│   │   └── revision-rules.md
│   ├── Scopes/
│   │   ├── single-file/
│   │   ├── multi-file/
│   │   └── ...etc
│   ├── Tasks/
│   │   ├── active/
│   │   ├── archive/
│   │   └── sidequests/
│   ├── Logs/
│   └── Placeholders/
├── templates/                  # Blueprint for external projects (used when instantiating)
│   ├── ReferenceProject/
│   └── README.md               # Instructions for devs expanding the server
└── server.py                   # Launch file that activates the MCP interface
🔧 What Goes Where?
Folder	Purpose
/core/	Logic modules that actually interpret tasks, routes, scopes, and file directives
/internal-state/	This is your AI’s internal “working memory”
/templates/	Used to create new external projects (ReferenceProject lives here)
/config/	Server config (archive behavior, scope limits, etc.)
server.py	Bootstraps everything — the AI’s interface to external commands

🧱 How This Enables MCP
When a user says:

“Continue development on Project X”

Your MCP server will:

Look inside /Projects/ProjectX/ProjectBlueprint/blueprint.md

Read the relevant /Tasks/active/TASK-*.json

Use retrieval-guidelines.md to determine how much scope to load

Load only what’s needed from Scopes/

Execute, log in Logs/, and queue next step


===========================

Avoiding placeholders. This MCP is meant for software/coding projects. We want to avoid the placeholder/truncation issue at all costs. We need directives to minimize file lengths, with a setting in the user settings to adjust that length (line numbers). Default will be 900 lines of code. AI, after every code edit, should evaluate the number of lines in the document and if exceeds the limit, must modularize the file into smaller files by function groups or other useful categorization.

Why Placeholders Get Added (When They Shouldn't)
Context Window Misjudgment
Sometimes the model wrongly assumes that including or rendering the entire text might exceed a token limit—even though it's safe. This is a protective behavior, but often unnecessary and overly conservative, especially in environments (like this canvas) with large limits.

Legacy Training Behavior
During training, models learned to avoid "overwriting" large blocks of content due to older interfaces that couldn't handle full-page replacements. That behavior stuck: AI now tends to err on the side of summarizing or inserting stubs like "... continued".

False Efficiency Heuristic
The model sometimes "thinks" it’s being efficient by abstracting unchanged content. It misjudges that you’ll know what it means and can fill in the blanks—when in reality, you want exact, complete edits, especially for code and documentation.

Internal Tooling Mismatch
Some LLM-connected tools (like Claude or others) have backend systems where code updates or document diffs are handled in chunks. These tools may render only partial replacements unless explicitly overridden.

Human Training Oversight
Many of these behaviors were reinforced by human raters who preferred "shorter, cleaner edits" over full verbose ones—because they assumed a human would "get the idea." That made models more likely to skip “boring” boilerplate unless asked not to.