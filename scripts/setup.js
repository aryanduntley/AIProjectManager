#!/usr/bin/env node

const fs = require('fs');
const path = require('path');
const { spawn } = require('child_process');
const chalk = require('chalk');

console.log(chalk.blue('🔧 Setting up AI Project Manager...'));

const packageRoot = path.resolve(__dirname, '..');
const mcpServerPath = path.join(packageRoot, 'mcp-server');

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

// Verify dependencies
async function verifySetup() {
  console.log(chalk.gray('📋 Verifying installation...'));
  
  // Check Python
  const pythonCmd = await checkPython();
  if (!pythonCmd) {
    console.warn(chalk.yellow('⚠️  Warning: Python 3.8+ not found.'));
    console.log(chalk.gray('   AI Project Manager requires Python to run.'));
    console.log(chalk.gray('   Please install Python from https://python.org'));
    return false;
  }
  console.log(chalk.green(`✓ Python found: ${pythonCmd}`));

  // Check MCP server files
  const serverScript = path.join(mcpServerPath, 'server.py');
  if (!fs.existsSync(serverScript)) {
    console.error(chalk.red('✗ MCP server files not found'));
    return false;
  }
  console.log(chalk.green('✓ MCP server files present'));

  // Check bundled dependencies
  const depsPath = path.join(mcpServerPath, 'deps');
  if (fs.existsSync(depsPath)) {
    console.log(chalk.green('✓ Python dependencies bundled'));
  } else {
    console.log(chalk.yellow('⚠️  Python dependencies not bundled - will attempt to use system packages'));
  }

  return true;
}

// Test basic functionality
async function testFunctionality() {
  console.log(chalk.gray('🧪 Testing basic functionality...'));
  
  const pythonCmd = await checkPython();
  const serverScript = path.join(mcpServerPath, 'server.py');
  
  return new Promise((resolve) => {
    const env = { ...process.env };
    const depsPath = path.join(mcpServerPath, 'deps');
    if (fs.existsSync(depsPath)) {
      env.PYTHONPATH = env.PYTHONPATH ? `${depsPath}:${env.PYTHONPATH}` : depsPath;
    }

    const testProcess = spawn(pythonCmd, [serverScript, '--help'], {
      stdio: 'pipe',
      cwd: mcpServerPath,
      env
    });

    testProcess.on('error', () => resolve(false));
    testProcess.on('close', (code) => resolve(code === 0));
  });
}

// Main setup function
async function setup() {
  try {
    const verified = await verifySetup();
    if (!verified) {
      console.log(chalk.yellow('\n📋 Setup completed with warnings.'));
      console.log(chalk.gray('   You may need to install Python before using AI Project Manager.'));
      return;
    }

    const tested = await testFunctionality();
    if (!tested) {
      console.log(chalk.yellow('\n⚠️  Setup completed but functionality test failed.'));
      console.log(chalk.gray('   You may need to install additional Python packages.'));
      return;
    }

    console.log(chalk.green('\n🎉 AI Project Manager setup completed successfully!'));
    console.log(chalk.gray('\n📖 Usage:'));
    console.log(chalk.gray('   ai-pm init [project-path]  # Initialize a new project'));
    console.log(chalk.gray('   ai-pm start                # Start the MCP server'));
    console.log(chalk.gray('   ai-pm --help               # Show all commands'));
    
  } catch (error) {
    console.error(chalk.red(`\n❌ Setup failed: ${error.message}`));
    process.exit(1);
  }
}

setup();