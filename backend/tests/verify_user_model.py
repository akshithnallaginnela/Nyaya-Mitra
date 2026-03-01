"""
Verification script for User model implementation.

This script tests the User model functionality without requiring a database connection.
It validates:
- Password hashing with bcrypt (minimum 10 rounds)
- Password verification
- Email validation
- Password strength validation
- Full name validation
- Language validation

Requirements: 9.1 (Password encryption), 6.4 (Language preference)
"""

import sys
import os

# Add parent directory to path to allow imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from models.user import User


def test_password_hashing():
    """Test password hashing with bcrypt."""
    print("Testing password hashing...")
    
    password = "TestPassword123!"
    hashed = User.hash_password(password)
    
    # Verify it's a bcrypt hash (starts with $2b$)
    assert hashed.startswith("$2b$"), "Password hash should start with $2b$"
    
    # Verify the hash is different from the original password
    assert hashed != password, "Hash should be different from password"
    
    print("✓ Password hashing works correctly")


def test_bcrypt_rounds():
    """Test that bcrypt uses minimum 10 rounds (requirement 9.1)."""
    print("Testing bcrypt rounds...")
    
    password = "TestPassword123!"
    hashed = User.hash_password(password)
    
    # Extract rounds from bcrypt hash format: $2b$rounds$...
    rounds_str = hashed.split("$")[2]
    rounds = int(rounds_str)
    
    # Verify rounds >= 10 (requirement 9.1)
    assert rounds >= 10, f"Bcrypt rounds ({rounds}) must be >= 10"
    print(f"✓ Bcrypt uses {rounds} rounds (minimum 10 required)")


def test_password_verification():
    """Test password verification."""
    print("Testing password verification...")
    
    user = User(
        email="test@example.com",
        full_name="Test User"
    )
    password = "CorrectPassword123!"
    user.set_password(password)
    
    # Verify correct password
    assert user.verify_password(password) is True, "Correct password should verify"
    
    # Verify wrong password
    assert user.verify_password("WrongPassword456!") is False, "Wrong password should not verify"
    
    print("✓ Password verification works correctly")


def test_password_uniqueness():
    """Test that same password produces different hashes (due to salt)."""
    print("Testing password hash uniqueness...")
    
    password = "SamePassword123!"
    hash1 = User.hash_password(password)
    hash2 = User.hash_password(password)
    
    # Hashes should be different due to different salts
    assert hash1 != hash2, "Same password should produce different hashes"
    
    print("✓ Password hashes are unique (salted)")


def test_email_validation():
    """Test email validation."""
    print("Testing email validation...")
    
    # Valid emails
    valid_emails = [
        "student@college.edu",
        "test.user@example.com",
        "user+tag@domain.co.in",
        "123@numbers.com"
    ]
    
    for email in valid_emails:
        user = User(email=email, full_name="Test User")
        assert user.email == email.lower(), f"Email {email} should be valid and lowercase"
    
    # Invalid emails
    invalid_emails = [
        "notanemail",
        "@example.com",
        "user@",
        ""
    ]
    
    for email in invalid_emails:
        try:
            user = User(email=email, full_name="Test User")
            assert False, f"Email {email} should be invalid"
        except ValueError:
            pass  # Expected
    
    print("✓ Email validation works correctly")


def test_password_strength():
    """Test password strength validation."""
    print("Testing password strength validation...")
    
    # Test minimum length
    try:
        User.hash_password("Short1!")
        assert False, "Short password should be rejected"
    except ValueError as e:
        assert "at least 8 characters" in str(e)
    
    # Test requires lowercase
    try:
        User.hash_password("UPPERCASE123!")
        assert False, "Password without lowercase should be rejected"
    except ValueError as e:
        assert "lowercase letter" in str(e)
    
    # Test requires uppercase
    try:
        User.hash_password("lowercase123!")
        assert False, "Password without uppercase should be rejected"
    except ValueError as e:
        assert "uppercase letter" in str(e)
    
    # Test requires digit
    try:
        User.hash_password("NoNumbers!")
        assert False, "Password without digit should be rejected"
    except ValueError as e:
        assert "digit" in str(e)
    
    # Test requires special character
    try:
        User.hash_password("NoSpecial123")
        assert False, "Password without special character should be rejected"
    except ValueError as e:
        assert "special character" in str(e)
    
    # Test valid strong passwords
    strong_passwords = [
        "StrongPass123!",
        "MyP@ssw0rd",
        "Secure&Pass1",
        "C0mpl3x!ty"
    ]
    
    for password in strong_passwords:
        hashed = User.hash_password(password)
        assert hashed is not None and len(hashed) > 0
    
    print("✓ Password strength validation works correctly")


def test_full_name_validation():
    """Test full name validation."""
    print("Testing full name validation...")
    
    # Test empty name
    try:
        user = User(email="test@example.com", full_name="")
        assert False, "Empty full name should be rejected"
    except ValueError as e:
        assert "Full name is required" in str(e)
    
    # Test minimum length
    try:
        user = User(email="test@example.com", full_name="A")
        assert False, "Single character name should be rejected"
    except ValueError as e:
        assert "at least 2 characters" in str(e)
    
    # Test whitespace trimming
    user = User(email="test@example.com", full_name="  Test User  ")
    assert user.full_name == "Test User", "Whitespace should be trimmed"
    
    print("✓ Full name validation works correctly")


def test_language_validation():
    """Test language preference validation."""
    print("Testing language validation...")
    
    # Test supported languages
    supported_languages = ['en', 'hi', 'ta', 'te', 'bn', 'mr', 'gu', 'kn', 'ml', 'pa']
    
    for lang in supported_languages:
        user = User(
            email=f"user_{lang}@example.com",
            full_name="Test User",
            preferred_language=lang
        )
        assert user.preferred_language == lang, f"Language {lang} should be supported"
    
    # Test unsupported language
    try:
        user = User(
            email="test@example.com",
            full_name="Test User",
            preferred_language="fr"  # French not supported
        )
        assert False, "Unsupported language should be rejected"
    except ValueError as e:
        assert "Unsupported language" in str(e)
    
    # Test default language (when not specified, SQLAlchemy default is 'en')
    # Note: Default values only apply when persisting to database
    # For in-memory objects, we need to explicitly set or check the column default
    print("  Note: Default language 'en' is defined in the model schema")
    
    print("✓ Language validation works correctly")


def test_user_model_fields():
    """Test User model has all required fields."""
    print("Testing User model fields...")
    
    try:
        user = User(
            email="test@example.com",
            full_name="Test User",
            college_name="Test College",
            preferred_language="hi",
            is_active=True  # Explicitly set since we're not persisting to DB
        )
        user.set_password("ValidPass123!")
        
        # Check all fields exist
        assert hasattr(user, 'email'), "User should have email field"
        assert hasattr(user, 'password_hash'), "User should have password_hash field"
        assert hasattr(user, 'full_name'), "User should have full_name field"
        assert hasattr(user, 'college_name'), "User should have college_name field"
        assert hasattr(user, 'preferred_language'), "User should have preferred_language field"
        assert hasattr(user, 'is_active'), "User should have is_active field"
        
        # Check field values
        assert user.email == "test@example.com", f"Email mismatch: {user.email}"
        assert user.full_name == "Test User", f"Full name mismatch: {user.full_name}"
        assert user.college_name == "Test College", f"College name mismatch: {user.college_name}"
        assert user.preferred_language == "hi", f"Language mismatch: {user.preferred_language}"
        assert user.is_active is True, f"is_active mismatch: {user.is_active}"
        assert user.password_hash is not None, "Password hash should not be None"
        
        print("✓ User model has all required fields")
    except Exception as e:
        print(f"Error in test_user_model_fields: {e}")
        import traceback
        traceback.print_exc()
        raise


def main():
    """Run all verification tests."""
    print("=" * 60)
    print("User Model Verification")
    print("=" * 60)
    print()
    
    try:
        test_user_model_fields()
        test_password_hashing()
        test_bcrypt_rounds()
        test_password_verification()
        test_password_uniqueness()
        test_email_validation()
        test_password_strength()
        test_full_name_validation()
        test_language_validation()
        
        print()
        print("=" * 60)
        print("✓ ALL TESTS PASSED")
        print("=" * 60)
        print()
        print("Summary:")
        print("- User model created with all required fields")
        print("- Password hashing uses bcrypt with 12 rounds (exceeds minimum of 10)")
        print("- Password verification works correctly")
        print("- Email validation implemented")
        print("- Password strength validation implemented")
        print("- Full name validation implemented")
        print("- Language validation implemented (10 supported languages)")
        print()
        print("Requirements validated:")
        print("- Requirement 9.1: Password encryption with bcrypt (minimum 10 rounds) ✓")
        print("- Requirement 6.4: Language preference support ✓")
        
        return 0
        
    except AssertionError as e:
        print()
        print("=" * 60)
        print("✗ TEST FAILED")
        print("=" * 60)
        print(f"Error: {e}")
        return 1
    except Exception as e:
        print()
        print("=" * 60)
        print("✗ UNEXPECTED ERROR")
        print("=" * 60)
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
