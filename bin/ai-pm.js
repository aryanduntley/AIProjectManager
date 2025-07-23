#!/usr/bin/env node

const { spawn } = require('child_process');
const path = require('path');
const fs = require('fs');
const { program } = require('commander');
const chalk = require('chalk');

// Get the directory where this package is installed
const packageRoot = path.resolve(__dirname, '..');
const mcpServerPath = path.join(packageRoot, 'mcp-server');
const serverScript = path.join(mcpServerPath, 'server.py');

// Check if Python is available
function checkPython() {
  return new Promise((resolve) => {
    const python = spawn('python3', ['--version'], { stdio: 'pipe' });
    python.on('error', () => {
      const python2 = spawn('python', ['--version'], { stdio: 'pipe' });
      python2.on('error', () => resolve(null));
      python2.on('close', (code) => resolve(code === 0 ? 'python' : null));
    });
    python.on('close', (code) => resolve(code === 0 ? 'python3' : null));
  });
}

// Run the Python MCP server
async function runServer(args = []) {
  const pythonCmd = await checkPython();
  
  if (!pythonCmd) {
    console.error(chalk.red('Error: Python 3.8+ is required but not found.'));
    console.error(chalk.yellow('Please install Python from https://python.org'));
    process.exit(1);
  }

  if (!fs.existsSync(serverScript)) {
    console.error(chalk.red('Error: MCP server not found.'));
    console.error(chalk.yellow('Please reinstall the package: npm install -g ai-project-manager'));
    process.exit(1);
  }

  console.log(chalk.blue('🚀 Starting AI Project Manager MCP Server...'));
  
  // Set up Python path to include bundled dependencies
  const env = { ...process.env };
  const depsPath = path.join(mcpServerPath, 'deps');
  if (fs.existsSync(depsPath)) {
    env.PYTHONPATH = env.PYTHONPATH ? `${depsPath}:${env.PYTHONPATH}` : depsPath;
  }

  const serverProcess = spawn(pythonCmd, [serverScript, ...args], {
    stdio: 'inherit',
    cwd: mcpServerPath,
    env
  });

  serverProcess.on('error', (error) => {
    console.error(chalk.red(`Failed to start server: ${error.message}`));
    process.exit(1);
  });

  serverProcess.on('close', (code) => {
    if (code !== 0) {
      console.error(chalk.red(`Server exited with code ${code}`));
      process.exit(code);
    }
  });

  // Handle Ctrl+C gracefully
  process.on('SIGINT', () => {
    console.log(chalk.yellow('\n🛑 Shutting down AI Project Manager...'));
    serverProcess.kill('SIGINT');
  });
}

// CLI Interface
program
  .name('ai-pm')
  .description('AI Project Manager - Intelligent project management through persistent context')
  .version('1.0.0');

program
  .command('init [project-path]')
  .description('Initialize AI Project Manager in the specified directory')
  .option('-f, --force', 'Force initialization even if structure exists')
  .action(async (projectPath = process.cwd(), options) => {
    const args = ['--init', projectPath];
    if (options.force) args.push('--force');
    await runServer(args);
  });

program
  .command('start')
  .description('Start the MCP server for an existing project')
  .option('-p, --port <port>', 'Port number for the server')
  .option('-d, --debug', 'Enable debug mode')
  .action(async (options) => {
    const args = [];
    if (options.port) args.push('--port', options.port);
    if (options.debug) args.push('--debug');
    await runServer(args);
  });

program
  .command('status')
  .description('Show project status and health')
  .action(async () => {
    await runServer(['--status']);
  });

program
  .command('instance <command>')
  .description('Manage project instances (create, list, merge)')
  .action(async (command) => {
    await runServer(['--instance', command]);
  });

program
  .command('server')
  .description('Start the MCP server (default mode)')
  .option('--stdio', 'Use stdio transport (default)')
  .option('--http <port>', 'Use HTTP transport on specified port')
  .action(async (options) => {
    const args = [];
    if (options.http) {
      args.push('--transport', 'http', '--port', options.http);
    }
    await runServer(args);
  });

// Default command - start server
if (process.argv.length === 2) {
  runServer();
} else {
  program.parse();
}