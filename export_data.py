#!/usr/bin/env python
"""
Database Data Export Script
Exports all data from the food redistribution database to CSV files.
"""
from app import app, db, User, Donation, FoodRequest
import csv
from datetime import datetime

def export_data():
    with app.app_context():
        print("Starting data export...")
        
        # Export Users
        print("\n1. Exporting Users...")
        with open('exported_users.csv', 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(['ID', 'Username', 'Email', 'User Type', 'Organization', 'Phone', 'Address', 'Created At'])
            users = User.query.all()
            for user in users:
                writer.writerow([
                    user.id, user.username, user.email, user.user_type,
                    user.organization_name or '', user.phone or '', 
                    user.address or '', user.created_at.strftime('%Y-%m-%d %H:%M:%S') if user.created_at else ''
                ])
            print(f"   Exported {len(users)} users")
        
        # Export Donations
        print("2. Exporting Donations...")
        with open('exported_donations.csv', 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(['ID', 'Donor ID', 'Donor Username', 'Food Type', 'Quantity', 'Unit', 'Description', 
                            'Location', 'Expiry Date', 'Status', 'Created At', 'Claimed By', 'Claimed At'])
            donations = Donation.query.all()
            for donation in donations:
                donor_name = donation.donor.username if donation.donor else 'N/A'
                writer.writerow([
                    donation.id, donation.donor_id, donor_name, donation.food_type, donation.quantity,
                    donation.quantity_unit, donation.description or '', donation.location,
                    donation.expiry_date.strftime('%Y-%m-%d') if donation.expiry_date else '', 
                    donation.status, donation.created_at.strftime('%Y-%m-%d %H:%M:%S') if donation.created_at else '',
                    donation.claimed_by or '', 
                    donation.claimed_at.strftime('%Y-%m-%d %H:%M:%S') if donation.claimed_at else ''
                ])
            print(f"   Exported {len(donations)} donations")
        
        # Export Food Requests
        print("3. Exporting Food Requests...")
        with open('exported_requests.csv', 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(['ID', 'Receiver ID', 'Receiver Username', 'Food Type Needed', 'Quantity Needed', 'Unit',
                            'Description', 'Location', 'Status', 'Created At', 'Fulfilled At'])
            requests = FoodRequest.query.all()
            for req in requests:
                receiver_name = req.receiver.username if req.receiver else 'N/A'
                writer.writerow([
                    req.id, req.receiver_id, receiver_name, req.food_type_needed, req.quantity_needed,
                    req.quantity_unit, req.description or '', req.location, req.status,
                    req.created_at.strftime('%Y-%m-%d %H:%M:%S') if req.created_at else '',
                    req.fulfilled_at.strftime('%Y-%m-%d %H:%M:%S') if req.fulfilled_at else ''
                ])
            print(f"   Exported {len(requests)} requests")
        
        # Export Summary Statistics
        print("4. Exporting Summary Statistics...")
        with open('exported_statistics.csv', 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(['Metric', 'Value'])
            
            total_users = User.query.count()
            total_donors = User.query.filter_by(user_type='donor').count()
            total_receivers = User.query.filter_by(user_type='receiver').count()
            total_admins = User.query.filter_by(user_type='admin').count()
            total_donations = Donation.query.count()
            total_quantity = db.session.query(db.func.sum(Donation.quantity)).scalar() or 0
            total_requests = FoodRequest.query.count()
            
            writer.writerow(['Total Users', total_users])
            writer.writerow(['Total Donors', total_donors])
            writer.writerow(['Total Receivers', total_receivers])
            writer.writerow(['Total Admins', total_admins])
            writer.writerow(['Total Donations', total_donations])
            writer.writerow(['Total Quantity (kg)', total_quantity])
            writer.writerow(['Total Requests', total_requests])
            
            print(f"   Exported statistics")
        
        print("\n" + "="*50)
        print("✓ Data export completed successfully!")
        print("="*50)
        print("\nExported files:")
        print("  - exported_users.csv")
        print("  - exported_donations.csv")
        print("  - exported_requests.csv")
        print("  - exported_statistics.csv")
        print("\nFiles are saved in the current directory.")

if __name__ == '__main__':
    export_data()

