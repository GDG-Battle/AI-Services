import os
import socket
from py_eureka_client import eureka_client

def get_container_hostname():
    """Get the container's hostname for Eureka registration"""
    # In Docker, hostname should be the service name
    hostname = os.getenv('EUREKA_INSTANCE_HOSTNAME', socket.gethostname())
    return hostname

def get_container_ip():
    """Get the container's IP address"""
    try:
        hostname = socket.gethostname()
        container_ip = socket.gethostbyname(hostname)
        return container_ip
    except Exception as e:
        print(f"Could not get container IP: {e}")
        return None

# Eureka configuration
EUREKA_SERVER_URL = os.getenv('DISCOVERY_SERVICE_URL', 'http://localhost:8080/eureka')
SERVICE_NAME = os.getenv('SERVICE_NAME', 'ai-service')
SERVICE_PORT = int(os.getenv('PORT', 8000))

# Use proper hostname for Docker networking
PREFER_IP_ADDRESS = os.getenv('EUREKA_INSTANCE_PREFER_IP_ADDRESS', 'false').lower() == 'true'
SERVICE_HOSTNAME = get_container_hostname()
CONTAINER_IP = get_container_ip()

print(f"Service Name: {SERVICE_NAME}")
print(f"Service Hostname: {SERVICE_HOSTNAME}")
print(f"Container IP: {CONTAINER_IP}")
print(f"Prefer IP Address: {PREFER_IP_ADDRESS}")

# Configure URLs based on preference
if PREFER_IP_ADDRESS and CONTAINER_IP:
    registration_host = CONTAINER_IP
else:
    registration_host = SERVICE_HOSTNAME

HEALTH_CHECK_URL = f"http://{registration_host}:{SERVICE_PORT}/health"
HOME_PAGE_URL = f"http://{registration_host}:{SERVICE_PORT}/"
STATUS_PAGE_URL = f"http://{registration_host}:{SERVICE_PORT}/actuator/info"

def register_with_eureka():
    """Register the Flask AI service with Eureka Discovery Server"""
    try:
        eureka_client.init(
            eureka_server=EUREKA_SERVER_URL,
            app_name=SERVICE_NAME,
            instance_port=SERVICE_PORT,
            instance_host=registration_host,
            health_check_url=HEALTH_CHECK_URL,
            home_page_url=HOME_PAGE_URL,
            status_page_url=STATUS_PAGE_URL,
            prefer_ip_address=PREFER_IP_ADDRESS,
            # Optional metadata for better service identification
            metadata={
                "description": "AI service for code generation, evaluation, and assistance",
                "version": "1.0.0",
                "framework": "Flask",
                "language": "Python",
                "zone": "default"
            }
        )
        print(f"Successfully registered {SERVICE_NAME} with Eureka at {EUREKA_SERVER_URL}")
        print(f"Registration host: {registration_host}")
        print(f"Health check URL: {HEALTH_CHECK_URL}")
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
