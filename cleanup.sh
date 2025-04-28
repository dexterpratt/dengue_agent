#!/bin/bash

# Cleanup script to remove agent implementation files
# and keep only the necessary files for Claude-as-agent approach

echo "Cleaning up agent implementation files..."

# Remove agent implementation files
rm -f run_agent.py agent_workflow.py

echo "Removed agent implementation files."
echo "Keeping only the necessary files for Claude-as-agent approach."

echo "====================================="
echo "Project structure now focuses on:"
echo "1. tools/ - Core analysis tools"
echo "2. prompts/ - Templates and documentation for Claude as agent"
echo "====================================="

echo "Done."
