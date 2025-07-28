#!/bin/bash
set -e

# Create expected dirs
mkdir -p /app/semanticAnalyzer/input
mkdir -p /app/semanticAnalyzer/output

# This is a mess for performance but should work nicely
cp -r /app/input/* /app/semanticAnalyzer/input/

python3 /app/semanticAnalyzer/main.py

cp -r /app/semanticAnalyzer/output/* /app/output/
