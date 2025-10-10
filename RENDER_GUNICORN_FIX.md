# 🚨 Render "gunicorn: command not found" - Solutions

## 🔧 **Multiple Fix Options:**

### ✅ **Solution 1: Use Python Module (Recommended)**
Update your Render service with:
```
Start Command: python -m gunicorn --bind 0.0.0.0:$PORT timetable_scheduler.app:app
```

### ✅ **Solution 2: Direct Python Start**
If gunicorn still fails, use Flask directly:
```
Start Command: python timetable_scheduler/app.py
```

### ✅ **Solution 3: Alternative WSGI Server**
Replace gunicorn with waitress (add to requirements.txt):
```
Start Command: waitress-serve --host=0.0.0.0 --port=$PORT timetable_scheduler.app:app
```

### ✅ **Solution 4: Manual Render Setup**
Instead of using render.yaml, create manually:

1. **Go to Render Dashboard** → New Web Service
2. **Connect GitHub** repository
3. **Settings:**
   - Name: `timetable-scheduler`
   - Environment: `Python 3`
   - Build Command: `pip install -r requirements.txt`
   - Start Command: `python -m gunicorn --bind 0.0.0.0:$PORT timetable_scheduler.app:app`

## 🔍 **Why This Happens:**
- Gunicorn might not be in PATH
- Build process didn't install gunicorn properly
- Render using Procfile instead of render.yaml

## 🚀 **Quick Fix Steps:**

### Step 1: Update requirements.txt
Ensure gunicorn is explicitly listed:
```
Flask==3.0.0
SQLAlchemy==2.0.35
Flask-SQLAlchemy==3.1.1
Werkzeug==3.0.1
Jinja2==3.1.2
python-dotenv==1.0.0
psycopg2-binary==2.9.9
gunicorn==21.2.0
waitress==3.0.0
```

### Step 2: Try Alternative Start Commands
1. First try: `python -m gunicorn --bind 0.0.0.0:$PORT timetable_scheduler.app:app`
2. If fails: `python timetable_scheduler/app.py`
3. Last resort: `waitress-serve --host=0.0.0.0 --port=$PORT timetable_scheduler.app:app`

### Step 3: Check Render Logs
Look for build errors that might prevent gunicorn installation.

This should resolve the "command not found" error!