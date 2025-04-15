from dotenv import load_dotenv
import os
import json
import google.generativeai as genai
from google.generativeai import GenerativeModel
import platform
import subprocess
import shutil

load_dotenv()

current_project = {
    "name": None,
    "directory": None,
    "type": None
}

def run_command(command, new_terminal=False):
    try:
        if new_terminal:
            system = platform.system().lower()
            
            if system == 'windows':
                full_command = 'start cmd /k "' + command + '"'
                subprocess.Popen(full_command, shell=True)
                return {"status": "success", "message": "Command '" + command + "' launched in a new terminal window"}
            
            elif system == 'darwin':  # macOS
                apple_script = '''
                tell application "Terminal"
                    do script "''' + command + '''"
                    activate
                end tell
                '''
                subprocess.Popen(['osascript', '-e', apple_script])
                return {"status": "success", "message": "Command '" + command + "' launched in a new terminal window"}
            
            elif system == 'linux':
                terminals = ['gnome-terminal', 'xterm', 'konsole', 'terminator']
                for terminal in terminals:
                    if shutil.which(terminal):
                        if terminal == 'gnome-terminal':
                            subprocess.Popen([terminal, '--', 'bash', '-c', command + '; exec bash'])
                        else:
                            subprocess.Popen([terminal, '-e', 'bash -c "' + command + '; exec bash"'])
                        return {"status": "success", "message": "Command '" + command + "' launched in a new terminal window (" + terminal + ")"}
                
                return {"error": "Could not find a suitable terminal emulator"}
        
        result = subprocess.run(command, shell=True, text=True, capture_output=True)
        return {
            "stdout": result.stdout,
            "stderr": result.stderr,
            "return_code": result.returncode
        }
    except Exception as e:
        return {"error": str(e)}

def read_file(file_path=None, path=None):
    actual_path = file_path or path
    
    if not actual_path:
        return {"error": "No file path provided"}
        
    encodings = [
        ('utf-8', 'strict'),
        ('latin1', 'strict'),
        ('utf-8', 'ignore')  
    ]
    
    for encoding, errors in encodings:
        try:
            with open(actual_path, 'r', encoding=encoding, errors=errors) as file:
                content = file.read()
                return {"content": content, "encoding_used": f"{encoding} with errors={errors}"}
        except Exception as e:
            continue
    
    return {"error": f"Failed to read file '{actual_path}' with all attempted encodings: {', '.join([e[0] for e in encodings])}"}

def write_file(file_path=None, path=None, content=""):
    actual_path = file_path or path
    
    if not actual_path:
        return {"error": "No file path provided"}
    
    try:
        directory = os.path.dirname(actual_path)
        if directory and not os.path.exists(directory):
            os.makedirs(directory)
            
        with open(actual_path, 'w') as file:
            file.write(content)
        return {"status": "success", "message": "Content written to " + actual_path}
    except Exception as e:
        return {"error": str(e)}

def create_project(project_type=None, project_name=None, template=None):
    """Creates a project structure based on the type or template"""
    if template and not project_type:
        project_type = template
    
    if not project_name:
        project_name = "my-project"
    
    templates = {
        "react": {
            "commands": [
                "npx create-react-app " + project_name,
                "cd " + project_name + " && npm install"
            ]
        },
        "node": {
            "commands": [
                "mkdir " + project_name,
                "cd " + project_name + " && npm init -y",
                "cd " + project_name + " && npm install express"
            ]
        },
        "python": {
            "commands": [
                "mkdir " + project_name,
                "cd " + project_name + " && python -m venv venv",
                "cd " + project_name + " && pip install pytest"
            ]
        },
        "vite": {
            "commands": [
                "npm create vite@latest " + project_name + " -- --template react",
                "cd " + project_name + " && npm install"
            ]
        },
        "vite-react": {
            "commands": [
                "npm create vite@latest " + project_name + " -- --template react",
                "cd " + project_name + " && npm install"
            ]
        },
        "vite-vue": {
            "commands": [
                "npm create vite@latest " + project_name + " -- --template vue",
                "cd " + project_name + " && npm install"
            ]
        },
        "vite-vanilla": {
            "commands": [
                "npm create vite@latest " + project_name + " -- --template vanilla",
                "cd " + project_name + " && npm install"
            ]
        }
    }
    
    if project_type not in templates:
        return {"error": "Project type '" + project_type + "' not supported. Supported types: " + ", ".join(templates.keys())}
    
    current_dir = os.getcwd()
    project_full_path = os.path.join(current_dir, project_name)
    
    results = []
    for cmd in templates[project_type]["commands"]:
        results.append(run_command(cmd))
    
    if os.path.exists(project_full_path):
        try:
            project_contents = os.listdir(project_full_path)
            print("Project created with the following files/directories: " + str(project_contents))
        except Exception as e:
            print("Warning: Could not list project contents: " + str(e))
    
    return {
        "results": results,
        "project_info": {
            "name": project_name,
            "directory": project_full_path,
            "type": project_type
        }
    }

def run_project(project_dir=None):
    """Runs a project in a new terminal window"""
    if not project_dir and current_project["directory"]:
        project_dir = current_project["directory"]
    
    if not project_dir:
        return {"error": "No project directory specified"}
    
    try:
        os.chdir(project_dir)
        
        if os.path.exists('package.json'):
            with open('package.json', 'r') as f:
                package_data = json.load(f)
            
            scripts = package_data.get('scripts', {})
            run_script = None
            
            for script_name in ['dev', 'start', 'serve']:
                if script_name in scripts:
                    run_script = script_name
                    break
            
            if run_script:
                return run_command("npm run " + run_script, new_terminal=True)
            else:
                return {"error": "No suitable run script found in package.json"}
        
        elif os.path.exists('app.py') or os.path.exists('main.py'):
            main_file = 'app.py' if os.path.exists('app.py') else 'main.py'
            return run_command("python " + main_file, new_terminal=True)
        
        else:
            return {"error": "Could not determine how to run this project"}
    
    except Exception as e:
        return {"error": str(e)}

available_tools = {
    "run_command": {
        "fn": run_command,
        "description": "Executes a system command and returns the output"
    },
    "read_file": {
        "fn": read_file,
        "description": "Reads the content of a file at the given path"
    },
    "write_file": {
        "fn": write_file,
        "description": "Writes content to a file at the given path"
    },
    "create_project": {
        "fn": create_project,
        "description": "Creates a new project with a predefined structure (react, node, python, vite, vite-react, vite-vue, vite-vanilla)"
    },
    "run_project": {
        "fn": run_project,
        "description": "Runs the current project in a new terminal window"
    }
}

def main():
    user_os = platform.system().lower()
    print("Detected OS: " + user_os)
    
    system_prompt = '''
    You are a helpful terminal-based AI Assistant specialized in Coding, Problem-solving, Creating, developing, and maintaining Full-Stack projects.
    You are capable of working in any programming language and on any framework.
    You are capable of creating folders and file structures.
    You work in start, plan, action, observe mode.
    For the given user query and the given available tools, plan the step-by-step execution, based on planning.
    Select the relevant tool from the available tools and based on tool selection perform an action to call the tool.
    Wait for the observation and based on the observation from the tool, resolve the user query further.
    
    Rules:
    - Follow the Output JSON Format.
    - Always perform one step at a time and wait for next input
    - Carefully analyse the user query
    - Always keep in mind that you'll be working for ''' + user_os + '''
    - The current working directory is ''' + os.getcwd() + '''
    - Always use Windows Command Prompt for writing commands when on Windows
    - For coding tasks, first understand what files exist in the current directory
    - When creating a file, make sure to use the appropriate extension and syntax for the language
    - When working with a frontend project, check package.json before installing packages and starting the project
    - If the user wants to edit a file, first read it, then modify it, then write it back
    - Be concise in your explanations but thorough in your actions
    - Prefer running commands over manually creating complex file structures
    - When creating project files, always ensure they are created within the project directory
    - When working with files, use relative paths starting at the project root
    - DO NOT create a nested directory with the project name inside the project
    - Example: For a React component in a project named "my-project", use "src/components/Component.jsx" NOT "my-project/src/components/Component.jsx"
    
    Output JSON Format:
    {
        "step": "string",
        "content": "string",
        "function": "The name of function if the step is action",
        "input": "The input parameter for the function"
    }
    
    Available Tools:
    - run_command: Executes a system command and returns the output
    - read_file: Reads the content of a file at the given path
    - write_file: Writes content to a file at the given path
    - create_project: Creates a new project with a predefined structure (react, node, python, vite, vite-react, vite-vue, vite-vanilla)
    - run_project: Runs the current project in a new terminal window
    
    Example:
    User Query: Create a python file for adding two numbers then displaying those two numbers.
    Output: {"step": "plan", "content": "The user wants you to create a file in python in which there should be the code to add two numbers"}
    Output: {"step": "plan", "content": "Okay from the available tools I should use run_command as I can create a file through system commands"}
    Output: {"step": "plan", "content": "Should choose the tool and according to its structure and to user requirement you should create an input or if not required should call the available tool"}
    Output: {"step": "action", "function": "write_file", "input": {"file_path": "add_numbers.py", "content": "a = float(input(\\'Enter first number: \\'))\\nb = float(input(\\'Enter second number: \\'))\\nsum = a + b\\nprint(f\\'{a} + {b} = {sum}\\')"}}
    Output: {"step": "observe", "content": "Content written to add_numbers.py"}
    Output: {"step": "output", "content": "The file has been created successfully"}
    
    Example 2:
    User Query: Setup the complete react setup for me and run it after setting things up
    Output: {"step": "plan", "content": "The user wants to create a Vite plus React app and execute it"}
    Output: {"step": "plan", "content": "Okay so now I should run the commands to create the Vite project and should install all the directories which are required for this to run"}
    Output: {"step": "plan", "content": "Make sure to create a new SEPARATE folder for this project and then for all FUTURE prompts related to this app you should work in that particular folder only"}
    Output: {"step": "action", "function": "create_project", "input": {"project_type": "vite-react", "project_name": "my-react-app"}}
    Output: {"step": "observe", "content": "The command will create the app we will then move to the next step"}
    Output: {"step": "action", "function": "run_project", "input": {"project_dir": "my-react-app"}}
    Output: {"step": "observe", "content": "The project is running in a new terminal window"}
    Output: {"step": "output", "content": "The Vite+React app is successfully running"}
    '''
    
    messages = [
        {"role": "system", "parts": [{"text": system_prompt}]}
    ]
    
    print("Terminal AI Assistant is ready! Type 'exit' or 'quit' to end the session.")
    while True:
        user_query = input('\nWhat would you like to do? ')
        print("\n🔍 Thinking...")
        
        if user_query.lower() in ['exit', 'quit']:
            print("Exiting Terminal AI Assistant. Goodbye!")
            break
        
        messages.append({"role": "user", "parts": [{"text": user_query}]})
        
        while True:
            prompt = "\n".join([msg["parts"][0]["text"] for msg in messages])
            
            try:
                model = genai.GenerativeModel("gemini-2.0-flash")
                response = model.generate_content(
                    prompt,
                    generation_config={
                        "response_mime_type": "application/json"
                    }
                )
                
                parsed_output = json.loads(response.text)
                messages.append({"role": "model", "parts": [{"text": json.dumps(parsed_output)}]})
                
                if parsed_output.get("step") == "plan":
                    print(f"Planning: {parsed_output.get('content')}")
                    continue
                
                if parsed_output.get("step") == "action":
                    tool_name = parsed_output.get("function")
                    tool_input = parsed_output.get("input")
                    print(f"⚙️ Action: Using {tool_name} with input: {str(tool_input)}")
                    
                    if tool_name in available_tools:
                        if tool_name == "create_project":
                            if isinstance(tool_input, dict):
                                output = available_tools[tool_name]["fn"](**tool_input)
                            else:
                                output = available_tools[tool_name]["fn"](tool_input)
                            
                            if "project_info" in output:
                                current_project.update(output["project_info"])
                                print(f"Project created: {current_project['name']} in {current_project['directory']}")
                        
                        elif tool_name == "write_file":
                            if isinstance(tool_input, dict):
                                file_path = tool_input.get("file_path") or tool_input.get("path")
                                
                                if current_project["directory"] and file_path and not os.path.isabs(file_path):
                                    if not file_path.startswith(current_project["directory"]) and not file_path.startswith(current_project["name"] + "/") and not file_path.startswith(current_project["name"] + "\\"):
                                        file_path = os.path.join(current_project["directory"], file_path)
                                    elif file_path.startswith(current_project["name"] + "/") or file_path.startswith(current_project["name"] + "\\"):
                                        rel_path = file_path[len(current_project["name"]) + 1:]
                                        file_path = os.path.join(current_project["directory"], rel_path)
                                    
                                    tool_input["file_path"] = file_path
                                    tool_input["path"] = file_path
                                    print(f"Writing to: {file_path}")
                                
                                output = available_tools[tool_name]["fn"](**tool_input)
                            else:
                                output = available_tools[tool_name]["fn"](tool_input)
                        
                        else:
                            if isinstance(tool_input, dict):
                                output = available_tools[tool_name]["fn"](**tool_input)
                            else:
                                output = available_tools[tool_name]["fn"](tool_input)
                        
                        print(f"Observation: {str(output)}")
                        messages.append({"role": "model", "parts": [{"text": json.dumps({"step": "observe", "output": output})}]})
                        continue
                    else:
                        error_msg = f"Error: Tool '{tool_name}' not available"
                        print(f"{error_msg}")
                        messages.append({"role": "model", "parts": [{"text": json.dumps({"step": "observe", "output": error_msg})}]})
                        continue
                
                if parsed_output.get("step") == "output":
                    print(f" Result: {parsed_output.get('content')}")
                    break
                
                print(f" Unexpected response format: {str(parsed_output)}")
                break
                
            except json.JSONDecodeError:
                print("Failed to parse response as JSON. Raw response:")
                print(response.text if 'response' in locals() else "No response received")
                break
                
            except Exception as e:
                print(f" Error processing response: {str(e)}")
                break

if __name__ == "__main__":
    main()