#!/usr/bin/env python3
"""
Database initialization for Render deployment
Run this if database tables are not created automatically
"""
import os
import sys

# Add the current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def initialize_database():
    """Initialize database tables and create default users"""
    try:
        print("Starting database initialization...")
        
        # Import Flask app
        from timetable_scheduler.app import app, db, init_db
        
        # Initialize database within app context
        with app.app_context():
            print("Creating database tables...")
            db.create_all()
            
            print("Ensuring default users exist...")
            from timetable_scheduler.app import ensure_default_users
            ensure_default_users()
            
            print("Database initialization completed successfully!")
            
    except Exception as e:
        print(f"Database initialization failed: {e}")
        print("This might be normal on first deployment - tables will be created when app starts")

if __name__ == "__main__":
    initialize_database()