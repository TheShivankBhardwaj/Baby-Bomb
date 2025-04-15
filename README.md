# Project Description

This project provides an AI assistant that operates within a terminal environment, designed to aid in coding, problem-solving, and full-stack project development. The assistant is capable of understanding natural language commands, creating project structures, writing code, and executing system commands.

## ai_agent.py Summary

The `ai_agent.py` file contains the core logic for the AI assistant. It includes the following key functions:

- `run_command`: Executes system commands, optionally in a new terminal window.
- `read_file`: Reads the content of a file, handling different encodings.
- `write_file`: Writes content to a file, creating directories as needed.
- `create_project`: Creates a new project with a predefined structure (React, Node, Python, Vite).
- `run_project`: Runs a project in a new terminal window by identifying the appropriate start script or main file.

The script uses the Gemini 2.0 Flash model for natural language processing and interacts with the user through the terminal. It operates in a plan-action-observe loop, using available tools to fulfill user requests.
