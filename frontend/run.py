#!/usr/bin/env python3
"""
Simple script to run the Streamlit frontend
"""
import subprocess
import sys
import os

def main():
    frontend_dir = os.path.dirname(os.path.abspath(__file__))
    os.chdir(frontend_dir)
    
    print("🚀 Starting Streamlit frontend...")
    print("📍 Frontend will be available at: http://localhost:8501")
    print("🔧 Make sure your FastAPI backend is running on http://localhost:8000")
    print("-" * 60)
    
    try:
        subprocess.run([
            sys.executable, "-m", "streamlit", "run", "app.py",
            "--server.port", "8501",
            "--server.address", "0.0.0.0",
            "--theme.base", "dark"
        ])
    except KeyboardInterrupt:
        print("\n👋 Shutting down frontend...")
    except Exception as e:
        print(f"❌ Error running frontend: {e}")

if __name__ == "__main__":
    main()