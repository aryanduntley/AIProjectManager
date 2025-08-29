# 🎯 AI Project Manager - Command Quick Reference

## Getting Started - New Users

**First time using AI Project Manager?** Try these commands in order:

```
1. run-aipm-status    - See what state your project is in
2. run-aipm-help      - Learn all available commands  
3. run-aipm-init      - Set up AI project management
4. run-aipm-resume    - Start working on your project
```

> **Note**: Due to Claude Code UI limitations with custom slash commands, all commands now use the `run-` prefix instead of `/`. Simply type the command naturally (e.g., "run-aipm-init") and the AI will execute it automatically.

## Essential Commands

### Discovery Commands
- **`run-aipm-status`** - Get current project state and suggested next steps
- **`run-aipm-help`** - Show all commands with detailed descriptions
- **`run-aipm-analyze`** - Full project analysis and theme discovery

### Setup Commands  
- **`run-aipm-init`** - Initialize AI project management (auto-selects best option)
- **`run-aipm-config`** - View current configuration settings

### Work Commands
- **`run-aipm-resume`** - Resume previous work and active tasks
- **`run-aipm-tasks`** - Show active tasks and progress
- **`run-aipm-newTask`** - Create and start working on new task
- **`run-aipm-pause`** - Find suitable stopping point and prepare for clean resumption

### Project Understanding
- **`run-aipm-themes`** - Show project themes and file organization
- **`run-aipm-flows`** - Show user experience flows and journeys

### Advanced Workflow
- **`run-aipm-branch`** - Create AI work branch for parallel development
- **`run-aipm-merge`** - Merge completed AI branch work back to ai-pm-org-main
- **`run-aipm-deploy`** - Deploy AI improvements to your main branch (ai-pm-org-main → user's main)

### Database Management
- **`run-aipm-backup`** - Create manual database backup with timestamp
- **`run-aipm-maintenance`** - Run database cleanup, archiving, and optimization
- **`run-aipm-db-stats`** - Show database health and storage statistics

### 🤖 AI-Handled Git Operations
The AI automatically handles complex git operations when needed. You can simply **request git actions in natural language**:

- *"Push the AI organizational changes to remote"*
- *"Pull the latest AI changes from the team"*  
- *"Set up remote collaboration for this project"*
- *"Sync with the remote AI branch"*
- *"Check if there are remote updates"*

The AI will automatically use the appropriate MCP tools for git operations behind the scenes.

## How Commands Work

### Workflow-Level Approval
When you use a command like `/aipm-init`, you're giving **workflow-level approval**. This means:

✅ **AI can chain multiple tools automatically**  
✅ **AI makes decisions based on your project data**  
✅ **AI executes complex multi-step processes**  
✅ **AI operates autonomously within the approved scope**

### Example Workflows

**Getting Started:**
```
User: "/aipm-status"
AI: Analyzes project → Shows current state → Suggests next commands

User: "/aipm-init"  
AI: Analyzes project → Presents options → Executes initialization → Sets up structure
```

**Daily Development:**
```
User: "/aipm-resume"
AI: Loads context → Finds active tasks → Continues where you left off

User: "/aipm-tasks"
AI: Shows active work → Progress status → Next steps

User: "/aipm-pause"
AI: Finds stopping point → Saves all progress → Prepares for clean resumption
```

**Project Analysis:**
```
User: "/aipm-analyze"
AI: Discovers themes → Maps project structure → Shows organization

User: "/aipm-themes"
AI: Shows discovered themes → File mappings → Relationships
```

**AI Development & Deployment:**
```
User: "/aipm-branch"
AI: Creates work branch → Switches to it → Ready for AI development

User: "/aipm-merge" 
AI: Merges work branch → Back to ai-pm-org-main → Creates PR if possible

User: "/aipm-deploy"
AI: Merges ai-pm-org-main → User's main → Creates backup → AI improvements deployed!
```

**Team Collaboration (AI-Handled):**
```
User: "Set up remote collaboration for this project"
AI: Creates ai-pm-org-main → Sets up team structure → Pushes to remote

User: "Pull the latest team changes" 
AI: Fetches remote updates → Merges changes → Keeps AI state current

User: "Push our AI improvements to the team"
AI: Pushes AI organizational changes → Updates remote → Confirms team sync
```

## Technical Details

### Command vs MCP Tools
- **Commands** (`/aipm-status`, `/aipm-init`, etc.) - High-level workflows with single approval
- **MCP Tools** (`get_project_state_analysis`, etc.) - Individual operations with separate approvals

### Available MCP Tools
The AI Project Manager provides 65+ MCP tools that commands use behind the scenes:
- Project management tools (initialize, status, blueprints)
- Task management tools (create, update, list, sidequests)  
- Context loading tools (themes, flows, escalation)
- File operations tools (read, analyze, cross-reference)
- Branch management tools (create, switch, merge, status)
- Session management tools (boot, persistence, restoration)
- Database tools (queries, analytics, optimization, backup, maintenance)

### Getting Help
- **`/aipm-help`** - Overview of all commands
- **`help_commands`** MCP tool - Detailed help system (AI uses automatically)
- **`help_commands` with specific command** - Detailed help for individual commands (AI uses automatically)

## Troubleshooting

### "Nothing happened when I said 'continue development'"
**Solution**: Use `/aipm-status` or `/aipm-resume` commands instead of natural language.

### "I don't know what state my project is in"
**Solution**: Use `/aipm-status` to get current state analysis and suggested next steps.

### "The AI isn't doing anything automatically"
**Solution**: Commands provide workflow approval. Use `/aipm-init` for initial setup, `/aipm-resume` for ongoing work.

### "I want to see all available options"
**Solution**: Use `/aipm-help` for command overview, or ask "show me detailed help" (AI will use `help_commands` tool automatically).

## Command Reference Card

| Command | Purpose | Approval Level | When to Use |
|---------|---------|----------------|-------------|
| `/aipm-status` | Project state | None | Always first step |
| `/aipm-help` | Show commands | None | When confused |
| `/aipm-init` | Initialize | Workflow | New project setup |
| `/aipm-resume` | Continue work | Workflow | Daily development |
| `/aipm-tasks` | Show tasks | None | Check progress |
| `/aipm-pause` | Pause & save | None | End work session |
| `/aipm-analyze` | Deep analysis | Workflow | Understand project |
| `/aipm-themes` | Show themes | None | See organization |
| `/aipm-flows` | Show flows | None | See user journeys |
| `/aipm-branch` | Create branch | Workflow | Parallel work |
| `/aipm-merge` | Merge branch | Workflow | Complete work |
| `/aipm-deploy` | Deploy to main | Workflow | Accept AI improvements |
| `/aipm-config` | Show config | None | Check settings |
| `/aipm-backup` | Database backup | None | Before major changes |
| `/aipm-maintenance` | Database cleanup | Workflow | Monthly maintenance |
| `/aipm-db-stats` | Database health | None | Check storage usage |

---

**Need more help?** Use `/aipm-help` for interactive command assistance or see the main README.md for full documentation.