# Smart Food Redistribution System

A web application for managing food donations, requests, and redistribution to help reduce food waste and feed those in need.

## Features

### Three User Types:

1. **Donor Login**
   - Dashboard with donation analytics
   - Donate food with details and location
   - View recent donations
   - Track donation statistics

2. **Shelter/Receiver Login**
   - Request food items needed
   - View available donations
   - Claim available donations
   - Track request statistics

3. **Admin/NGO Login**
   - Overall system analytics
   - Daily food data analysis
   - Total donations, quantity, and receivers tracking
   - Donor badges and recognition system
   - Monthly statistics

## Installation

1. Install Python dependencies:
```bash
pip install -r requirements.txt
```

2. Run the application:
```bash
python app.py
```

3. Open your browser and navigate to:
```
http://localhost:5000
```

## Default Admin Account

- **Username:** admin
- **Password:** admin123
- **User Type:** Admin

*Note: Please change the admin password in production!*

## Registration

Users can register as:
- Donor
- Shelter/Receiver
- Admin/NGO

Each user type has access to their respective dashboard and features.

## Database

The application uses SQLite database (`food_redistribution.db`) which will be created automatically on first run.

## Technologies Used

- **Backend:** Flask (Python)
- **Database:** SQLite with SQLAlchemy ORM
- **Frontend:** HTML, CSS, JavaScript
- **Styling:** Modern CSS with gradient design

## Features Overview

- User authentication and authorization
- Role-based access control
- Food donation management
- Food request system
- Real-time statistics and analytics
- Donor badge system
- Monthly and daily reporting
- Responsive design

## Security Notes

- Change the SECRET_KEY in `app.py` for production
- Use environment variables for sensitive data
- Consider using PostgreSQL for production instead of SQLite
- Implement proper password hashing (already included)

