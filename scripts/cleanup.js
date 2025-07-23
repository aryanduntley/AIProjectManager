#!/usr/bin/env node

const fs = require('fs');
const path = require('path');
const chalk = require('chalk');

console.log(chalk.blue('🧹 Cleaning up AI Project Manager...'));

// Clean up any temporary files or caches
function cleanup() {
  const packageRoot = path.resolve(__dirname, '..');
  const tempDirs = [
    path.join(packageRoot, '.temp'),
    path.join(packageRoot, 'mcp-server', '__pycache__'),
    path.join(packageRoot, 'mcp-server', '.pytest_cache')
  ];

  let cleaned = 0;
  tempDirs.forEach(dir => {
    if (fs.existsSync(dir)) {
      try {
        fs.rmSync(dir, { recursive: true, force: true });
        cleaned++;
        console.log(chalk.gray(`   Removed: ${path.relative(packageRoot, dir)}`));
      } catch (error) {
        console.warn(chalk.yellow(`   Warning: Could not remove ${dir}`));
      }
    }
  });

  if (cleaned > 0) {
    console.log(chalk.green(`✓ Cleaned up ${cleaned} temporary directories`));
  } else {
    console.log(chalk.gray('✓ No cleanup needed'));
  }
}

cleanup();