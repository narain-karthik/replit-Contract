# Contract Document Management System

A comprehensive web-based Contract Document Management System built with Flask, featuring user authentication, document tracking, and reporting capabilities.

## Features

- **User Authentication**: Secure login system with password hashing
- **Document Master Data**: SAP-style layout for managing document details with 15 field rows
- **User Management**: Create and manage user accounts with departments
- **Document Upload**: Upload files with autocomplete metadata fields
- **Document Download**: Search and download documents with tracking
- **Reporting**: Detailed reports with filters showing upload/download history

## Getting Started

### Prerequisites
- Python 3.11
- Flask 3.1.2
- SQLite3

### Installation

1. The application automatically installs required packages when you run it in Replit.

2. Start the Flask server:
```bash
python app.py
```

3. Access the application at `http://0.0.0.0:5000`

### Default Login Credentials
- **Username**: admin
- **Password**: admin123

## Application Structure

### Main Pages

1. **Login Page**: Authentication with session management
2. **Main Menu**: Central hub for navigating all features
3. **Master Data - Documents**: Manage document details with 15 rows
4. **Master Data - Users**: Add and manage user accounts
5. **Upload Page**: Upload documents with autocomplete fields
6. **Download Page**: Search and download documents
7. **View Report**: Filter and view document tracking reports

### Database Schema

- **users**: User accounts with hashed passwords
- **documents**: Document master data (material info, document numbers, etc.)
- **uploads**: File upload records with user tracking
- **downloads**: Download history with timestamps

## Features in Detail

### Document Details (SAP-Style Layout)
- Material Number
- Material Name
- Vendor
- Document Number
- Revision Number
- Date & Time (auto-generated)
- Status (ACTIVE/INACTIVE)

### Autocomplete Functionality
Upload and download pages feature autocomplete for:
- S.NO (Material Number)
- Document Number
- Revision Number

Data is pulled from the master document database for quick entry.

### Reporting & Tracking
View detailed reports showing:
- Document master data with filters
- Upload history with uploader information
- Download history with user details and timestamps

## Security Features

- Password hashing using Werkzeug
- Session-based authentication
- Protected routes requiring login
- Secure file handling with filename sanitization
- 16MB file size limit

## File Storage

Uploaded documents are stored in the `/uploads` directory with secure filenames.

## Technology Stack

- **Backend**: Flask (Python)
- **Database**: SQLite3
- **Frontend**: HTML5, CSS3, JavaScript
- **Session Management**: Flask-Session
- **Security**: Werkzeug

## License

This project is provided as-is for document management purposes.
