import os
import sys
import subprocess

def run_build():
    print("Preparing GymOS Desktop for packaging...")
    
    # Ensure pyinstaller is installed
    try:
        import PyInstaller
    except ImportError:
        print("PyInstaller is not installed. Please run: pip install pyinstaller")
        sys.exit(1)
        
    sep = ";" if sys.platform.startswith("win") else ":"
    
    cmd = [
        "pyinstaller",
        "--name=GymOS",
        "--noconfirm",
        "--windowed",
        "--clean",
        f"--add-data=data/program.json{sep}data",
        "main.py"
    ]
    
    print(f"Running command: {' '.join(cmd)}")
    result = subprocess.run(cmd)
    if result.returncode == 0:
        print("Build completed successfully! Check the 'dist' directory.")
    else:
        print(f"Build failed with exit code: {result.returncode}")
        sys.exit(result.returncode)

if __name__ == "__main__":
    run_build()
