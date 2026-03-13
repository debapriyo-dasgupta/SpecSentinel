"""
SpecSentinel Unified Launcher
Runs both backend (FastAPI) and frontend (Flask) servers simultaneously
"""

import subprocess
import sys
import time
import os
from pathlib import Path
import threading

def run_backend():
    """Run the FastAPI backend server"""
    print("🚀 Starting Backend API Server (FastAPI on port 8000)...")
    backend_path = Path(__file__).parent / "src" / "api"
    
    # Change to backend directory and run
    os.chdir(backend_path)
    subprocess.run([
        sys.executable, "-m", "uvicorn",
        "app:app",
        "--host", "0.0.0.0",
        "--port", "8000",
        "--reload"
    ])

def run_frontend():
    """Run the Flask frontend server"""
    print("🌐 Starting Frontend Server (Flask on port 5000)...")
    
    # Wait a bit for backend to start
    time.sleep(3)
    
    frontend_path = Path(__file__).parent / "frontend"
    
    # Change to frontend directory and run
    os.chdir(frontend_path)
    subprocess.run([
        sys.executable, "app.py"
    ])

def main():
    """Main launcher function"""
    print("=" * 60)
    print("  SpecSentinel 🛡️ - Unified Launcher")
    print("  Agentic AI API Health, Compliance & Governance Bot")
    print("=" * 60)
    print()
    
    # Create threads for both servers
    backend_thread = threading.Thread(target=run_backend, daemon=True)
    frontend_thread = threading.Thread(target=run_frontend, daemon=True)
    
    try:
        # Start backend first
        backend_thread.start()
        
        # Give backend time to initialize
        print("\n⏳ Waiting for backend to initialize...")
        time.sleep(5)
        
        # Start frontend
        frontend_thread.start()
        
        print("\n" + "=" * 60)
        print("✅ Both servers are starting!")
        print("=" * 60)
        print()
        print("📍 Backend API:  http://localhost:8000")
        print("📍 Frontend UI:  http://localhost:5000")
        print()
        print("📖 API Docs:     http://localhost:8000/docs")
        print("📊 Health Check: http://localhost:8000/health")
        print()
        print("=" * 60)
        print("Press Ctrl+C to stop both servers")
        print("=" * 60)
        print()
        
        # Keep main thread alive
        backend_thread.join()
        frontend_thread.join()
        
    except KeyboardInterrupt:
        print("\n\n🛑 Shutting down servers...")
        print("✅ Servers stopped successfully")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()

# Made with Bob
