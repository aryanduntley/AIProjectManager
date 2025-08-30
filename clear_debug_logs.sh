#!/bin/bash
# Clear debug log files for AI Project Manager debugging

echo "Clearing debug log files..."

# Remove debug files
rm -f debug_init.log
rm -f debug_directive.log

# Remove any old project management directories for clean testing
if [ -d "projectManagement" ]; then
    echo "Removing existing projectManagement directory..."
    rm -rf projectManagement
fi

echo "Debug logs and project structure cleared successfully!"
echo "Ready for clean initialization testing."