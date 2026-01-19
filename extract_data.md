# Database Data Extraction Commands

## Using SQLite Command Line

### 1. Open SQLite Database
```bash
sqlite3 instance/food_redistribution.db
```

### 2. View All Tables
```sql
.tables
```

### 3. View Table Structure
```sql
.schema user
.schema donation
.schema food_request
```

### 4. View All Data from Tables

#### View All Users
```sql
SELECT * FROM user;
```

#### View All Donations
```sql
SELECT * FROM donation;
```

#### View All Food Requests
```sql
SELECT * FROM food_request;
```

### 5. Export Data to CSV

#### Export Users to CSV
```sql
.headers on
.mode csv
.output users.csv
SELECT * FROM user;
.output stdout
```

#### Export Donations to CSV
```sql
.headers on
.mode csv
.output donations.csv
SELECT * FROM donation;
.output stdout
```

#### Export Food Requests to CSV
```sql
.headers on
.mode csv
.output food_requests.csv
SELECT * FROM food_request;
.output stdout
```

### 6. Export All Tables to CSV (One Command)
```sql
.headers on
.mode csv
.output all_users.csv
SELECT * FROM user;
.output all_donations.csv
SELECT * FROM donation;
.output all_requests.csv
SELECT * FROM food_request;
.output stdout
```

### 7. Query Specific Data

#### View Users by Type
```sql
SELECT * FROM user WHERE user_type = 'donor';
SELECT * FROM user WHERE user_type = 'receiver';
SELECT * FROM user WHERE user_type = 'admin';
```

#### View Available Donations
```sql
SELECT * FROM donation WHERE status = 'available';
```

#### View Recent Donations (Last 10)
```sql
SELECT * FROM donation ORDER BY created_at DESC LIMIT 10;
```

#### View Statistics
```sql
-- Total donations
SELECT COUNT(*) as total_donations FROM donation;

-- Total quantity
SELECT SUM(quantity) as total_quantity FROM donation;

-- Total users by type
SELECT user_type, COUNT(*) as count FROM user GROUP BY user_type;
```

### 8. Exit SQLite
```sql
.exit
```

---

## Using Python Scripts (Alternative Method)

### Quick Python Export Script
Save this as `export_data.py`:

```python
from app import app, db, User, Donation, FoodRequest
import csv
from datetime import datetime

with app.app_context():
    # Export Users
    with open('exported_users.csv', 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(['ID', 'Username', 'Email', 'User Type', 'Organization', 'Phone', 'Address', 'Created At'])
        for user in User.query.all():
            writer.writerow([
                user.id, user.username, user.email, user.user_type,
                user.organization_name or '', user.phone or '', 
                user.address or '', user.created_at
            ])
    
    # Export Donations
    with open('exported_donations.csv', 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(['ID', 'Donor ID', 'Food Type', 'Quantity', 'Unit', 'Description', 
                        'Location', 'Expiry Date', 'Status', 'Created At', 'Claimed By', 'Claimed At'])
        for donation in Donation.query.all():
            writer.writerow([
                donation.id, donation.donor_id, donation.food_type, donation.quantity,
                donation.quantity_unit, donation.description or '', donation.location,
                donation.expiry_date or '', donation.status, donation.created_at,
                donation.claimed_by or '', donation.claimed_at or ''
            ])
    
    # Export Food Requests
    with open('exported_requests.csv', 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(['ID', 'Receiver ID', 'Food Type Needed', 'Quantity Needed', 'Unit',
                        'Description', 'Location', 'Status', 'Created At', 'Fulfilled At'])
        for req in FoodRequest.query.all():
            writer.writerow([
                req.id, req.receiver_id, req.food_type_needed, req.quantity_needed,
                req.quantity_unit, req.description or '', req.location, req.status,
                req.created_at, req.fulfilled_at or ''
            ])
    
    print("Data exported successfully!")
    print("- exported_users.csv")
    print("- exported_donations.csv")
    print("- exported_requests.csv")
```

Run with: `python export_data.py`

---

## Quick One-Line Commands (PowerShell/CMD)

### View all users
```bash
sqlite3 instance/food_redistribution.db "SELECT * FROM user;"
```

### View all donations
```bash
sqlite3 instance/food_redistribution.db "SELECT * FROM donation;"
```

### View all requests
```bash
sqlite3 instance/food_redistribution.db "SELECT * FROM food_request;"
```

### Export to CSV (PowerShell)
```powershell
sqlite3 instance/food_redistribution.db -header -csv "SELECT * FROM user;" > users.csv
sqlite3 instance/food_redistribution.db -header -csv "SELECT * FROM donation;" > donations.csv
sqlite3 instance/food_redistribution.db -header -csv "SELECT * FROM food_request;" > requests.csv
```

### Export to CSV (CMD)
```cmd
sqlite3 instance/food_redistribution.db -header -csv "SELECT * FROM user;" > users.csv
sqlite3 instance/food_redistribution.db -header -csv "SELECT * FROM donation;" > donations.csv
sqlite3 instance/food_redistribution.db -header -csv "SELECT * FROM food_request;" > requests.csv
```

