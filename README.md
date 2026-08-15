# LLM-Powered File Assistant

## Project Overview

The **LLM-Powered File Assistant** is a Python application that demonstrates how a **Large Language Model (LLM)** can safely interact with a local file system using **Tool (Function) Calling**.

Instead of allowing the LLM to directly access files, the application exposes a controlled set of Python functions (tools). The LLM intelligently decides which tool to invoke based on the user's request, while the Python application executes the requested operation and returns the result back to the LLM.

This project demonstrates one of the core concepts behind modern AI agents such as **ChatGPT, Claude, Cursor AI, GitHub Copilot, and other autonomous AI assistants**.

---

# Learning Objectives

This project demonstrates the following concepts:

- Understanding LLM Tool / Function Calling
- Designing structured tool interfaces using JSON Schemas
- Implementing File I/O operations in Python
- Parsing PDF, DOCX and TXT files
- Building an AI-powered file assistant
- Integrating an LLM using the OpenAI-compatible API (OpenRouter)
- Building an end-to-end tool execution pipeline

---

# Features

The assistant currently supports the following operations:

- Read TXT, PDF and DOCX files
- List files inside a directory
- Write text content into files
- Search keywords inside files
- Automatic tool selection using an LLM
- Natural language interaction with the user

---

# Technologies Used

- Python 3.x
- OpenRouter API
- Google Gemini 2.5 Flash
- OpenAI Python SDK
- python-dotenv
- PyMuPDF
- python-docx
- pathlib

---

# Core Concepts Demonstrated

## 1. Tool (Function) Calling

Instead of generating an answer directly, the LLM can decide to invoke a Python function.

Example:

User:

> Read `resume_john.pdf`

LLM:

```
Call Tool:
read_file(filepath="resume_john.pdf")
```

Python:

```
read_file("resume_john.pdf")
```

Result:

```
Resume contents...
```

The result is then returned back to the LLM, which generates a human-friendly response.

---

## 2. Structured Tool Definitions

Each Python function is described using a JSON Schema.

Example:

```python
{
    "type": "function",
    "function": {
        "name": "read_file",
        ...
    }
}
```

This allows the LLM to understand:

- available functions
- required parameters
- parameter types
- purpose of each tool

---

## 3. Dispatcher Pattern

The application separates the LLM from the implementation.

Instead of the LLM calling Python directly:

```
LLM
  ↓
execute_tool()
  ↓
read_file()
```

The dispatcher maps the selected tool name to the corresponding Python function.

This makes adding future tools very simple.

---

## 4. Structured API Responses

Every filesystem tool returns a consistent response format.

Example:

```python
{
    "success": True,
    "message": "File read successfully.",
    "data": {
        ...
    }
}
```

A consistent response structure simplifies error handling and allows the LLM to interpret tool outputs reliably.

---

# Project Architecture

```
                    User
                      │
                      ▼
             LLM (Gemini via OpenRouter)
                      │
      Decides which tool should be used
                      │
                      ▼
               execute_tool()
                      │
        ┌─────────────┼─────────────┐
        │             │             │
        ▼             ▼             ▼
   read_file()   list_files()  search_in_file()
                      │
                      ▼
               write_file()
                      │
                      ▼
          Structured JSON Response
                      │
                      ▼
             Returned back to LLM
                      │
                      ▼
        Natural Language Response
                      │
                      ▼
                     User
```

---

# Project Structure

```
LLM-PoweredFileAssistant/
│
├── resumes/
│   ├── sample1.pdf
│   ├── sample2.docx
│   └── sample3.txt
│
├── output/
│
├── fs_tools.py
├── llm_file_assistant.py
├── requirements.txt
├── .env
├── README.md
│
├── test_read_file.py
├── test_list_files.py
├── test_write_file.py
└── test_search_in_file.py
```

---

# Control Flow

The execution flow of the application is shown below.

---

## Step 1

The user runs

```bash
python llm_file_assistant.py
```

Execution begins from:

```python
if __name__ == "__main__":
    main()
```

---

## Step 2

The application:

- loads environment variables
- creates the OpenRouter client
- loads all available tool definitions

---

## Step 3

The user enters a query.

Example:

```
Read resumes/resume_maria_garcia.pdf
```

---

## Step 4

The query is sent to the LLM.

```python
get_llm_response(user_query)
```

The LLM receives:

- system prompt
- user query
- available tool definitions

---

## Step 5

The LLM decides whether a tool is required.

If no tool is needed:

```
LLM
↓

Natural Response
```

If a tool is required:

```
LLM
↓

Tool Call
```

Example:

```
read_file(
    filepath="resumes/resume_maria_garcia.pdf"
)
```

---

## Step 6

The application extracts:

- tool name
- tool arguments

Example:

```python
function_name = "read_file"

arguments = {
    "filepath": "resumes/resume_maria_garcia.pdf"
}
```

---

## Step 7

The dispatcher executes the corresponding Python function.

```python
execute_tool(
    function_name,
    arguments
)
```

Which internally calls:

```python
read_file(...)
```

---

## Step 8

The filesystem tool performs the requested operation.

Example:

- open PDF
- extract text
- collect metadata

The tool returns a structured dictionary.

Example:

```python
{
    "success": True,
    "message": "...",
    "data": {
        ...
    }
}
```

---

## Step 9

The tool result is sent back to the LLM.

The conversation now contains:

- original user message
- assistant tool call
- tool response

---

## Step 10

The LLM generates a natural language response.

Example:

```
The resume was successfully read.

The candidate has experience in Python, Machine Learning and SQL.
```

instead of displaying raw JSON.

---

# Overall Workflow

```
User Query
     │
     ▼
LLM receives query
     │
     ▼
LLM selects appropriate tool
     │
     ▼
execute_tool()
     │
     ▼
Filesystem Tool
     │
     ▼
Structured JSON Result
     │
     ▼
LLM interprets result
     │
     ▼
Natural Language Response
```

---

# Sample Queries

```
Read resumes/resume_john_doe.pdf
```

```
List all PDF files in the resumes folder
```

```
Search for the keyword Python in resumes/resume_maria_garcia.txt
```

```
Write "Summary generated by AI" to output/summary.txt
```

```
Read all resumes in the resumes folder
```

---

# Future Enhancements

This project can be extended with several additional capabilities:

- Recursive directory traversal
- Semantic search using embeddings
- Resume summarization
- Resume comparison
- Candidate ranking
- RAG (Retrieval-Augmented Generation)
- Multi-turn conversational memory
- Streamlit or Gradio web interface
- Support for Excel, CSV and PowerPoint files
- Vector database integration (FAISS/ChromaDB)

---

# Conclusion

This project demonstrates how Large Language Models can safely interact with external systems through **structured tool calling** rather than direct execution.

By combining Python-based filesystem operations with LLM reasoning, the assistant is able to understand user intent, select the appropriate tool, execute the requested action, and generate meaningful natural language responses.

The architecture used in this project closely mirrors the design employed by modern AI assistants and agent frameworks, making it an excellent foundation for building more advanced autonomous AI applications.