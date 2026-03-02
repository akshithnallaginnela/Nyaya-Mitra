"""
Emergency Contacts Database Seeding Script

This script populates the emergency_contacts table with:
- National emergency numbers (police, legal, mental health, student services)
- Location-specific contacts for major Indian states and cities
- Categorized contacts for quick filtering

Requirements: 8.3 (Contact categorization), 8.5 (Location-specific), 8.6 (National fallback)
"""

import json
from pathlib import Path
from typing import Dict, List

from sqlalchemy.orm import Session

from database import SessionLocal, init_db
from models.emergency_contact import EmergencyContact


def load_seed_data() -> Dict[str, List[Dict]]:
    """
    Load emergency contacts seed data from JSON file.
    
    Returns:
        Dict containing national_contacts and state_contacts lists
    """
    seed_file = Path(__file__).parent / "emergency_contacts_seed_data.json"
    
    with open(seed_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    return data


def seed_emergency_contacts(db: Session) -> None:
    """
    Seed the database with emergency contacts.
    
    Args:
        db: Database session
    """
    # Load seed data
    data = load_seed_data()
    
    # Check if data already exists
    existing_count = db.query(EmergencyContact).count()
    if existing_count > 0:
        print(f"Database already contains {existing_count} emergency contacts.")
        response = input("Do you want to clear and re-seed? (yes/no): ")
        if response.lower() != 'yes':
            print("Seeding cancelled.")
            return
        
        # Clear existing data
        db.query(EmergencyContact).delete()
        db.commit()
        print("Cleared existing emergency contacts.")
    
    # Seed national contacts
    print("\nSeeding national emergency contacts...")
    national_count = 0
    for contact_data in data['national_contacts']:
        contact = EmergencyContact(
            name=contact_data['name'],
            category=contact_data['category'],
            phone_number=contact_data['phone_number'],
            description=contact_data.get('description'),
            state=None,
            city=None,
            is_national=True,
            is_active=True
        )
        db.add(contact)
        national_count += 1
    
    print(f"Added {national_count} national emergency contacts.")
    
    # Seed state-specific contacts
    print("\nSeeding state-specific emergency contacts...")
    state_count = 0
    for contact_data in data['state_contacts']:
        contact = EmergencyContact(
            name=contact_data['name'],
            category=contact_data['category'],
            phone_number=contact_data['phone_number'],
            description=contact_data.get('description'),
            state=contact_data.get('state'),
            city=contact_data.get('city'),
            is_national=False,
            is_active=True
        )
        db.add(contact)
        state_count += 1
    
    print(f"Added {state_count} state-specific emergency contacts.")
    
    # Commit all changes
    db.commit()
    
    print(f"\n✓ Successfully seeded {national_count + state_count} emergency contacts!")
    print(f"  - National contacts: {national_count}")
    print(f"  - State-specific contacts: {state_count}")
    
    # Display category breakdown
    print("\nCategory breakdown:")
    for category in EmergencyContact.VALID_CATEGORIES:
        count = db.query(EmergencyContact).filter(
            EmergencyContact.category == category
        ).count()
        print(f"  - {category}: {count}")


def verify_seeding(db: Session) -> None:
    """
    Verify that seeding was successful.
    
    Args:
        db: Database session
    """
    print("\n" + "="*60)
    print("VERIFICATION")
    print("="*60)
    
    # Total count
    total = db.query(EmergencyContact).count()
    print(f"\nTotal emergency contacts: {total}")
    
    # National contacts
    national = db.query(EmergencyContact).filter(
        EmergencyContact.is_national == True
    ).count()
    print(f"National contacts: {national}")
    
    # State-specific contacts
    state_specific = db.query(EmergencyContact).filter(
        EmergencyContact.is_national == False
    ).count()
    print(f"State-specific contacts: {state_specific}")
    
    # Contacts by category
    print("\nContacts by category:")
    for category in EmergencyContact.VALID_CATEGORIES:
        count = db.query(EmergencyContact).filter(
            EmergencyContact.category == category
        ).count()
        print(f"  - {category}: {count}")
    
    # Sample contacts
    print("\nSample national contacts:")
    sample_national = db.query(EmergencyContact).filter(
        EmergencyContact.is_national == True
    ).limit(3).all()
    for contact in sample_national:
        print(f"  - {contact.name} ({contact.category}): {contact.phone_number}")
    
    print("\nSample state-specific contacts:")
    sample_state = db.query(EmergencyContact).filter(
        EmergencyContact.is_national == False
    ).limit(3).all()
    for contact in sample_state:
        location = f"{contact.city}, {contact.state}" if contact.city else contact.state
        print(f"  - {contact.name} ({contact.category}) - {location}: {contact.phone_number}")
    
    print("\n✓ Verification complete!")


def main():
    """Main function to run the seeding script."""
    print("="*60)
    print("EMERGENCY CONTACTS DATABASE SEEDING")
    print("="*60)
    
    # Initialize database
    print("\nInitializing database...")
    init_db()
    
    # Create database session
    db = SessionLocal()
    
    try:
        # Seed emergency contacts
        seed_emergency_contacts(db)
        
        # Verify seeding
        verify_seeding(db)
        
    except Exception as e:
        print(f"\n✗ Error during seeding: {str(e)}")
        db.rollback()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    main()
