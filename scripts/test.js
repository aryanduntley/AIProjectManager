#!/usr/bin/env node

const { spawn } = require('child_process');
const path = require('path');
const chalk = require('chalk');

console.log(chalk.blue('🧪 Running AI Project Manager tests...'));

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

// Run Python tests
async function runTests() {
  const pythonCmd = await checkPython();
  
  if (!pythonCmd) {
    console.error(chalk.red('Error: Python 3.8+ is required for testing.'));
    process.exit(1);
  }

  console.log(chalk.gray('📋 Running Python test suite...'));

  // Set up Python path
  const env = { ...process.env };
  const depsPath = path.join(mcpServerPath, 'deps');
  if (require('fs').existsSync(depsPath)) {
    env.PYTHONPATH = env.PYTHONPATH ? `${depsPath}:${env.PYTHONPATH}` : depsPath;
  }

  // List of test files to run
  const testFiles = [
    'test_comprehensive.py',
    'test_database_infrastructure.py',
    'test_directive_escalation.py'
  ];

  let allPassed = true;

  for (const testFile of testFiles) {
    const testPath = path.join(packageRoot, testFile);
    if (!require('fs').existsSync(testPath)) {
      console.log(chalk.yellow(`⚠️  Test file not found: ${testFile}`));
      continue;
    }

    console.log(chalk.gray(`   Running ${testFile}...`));
    
    const testProcess = spawn(pythonCmd, [testPath], {
      stdio: 'pipe',
      cwd: packageRoot,
      env
    });

    const result = await new Promise((resolve) => {
      let output = '';
      let errorOutput = '';

      testProcess.stdout.on('data', (data) => {
        output += data.toString();
      });

      testProcess.stderr.on('data', (data) => {
        errorOutput += data.toString();
      });

      testProcess.on('close', (code) => {
        resolve({ code, output, errorOutput });
      });
    });

    if (result.code === 0) {
      console.log(chalk.green(`   ✓ ${testFile} passed`));
    } else {
      console.log(chalk.red(`   ✗ ${testFile} failed`));
      if (result.errorOutput) {
        console.log(chalk.red(`     Error: ${result.errorOutput.trim()}`));
      }
      allPassed = false;
    }
  }

  if (allPassed) {
    console.log(chalk.green('\n🎉 All tests passed!'));
  } else {
    console.log(chalk.red('\n❌ Some tests failed.'));
    process.exit(1);
  }
}

runTests().catch(error => {
  console.error(chalk.red(`Test runner error: ${error.message}`));
  process.exit(1);
});