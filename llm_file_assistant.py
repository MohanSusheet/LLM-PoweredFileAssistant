import os
import json
from dotenv import load_dotenv
from openai import OpenAI

from fs_tools import (
    read_file,
    list_files,
    write_file,
    search_in_file
)

load_dotenv()

client = OpenAI(api_key = os.getenv("OPENROUTER_API_KEY"), base_url="https://openrouter.ai/api/v1")


SYSTEM_PROMPT = """
You are an AI File Assistant.

You have access to filesystem tools.

Whenever the user asks to:

- read a file
- search inside a file
- list files
- write a file

ALWAYS use the appropriate tool.

Never invent file contents.

Never assume files exist.

Use tools whenever possible.
"""

# Defining the Tools for the LLM
TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "read_file",
            "description": "Read a TXT, PDF or DOCX file and return its contents with metadata.",
            "parameters": {
                "type": "object",
                "properties": {
                    "filepath": {
                        "type": "string",
                        "description": "Path to the file."
                    }
                },
                "required": ["filepath"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "list_files",
            "description": "List all files inside a directory. Optionally filter by file extension.",
            "parameters": {
                "type": "object",
                "properties": {
                    "directory": {
                        "type": "string",
                        "description": "Directory to inspect."
                    },
                    "extension": {
                        "type": "string",
                        "description": "Optional file extension such as .pdf or .txt."
                    }
                },
                "required": ["directory"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "write_file",
            "description": "Write text content to a file and create parent directories if they do not exist.",
            "parameters": {
                "type": "object",
                "properties": {
                    "filepath": {
                        "type": "string"
                    },
                    "content": {
                        "type": "string"
                    }
                },
                "required": [
                    "filepath",
                    "content"
                ]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "search_in_file",
            "description": "Search for a keyword inside a TXT, PDF or DOCX file. Requires both filepath and keyword.",
            "parameters": {
                "type": "object",
                "properties": {
                    "filepath": {
                        "type": "string"
                    },
                    "keyword": {
                        "type": "string"
                    }
                },
                "required": [
                    "filepath",
                    "keyword"
                ]
            }
        }
    }
]

#Request Dispatcher
def execute_tool(function_name: str, arguments: dict):
    """
    Executes the requested tool using the provided arguments.

    Args:
        function_name (str): Name of the tool.
        arguments (dict): Arguments for the tool.

    Returns:
        dict: Tool execution result.
    """

    if function_name == "read_file":
        return read_file(**arguments)

    elif function_name == "list_files":
        return list_files(**arguments)

    elif function_name == "write_file":
        return write_file(**arguments)

    elif function_name == "search_in_file":
        return search_in_file(**arguments)

    else:
        return {
            "success": False,
            "message": f"Unknown tool: {function_name}",
            "data": None
        }


def get_llm_response(user_query: str):
    response = client.chat.completions.create(
        model="google/gemini-2.5-flash",
        messages=[
            {
                "role":"system",
                "content":SYSTEM_PROMPT
            },
            {
                "role":"user",
                "content":user_query
            }
        ],
        tools=TOOLS,
        tool_choice="auto",
        temperature=0,
        max_tokens=300
    )

    return response


def chat(user_query: str):
    response = get_llm_response(user_query)

    # print(response)
    message = response.choices[0].message
    print(f"Message from response: {message}")

    if not message.tool_calls:
            return message.content

    # if message.tool_calls:
    #     print("Tool call detected!")
    # else:
    #     print("No Too call")

    tool_call = message.tool_calls[0]

    function_name = tool_call.function.name

    arguments = json.loads(tool_call.function.arguments)

    # print(f"function name is: {function_name}")
    # print(f"arguments: {arguments}")

    tool_result = execute_tool(function_name, arguments)

    print(f"\n Tool Result: {json.dumps(tool_result, indent = 4)}")
    messages = [
        {
            "role": "user",
            "content": user_query
        },
        message,
        {
            "role": "tool",
            "tool_call_id": tool_call.id,
            "content": json.dumps(tool_result)
        }
    ]

    final_response = client.chat.completions.create(
        model="google/gemini-2.5-flash",
        messages=messages,
        temperature=0,
        max_tokens=300
    )

    return final_response.choices[0].message.content


if __name__ == "__main__":

    print("=" * 60)
    print("LLM Powered File Assistant")
    print("Type 'exit' to quit.")
    print("=" * 60)

    while True:

        query = input("\nYou: ")

        if query.lower() == "exit":
            print("Goodbye!")
            break

        try:
            answer = chat(query)

            print("\nAssistant:")
            print(answer)

        except Exception as e:
            print(f"\nError: {e}")

