#!/usr/bin/env python3
"""
AI Service Configuration Checker
Verifies the configuration and connectivity of the AI microservice
"""

import sys
import os
import requests
import json
import time
from datetime import datetime

# Add the src directory to Python path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

def check_environment_variables():
    """Check if required environment variables are set"""
    print("🔧 Checking Environment Variables...")
    
    required_vars = [
        'SERVICE_NAME',
        'HOST', 
        'PORT',
        'DISCOVERY_SERVICE_URL'
    ]
    
    optional_vars = [
        'CONFIG_SERVICE_URL',
        'LANGSMITH_API_KEY',
        'LANGSMITH_PROJECT'
    ]
    
    issues = []
    
    for var in required_vars:
        value = os.getenv(var)
        if value:
            print(f"  ✅ {var}: {value}")
        else:
            print(f"  ❌ {var}: Not set")
            issues.append(var)
    
    print("\n  Optional variables:")
    for var in optional_vars:
        value = os.getenv(var)
        if value:
            print(f"  ✅ {var}: {value}")
        else:
            print(f"  ⚠️  {var}: Not set (optional)")
    
    return len(issues) == 0

def check_dependencies():
    """Check if required Python packages are installed"""
    print("\n📦 Checking Python Dependencies...")
    
    required_packages = [
        'flask',
        'py_eureka_client',
        'requests',
        'python-dotenv',
        'langchain_core'
    ]
    
    missing_packages = []
    
    for package in required_packages:
        try:
            __import__(package.replace('-', '_'))
            print(f"  ✅ {package}: Installed")
        except ImportError:
            print(f"  ❌ {package}: Missing")
            missing_packages.append(package)
    
    if missing_packages:
        print(f"\n  Install missing packages with:")
        print(f"  pip install {' '.join(missing_packages)}")
    
    return len(missing_packages) == 0

def check_flask_app():
    """Check if Flask app can be imported and configured"""
    print("\n🐍 Checking Flask Application...")
    
    try:
        # Set environment variables for testing
        os.environ.setdefault('SERVICE_NAME', 'ai-service')
        os.environ.setdefault('HOST', 'localhost')
        os.environ.setdefault('PORT', '8000')
        os.environ.setdefault('DISCOVERY_SERVICE_URL', 'http://localhost:8080/eureka')
        
        from main import app
        print("  ✅ Flask app imported successfully")
        
        # Check routes
        routes = []
        for rule in app.url_map.iter_rules():
            routes.append(f"{rule.methods} {rule.rule}")
        
        expected_routes = ['/health', '/actuator/info', '/generate', '/evaluate', '/aiassistant']
        for route in expected_routes:
            if any(route in r for r in routes):
                print(f"  ✅ Route {route}: Configured")
            else:
                print(f"  ❌ Route {route}: Missing")
        
        return True
    except Exception as e:
        print(f"  ❌ Flask app import failed: {e}")
        return False

def check_eureka_connectivity():
    """Check connectivity to Eureka server"""
    print("\n🔍 Checking Eureka Connectivity...")
    
    eureka_url = os.getenv('DISCOVERY_SERVICE_URL', 'http://localhost:8080/eureka')
    
    try:
        # Check if Eureka server is reachable
        response = requests.get(f"{eureka_url.replace('/eureka', '')}/actuator/health", timeout=5)
        if response.status_code == 200:
            print(f"  ✅ Eureka server reachable at {eureka_url}")
        else:
            print(f"  ⚠️  Eureka server responded with status {response.status_code}")
    except requests.exceptions.RequestException as e:
        print(f"  ❌ Cannot reach Eureka server: {e}")
        return False
    
    # Check if AI service is registered
    try:
        response = requests.get(f"{eureka_url}/apps/AI-SERVICE", timeout=5)
        if response.status_code == 200:
            print("  ✅ AI service is registered with Eureka")
        else:
            print("  ⚠️  AI service not yet registered (may need to start the service)")
    except requests.exceptions.RequestException as e:
        print(f"  ⚠️  Cannot check service registration: {e}")
    
    return True

def check_gateway_routing():
    """Check if gateway is configured for AI service"""
    print("\n🚪 Checking Gateway Configuration...")
    
    gateway_url = os.getenv('GATEWAY_SERVICE_URL', 'http://localhost:8082')
    
    try:
        # Check if gateway is reachable
        response = requests.get(f"{gateway_url}/actuator/health", timeout=5)
        if response.status_code == 200:
            print(f"  ✅ Gateway reachable at {gateway_url}")
        else:
            print(f"  ⚠️  Gateway responded with status {response.status_code}")
    except requests.exceptions.RequestException as e:
        print(f"  ❌ Cannot reach gateway: {e}")
        return False
    
    # Test routing (if AI service is running)
    try:
        response = requests.get(f"{gateway_url}/api/v1/ai/health", timeout=5)
        if response.status_code == 200:
            print("  ✅ Gateway routing to AI service is working")
        else:
            print("  ⚠️  Gateway routing not working (AI service may not be running)")
    except requests.exceptions.RequestException as e:
        print(f"  ⚠️  Cannot test gateway routing: {e}")
    
    return True

def check_ai_service_health():
    """Check if AI service is running and healthy"""
    print("\n🤖 Checking AI Service Health...")
    
    service_url = f"http://{os.getenv('HOST', 'localhost')}:{os.getenv('PORT', '8000')}"
    
    try:
        response = requests.get(f"{service_url}/health", timeout=5)
        if response.status_code == 200:
            health_data = response.json()
            print(f"  ✅ AI service is healthy: {health_data.get('status', 'Unknown')}")
            return True
        else:
            print(f"  ❌ AI service health check failed: {response.status_code}")
    except requests.exceptions.RequestException as e:
        print(f"  ⚠️  AI service not running or not reachable: {e}")
    
    return False

def run_configuration_test():
    """Test AI service endpoints"""
    print("\n🧪 Testing AI Service Endpoints...")
    
    service_url = f"http://{os.getenv('HOST', 'localhost')}:{os.getenv('PORT', '8000')}"
    
    # Test data
    test_requests = [
        {
            "endpoint": "/health",
            "method": "GET",
            "data": None,
            "description": "Health check"
        },
        {
            "endpoint": "/actuator/info",
            "method": "GET", 
            "data": None,
            "description": "Service info"
        },
        {
            "endpoint": "/generate",
            "method": "POST",
            "data": {
                "context": "Test context",
                "number_of_questions": 1,
                "user_query": "test query",
                "task": "code",
                "difficulty": "easy"
            },
            "description": "Generate exercise"
        }
    ]
    
    results = []
    
    for test in test_requests:
        try:
            if test["method"] == "GET":
                response = requests.get(f"{service_url}{test['endpoint']}", timeout=10)
            else:
                response = requests.post(
                    f"{service_url}{test['endpoint']}", 
                    json=test["data"],
                    headers={"Content-Type": "application/json"},
                    timeout=10
                )
            
            if response.status_code == 200:
                print(f"  ✅ {test['description']}: Success")
                results.append(True)
            else:
                print(f"  ❌ {test['description']}: Failed ({response.status_code})")
                results.append(False)
                
        except requests.exceptions.RequestException as e:
            print(f"  ❌ {test['description']}: Error - {e}")
            results.append(False)
    
    return all(results)

def main():
    """Main configuration checker"""
    print("🔍 AI Service Configuration Checker")
    print("=" * 50)
    print(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("")
    
    # Load environment variables from .env file
    try:
        from dotenv import load_dotenv
        load_dotenv()
        print("✅ Loaded environment variables from .env file")
    except ImportError:
        print("⚠️  python-dotenv not installed, using system environment variables")
    except Exception as e:
        print(f"⚠️  Error loading .env file: {e}")
    
    checks = [
        ("Environment Variables", check_environment_variables),
        ("Python Dependencies", check_dependencies), 
        ("Flask Application", check_flask_app),
        ("Eureka Connectivity", check_eureka_connectivity),
        ("Gateway Configuration", check_gateway_routing),
        ("AI Service Health", check_ai_service_health),
        ("Endpoint Testing", run_configuration_test)
    ]
    
    results = []
    
    for check_name, check_func in checks:
        try:
            result = check_func()
            results.append(result)
        except Exception as e:
            print(f"  ❌ Error during {check_name}: {e}")
            results.append(False)
    
    print("\n" + "=" * 50)
    print("📊 Summary:")
    print(f"Passed: {sum(results)}/{len(results)} checks")
    
    if all(results):
        print("🎉 All checks passed! AI service is properly configured.")
        return 0
    else:
        print("⚠️  Some checks failed. Review the output above for details.")
        print("\nCommon solutions:")
        print("1. Start required services: docker-compose up discovery-service config-service")
        print("2. Install missing dependencies: pip install -r requirements.txt")
        print("3. Check environment variables in .env file")
        print("4. Start the AI service: python -m src.main")
        return 1

if __name__ == "__main__":
    sys.exit(main())
