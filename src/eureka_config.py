import os
from py_eureka_client import eureka_client

# Eureka configuration
EUREKA_SERVER_URL = os.getenv('DISCOVERY_SERVICE_URL', 'http://localhost:8080/eureka')
SERVICE_NAME = os.getenv('SERVICE_NAME', 'ai-service')
SERVICE_PORT = int(os.getenv('PORT', 8000))
SERVICE_HOST = os.getenv('HOST', 'localhost')

# Health check endpoint
HEALTH_CHECK_URL = f"http://{SERVICE_HOST}:{SERVICE_PORT}/health"
HOME_PAGE_URL = f"http://{SERVICE_HOST}:{SERVICE_PORT}/"
STATUS_PAGE_URL = f"http://{SERVICE_HOST}:{SERVICE_PORT}/actuator/info"

def register_with_eureka():
    """Register the Flask AI service with Eureka Discovery Server"""
    try:
        eureka_client.init(
            eureka_server=EUREKA_SERVER_URL,
            app_name=SERVICE_NAME,
            instance_port=SERVICE_PORT,
            instance_host=SERVICE_HOST,
            health_check_url=HEALTH_CHECK_URL,
            home_page_url=HOME_PAGE_URL,
            status_page_url=STATUS_PAGE_URL,
            # Optional metadata
            metadata={
                "description": "AI service for code generation, evaluation, and assistance",
                "version": "1.0.0",
                "framework": "Flask",
                "language": "Python"
            }
        )
        print(f"Successfully registered {SERVICE_NAME} with Eureka at {EUREKA_SERVER_URL}")
        return True
    except Exception as e:
        print(f"Failed to register with Eureka: {str(e)}")
        return False

def unregister_from_eureka():
    """Unregister the service from Eureka when shutting down"""
    try:
        eureka_client.stop()
        print(f"Successfully unregistered {SERVICE_NAME} from Eureka")
    except Exception as e:
        print(f"Error during Eureka unregistration: {str(e)}")
