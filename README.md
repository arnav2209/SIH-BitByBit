# Co### 🎯 Features

### Core Functionality
- **Automated Timetable Generation**: Intelligent scheduling algorithm that considers multiple constraints
- **Multi-Entity Management**: Manage classrooms, faculty, subjects, and student batches
- **Dual Access Levels**: Separate portals for administrators and students
- **Student Timetable Viewing**: Students can view their class schedules with detailed information
- **Conflict Resolution**: Automatic detection and prevention of scheduling conflicts
- **Multiple Optimization Options**: Generate different timetable variants to choose from
- **Review & Approval Workflow**: Built-in approval system for competent authoritiesmetable Scheduler

A modern, web-based timetable scheduling system designed for higher education institutions. Built with Python Flask, SQLite, and Tailwind CSS for efficient academic scheduling.

## 🎯 Features

### Core Functionality
- **Automated Timetable Generation**: Intelligent scheduling algorithm that considers multiple constraints
- **Multi-Entity Management**: Manage classrooms, faculty, subjects, and student batches
- **Conflict Resolution**: Automatic detection and prevention of scheduling conflicts
- **Multiple Optimization Options**: Generate different timetable variants to choose from
- **Review & Approval Workflow**: Built-in approval system for competent authorities

### Smart Scheduling
- **Resource Optimization**: Maximizes classroom and faculty utilization
- **Workload Balancing**: Distributes teaching load evenly across faculty
- **Flexible Time Slots**: Customizable working days and time periods
- **Special Constraints**: Handles fixed slots, lunch breaks, and faculty availability
- **Multi-Department Support**: Simultaneous scheduling for multiple departments

### User Experience
- **Modern UI**: Clean, college-themed interface with Tailwind CSS
- **Role-Based Access**: Different interfaces for administrators and students
- **Student Portal**: Dedicated dashboard for students to view their timetables
- **Responsive Design**: Works seamlessly on desktop, tablet, and mobile devices
- **Export Capabilities**: Print and export timetables in various formats
- **Real-time Validation**: Instant feedback on data entry and conflicts

## 🚀 Quick Start

### Prerequisites
- Python 3.7 or higher
- pip (Python package manager)
- Modern web browser

### Installation

1. **Clone/Download the project**
   ```bash
   cd "c:\Users\arnav\Desktop\NEW simple"
   ```

2. **Create a virtual environment** (Recommended)
   ```bash
   python -m venv timetable_env
   # Activate it:
   # Windows:
   timetable_env\Scripts\activate
   # macOS/Linux:
   source timetable_env/bin/activate
   ```

3. **Install dependencies**
   ```bash
   python -m pip install -r requirements.txt
   ```

4. **Set up environment variables** (Optional)
   ```bash
   copy .env.example .env
   # Edit .env file with your settings
   ```

5. **Run the application**
   ```bash
   cd timetable_scheduler
   python app.py
   ```

6. **Access the application**
   - Open your browser and go to: `http://localhost:5000`
   - Login with default credentials:
     - **Administrator**: `admin` / `admin123`
     - **Student**: `student` / `student123`

## 📁 Project Structure

```
timetable_scheduler/
├── app.py                 # Main Flask application
├── requirements.txt       # Python dependencies
├── .env.example          # Environment configuration template
├── timetable_scheduler/
│   ├── static/
│   │   ├── css/
│   │   │   └── custom.css    # Custom styles
│   │   └── js/
│   │       └── main.js       # JavaScript functionality
│   └── templates/
│       ├── base.html         # Base template
│       ├── login.html        # Login page
│       ├── dashboard.html    # Main dashboard
│       ├── setup.html        # Setup wizard
│       ├── manage.html       # Entity management
│       ├── generate_timetable.html  # Timetable generation
│       └── view_timetable.html      # Timetable display
└── timetable.db          # SQLite database (created automatically)
```

## 🛠️ Usage Guide

### 1. Initial Setup
1. **Login** with admin credentials
2. **Navigate to Setup** to configure basic data
3. **Add Classrooms** - Define rooms with capacities and types
4. **Add Faculty** - Create faculty profiles with workload limits
5. **Add Subjects** - Define subjects and assign to faculty
6. **Create Batches** - Organize students by year, semester, and department

### 2. Generate Timetables
1. **Go to Generate Timetable** page
2. **Select a student batch**
3. **Configure generation options**:
   - Maximum classes per day
   - Working days
   - Optimization preferences
4. **Click Generate** to create optimized schedules
5. **Review and approve** the generated timetable

### 3. Management Features (Admin)
- **View/Edit** all entities through the management interface
- **Student Management**: Create student accounts and assign to batches
- **Export timetables** to CSV or print format
- **Track statistics** on the dashboard
- **Approve or modify** generated schedules

### 4. Student Features
- **Personal Dashboard**: View your assigned timetable
- **Class Details**: See faculty, classroom, and subject type information
- **Export Options**: Print or download your schedule
- **Mobile Friendly**: Access your timetable from any device

## ⚙️ Configuration

### Key Parameters
- **Classrooms**: Room capacity, type (regular/lab/auditorium)
- **Faculty**: Maximum teaching hours per day, average leaves per month
- **Subjects**: Weekly hours, type (theory/practical/tutorial)
- **Batches**: Student strength, academic year and semester
- **Time Slots**: Customizable working hours and days

### Advanced Options
- Avoid consecutive practical sessions
- Balance daily class load
- Reserve lunch break periods
- Optimize classroom utilization
- Multi-shift scheduling support

## 🔧 Technical Details

### Backend
- **Framework**: Flask 3.0
- **Database**: SQLite with SQLAlchemy ORM
- **Authentication**: Session-based with password hashing
- **API**: RESTful endpoints for all operations

### Frontend
- **CSS Framework**: Tailwind CSS 3.0
- **Icons**: Font Awesome 6.0
- **JavaScript**: Vanilla JS with modern ES6+ features
- **Responsive**: Mobile-first design approach

### Database Schema
- **Users**: Authentication and role management
- **Classrooms**: Room information and availability
- **Faculty**: Staff details and constraints
- **Subjects**: Course information and assignments
- **Batches**: Student group organization
- **Timetables**: Generated schedule entries

## 🔒 Security Features

- **Password Hashing**: Secure password storage with Werkzeug
- **Session Management**: Server-side session handling
- **Input Validation**: Form validation and sanitization
- **CSRF Protection**: Built-in Flask security features
- **SQL Injection Prevention**: SQLAlchemy ORM protection

## 📱 Browser Support

- Chrome 70+
- Firefox 65+
- Safari 12+
- Edge 79+
- Mobile browsers (iOS Safari, Chrome Mobile)

## 🐛 Troubleshooting

### Common Issues

1. **Port already in use**
   ```bash
   # Run on different port
   python app.py --port 5001
   ```

2. **Database errors**
   ```bash
   # Delete database and restart
   del timetable.db
   python app.py
   ```

3. **Module not found**
   ```bash
   # Ensure virtual environment is activated
   python -m pip install -r requirements.txt
   ```

4. **Permission errors**
   ```bash
   # Run as administrator or check file permissions
   ```

### Getting Help
- Check the console output for error messages
- Ensure all prerequisites are installed
- Verify Python version compatibility
- Check firewall settings for port 5000

## 🚀 Deployment

### Ready for Render Deployment! 🎉

This project is now fully configured for deployment on Render with:
- **PostgreSQL** database support
- **Automatic** environment configuration
- **Production-ready** setup with Gunicorn
- **One-click** deployment via Blueprint

#### Quick Deploy to Render:
1. Push your code to GitHub
2. Go to [Render](https://render.com) and create a new Blueprint
3. Connect your repository
4. Deploy automatically with the included `render.yaml`

#### What's Included for Deployment:
- `render.yaml` - Complete Render service configuration
- `Procfile` - Process configuration for web service
- `build.sh` - Database initialization script
- `requirements.txt` - Updated with PostgreSQL support
- `runtime.txt` - Python version specification
- `.gitignore` - Proper file exclusions
- `DEPLOYMENT_GUIDE.md` - Detailed deployment instructions

#### Environment Features:
- **Automatic PostgreSQL** database creation and connection
- **Auto-generated secrets** for security
- **Production optimizations** with Gunicorn
- **Health checks** and monitoring ready
- **Free tier compatible** for testing

### Local Development
```bash
# Clone and set up locally
python -m venv timetable_env
timetable_env\Scripts\activate  # Windows
pip install -r requirements.txt
cd timetable_scheduler
python app.py
```

### Production Features
- **PostgreSQL** database with automatic backups
- **HTTPS** enabled by default on Render
- **Environment-based** configuration
- **Scalable** architecture ready for growth
- **Monitoring** and logging built-in

## 📄 License

This project is created for educational and institutional use. Feel free to modify and adapt according to your college's specific requirements.

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## 📞 Support

For technical support or feature requests, please contact the development team or create an issue in the project repository.

---

**Built with ❤️ for Higher Education Institutions**