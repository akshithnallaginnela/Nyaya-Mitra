"""
Database seeding script for legal aid providers.

This script loads legal aid provider data from a JSON file and populates
the LegalAidProvider table in the database.

Requirements: 5.5 (Legal aid provider database)
"""

import json
import sys
from pathlib import Path
from typing import List, Dict, Any

from sqlalchemy.orm import Session

from database import SessionLocal, engine, Base
from models.legal_aid_provider import LegalAidProvider


def load_seed_data(file_path: str = "legal_aid_providers_seed_data.json") -> List[Dict[str, Any]]:
    """
    Load legal aid provider seed data from JSON file.
    
    Args:
        file_path: Path to the JSON seed data file
        
    Returns:
        List[Dict[str, Any]]: List of provider data dictionaries
        
    Raises:
        FileNotFoundError: If seed data file doesn't exist
        json.JSONDecodeError: If JSON file is malformed
    """
    seed_file = Path(__file__).parent / file_path
    
    if not seed_file.exists():
        raise FileNotFoundError(f"Seed data file not found: {seed_file}")
    
    with open(seed_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    print(f"✓ Loaded {len(data)} legal aid providers from {file_path}")
    return data


def clear_existing_data(db: Session) -> int:
    """
    Clear existing legal aid provider data from database.
    
    Args:
        db: Database session
        
    Returns:
        int: Number of records deleted
    """
    count = db.query(LegalAidProvider).count()
    
    if count > 0:
        db.query(LegalAidProvider).delete()
        db.commit()
        print(f"✓ Cleared {count} existing legal aid provider records")
    else:
        print("✓ No existing records to clear")
    
    return count


def seed_legal_aid_providers(
    db: Session,
    providers_data: List[Dict[str, Any]],
    clear_existing: bool = True
) -> int:
    """
    Seed legal aid provider data into the database.
    
    Args:
        db: Database session
        providers_data: List of provider data dictionaries
        clear_existing: Whether to clear existing data before seeding
        
    Returns:
        int: Number of providers successfully seeded
        
    Raises:
        ValueError: If provider data is invalid
    """
    if clear_existing:
        clear_existing_data(db)
    
    seeded_count = 0
    errors = []
    
    for idx, provider_data in enumerate(providers_data, 1):
        try:
            # Convert lists to JSON strings for storage
            specializations_json = json.dumps(provider_data.get('specializations', []))
            languages_json = json.dumps(provider_data.get('languages_supported', []))
            
            # Create provider instance
            provider = LegalAidProvider(
                name=provider_data['name'],
                organization_type=provider_data['organization_type'],
                specializations=specializations_json,
                languages_supported=languages_json,
                contact_phone=provider_data.get('contact_phone'),
                contact_email=provider_data.get('contact_email'),
                address=provider_data.get('address'),
                city=provider_data['city'],
                state=provider_data['state'],
                is_verified=provider_data.get('is_verified', False)
            )
            
            db.add(provider)
            seeded_count += 1
            
            # Print progress every 10 providers
            if idx % 10 == 0:
                print(f"  Processed {idx}/{len(providers_data)} providers...")
            
        except KeyError as e:
            error_msg = f"Provider {idx}: Missing required field {e}"
            errors.append(error_msg)
            print(f"✗ {error_msg}")
            
        except ValueError as e:
            error_msg = f"Provider {idx} ({provider_data.get('name', 'Unknown')}): {e}"
            errors.append(error_msg)
            print(f"✗ {error_msg}")
            
        except Exception as e:
            error_msg = f"Provider {idx} ({provider_data.get('name', 'Unknown')}): Unexpected error - {e}"
            errors.append(error_msg)
            print(f"✗ {error_msg}")
    
    # Commit all changes
    try:
        db.commit()
        print(f"\n✓ Successfully seeded {seeded_count} legal aid providers")
        
        if errors:
            print(f"\n⚠ Encountered {len(errors)} errors during seeding:")
            for error in errors:
                print(f"  - {error}")
        
        return seeded_count
        
    except Exception as e:
        db.rollback()
        print(f"\n✗ Failed to commit changes: {e}")
        raise


def verify_seeded_data(db: Session) -> None:
    """
    Verify seeded data by running some basic queries.
    
    Args:
        db: Database session
    """
    print("\n" + "="*60)
    print("VERIFICATION REPORT")
    print("="*60)
    
    # Total count
    total_count = db.query(LegalAidProvider).count()
    print(f"\nTotal providers in database: {total_count}")
    
    # Count by organization type
    print("\nProviders by organization type:")
    org_types = db.query(
        LegalAidProvider.organization_type,
        db.func.count(LegalAidProvider.id)
    ).group_by(LegalAidProvider.organization_type).all()
    
    for org_type, count in org_types:
        print(f"  {org_type}: {count}")
    
    # Count by state (top 10)
    print("\nTop 10 states by provider count:")
    states = db.query(
        LegalAidProvider.state,
        db.func.count(LegalAidProvider.id)
    ).group_by(LegalAidProvider.state).order_by(
        db.func.count(LegalAidProvider.id).desc()
    ).limit(10).all()
    
    for state, count in states:
        print(f"  {state}: {count}")
    
    # Verified vs unverified
    verified_count = db.query(LegalAidProvider).filter(
        LegalAidProvider.is_verified == True
    ).count()
    unverified_count = total_count - verified_count
    
    print(f"\nVerification status:")
    print(f"  Verified: {verified_count}")
    print(f"  Unverified: {unverified_count}")
    
    # Sample providers
    print("\nSample providers (first 5):")
    sample_providers = db.query(LegalAidProvider).limit(5).all()
    
    for provider in sample_providers:
        print(f"\n  {provider.name}")
        print(f"    Type: {provider.organization_type}")
        print(f"    Location: {provider.city}, {provider.state}")
        print(f"    Phone: {provider.contact_phone or 'N/A'}")
        print(f"    Email: {provider.contact_email or 'N/A'}")
    
    print("\n" + "="*60)


def main():
    """
    Main function to run the seeding script.
    """
    print("="*60)
    print("LEGAL AID PROVIDER DATABASE SEEDING")
    print("="*60)
    print()
    
    try:
        # Create tables if they don't exist
        print("Creating database tables...")
        Base.metadata.create_all(bind=engine)
        print("✓ Database tables ready")
        print()
        
        # Load seed data
        print("Loading seed data...")
        providers_data = load_seed_data()
        print()
        
        # Create database session
        db = SessionLocal()
        
        try:
            # Seed the database
            print("Seeding database...")
            seeded_count = seed_legal_aid_providers(db, providers_data, clear_existing=True)
            
            # Verify seeded data
            verify_seeded_data(db)
            
            print("\n✓ Seeding completed successfully!")
            return 0
            
        finally:
            db.close()
            
    except FileNotFoundError as e:
        print(f"\n✗ Error: {e}")
        return 1
        
    except json.JSONDecodeError as e:
        print(f"\n✗ Error: Invalid JSON in seed data file - {e}")
        return 1
        
    except Exception as e:
        print(f"\n✗ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
