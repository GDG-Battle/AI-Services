# AI Services API Documentation

This document provides comprehensive information about all available endpoints in the AI Services API, including request and response formats.

## Base Configuration

- **Base URL**: `http://localhost:8000` (or your configured HOST:PORT)
- **Framework**: Flask
- **Max File Size**: 30MB
- **Upload Folder**: `../uploads`
- **Processed Data Folder**: `../data/extracted_data`

## Authentication

The API uses NVIDIA AI models and supports LangSmith tracing when configured with appropriate environment variables:
- `NVIDIA_API_KEY`
- `LANGSMITH_API_KEY` (optional)
- `LANGSMITH_PROJECT` (optional)

---

## Endpoints

### 1. Root Endpoint

**GET /**

Returns a welcome message.

#### Response
```
Welcome to the Code and Exercise Generation API!
```

---

### 2. Generate Exercise/QCM

**POST /generate**

Generates either a QCM (multiple choice questions) or a coding exercise based on the specified task type.

#### Request Body

```json
{
    "context": "string (optional) - Additional context for generation",
    "number_of_questions": "integer (optional, default: 1) - Number of questions for QCM",
    "user_query": "string (required) - The topic or description for generation",
    "task": "string (required) - Either 'qcm' or 'code'",
    "difficulty": "string (optional, default: 'easy') - Difficulty level"
}
```

#### Example Request - QCM Generation

```json
{
    "context": "",
    "number_of_questions": 5,
    "user_query": "generative AI QCM",
    "task": "qcm",
    "difficulty": "easy"
}
```

#### Example Request - Code Exercise Generation

```json
{
    "context": "",
    "number_of_questions": 0,
    "user_query": "reverse string",
    "task": "code",
    "difficulty": "easy"
}
```

#### Response - QCM Format

```json
{
    "quiz": [
        {
            "question": "string - The question text",
            "options": ["option1", "option2", "option3"],
            "answer": 1
        }
    ]
}
```

#### Response - Code Exercise Format

```json
{
    "exercise": "string - Problem description with function signature",
    "solution": "string - Python code solution",
    "inputs": [["arg1", "arg2"], ["arg3", "arg4"]],
    "outputs": ["expected_result1", "expected_result2"]
}
```

#### Error Response

```json
{
    "error": "string - Error message"
}
```

**Status Codes:**
- `200`: Success
- `400`: Bad Request (invalid task type or other validation errors)

---

### 3. Evaluate Code

**POST /evaluate**

Evaluates user-submitted code against test cases and provides feedback.

#### Request Body

```json
{
    "exercise": "string (required) - The exercise description",
    "user_code": "string (required) - User's Python code solution",
    "inputs": ["array of test inputs"],
    "outputs": ["array of expected outputs"]
}
```

#### Example Request

```json
{
    "exercise": "Write a function called reverse_string that takes a string as input and returns the reversed string. The function signature is def reverse_string(s: str) -> str:",
    "user_code": "def reverse_string(s: str) -> str:\n    return s[::-1]",
    "inputs": [
        "hello",
        "world",
        "python"
    ],
    "outputs": [
        "olleh",
        "dlrow",
        "nohtyp"
    ]
}
```

#### Response

```json
{
    "correct": "boolean - Whether the code is correct",
    "feedback": "string - Markdown formatted feedback from AI tutor"
}
```

#### Error Response

```json
{
    "error": "string - Error message"
}
```

**Status Codes:**
- `200`: Success
- `400`: Bad Request

---

### 4. AI Assistant (Router)

**POST /aiassistant**

Routes queries to appropriate AI agents (mentor or hint) based on the query type.

#### Request Body

```json
{
    "query": "string (required) - User's question or request"
}
```

#### Example Request

```json
{
    "query": "Explain machine learning concepts"
}
```

#### Response

```json
{
    "type": "string - Agent type ('mentor' or 'hint')",
    "response": "string - AI response content"
}
```

#### Agent Types

- **mentor**: For explanation/learning about concepts
- **hint**: For help with specific problems/challenges

#### Error Response

```json
{
    "error": "string - Error message"
}
```

**Status Codes:**
- `200`: Success
- `400`: Bad Request (missing query)

---

### 5. Process Documents

**POST /process-documents**

Processes uploaded documents and extracts data for use in the AI system.

#### Request

- **Content-Type**: `multipart/form-data`
- **Field Name**: `files` (accepts multiple files)
- **Max File Size**: 30MB per request

#### Supported File Types

The API accepts various document formats including:
- PDF files
- Word documents (.docx)
- PowerPoint presentations (.pptx)
- Text files (.txt)
- Images (for OCR processing)

#### Response

```json
{
    "message": "Documents processed successfully",
    "results": "object - Processing results with details",
    "total_processing_time_seconds": "number - Time taken to process"
}
```

#### Error Responses

```json
{
    "error": "No files provided"
}
```

```json
{
    "error": "No selected files"
}
```

```json
{
    "error": "No valid files uploaded"
}
```

**Status Codes:**
- `200`: Success
- `400`: Bad Request (no files provided)
- `500`: Internal Server Error

---

## Common Error Handling

All endpoints return errors in the following format:

```json
{
    "error": "string - Descriptive error message"
}
```

## Environment Variables

Required environment variables:

```env
NVIDIA_API_KEY=your_nvidia_api_key
HOST=0.0.0.0
PORT=8000
```

Optional environment variables for LangSmith tracing:

```env
LANGSMITH_API_KEY=your_langsmith_api_key
LANGSMITH_PROJECT=code-exercise-generation
LANGSMITH_TRACING_V2=true
```

## Usage Examples

### Using curl

#### Generate a QCM
```bash
curl -X POST http://localhost:8000/generate \
  -H "Content-Type: application/json" \
  -d '{
    "user_query": "Python basics",
    "task": "qcm",
    "difficulty": "easy",
    "number_of_questions": 3
  }'
```

#### Evaluate Code
```bash
curl -X POST http://localhost:8000/evaluate \
  -H "Content-Type: application/json" \
  -d '{
    "exercise": "Write a function to add two numbers",
    "user_code": "def add(a, b):\n    return a + b",
    "inputs": [[1, 2], [3, 4]],
    "outputs": [3, 7]
  }'
```

#### Upload Documents
```bash
curl -X POST http://localhost:8000/process-documents \
  -F "files=@document1.pdf" \
  -F "files=@document2.docx"
```

### Using Python requests

```python
import requests

# Generate QCM
response = requests.post('http://localhost:8000/generate', json={
    "user_query": "machine learning",
    "task": "qcm",
    "difficulty": "medium",
    "number_of_questions": 5
})

# AI Assistant
response = requests.post('http://localhost:8000/aiassistant', json={
    "query": "How do neural networks work?"
})
```

## Notes

- All POST endpoints expect JSON content unless specified otherwise
- File uploads use multipart/form-data
- Responses are in JSON format except for the root endpoint
- The API automatically creates necessary directories for file storage
- Uploaded files are automatically cleaned up after processing
