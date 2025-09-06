#!/usr/bin/env python3
"""
Setup script for MCP Weather Server
"""

import subprocess
import sys
import os

def install_dependencies():
    """Install Python dependencies"""
    print("Installing Python dependencies...")
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
        print("✅ Python dependencies installed successfully!")
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to install dependencies: {e}")
        return False
    return True

def setup_environment():
    """Setup environment file"""
    if not os.path.exists(".env"):
        print("Creating .env file from template...")
        try:
            if os.path.exists(".env.example"):
                with open(".env.example", "r") as source:
                    content = source.read()
                with open(".env", "w") as target:
                    target.write(content)
                print("✅ .env file created! Please edit it with your API keys.")
            else:
                # Create a basic .env file if template doesn't exist
                with open(".env", "w") as target:
                    target.write("# Add your API keys here\n")
                    target.write("WEATHER_API_KEY=\n")
                    target.write("OPENAI_API_KEY=\n")
                print("✅ Basic .env file created! Please add your API keys.")
        except Exception as e:
            print(f"❌ Failed to create .env file: {e}")
            return False
    else:
        print("✅ .env file already exists")
    return True

def main():
    print("🚀 Setting up MCP Weather Server...")
    
    if not install_dependencies():
        return 1
    
    if not setup_environment():
        return 1
    
    print("\n🎉 Setup complete!")
    print("\nNext steps:")
    print("1. Edit .env file with your API keys (optional)")
    print("2. Run: python main.py")
    print("3. Server will be available at http://localhost:8000")
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
