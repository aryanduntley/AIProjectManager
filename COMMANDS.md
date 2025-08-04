# 🎯 AI Project Manager - Command Quick Reference

## Getting Started - New Users

**First time using AI Project Manager?** Try these commands in order:

```
1. /status    - See what state your project is in
2. /help      - Learn all available commands  
3. /init      - Set up AI project management
4. /resume    - Start working on your project
```

## Essential Commands

### Discovery Commands
- **`/status`** - Get current project state and suggested next steps
- **`/help`** - Show all commands with detailed descriptions
- **`/analyze`** - Full project analysis and theme discovery

### Setup Commands  
- **`/init`** - Initialize AI project management (auto-selects best option)
- **`/config`** - View current configuration settings

### Work Commands
- **`/resume`** - Resume previous work and active tasks
- **`/tasks`** - Show active tasks and progress
- **`/newTask <description>`** - Create and start working on new task

### Project Understanding
- **`/themes`** - Show project themes and file organization
- **`/flows`** - Show user experience flows and journeys

### Advanced Workflow
- **`/branch`** - Create AI work branch for parallel development
- **`/merge`** - Merge completed AI work back to main

## How Commands Work

### Workflow-Level Approval
When you use a command like `/init`, you're giving **workflow-level approval**. This means:

✅ **AI can chain multiple tools automatically**  
✅ **AI makes decisions based on your project data**  
✅ **AI executes complex multi-step processes**  
✅ **AI operates autonomously within the approved scope**

### Example Workflows

**Getting Started:**
```
User: "/status"
AI: Analyzes project → Shows current state → Suggests next commands

User: "/init"  
AI: Analyzes project → Presents options → Executes initialization → Sets up structure
```

**Daily Development:**
```
User: "/resume"
AI: Loads context → Finds active tasks → Continues where you left off

User: "/tasks"
AI: Shows active work → Progress status → Next steps
```

**Project Analysis:**
```
User: "/analyze"
AI: Discovers themes → Maps project structure → Shows organization

User: "/themes"
AI: Shows discovered themes → File mappings → Relationships
```

## Technical Details

### Command vs MCP Tools
- **Commands** (`/status`, `/init`, etc.) - High-level workflows with single approval
- **MCP Tools** (`get_project_state_analysis`, etc.) - Individual operations with separate approvals

### Available MCP Tools
The AI Project Manager provides 62+ MCP tools that commands use behind the scenes:
- Project management tools (initialize, status, blueprints)
- Task management tools (create, update, list, sidequests)  
- Context loading tools (themes, flows, escalation)
- File operations tools (read, analyze, cross-reference)
- Branch management tools (create, switch, merge, status)
- Session management tools (boot, persistence, restoration)
- Database tools (queries, analytics, optimization)

### Getting Help
- **`/help`** - Overview of all commands
- **`help_commands`** tool - Detailed help system
- **`help_commands` with specific command** - Detailed help for individual commands

## Troubleshooting

### "Nothing happened when I said 'continue development'"
**Solution**: Use `/status` or `/resume` commands instead of natural language.

### "I don't know what state my project is in"
**Solution**: Use `/status` to get current state analysis and suggested next steps.

### "The AI isn't doing anything automatically"
**Solution**: Commands provide workflow approval. Use `/init` for initial setup, `/resume` for ongoing work.

### "I want to see all available options"
**Solution**: Use `/help` for command overview, or `help_commands` tool for detailed information.

## Command Reference Card

| Command | Purpose | Approval Level | When to Use |
|---------|---------|----------------|-------------|
| `/status` | Project state | None | Always first step |
| `/help` | Show commands | None | When confused |
| `/init` | Initialize | Workflow | New project setup |
| `/resume` | Continue work | Workflow | Daily development |
| `/tasks` | Show tasks | None | Check progress |
| `/analyze` | Deep analysis | Workflow | Understand project |
| `/themes` | Show themes | None | See organization |
| `/flows` | Show flows | None | See user journeys |
| `/branch` | Create branch | Workflow | Parallel work |
| `/merge` | Merge branch | Workflow | Complete work |
| `/config` | Show config | None | Check settings |

---

**Need more help?** Use `/help` for interactive command assistance or see the main README.md for full documentation.