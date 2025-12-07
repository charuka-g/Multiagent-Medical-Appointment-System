# #!/usr/bin/env python3
# """Standalone script to test database connection"""

# import os
# import sys
# from pathlib import Path

# # Add parent directory to path
# # sys.path.insert(0, str(Path(__file__).parent))

# from db_connection import connect_to_db

# def test_db():
#     """Test database connection"""
#     try:
#         conn = connect_to_db()
#         conn.close()
#         print("status: success, message: Database connection successful")
#     except Exception as e:
#         print(f"Database connection failed: {str(e)}")
#         print(f"status: error, message: {str(e)}")

# if __name__ == "__main__":
#     test_db()

"""
Script to seed dummy customer data into PostgreSQL database.
Run this script to populate the customers table with test data.
"""

import os
import sys
from pathlib import Path
from datetime import datetime
import random

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from db_connection import connect_to_db
from dotenv import load_dotenv

load_dotenv()


def generate_dummy_customers(count=10):
    """Generate dummy customer data"""
    first_names = [
        "John", "Jane", "Michael", "Sarah", "David", "Emily", "Robert", "Jessica",
        "William", "Ashley", "James", "Amanda", "Christopher", "Melissa"
    ]
    
    last_names = [
        "Smith", "Johnson", "Williams", "Brown", "Jones", "Garcia", "Miller", "Davis",
        "Rodriguez", "Martinez", "Hernandez", "Lopez", "Wilson", "Anderson"
    ]
    
    customers = []
    used_emails = set()
    
    for i in range(count):
        first_name = random.choice(first_names)
        last_name = random.choice(last_names)
        name = f"{first_name} {last_name}"
        
        # Generate unique email
        email_base = f"{first_name.lower()}.{last_name.lower()}"
        email_num = random.randint(1, 9999)
        email = f"{email_base}{email_num}@example.com"
        
        # Ensure email is unique
        while email in used_emails:
            email_num = random.randint(1, 9999)
            email = f"{email_base}{email_num}@example.com"
        used_emails.add(email)
        
        customers.append({
            "name": name,
            "email": email
        })
    
    return customers


def seed_customers(num_customers=10):
    """Seed customers table with dummy data"""
    try:
        print(f"Connecting to database...")
        conn = connect_to_db()
        cur = conn.cursor()
        print("✓ Database connection established")
        
        # Check if table exists
        cur.execute("""
            SELECT EXISTS (
                SELECT FROM information_schema.tables 
                WHERE table_schema = 'public' 
                AND table_name = 'customers'
            );
        """)
        table_exists = cur.fetchone()[0]
        
        if not table_exists:
            print("❌ Error: 'customers' table does not exist!")
            print("Please create the table first with:")
            print("""
            CREATE TABLE customers (
                customer_id SERIAL PRIMARY KEY,
                name VARCHAR(100),
                email VARCHAR(100) UNIQUE NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
            """)
            cur.close()
            conn.close()
            return False
        
        # Check current count
        cur.execute("SELECT COUNT(*) FROM customers;")
        initial_count = cur.fetchone()[0]
        print(f"Current customers in database: {initial_count}")
        
        # Generate dummy data
        print(f"\nGenerating {num_customers} dummy customers...")
        customers = generate_dummy_customers(num_customers)
        
        # Insert customers
        print(f"\nInserting {num_customers} customers into database...")
        inserted_count = 0
        skipped_count = 0
        
        for customer in customers:
            try:
                cur.execute("""
                    INSERT INTO customers (name, email)
                    VALUES (%s, %s)
                    ON CONFLICT (email) DO NOTHING
                    RETURNING customer_id;
                """, (customer["name"], customer["email"]))
                
                result = cur.fetchone()
                if result:
                    inserted_count += 1
                    print(f"  ✓ Inserted: {customer['name']} ({customer['email']}) - ID: {result[0]}")
                else:
                    skipped_count += 1
                    print(f"  ⊘ Skipped (duplicate): {customer['email']}")
                    
            except Exception as e:
                print(f"  ✗ Error inserting {customer['name']}: {e}")
                skipped_count += 1
        
        # Commit changes
        conn.commit()
        
        # Get final count
        cur.execute("SELECT COUNT(*) FROM customers;")
        final_count = cur.fetchone()[0]
        
        print(f"\n{'='*60}")
        print(f"Summary:")
        print(f"  - Initial count: {initial_count}")
        print(f"  - Attempted to insert: {num_customers}")
        print(f"  - Successfully inserted: {inserted_count}")
        print(f"  - Skipped (duplicates): {skipped_count}")
        print(f"  - Final count: {final_count}")
        print(f"{'='*60}")
        
        # Display sample of inserted customers
        if inserted_count > 0:
            print(f"\nSample of inserted customers:")
            cur.execute("""
                SELECT customer_id, name, email, created_at
                FROM customers
                ORDER BY customer_id DESC
                LIMIT 5;
            """)
            samples = cur.fetchall()
            for sample in samples:
                print(f"  ID: {sample[0]}, Name: {sample[1]}, Email: {sample[2]}, Created: {sample[3]}")
        
        cur.close()
        conn.close()
        
        print(f"\n✅ Successfully seeded customers table!")
        return True
        
    except cur.Error as e:
        print(f"\n❌ Database error: {e}")
        if conn:
            conn.rollback()
            conn.close()
        return False
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        if conn:
            conn.rollback()
            conn.close()
        return False


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Seed customers table with dummy data")
    parser.add_argument(
        "--count",
        type=int,
        default=10,
        help="Number of customers to insert (default: 10)"
    )
    
    args = parser.parse_args()
    
    print("="*60)
    print("Customer Data Seeding Script")
    print("="*60)
    
    seed_customers(10)