# AI Service Python Client

This directory contains the Python client for integrating with the AI Service.

## Overview

The AI service is implemented entirely in Python/Flask and provides a robust client library for other Python services to integrate with.

## Features

- **Robust Error Handling**: Handles network errors, service unavailability, and invalid requests
- **Retry Logic**: Automatic retry with exponential backoff
- **Circuit Breaker**: Prevents cascading failures when service is down
- **Type Safety**: Uses dataclasses and enums for better type checking
- **Logging**: Comprehensive logging for debugging
- **Convenience Functions**: Quick functions for common operations

### Installation

```bash
pip install -r requirements.txt
```

### Basic Usage

```python
from ai_service_client import AIServiceClient, TaskType, Difficulty

# Create client (uses gateway by default)
client = AIServiceClient(use_gateway=True)

# Generate a code exercise
exercise = client.generate_exercise(
    user_query="implement bubble sort",
    task=TaskType.CODE,
    difficulty=Difficulty.MEDIUM
)

# Evaluate user code
result = client.evaluate_code(
    exercise="Write a function to sort a list",
    user_code="def sort_list(arr): return sorted(arr)",
    inputs=[["3,1,2"], ["5,4,3,2,1"]],
    outputs=[["1,2,3"], ["1,2,3,4,5"]]
)

# Use AI assistant
help_response = client.ai_assistant("How do I optimize this algorithm?")
```

### Quick Functions

For simple operations, use the convenience functions:

```python
from ai_service_client import quick_generate_code, quick_ask_ai

# Quick code generation
exercise = quick_generate_code("binary search", "hard")

# Quick AI assistance
response = quick_ask_ai("Explain time complexity")
```

### Configuration

Customize the client behavior:

```python
from ai_service_client import AIServiceClient, AIServiceConfig

config = AIServiceConfig(
    base_url="http://localhost:8000",
    timeout=60,
    max_retries=5,
    use_circuit_breaker=True
)

client = AIServiceClient(config=config, use_gateway=False)
```

### Environment Variables

- `GATEWAY_SERVICE_URL`: Gateway service URL (default: `http://localhost:8082`)
- `AI_SERVICE_URL`: Direct AI service URL (default: `http://localhost:8000`)

## Service Endpoints

### Via Gateway (Production)
- Base URL: `http://localhost:8082/api/v1/ai`
- All endpoints are prefixed with `/api/v1/ai`

### Direct Access (Development)
- Base URL: `http://localhost:8000`
- Direct access to Flask endpoints

### Available Endpoints

1. **Generate Exercise/QCM**: `POST /generate`
   ```json
   {
     "context": "Programming fundamentals",
     "number_of_questions": 1,
     "user_query": "implement merge sort",
     "task": "code",
     "difficulty": "medium"
   }
   ```

2. **Evaluate Code**: `POST /evaluate`
   ```json
   {
     "exercise": "Sort an array",
     "user_code": "def sort_array(arr): return sorted(arr)",
     "inputs": ["[3,1,2]"],
     "outputs": ["[1,2,3]"]
   }
   ```

3. **AI Assistant**: `POST /aiassistant`
   ```json
   {
     "query": "How do I optimize this sorting algorithm?"
   }
   ```

4. **Process Documents**: `POST /process-documents`
   - Multipart form upload with `files` field

5. **Health Check**: `GET /health`
6. **Service Info**: `GET /actuator/info`

## Error Handling

The Python client handles various error scenarios:

- **Network Errors**: Automatic retry with exponential backoff
- **Service Unavailable (500, 503)**: Circuit breaker protection
- **Bad Request (400)**: Invalid request exception
- **Timeout**: Configurable timeout with retries

## Testing

Run the client examples:

```bash
# Python client
python ai_service_client.py

# Check if AI service is reachable
python -c "from ai_service_client import create_client; print(create_client().is_healthy())"
```

## Integration Examples

### In a Flask Application

```python
from flask import Flask, request, jsonify
from ai_service_client import create_client

app = Flask(__name__)
ai_client = create_client()

@app.route('/api/exercise', methods=['POST'])
def create_exercise():
    data = request.json
    try:
        exercise = ai_client.generate_exercise(
            user_query=data['topic'],
            task=data.get('type', 'code'),
            difficulty=data.get('difficulty', 'medium')
        )
        return jsonify(exercise)
    except Exception as e:
        return jsonify({'error': str(e)}), 500
```

### In a Django Application

```python
from django.http import JsonResponse
from django.views import View
from ai_service_client import create_client

class ExerciseView(View):
    def __init__(self):
        self.ai_client = create_client()
    
    def post(self, request):
        try:
            exercise = self.ai_client.generate_exercise(
                user_query=request.POST['topic']
            )
            return JsonResponse(exercise)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
```

## Best Practices

1. **Use Gateway in Production**: Always route through the gateway for load balancing and monitoring
2. **Handle Errors Gracefully**: Implement proper error handling and fallback mechanisms
3. **Configure Timeouts**: Set appropriate timeouts for your use case
4. **Monitor Circuit Breaker**: Check circuit breaker state for service health
5. **Log Appropriately**: Use proper logging levels (DEBUG for development, INFO for production)
6. **Cache When Possible**: Cache AI responses when appropriate to reduce load
