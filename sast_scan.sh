#!/bin/bash
set -e

# Check if Bandit is installed
if ! command -v bandit &> /dev/null; then
    echo "Installing Bandit..."
    pip install bandit
fi

# Run SAST scan
echo "Starting SAST scan..."
bandit -r app/ -f json -o sast_report.json
echo "Scan completed! Report saved to sast_report.json"

# Check for high severity vulnerabilities
high_severity=$(jq '.results[] | select(.issue_severity == "HIGH")' sast_report.json | wc -l)
if [ $high_severity -gt 0 ]; then
    echo "Warning: ${high_severity} high severity vulnerabilities found!"
    exit 1
else
    echo "No high severity vulnerabilities found"
fi