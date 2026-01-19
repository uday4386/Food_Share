from app import app, db, User, Donation
from datetime import datetime, date
import random
import string

def verify():
    with app.app_context():
        print("Starting Verification...")
        
        # 1. Create a dummy donor
        suffix = ''.join(random.choices(string.ascii_lowercase, k=5))
        donor_name = f"test_donor_{suffix}"
        donor = User(
            username=donor_name,
            email=f"{donor_name}@example.com",
            password='hashed_password',
            user_type='donor',
            unique_id=f"TMP{suffix}"
        )
        db.session.add(donor)
        db.session.commit()
        print(f"Created test donor: {donor.username}")

        try:
            # 2. Add Donations
            # Donation A: Expires later (Benefit of doubt, should be lower priority)
            donation_late = Donation(
                donor_id=donor.id,
                food_type="Late Expiry Food",
                quantity=10,
                location="Test Loc",
                expiry_date=date(2025, 12, 30),
                status='available'
            )
            
            # Donation B: Expires sooner (Should be higher priority)
            donation_soon = Donation(
                donor_id=donor.id,
                food_type="Soon Expiry Food",
                quantity=10,
                location="Test Loc",
                expiry_date=date(2025, 12, 25),
                status='available'
            )

            db.session.add(donation_late)
            db.session.add(donation_soon)
            db.session.commit()
            print("Created two donations with different expiry dates.")

            # 3. Query using the logic from app.py
            # Donation.expiry_date.asc(), Donation.created_at.desc()
            results = db.session.query(Donation).filter_by(
                status='available',
                donor_id=donor.id # Filter by our test donor to avoid noise
            ).order_by(
                Donation.expiry_date.asc(),
                Donation.created_at.desc()
            ).all()

            # 4. Verify Order
            if not results:
                print("FAILED: No donations found.")
                return

            first = results[0]
            second = results[1]

            print(f"First item expiry: {first.expiry_date}")
            print(f"Second item expiry: {second.expiry_date}")

            if first.expiry_date == date(2025, 12, 25) and second.expiry_date == date(2025, 12, 30):
                print("SUCCESS: Donations are sorted by expiry date correctly (Sooner -> Later).")
            else:
                print("FAILED: Order is incorrect.")

        finally:
            # Cleanup
            print("Cleaning up test data...")
            db.session.delete(donation_late)
            db.session.delete(donation_soon)
            db.session.delete(donor)
            db.session.commit()
            print("Cleanup complete.")

if __name__ == "__main__":
    verify()
