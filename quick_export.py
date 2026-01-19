#!/usr/bin/env python
"""
Quick database query and export tool
Usage: python quick_export.py [command]
Commands:
  - view_users      : View all users
  - view_donations  : View all donations
  - view_requests   : View all requests
  - export_all      : Export all data to CSV
  - stats           : Show statistics
"""
from app import app, db, User, Donation, FoodRequest
from sqlalchemy import func
import sys
import csv

def view_users():
    """Display all users"""
    with app.app_context():
        users = User.query.all()
        print("\n" + "="*80)
        print("USERS TABLE")
        print("="*80)
        print(f"{'ID':<5} {'Username':<20} {'Email':<30} {'Type':<10} {'Organization':<20}")
        print("-"*80)
        for user in users:
            org = (user.organization_name or '')[:18]
            print(f"{user.id:<5} {user.username:<20} {user.email:<30} {user.user_type:<10} {org:<20}")
        print(f"\nTotal: {len(users)} users")

def view_donations():
    """Display all donations"""
    with app.app_context():
        donations = Donation.query.all()
        print("\n" + "="*100)
        print("DONATIONS TABLE")
        print("="*100)
        print(f"{'ID':<5} {'Donor':<20} {'Food Type':<20} {'Quantity':<10} {'Status':<12} {'Location':<20} {'Date':<20}")
        print("-"*100)
        for donation in donations:
            donor_name = donation.donor.username if donation.donor else 'N/A'
            date_str = donation.created_at.strftime('%Y-%m-%d %H:%M') if donation.created_at else 'N/A'
            location = donation.location[:18] if donation.location else ''
            print(f"{donation.id:<5} {donor_name:<20} {donation.food_type:<20} {str(donation.quantity)+' '+donation.quantity_unit:<10} {donation.status:<12} {location:<20} {date_str:<20}")
        print(f"\nTotal: {len(donations)} donations")

def view_requests():
    """Display all food requests"""
    with app.app_context():
        requests = FoodRequest.query.all()
        print("\n" + "="*100)
        print("FOOD REQUESTS TABLE")
        print("="*100)
        print(f"{'ID':<5} {'Receiver':<20} {'Food Type':<20} {'Quantity':<10} {'Status':<12} {'Location':<20} {'Date':<20}")
        print("-"*100)
        for req in requests:
            receiver_name = req.receiver.username if req.receiver else 'N/A'
            date_str = req.created_at.strftime('%Y-%m-%d %H:%M') if req.created_at else 'N/A'
            location = req.location[:18] if req.location else ''
            print(f"{req.id:<5} {receiver_name:<20} {req.food_type_needed:<20} {str(req.quantity_needed)+' '+req.quantity_unit:<10} {req.status:<12} {location:<20} {date_str:<20}")
        print(f"\nTotal: {len(requests)} requests")

def export_all():
    """Export all data to CSV files"""
    from export_data import export_data
    export_data()

def show_stats():
    """Show database statistics"""
    with app.app_context():
        total_users = User.query.count()
        total_donors = User.query.filter_by(user_type='donor').count()
        total_receivers = User.query.filter_by(user_type='receiver').count()
        total_admins = User.query.filter_by(user_type='admin').count()
        total_donations = Donation.query.count()
        total_quantity = db.session.query(func.sum(Donation.quantity)).scalar() or 0
        available = Donation.query.filter_by(status='available').count()
        claimed = Donation.query.filter_by(status='claimed').count()
        completed = Donation.query.filter_by(status='completed').count()
        total_requests = FoodRequest.query.count()
        pending = FoodRequest.query.filter_by(status='pending').count()
        fulfilled = FoodRequest.query.filter_by(status='fulfilled').count()
        
        print("\n" + "="*50)
        print("DATABASE STATISTICS")
        print("="*50)
        print(f"\nUsers:")
        print(f"  Total Users:     {total_users}")
        print(f"  Donors:          {total_donors}")
        print(f"  Receivers:       {total_receivers}")
        print(f"  Admins:          {total_admins}")
        print(f"\nDonations:")
        print(f"  Total:           {total_donations}")
        print(f"  Total Quantity:  {total_quantity:.1f} kg")
        print(f"  Available:       {available}")
        print(f"  Claimed:         {claimed}")
        print(f"  Completed:       {completed}")
        print(f"\nRequests:")
        print(f"  Total:           {total_requests}")
        print(f"  Pending:         {pending}")
        print(f"  Fulfilled:       {fulfilled}")
        print("="*50)

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("\nUsage: python quick_export.py [command]")
        print("\nCommands:")
        print("  view_users      - View all users")
        print("  view_donations  - View all donations")
        print("  view_requests   - View all requests")
        print("  export_all      - Export all data to CSV")
        print("  stats           - Show statistics")
        print("\nExample: python quick_export.py view_users")
        sys.exit(1)
    
    command = sys.argv[1].lower()
    
    if command == 'view_users':
        view_users()
    elif command == 'view_donations':
        view_donations()
    elif command == 'view_requests':
        view_requests()
    elif command == 'export_all':
        export_all()
    elif command == 'stats':
        show_stats()
    else:
        print(f"Unknown command: {command}")
        sys.exit(1)

