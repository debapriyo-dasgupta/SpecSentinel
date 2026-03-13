"""
SpecSentinel - Unified Application Launcher
Starts both backend API and frontend Flask server
"""

import subprocess
import sys
import time
import os
from pathlib import Path

def start_backend():
    """Start the FastAPI backend server"""
    backend_path = Path(__file__).parent / "src" / "api" / "app.py"
    print("🚀 Starting Backend API on http://localhost:8000...")
    return subprocess.Popen(
        [sys.executable, str(backend_path)],
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        bufsize=1
    )

def start_frontend():
    """Start the Flask frontend server"""
    frontend_path = Path(__file__).parent / "frontend" / "app.py"
    print("🌐 Starting Frontend on http://localhost:5000...")
    return subprocess.Popen(
        [sys.executable, str(frontend_path)],
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        bufsize=1
    )

def main():
    """Main entry point"""
    print("=" * 60)
    print("SpecSentinel - API Health Analyzer")
    print("=" * 60)
    print()
    
    backend_process = None
    frontend_process = None
    
    try:
        # Start backend
        backend_process = start_backend()
        time.sleep(2)  # Give backend time to start
        
        # Start frontend
        frontend_process = start_frontend()
        time.sleep(2)  # Give frontend time to start
        
        print()
        print("=" * 60)
        print("✅ Both servers are running!")
        print("=" * 60)
        print()
        print("📍 Backend API:  http://localhost:8000")
        print("📍 Frontend UI:  http://localhost:5000")
        print()
        print("🌐 Open your browser and navigate to: http://localhost:5000")
        print()
        print("Press Ctrl+C to stop both servers")
        print("=" * 60)
        print()
        
        # Stream output from both processes
        while True:
            # Check if processes are still running
            if backend_process.poll() is not None:
                print("❌ Backend process stopped unexpectedly")
                break
            if frontend_process.poll() is not None:
                print("❌ Frontend process stopped unexpectedly")
                break
            
            # Read and print output
            if backend_process.stdout:
                line = backend_process.stdout.readline()
                if line:
                    print(f"[Backend] {line.rstrip()}")
            
            if frontend_process.stdout:
                line = frontend_process.stdout.readline()
                if line:
                    print(f"[Frontend] {line.rstrip()}")
            
            time.sleep(0.1)
            
    except KeyboardInterrupt:
        print("\n\n🛑 Shutting down servers...")
    except Exception as e:
        print(f"\n❌ Error: {e}")
    finally:
        # Cleanup
        if backend_process:
            backend_process.terminate()
            backend_process.wait(timeout=5)
            print("✅ Backend stopped")
        
        if frontend_process:
            frontend_process.terminate()
            frontend_process.wait(timeout=5)
            print("✅ Frontend stopped")
        
        print("\n👋 SpecSentinel stopped successfully")

if __name__ == "__main__":
    main()

# Made with Bob
