#!/bin/bash

# Install Python dependencies
pip install -r requirements.txt

# Initialize the database (will create tables if they don't exist)
echo "Initializing database..."
python -c "
from timetable_scheduler.app import app, init_db
with app.app_context():
    init_db()
    print('Database initialized successfully')
"

echo "Build completed successfully"