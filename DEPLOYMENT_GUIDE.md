# Render Deployment Guide

This guide will help you deploy the Timetable Scheduler application to Render.

## Prerequisites

1. A GitHub account
2. A Render account (sign up at https://render.com)
3. Your project code pushed to a GitHub repository

## Step-by-Step Deployment

### 1. Prepare Your Repository

Ensure your repository contains all the files created for Render deployment:
- `render.yaml` - Render service configuration
- `requirements.txt` - Python dependencies (updated with PostgreSQL support)
- `Procfile` - Process file for Render
- `build.sh` - Build script for initialization
- `.env.example` - Environment variables template

### 2. Connect GitHub to Render

1. Go to https://render.com and sign in
2. Click "New +" and select "Blueprint"
3. Connect your GitHub account if not already connected
4. Select your repository containing the timetable scheduler

### 3. Configure Environment Variables

Render will automatically create environment variables from the `render.yaml` file, but you may want to customize:

- `SECRET_KEY`: Auto-generated secure key (recommended to keep auto-generated)
- `FLASK_ENV`: Set to "production"
- `DATABASE_URL`: Automatically provided by the PostgreSQL database

### 4. Database Setup

The `render.yaml` file includes PostgreSQL database configuration:
- Database name: `timetable_db`
- User: `timetable_user`
- Plan: Free tier

### 5. Deploy

1. Click "Create New Blueprint"
2. Render will automatically:
   - Create the web service
   - Create the PostgreSQL database
   - Install dependencies
   - Initialize the database with tables
   - Start the application

### 6. Access Your Application

After deployment:
1. Render will provide a URL like: `https://your-app-name.onrender.com`
2. The application will initialize with default users:
   - **Admin**: username `admin`, password `admin123`
   - **Student**: username `student1`, password `password123`

## Alternative Manual Setup (if Blueprint doesn't work)

### 1. Create Web Service

1. In Render dashboard, click "New +" → "Web Service"
2. Connect your GitHub repository
3. Configure:
   - **Name**: `timetable-scheduler`
   - **Environment**: `Python 3`
   - **Build Command**: `./build.sh`
   - **Start Command**: `gunicorn --bind 0.0.0.0:$PORT timetable_scheduler.app:app`

### 2. Create Database

1. Click "New +" → "PostgreSQL"
2. Configure:
   - **Name**: `timetable-db`
   - **Database**: `timetable_db`
   - **User**: `timetable_user`

### 3. Environment Variables

Add these in your web service settings:
```
FLASK_ENV=production
SECRET_KEY=[auto-generate in Render]
DATABASE_URL=[link to your PostgreSQL database]
```

## Post-Deployment Setup

### 1. Initial Login
- Use admin credentials to log in
- Change default passwords immediately

### 2. Configure Your Institution
1. Go to Setup → Manage entities
2. Add your classrooms, faculty, subjects, and batches
3. Generate timetables as needed

### 3. Create Student Accounts
1. Use the admin panel to create student accounts
2. Assign students to appropriate batches

## Troubleshooting

### Common Issues

1. **Build Failures**
   - Check that `requirements.txt` includes all dependencies
   - Ensure `build.sh` has proper permissions
   - Check Render build logs for specific errors

2. **Database Connection Issues**
   - Verify `DATABASE_URL` environment variable is set
   - Check PostgreSQL database is running
   - Ensure database credentials are correct

3. **Application Not Starting**
   - Check the start command in `Procfile`
   - Verify Gunicorn is installed
   - Check application logs in Render dashboard

4. **Static Files Not Loading**
   - Ensure CSS and JS files are in the correct `static/` directory
   - Check file paths in templates

### Logs and Debugging

- View logs in Render dashboard under your service
- Enable debug mode temporarily if needed (not recommended for production)
- Check database connectivity with Render's database explorer

## Security Considerations

1. **Change Default Passwords**: Immediately change admin and student passwords
2. **Environment Variables**: Never commit sensitive data to Git
3. **Database Backups**: Set up regular backups through Render
4. **HTTPS**: Render provides HTTPS by default
5. **Secret Key**: Use Render's auto-generated secret key

## Performance Optimization

1. **Database Indexing**: Add indexes for frequently queried fields
2. **Caching**: Consider implementing Flask-Caching for better performance
3. **Static Files**: Use CDN for static assets if needed
4. **Database Pool**: Configure connection pooling for high traffic

## Monitoring

- Use Render's built-in monitoring
- Set up alerts for service downtime
- Monitor database performance and usage
- Track application logs for errors

## Scaling

- Start with free tier for testing
- Upgrade to paid plans for production use
- Consider horizontal scaling for high traffic
- Monitor resource usage and upgrade as needed

## Support

- Render Documentation: https://render.com/docs
- Flask Documentation: https://flask.palletsprojects.com/
- SQLAlchemy Documentation: https://docs.sqlalchemy.org/

## Backup and Recovery

1. **Database Backups**: Render provides automatic backups for PostgreSQL
2. **Code Backups**: Your code is backed up in GitHub
3. **Configuration Backups**: Document your environment variables
4. **Data Export**: Implement data export features in the application

---

Your timetable scheduler is now ready for production deployment on Render!