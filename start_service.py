#!/usr/bin/env python3
"""
AI Service Startup Script
Clean startup for the Python AI microservice
"""

import os
import sys
import subprocess
import time
from pathlib import Path

def setup_environment():
    """Set up the environment for the AI service"""
    print("🔧 Setting up environment...")
    
    # Add src directory to Python path
    src_path = Path(__file__).parent / "src"
    sys.path.insert(0, str(src_path))
    
    # Load environment variables
    try:
        from dotenv import load_dotenv
        load_dotenv()
        print("✅ Environment variables loaded")
    except ImportError:
        print("⚠️  python-dotenv not available, using system environment")
    
    # Set default environment variables
    defaults = {
        'SERVICE_NAME': 'ai-service',
        'HOST': '0.0.0.0',
        'PORT': '8000',
        'DISCOVERY_SERVICE_URL': 'http://localhost:8080/eureka',
        'FLASK_ENV': 'development'
    }
    
    for key, value in defaults.items():
        if not os.getenv(key):
            os.environ[key] = value
            print(f"  Set {key}={value}")

def check_dependencies():
    """Check if required dependencies are installed"""
    print("\n📦 Checking dependencies...")
    
    required = ['flask', 'py_eureka_client', 'requests', 'python_dotenv']
    missing = []
    
    for package in required:
        try:
            __import__(package.replace('-', '_'))
            print(f"  ✅ {package}")
        except ImportError:
            print(f"  ❌ {package} - missing")
            missing.append(package)
    
    if missing:
        print(f"\nInstall missing packages:")
        print(f"pip install {' '.join(missing)}")
        return False
    
    return True

def start_service():
    """Start the AI service"""
    print("\n🚀 Starting AI Service...")
    
    # Import and run the Flask app
    try:
        from src.main import app
        
        host = os.getenv('HOST', '0.0.0.0')
        port = int(os.getenv('PORT', 8000))
        debug = os.getenv('FLASK_ENV') == 'development'
        
        print(f"Starting AI service on {host}:{port}")
        print(f"Debug mode: {debug}")
        print(f"Service name: {os.getenv('SERVICE_NAME')}")
        print(f"Eureka server: {os.getenv('DISCOVERY_SERVICE_URL')}")
        
        app.run(host=host, port=port, debug=debug)
        
    except ImportError as e:
        print(f"❌ Cannot import Flask app: {e}")
        return False
    except Exception as e:
        print(f"❌ Error starting service: {e}")
        return False

def main():
    """Main startup function"""
    print("🤖 AI Service Startup")
    print("=" * 30)
    
    # Setup environment
    setup_environment()
    
    # Check dependencies
    if not check_dependencies():
        print("\n❌ Missing dependencies. Please install them first.")
        return 1
    
    # Start the service
    try:
        start_service()
        return 0
    except KeyboardInterrupt:
        print("\n👋 Service stopped by user")
        return 0
    except Exception as e:
        print(f"\n❌ Service failed: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(main())
