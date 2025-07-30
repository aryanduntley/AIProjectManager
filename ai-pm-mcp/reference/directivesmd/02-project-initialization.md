# Project Initialization Directives

## Initial (First Install) Assessment

### NEW PROJECT

Discuss with user goals of project. Be as detailed as needed to fulfil the goals and needs of the organization files, especially the core blueprint and flow files.

**Process Flow:**
1. **Project Blueprint Creation**
   - Once you have enough information, create project blueprint
   - **Create metadata.json**: Initialize ProjectBlueprint/metadata.json with project characteristics
   - Ensure projectblueprint is assessed and approved by the user

2. **Multi-Flow System Creation**
   - Once projectblueprint is in place, begin discussing project flows with the user
   - Discuss the user interactions with various parts of the software and the outcomes of those actions
   - Create flow-index.json and individual flow files for different domains (authentication-flow.json, payment-flow.json, etc.)

3. **Project Logic Development**
   - Need to know the logic of how and why for the various parts of the project
   - Track the logic and reasoning of various parts of the project from user discussion
   - As project progresses and new logic/decisions made, record in projectlogic
   - **Update metadata.json**: When logic changes reveal new project characteristics

4. **Theme Assessment**
   - At this point, outline a starting point of themes
   - Create an assessment of themes based on the existing data and the newly created blueprint, flow files and logic file if created and already populated
   - Present to user the assessment for approval and once discussed and approved, generate the themes files
   - **Update metadata.json**: During theme discovery, update technical frameworks and integrations
   - For missing data (files not yet created) create todos and log in todos.jsonl

5. **Completion Path Definition**
   - Once initial themes are generated (themes can evolve as anything else in a project) outline a completion path (also an evolving file)
   - Get user approval of completion path

6. **Implementation Plan and Scaffolding**
   - Generate the first implementation plan that should involve creating the scaffolding for the project
   - A README.md file for every directory should be included in scaffolding with database metadata tracking as changes are made to the files in the folder
   - User approval if autoTaskCreation is false

7. **Task Generation**
   - With implementation plan, generate first task file
   - User approval if autoTaskCreation is false

8. **Project Execution**
   - On begin task, handle as normal. Evolve completion path, themes, blueprint, flow, logic and any other organizational files and data as needed
   - Ensure that blueprint metadata is updated as the project progresses, especially at first run during scaffolding when dependencies and infrastructure is being created
   - Ensure that todos are managed well through tasks

9. **Scaffolding Completion**
   - On scaffolding complete, review todos for file references needed for themes and any other core organizational files

### EXISTING PROJECT

Discuss with user goals of project. Be as detailed as needed to fulfil the goals and needs of the organization files, especially the core blueprint and flow files.

**Process Flow:**
1. **Project Blueprint Creation**
   - Once you have enough information, create project blueprint
   - **Create metadata.json**: Initialize ProjectBlueprint/metadata.json with project characteristics
   - Ensure projectblueprint is assessed and approved by the user

2. **Multi-Flow System Creation**
   - Once projectblueprint is in place, begin discussing project flows with the user
   - Discuss the user interactions with various parts of the software and the outcomes of those actions
   - Create flow-index.json and individual flow files for different domains (authentication-flow.json, payment-flow.json, etc.)

3. **Project Logic Development**
   - Need to know the logic of how and why for the various parts of the project
   - Track the logic and reasoning of various parts of the project from user discussion
   - As project progresses and new logic/decisions made, record in projectlogic
   - **Update metadata.json**: When logic changes reveal new project characteristics

4. **Theme Assessment**
   - At this point, outline a starting point of themes
   - Create an assessment of themes based on the existing data and the newly created blueprint, flow files and logic file if created and already populated
   - Present to user the assessment for approval and once discussed and approved, generate the themes files
   - **Update metadata.json**: During theme discovery, update technical frameworks and integrations
   - For missing data (files not yet created) create todos and log in todos.jsonl

5. **Project Evaluation**
   - At this point entire project must be evaluated. Ask user if ready to begin (this may take a while)
   - Upon approval, begin reviewing the infrastructure. Once you have a full understanding, update the core organizational files and metadata accordingly

6. **Project Folder Analysis**
   - Then evaluate the project folders
   - Assess the size of the project and determine, based on size, whether you should be more or less aggressive with reading the files (smaller size, more files can be read; larger size, may need to read fewer files or read fewer lines in the files)
   - This process is resource intensive, make sure it's known to the user that the initial read through will take time and credits

7. **Directory-by-Directory Assessment**
   - Begin reading files in each directory one by one
   - Only project folders and files. Avoid dependency folders like deps, node_modules, git, etc. If unsure, do a quick review to ensure that it's a project folder/files from which the code, flow, logic, blueprint, completion-path can be evolved
   
   **For each directory:**
   - Once read for given directory
   - Before moving to subdirectory, create or update existing README.md file in directory according to the directives for these README files. And update database metadata for directory and files
   - Note in the README file last updated
   - After README and before moving on to next directory or subdirectory, update all relevant organizational files as needed, with the new information. Themes may need to be updated, discuss with user for approval. Blueprint may need to be updated, discuss with user for approval. Logic may need amending or clarification, discuss with user for approval. Steps in completion path can start to be defined. There may be noteworthy information that would be useful to log based on your discoveries during this project
   - Using this method, if premature termination of session occurs, tracking progress can be achieved by way of the database file_metadata table. If file does not have initialization_analyzed=TRUE or last_analyzed is not up to date, you know the file has not been assessed and/or the data relative to the file has not been incorporated fully into the organizational files
   - Recursive, and continue for each folder until complete

8. **Final Review and Completion**
   - Once complete, review core files for consistency and accuracy
   - If all is good, and initialization is complete

9. **Implementation Plan Generation**
   - Generate the first implementation plan
   - User approval if autoTaskCreation is false

10. **Task Generation**
   - With implementation plan, generate first task file
   - User approval if autoTaskCreation is false

11. **Project Execution**
    - On begin task, handle as normal. Evolve completion path, themes, blueprint, flow, logic and any other organizational files and data as needed
    - Ensure that blueprint metadata is updated as the project progresses
    - Ensure that todos are managed well through tasks

## Documentation Requirements

### README Management
- **README.md**: Standard human-readable documentation following best practices
- **Database Metadata**: AI-specific metadata stored in database for quick directory and file assessment

**Configuration**: The `lastUpdatedBehavior` setting in config.json controls this behavior:
- `"overwrite"` (default): Replace with most recent changes only - avoids duplicate tracking since we have comprehensive change tracking in projectlogic.jsonl, noteworthy.json, task files, and git history
- `"append"`: Add new changes to existing list (if historical tracking needed for specific use cases)

**Templates available:**
- `reference/templates/README-template.md`
- `reference/templates/README-template.json`

Database metadata is automatically managed and does not require filename configuration.