"""
SpecSentinel - Unified Application Launcher
Starts both backend API and frontend Flask server
"""

import subprocess
import sys
import time
import os
import threading
import queue
from pathlib import Path

# Constants
STARTUP_DELAY = 2  # seconds to wait for server startup
POLL_INTERVAL = 0.1  # seconds between process checks
SHUTDOWN_TIMEOUT = 5  # seconds to wait for graceful shutdown

def stream_output(process, prefix, output_queue):
    """Read process output in a separate thread to prevent blocking"""
    try:
        for line in iter(process.stdout.readline, ''):
            if line:
                output_queue.put((prefix, line.rstrip()))
    except Exception as e:
        output_queue.put((prefix, f"Error reading output: {e}"))
    finally:
        output_queue.put((prefix, None))  # Signal end of stream

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
    output_queue = queue.Queue()
    backend_thread = None
    frontend_thread = None
    
    try:
        # Start backend
        backend_process = start_backend()
        
        # Check if backend started successfully
        time.sleep(0.5)
        if backend_process.poll() is not None:
            print("❌ Backend failed to start")
            return
        
        time.sleep(STARTUP_DELAY - 0.5)  # Complete startup delay
        
        # Start frontend
        frontend_process = start_frontend()
        
        # Check if frontend started successfully
        time.sleep(0.5)
        if frontend_process.poll() is not None:
            print("❌ Frontend failed to start")
            return
        
        time.sleep(STARTUP_DELAY - 0.5)  # Complete startup delay
        
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
        
        # Start output reader threads to prevent pipe blocking
        backend_thread = threading.Thread(
            target=stream_output,
            args=(backend_process, "Backend", output_queue),
            daemon=True
        )
        frontend_thread = threading.Thread(
            target=stream_output,
            args=(frontend_process, "Frontend", output_queue),
            daemon=True
        )
        backend_thread.start()
        frontend_thread.start()
        
        # Monitor processes and print output
        backend_alive = True
        frontend_alive = True
        
        while backend_alive or frontend_alive:
            # Check if processes are still running
            if backend_alive and backend_process.poll() is not None:
                print("❌ Backend process stopped unexpectedly")
                backend_alive = False
            if frontend_alive and frontend_process.poll() is not None:
                print("❌ Frontend process stopped unexpectedly")
                frontend_alive = False
            
            # Print queued output (non-blocking)
            try:
                while True:
                    prefix, line = output_queue.get_nowait()
                    if line is None:
                        # Thread signaled end of stream
                        if prefix == "Backend":
                            backend_alive = False
                        else:
                            frontend_alive = False
                    else:
                        print(f"[{prefix}] {line}")
            except queue.Empty:
                pass
            
            time.sleep(POLL_INTERVAL)
            
    except KeyboardInterrupt:
        print("\n\n🛑 Shutting down servers...")
    except Exception as e:
        print(f"\n❌ Error: {e}")
    finally:
        # Cleanup
        if backend_process:
            print("Stopping backend...")
            backend_process.terminate()
            try:
                backend_process.wait(timeout=SHUTDOWN_TIMEOUT)
                print("✅ Backend stopped")
            except subprocess.TimeoutExpired:
                print("⚠️  Backend didn't stop gracefully, forcing...")
                backend_process.kill()
                backend_process.wait()
                print("✅ Backend killed")
        
        if frontend_process:
            print("Stopping frontend...")
            frontend_process.terminate()
            try:
                frontend_process.wait(timeout=SHUTDOWN_TIMEOUT)
                print("✅ Frontend stopped")
            except subprocess.TimeoutExpired:
                print("⚠️  Frontend didn't stop gracefully, forcing...")
                frontend_process.kill()
                frontend_process.wait()
                print("✅ Frontend killed")
        
        print("\n👋 SpecSentinel stopped successfully")

if __name__ == "__main__":
    main()

# Made with Bob
