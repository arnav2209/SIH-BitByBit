#!/usr/bin/env python3
"""
Pre-deployment test script
Run this to verify your setup before deploying to Render
"""

import os
import sys
import subprocess
import importlib.util

def check_file_exists(filepath, description):
    """Check if a required file exists"""
    if os.path.exists(filepath):
        print(f"✅ {description}: {filepath}")
        return True
    else:
        print(f"❌ {description}: {filepath} - NOT FOUND")
        return False

def check_requirements():
    """Check if all required packages can be installed"""
    print("\n📦 Checking Python dependencies...")
    try:
        with open('requirements.txt', 'r') as f:
            requirements = f.read().strip().split('\n')
        
        print(f"✅ Found {len(requirements)} requirements")
        
        # Check if critical packages are listed
        critical_packages = ['flask', 'sqlalchemy', 'psycopg2-binary', 'gunicorn']
        for pkg in critical_packages:
            found = any(pkg.lower() in req.lower() for req in requirements)
            if found:
                print(f"✅ Critical package found: {pkg}")
            else:
                print(f"❌ Critical package missing: {pkg}")
                return False
        return True
        
    except Exception as e:
        print(f"❌ Error reading requirements.txt: {e}")
        return False

def check_app_structure():
    """Check if the Flask app structure is correct"""
    print("\n🏗️ Checking application structure...")
    
    # Check if the main app file exists
    app_path = os.path.join('timetable_scheduler', 'app.py')
    if not check_file_exists(app_path, "Main application file"):
        return False
    
    # Check for templates directory
    templates_path = os.path.join('timetable_scheduler', 'templates')
    if not os.path.isdir(templates_path):
        print(f"❌ Templates directory not found: {templates_path}")
        return False
    else:
        print(f"✅ Templates directory: {templates_path}")
    
    # Check for static directory
    static_path = os.path.join('timetable_scheduler', 'static')
    if not os.path.isdir(static_path):
        print(f"❌ Static directory not found: {static_path}")
        return False
    else:
        print(f"✅ Static directory: {static_path}")
    
    return True

def check_configuration_files():
    """Check if all deployment configuration files exist"""
    print("\n⚙️ Checking deployment configuration...")
    
    files = [
        ('render.yaml', 'Render service configuration'),
        ('Procfile', 'Process file for web service'),
        ('build.sh', 'Build script'),
        ('runtime.txt', 'Python runtime specification'),
        ('.gitignore', 'Git ignore file'),
        ('DEPLOYMENT_GUIDE.md', 'Deployment guide')
    ]
    
    all_exist = True
    for filepath, description in files:
        if not check_file_exists(filepath, description):
            all_exist = False
    
    return all_exist

def main():
    """Run all pre-deployment checks"""
    print("🚀 Pre-Deployment Check for Render")
    print("=" * 50)
    
    checks = [
        check_requirements(),
        check_app_structure(),
        check_configuration_files()
    ]
    
    print("\n" + "=" * 50)
    
    if all(checks):
        print("🎉 ALL CHECKS PASSED!")
        print("\n✅ Your project is ready for Render deployment!")
        print("\nNext steps:")
        print("1. Push your code to GitHub")
        print("2. Go to https://render.com")
        print("3. Create a new Blueprint")
        print("4. Connect your repository")
        print("5. Deploy!")
    else:
        print("❌ SOME CHECKS FAILED!")
        print("\n🔧 Please fix the issues above before deploying.")
        sys.exit(1)

if __name__ == "__main__":
    main()