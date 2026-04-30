import subprocess
import time
import sys
import os

def main():
    print("Starting Main Application runner...")
    
    # Make sure we're in the right directory
    root_dir = os.path.dirname(os.path.abspath(__file__))
    os.chdir(root_dir)

    print("1. Starting FastAPI Backend on port 8000...")
    # Use Popen to run the process in the background
    api_process = subprocess.Popen(
        [sys.executable, "-m", "uvicorn", "api.main:app", "--host", "localhost", "--port", "8000"],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
    )
    
    # Give the API a moment to start
    time.sleep(3)
    
    if api_process.poll() is not None:
        print("Failed to start the API backend.")
        sys.exit(1)

    print("2. Starting Streamlit Frontend on port 8501...")
    frontend_process = subprocess.Popen(
        [sys.executable, "-m", "streamlit", "run", "frontend/app.py"],
        stdout=sys.stdout,
        stderr=sys.stderr
    )

    try:
        # Keep the main thread alive, waiting for frontend to finish (e.g. user hits Ctrl+C)
        frontend_process.wait()
    except KeyboardInterrupt:
        print("\nShutting down services...")
        api_process.terminate()
        frontend_process.terminate()
        api_process.wait()
        frontend_process.wait()
        print("Shutdown complete.")

if __name__ == "__main__":
    main()
