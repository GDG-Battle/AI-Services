"""
Enhanced Python client for AI Service
This client provides a robust interface for Python services to communicate with the AI service
Includes error handling, retry logic, and circuit breaker pattern
"""

import requests
import json
import time
import logging
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from enum import Enum
import os
from functools import wraps

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class TaskType(Enum):
    """Supported task types for exercise generation"""
    QCM = "qcm"
    CODE = "code"

class Difficulty(Enum):
    """Supported difficulty levels"""
    EASY = "easy"
    MEDIUM = "medium"
    HARD = "hard"

@dataclass
class AIServiceConfig:
    """Configuration for AI Service client"""
    base_url: str
    timeout: int = 30
    max_retries: int = 3
    retry_delay: float = 1.0
    use_circuit_breaker: bool = True
    circuit_breaker_threshold: int = 5
    circuit_breaker_timeout: int = 60

class CircuitBreakerState(Enum):
    """Circuit breaker states"""
    CLOSED = "closed"
    OPEN = "open"
    HALF_OPEN = "half_open"

class CircuitBreaker:
    """Simple circuit breaker implementation"""
    
    def __init__(self, threshold: int = 5, timeout: int = 60):
        self.threshold = threshold
        self.timeout = timeout
        self.failure_count = 0
        self.last_failure_time = 0
        self.state = CircuitBreakerState.CLOSED
    
    def call(self, func):
        """Decorator for circuit breaker functionality"""
        @wraps(func)
        def wrapper(*args, **kwargs):
            if self.state == CircuitBreakerState.OPEN:
                if time.time() - self.last_failure_time > self.timeout:
                    self.state = CircuitBreakerState.HALF_OPEN
                else:
                    raise Exception("Circuit breaker is OPEN")
            
            try:
                result = func(*args, **kwargs)
                if self.state == CircuitBreakerState.HALF_OPEN:
                    self.state = CircuitBreakerState.CLOSED
                    self.failure_count = 0
                return result
            except Exception as e:
                self.failure_count += 1
                self.last_failure_time = time.time()
                
                if self.failure_count >= self.threshold:
                    self.state = CircuitBreakerState.OPEN
                
                raise e
        return wrapper

class AIServiceException(Exception):
    """Base exception for AI Service errors"""
    pass

class AIServiceUnavailableException(AIServiceException):
    """Exception when AI Service is unavailable"""
    pass

class InvalidRequestException(AIServiceException):
    """Exception for invalid requests"""
    pass

class AIServiceClient:
    """Enhanced client for interacting with the AI Service"""
    
    def __init__(self, config: Optional[AIServiceConfig] = None, use_gateway: bool = True):
        """
        Initialize the AI Service client
        
        Args:
            config: Configuration object for the client
            use_gateway: Whether to use gateway routing (recommended for production)
        """
        if config:
            self.config = config
        else:
            # Default configuration
            if use_gateway:
                gateway_url = os.getenv('GATEWAY_SERVICE_URL', 'http://localhost:8082')
                base_url = f"{gateway_url}/api/v1/ai"
            else:
                base_url = os.getenv('AI_SERVICE_URL', 'http://localhost:8000')
            
            self.config = AIServiceConfig(base_url=base_url)
            
        self.session = requests.Session()
        self.session.headers.update({
            'Content-Type': 'application/json',
            'User-Agent': 'AIServiceClient/1.0'
        })
        
        # Initialize circuit breaker if enabled
        if self.config.use_circuit_breaker:
            self.circuit_breaker = CircuitBreaker(
                threshold=self.config.circuit_breaker_threshold,
                timeout=self.config.circuit_breaker_timeout
            )
        else:
            self.circuit_breaker = None
    
    def _make_request(self, method: str, endpoint: str, **kwargs) -> Dict[str, Any]:
        """
        Make HTTP request with retry logic and circuit breaker
        
        Args:
            method: HTTP method (GET, POST, etc.)
            endpoint: API endpoint
            **kwargs: Additional arguments for requests
            
        Returns:
            Response JSON data
            
        Raises:
            AIServiceException: On API errors
        """
        url = f"{self.config.base_url}{endpoint}"
        
        def _request():
            for attempt in range(self.config.max_retries + 1):
                try:
                    logger.debug(f"Making {method} request to {url}, attempt {attempt + 1}")
                    
                    response = self.session.request(
                        method=method,
                        url=url,
                        timeout=self.config.timeout,
                        **kwargs
                    )
                    
                    if response.status_code == 200:
                        return response.json()
                    elif response.status_code == 400:
                        raise InvalidRequestException(f"Invalid request: {response.text}")
                    elif response.status_code in [500, 503]:
                        raise AIServiceUnavailableException(f"AI service unavailable: {response.text}")
                    else:
                        response.raise_for_status()
                        
                except requests.exceptions.RequestException as e:
                    if attempt < self.config.max_retries:
                        delay = self.config.retry_delay * (2 ** attempt)  # Exponential backoff
                        logger.warning(f"Request failed, retrying in {delay}s: {e}")
                        time.sleep(delay)
                    else:
                        logger.error(f"Request failed after {self.config.max_retries + 1} attempts: {e}")
                        raise AIServiceUnavailableException(f"Failed to connect to AI service: {e}")
            
            raise AIServiceUnavailableException("Max retries exceeded")
        
        if self.circuit_breaker:
            return self.circuit_breaker.call(_request)()
        else:
            return _request()
    
    def generate_exercise(self, 
                         context: str = "",
                         number_of_questions: int = 1,
                         user_query: str = "",
                         task: TaskType = TaskType.QCM,
                         difficulty: Difficulty = Difficulty.EASY) -> Dict[str, Any]:
        """
        Generate code exercises or QCM
        
        Args:
            context: Additional context for generation
            number_of_questions: Number of questions to generate
            user_query: User's specific query
            task: Type of task (QCM or CODE)
            difficulty: Difficulty level
            
        Returns:
            Generated exercise response
        """
        payload = {
            "context": context,
            "number_of_questions": number_of_questions,
            "user_query": user_query,
            "task": task.value,
            "difficulty": difficulty.value
        }
        
        logger.info(f"Generating {task.value} exercise: {user_query}")
        return self._make_request("POST", "/generate", json=payload)
    
    def evaluate_code(self,
                     exercise: str,
                     user_code: str,
                     inputs: List[str],
                     outputs: List[str]) -> Dict[str, Any]:
        """
        Evaluate user code submission
        
        Args:
            exercise: Exercise description
            user_code: User's code submission
            inputs: Test inputs
            outputs: Expected outputs
            
        Returns:
            Evaluation result with feedback
        """
        payload = {
            "exercise": exercise,
            "user_code": user_code,
            "inputs": inputs,
            "outputs": outputs
        }
        
        logger.info("Evaluating user code submission")
        return self._make_request("POST", "/evaluate", json=payload)
    
    def ai_assistant(self, query: str) -> Dict[str, Any]:
        """
        Get AI assistance for a query
        
        Args:
            query: User's query for the AI assistant
            
        Returns:
            AI assistant response
        """
        payload = {"query": query}
        
        logger.info(f"AI assistant query: {query[:50]}...")
        return self._make_request("POST", "/aiassistant", json=payload)
    
    def process_documents(self, file_paths: List[str]) -> Dict[str, Any]:
        """
        Process uploaded documents
        
        Args:
            file_paths: List of file paths to process
            
        Returns:
            Document processing results
        """
        files = []
        for file_path in file_paths:
            if not os.path.exists(file_path):
                raise FileNotFoundError(f"File not found: {file_path}")
            
            with open(file_path, 'rb') as f:
                files.append(('files', (os.path.basename(file_path), f.read(), 'application/octet-stream')))
        
        logger.info(f"Processing {len(files)} documents")
        
        # Remove Content-Type header for multipart upload
        headers = {k: v for k, v in self.session.headers.items() if k.lower() != 'content-type'}
        
        url = f"{self.config.base_url}/process-documents"
        response = requests.post(url, files=files, headers=headers, timeout=self.config.timeout)
        
        if response.status_code == 200:
            return response.json()
        else:
            response.raise_for_status()
    
    def health_check(self) -> Dict[str, Any]:
        """
        Check service health
        
        Returns:
            Health status
        """
        return self._make_request("GET", "/health")
    
    def service_info(self) -> Dict[str, Any]:
        """
        Get service information
        
        Returns:
            Service info
        """
        return self._make_request("GET", "/actuator/info")
    
    def is_healthy(self) -> bool:
        """
        Check if the AI service is healthy
        
        Returns:
            True if service is healthy, False otherwise
        """
        try:
            health = self.health_check()
            return health.get("status") == "UP"
        except Exception as e:
            logger.warning(f"Health check failed: {e}")
            return False


# Convenience functions for quick usage
def create_client(use_gateway: bool = True, **config_kwargs) -> AIServiceClient:
    """
    Create a configured AI Service client
    
    Args:
        use_gateway: Whether to use gateway routing
        **config_kwargs: Additional configuration parameters
        
    Returns:
        Configured AIServiceClient instance
    """
    config = AIServiceConfig(**config_kwargs) if config_kwargs else None
    return AIServiceClient(config=config, use_gateway=use_gateway)

def quick_generate_code(topic: str, difficulty: str = "easy") -> Dict[str, Any]:
    """
    Quick function to generate a code exercise
    
    Args:
        topic: Topic for the exercise
        difficulty: Difficulty level
        
    Returns:
        Generated exercise
    """
    client = create_client()
    return client.generate_exercise(
        user_query=topic,
        task=TaskType.CODE,
        difficulty=Difficulty(difficulty)
    )

def quick_generate_qcm(topic: str, num_questions: int = 5) -> Dict[str, Any]:
    """
    Quick function to generate QCM questions
    
    Args:
        topic: Topic for the questions
        num_questions: Number of questions
        
    Returns:
        Generated QCM
    """
    client = create_client()
    return client.generate_exercise(
        user_query=topic,
        number_of_questions=num_questions,
        task=TaskType.QCM
    )

def quick_evaluate(exercise: str, code: str, test_inputs: List[str], expected_outputs: List[str]) -> Dict[str, Any]:
    """
    Quick function to evaluate code
    
    Args:
        exercise: Exercise description
        code: User's code
        test_inputs: Test input cases
        expected_outputs: Expected output cases
        
    Returns:
        Evaluation result
    """
    client = create_client()
    return client.evaluate_code(exercise, code, test_inputs, expected_outputs)

def quick_ask_ai(question: str) -> Dict[str, Any]:
    """
    Quick function to ask AI assistant
    
    Args:
        question: Question to ask
        
    Returns:
        AI response
    """
    client = create_client()
    return client.ai_assistant(question)


# Example usage and testing
if __name__ == "__main__":
    # Example 1: Basic usage with default configuration
    print("🤖 AI Service Client Examples")
    print("=" * 50)
    
    try:
        # Create client
        client = create_client(use_gateway=True)
        
        # Check service health
        print("\n1. Health Check:")
        health = client.health_check()
        print(f"   Status: {health.get('status', 'Unknown')}")
        print(f"   Service healthy: {client.is_healthy()}")
        
        # Generate a code exercise
        print("\n2. Generate Code Exercise:")
        exercise = client.generate_exercise(
            context="Python programming basics",
            user_query="write a function to reverse a string",
            task=TaskType.CODE,
            difficulty=Difficulty.EASY
        )
        print(f"   Generated exercise: {exercise.get('title', 'No title')}")
        
        # Generate QCM
        print("\n3. Generate QCM:")
        qcm = client.generate_exercise(
            user_query="Python data structures",
            number_of_questions=3,
            task=TaskType.QCM,
            difficulty=Difficulty.MEDIUM
        )
        print(f"   Generated QCM with {len(qcm.get('questions', []))} questions")
        
        # Evaluate some code
        print("\n4. Evaluate Code:")
        evaluation = client.evaluate_code(
            exercise="Write a function to reverse a string",
            user_code="def reverse_string(s: str) -> str:\n    return s[::-1]",
            inputs=["hello", "world"],
            outputs=["olleh", "dlrow"]
        )
        print(f"   Evaluation score: {evaluation.get('score', 'N/A')}")
        
        # Use AI assistant
        print("\n5. AI Assistant:")
        assistant_response = client.ai_assistant(
            "How do I implement a binary search algorithm in Python?"
        )
        print(f"   Response type: {assistant_response.get('type', 'Unknown')}")
        
        print("\n✅ All examples completed successfully!")
        
    except AIServiceUnavailableException as e:
        print(f"❌ AI Service is unavailable: {e}")
    except InvalidRequestException as e:
        print(f"❌ Invalid request: {e}")
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
    
    # Example 2: Using quick convenience functions
    print("\n" + "=" * 50)
    print("🚀 Quick Functions Examples")
    print("=" * 50)
    
    try:
        # Quick code generation
        print("\n1. Quick Code Generation:")
        code_exercise = quick_generate_code("fibonacci sequence", "medium")
        print(f"   Exercise: {code_exercise.get('title', 'Generated')}")
        
        # Quick QCM generation
        print("\n2. Quick QCM Generation:")
        qcm_questions = quick_generate_qcm("object-oriented programming", 3)
        print(f"   QCM: {len(qcm_questions.get('questions', []))} questions")
        
        # Quick AI assistance
        print("\n3. Quick AI Assistance:")
        ai_help = quick_ask_ai("What is the time complexity of quicksort?")
        print(f"   AI Response: {ai_help.get('response', 'No response')[:100]}...")
        
        print("\n✅ Quick functions examples completed!")
        
    except Exception as e:
        print(f"❌ Error in quick functions: {e}")
        
    print("\n🎉 AI Service Client demo completed!")
