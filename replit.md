# Contract Document Management System

## Overview
A comprehensive Contract Document Management System built with Flask, HTML, CSS, JavaScript, and SQLite database. The system provides secure document upload, download, management, and tracking capabilities with user authentication and detailed reporting.

## Project Status
**Current State**: Fully functional Document Management System with all core features implemented and updated
**Last Updated**: October 9, 2025

## Features

### 1. Authentication System
- Login page with session management
- Default admin credentials: `admin` / `admin123`
- Secure password hashing with Werkzeug
- Session-based authentication

### 2. Main Menu
Centralized navigation hub with access to:
- Upload Page
- Download Page
- Master Data (Documents & Users)
- View Report

### 3. Master Data Management

#### Document Details
- Simple form layout (single row entry)
- Fields:
  - Quantity (textbox)
  - Material Number (textbox)
  - Material Name (textbox)
  - Vendor (textbox)
  - Document Number (textbox)
  - Revision Number (textbox)
  - Price (textbox)
  - Date (auto-generated, date only)
  - Status (dropdown: ACTIVE/INACTIVE)
- No field validation as per requirements
- Edit and Delete functionality for each document
- Stores all document metadata

#### User Details
- Username (unique)
- Password (hashed)
- Department
- Name
- Edit and Delete functionality for each user
- User management interface

### 4. Upload Page
- Document Number field with autocomplete
- Revision Number field with autocomplete
- Date (auto-generated, date only - no time)
- File upload functionality
- Tracks uploaded files and uploading user

### 5. Download Page
- Search functionality with autocomplete:
  - Document Number
  - Revision Number
- Displays search results in table format
- Download button for each document
- Tracks downloads with user information and date

### 6. View Report
- Filter options:
  - Document Number
  - Revision Number
  - Date
  - Material Name
- Three main report sections:
  1. **Document Details**: Shows filtered document master data with all fields
  2. **Upload Items**: Lists all uploaded documents with uploader info
  3. **Download Items**: Shows download history with user details

## Technical Architecture

### Backend
- **Framework**: Flask 3.1.2
- **Database**: SQLite3 (file-based)
- **Session Management**: Flask-Session 0.8.0
- **Security**: Werkzeug password hashing
- **File Handling**: Secure filename processing

### Database Schema

#### Tables:
1. **users**
   - id (PRIMARY KEY)
   - username (UNIQUE)
   - password (hashed)
   - department
   - name

2. **documents**
   - id (PRIMARY KEY)
   - quantity
   - material_number
   - material_name
   - vendor
   - document_number
   - revision_number
   - price
   - date
   - status

3. **uploads**
   - id (PRIMARY KEY)
   - document_number
   - revision_number
   - date
   - filename
   - filepath
   - uploaded_by

4. **downloads**
   - id (PRIMARY KEY)
   - upload_id (FOREIGN KEY)
   - document_number
   - downloaded_by
   - download_date

### Frontend
- **HTML5**: Template structure
- **CSS3**: Custom responsive styling with gradient design
- **JavaScript**: Autocomplete functionality, dynamic date
- **Design**: Professional UI with edit/delete actions

### File Storage
- Uploaded files stored in `/uploads` directory
- Secure filename handling
- 16MB maximum file size limit

## Project Structure
```
.
├── app.py                  # Main Flask application
├── templates/              # HTML templates
│   ├── login.html
│   ├── menu.html
│   ├── master_documents.html
│   ├── master_users.html
│   ├── edit_document.html
│   ├── edit_user.html
│   ├── upload.html
│   ├── download.html
│   └── view_report.html
├── static/                 # Static assets
│   └── style.css
├── uploads/               # Uploaded documents storage
├── dms.db                 # SQLite database (auto-created)
└── replit.md             # This file
```

## Running the Application

The Flask server runs on port 5000:
```bash
python app.py
```

Access the application at: `http://0.0.0.0:5000`

## Default Credentials
- Username: `admin`
- Password: `admin123`

## API Endpoints

### Public Routes
- `GET /` - Redirects to login or menu
- `GET /login` - Login page
- `POST /login` - Login authentication
- `GET /logout` - Logout user

### Protected Routes (requires authentication)
- `GET /menu` - Main menu
- `GET/POST /master/documents` - Document master data
- `GET/POST /master/documents/edit/<id>` - Edit document
- `GET /master/documents/delete/<id>` - Delete document
- `GET/POST /master/users` - User master data
- `GET/POST /master/users/edit/<id>` - Edit user
- `GET /master/users/delete/<id>` - Delete user
- `GET/POST /upload` - Upload documents
- `GET/POST /download` - Search and download
- `GET /download_file/<id>` - Download specific file
- `GET /view_report` - View reports with filters
- `GET /api/search_documents` - Autocomplete API

## User Preferences
None specified yet

## Recent Changes
- October 9, 2025: Initial implementation completed
  - Created Flask application with SQLite database
  - Implemented all 6 main features (Login, Menu, Master Data, Upload, Download, View Report)
  
- October 9, 2025: Major updates implemented
  - Changed "No of Material" to "Quantity" in document master data
  - Reduced document entry from 15 rows to single row form
  - Added Material Number and Price fields to documents
  - Removed time tracking (kept only date) from all modules
  - Removed S.No field from Upload and Download pages
  - Added Edit functionality for both documents and users
  - Added Delete functionality for both documents and users
  - Updated database schema to reflect new field structure
  - Added action buttons (Edit/Delete) styling
  - Updated all templates to match new requirements
