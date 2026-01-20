#!/usr/bin/env python3
"""
Quick setup script for the audio fingerprinting system.
"""

import os
import sys
import subprocess


def print_header(text):
    """Print formatted header."""
    print("\n" + "=" * 60)
    print(f"  {text}")
    print("=" * 60)


def check_python_version():
    """Check if Python version is 3.10+."""
    print_header("Checking Python Version")
    version = sys.version_info
    print(f"Python version: {version.major}.{version.minor}.{version.micro}")
    
    if version.major < 3 or (version.major == 3 and version.minor < 10):
        print("❌ Python 3.10+ required")
        return False
    
    print("✓ Python version OK")
    return True


def install_dependencies():
    """Install Python dependencies."""
    print_header("Installing Dependencies")
    
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
        print("✓ Dependencies installed")
        return True
    except subprocess.CalledProcessError:
        print("❌ Failed to install dependencies")
        return False


def create_env_file():
    """Create .env file from template."""
    print_header("Setting Up Environment")
    
    if os.path.exists(".env"):
        print("⚠ .env file already exists, skipping")
        return True
    
    if os.path.exists(".env.example"):
        try:
            with open(".env.example", "r") as src:
                content = src.read()
            
            with open(".env", "w") as dst:
                dst.write(content)
            
            print("✓ Created .env file from template")
            print("⚠ Please edit .env with your database credentials")
            return True
        except Exception as e:
            print(f"❌ Failed to create .env: {e}")
            return False
    else:
        print("❌ .env.example not found")
        return False


def check_postgresql():
    """Check if PostgreSQL is accessible."""
    print_header("Checking PostgreSQL")
    
    try:
        import psycopg2
        print("✓ psycopg2 installed")
        
        # Try to connect (will use .env values)
        print("Note: Database connection will be tested when you run the app")
        return True
    except ImportError:
        print("❌ psycopg2 not installed")
        return False


def main():
    """Main setup function."""
    print_header("Vesper Audio Fingerprinting System - Setup")
    
    steps = [
        ("Python Version", check_python_version),
        ("Dependencies", install_dependencies),
        ("Environment File", create_env_file),
        ("PostgreSQL Check", check_postgresql),
    ]
    
    results = []
    for name, func in steps:
        try:
            result = func()
            results.append((name, result))
        except Exception as e:
            print(f"❌ Error in {name}: {e}")
            results.append((name, False))
    
    # Summary
    print_header("Setup Summary")
    
    all_passed = True
    for name, result in results:
        status = "✓" if result else "❌"
        print(f"{status} {name}")
        if not result:
            all_passed = False
    
    if all_passed:
        print_header("Setup Complete!")
        print("\nNext steps:")
        print("1. Configure PostgreSQL:")
        print("   createdb audio_fingerprinting")
        print("\n2. Update .env with your database credentials")
        print("\n3. Initialize database schema:")
        print("   psql -U postgres -d audio_fingerprinting -f sql/schema.sql")
        print("\n4. Add audio files to dataset/ directory")
        print("\n5. Populate database:")
        print("   python -m app.services.populate_db")
        print("\n6. Start the API server:")
        print("   uvicorn app.main:app --reload")
        print("\n7. Visit http://localhost:8000/docs for API documentation")
    else:
        print_header("Setup Incomplete")
        print("\nPlease fix the errors above and run setup again.")
    
    print("=" * 60)


if __name__ == "__main__":
    main()
