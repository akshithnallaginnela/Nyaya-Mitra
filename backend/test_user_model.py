"""
Unit tests for User model with authentication fields.

Tests cover:
- User model creation with all fields
- Password hashing with bcrypt (minimum 10 rounds)
- Password verification
- Email validation
- Password strength validation
- Full name validation
- Language validation

Requirements: 9.1 (Password encryption), 6.4 (Language preference)
"""

import pytest
import bcrypt
from sqlalchemy.exc import IntegrityError

from database import Base, engine, get_db
from models.user import User


@pytest.fixture(scope="function")
def setup_database():
    """Create tables before each test and drop after."""
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


class TestUserModelCreation:
    """Test User model creation and field validation."""
    
    def test_create_user_with_all_fields(self, setup_database):
        """Test creating a user with all required and optional fields."""
        with get_db() as db:
            user = User(
                email="student@example.com",
                full_name="Test Student",
                college_name="Test College",
                preferred_language="en"
            )
            user.set_password("SecurePass123!")
            
            db.add(user)
            db.commit()
            db.refresh(user)
            
            assert user.id is not None
            assert user.email == "student@example.com"
            assert user.full_name == "Test Student"
            assert user.college_name == "Test College"
            assert user.preferred_language == "en"
            assert user.is_active is True
            assert user.created_at is not None
            assert user.updated_at is not None
            assert user.password_hash is not None
    
    def test_create_user_without_optional_fields(self, setup_database):
        """Test creating a user without optional fields."""
        with get_db() as db:
            user = User(
                email="student2@example.com",
                full_name="Another Student"
            )
            user.set_password("AnotherPass456!")
            
            db.add(user)
            db.commit()
            db.refresh(user)
            
            assert user.id is not None
            assert user.email == "student2@example.com"
            assert user.college_name is None
            assert user.preferred_language == "en"  # Default value
    
    def test_email_uniqueness_constraint(self, setup_database):
        """Test that duplicate emails are not allowed."""
        with get_db() as db:
            user1 = User(
                email="duplicate@example.com",
                full_name="User One"
            )
            user1.set_password("Password123!")
            db.add(user1)
            db.commit()
        
        with pytest.raises(IntegrityError):
            with get_db() as db:
                user2 = User(
                    email="duplicate@example.com",
                    full_name="User Two"
                )
                user2.set_password("Password456!")
                db.add(user2)
                db.commit()


class TestPasswordHashing:
    """Test password hashing and verification with bcrypt."""
    
    def test_password_hashing_with_bcrypt(self, setup_database):
        """Test that passwords are hashed using bcrypt."""
        password = "TestPassword123!"
        hashed = User.hash_password(password)
        
        # Verify it's a bcrypt hash (starts with $2b$)
        assert hashed.startswith("$2b$")
        
        # Verify the hash is different from the original password
        assert hashed != password
    
    def test_bcrypt_minimum_rounds(self, setup_database):
        """Test that bcrypt uses minimum 10 rounds (requirement 9.1)."""
        password = "TestPassword123!"
        hashed = User.hash_password(password)
        
        # Extract rounds from bcrypt hash format: $2b$rounds$...
        # Format: $2b$12$... where 12 is the number of rounds
        rounds_str = hashed.split("$")[2]
        rounds = int(rounds_str)
        
        # Verify rounds >= 10 (requirement 9.1)
        assert rounds >= 10, f"Bcrypt rounds ({rounds}) must be >= 10"
    
    def test_password_verification_success(self, setup_database):
        """Test successful password verification."""
        with get_db() as db:
            user = User(
                email="verify@example.com",
                full_name="Verify User"
            )
            password = "CorrectPassword123!"
            user.set_password(password)
            
            db.add(user)
            db.commit()
            db.refresh(user)
            
            # Verify correct password
            assert user.verify_password(password) is True
    
    def test_password_verification_failure(self, setup_database):
        """Test failed password verification with wrong password."""
        with get_db() as db:
            user = User(
                email="verify2@example.com",
                full_name="Verify User 2"
            )
            user.set_password("CorrectPassword123!")
            
            db.add(user)
            db.commit()
            db.refresh(user)
            
            # Verify wrong password
            assert user.verify_password("WrongPassword456!") is False
    
    def test_password_hashes_are_unique(self, setup_database):
        """Test that same password produces different hashes (due to salt)."""
        password = "SamePassword123!"
        hash1 = User.hash_password(password)
        hash2 = User.hash_password(password)
        
        # Hashes should be different due to different salts
        assert hash1 != hash2
        
        # But both should verify correctly
        user = User(email="test@example.com", full_name="Test")
        user.password_hash = hash1
        assert user.verify_password(password) is True
        
        user.password_hash = hash2
        assert user.verify_password(password) is True


class TestEmailValidation:
    """Test email validation."""
    
    def test_valid_email_formats(self, setup_database):
        """Test various valid email formats."""
        valid_emails = [
            "student@college.edu",
            "test.user@example.com",
            "user+tag@domain.co.in",
            "123@numbers.com",
            "a@b.co"
        ]
        
        for email in valid_emails:
            with get_db() as db:
                user = User(
                    email=email,
                    full_name="Test User"
                )
                user.set_password("ValidPass123!")
                db.add(user)
                db.commit()
                db.refresh(user)
                
                assert user.email == email.lower()
    
    def test_email_normalization_to_lowercase(self, setup_database):
        """Test that emails are normalized to lowercase."""
        with get_db() as db:
            user = User(
                email="UPPERCASE@EXAMPLE.COM",
                full_name="Test User"
            )
            user.set_password("ValidPass123!")
            db.add(user)
            db.commit()
            db.refresh(user)
            
            assert user.email == "uppercase@example.com"
    
    def test_invalid_email_formats(self, setup_database):
        """Test that invalid email formats are rejected."""
        invalid_emails = [
            "notanemail",
            "@example.com",
            "user@",
            "user @example.com",
            "user@.com",
            ""
        ]
        
        for email in invalid_emails:
            with pytest.raises(ValueError, match="Invalid email format|Email is required"):
                user = User(
                    email=email,
                    full_name="Test User"
                )


class TestPasswordStrengthValidation:
    """Test password strength validation."""
    
    def test_password_minimum_length(self):
        """Test that passwords must be at least 8 characters."""
        with pytest.raises(ValueError, match="at least 8 characters"):
            User.hash_password("Short1!")
    
    def test_password_requires_lowercase(self):
        """Test that passwords must contain lowercase letters."""
        with pytest.raises(ValueError, match="lowercase letter"):
            User.hash_password("UPPERCASE123!")
    
    def test_password_requires_uppercase(self):
        """Test that passwords must contain uppercase letters."""
        with pytest.raises(ValueError, match="uppercase letter"):
            User.hash_password("lowercase123!")
    
    def test_password_requires_digit(self):
        """Test that passwords must contain digits."""
        with pytest.raises(ValueError, match="digit"):
            User.hash_password("NoNumbers!")
    
    def test_password_requires_special_character(self):
        """Test that passwords must contain special characters."""
        with pytest.raises(ValueError, match="special character"):
            User.hash_password("NoSpecial123")
    
    def test_valid_strong_passwords(self):
        """Test that strong passwords are accepted."""
        strong_passwords = [
            "StrongPass123!",
            "MyP@ssw0rd",
            "Secure&Pass1",
            "C0mpl3x!ty",
            "Test@1234"
        ]
        
        for password in strong_passwords:
            hashed = User.hash_password(password)
            assert hashed is not None
            assert len(hashed) > 0


class TestFullNameValidation:
    """Test full name validation."""
    
    def test_full_name_required(self, setup_database):
        """Test that full name is required."""
        with pytest.raises(ValueError, match="Full name is required"):
            user = User(
                email="test@example.com",
                full_name=""
            )
    
    def test_full_name_minimum_length(self, setup_database):
        """Test that full name must be at least 2 characters."""
        with pytest.raises(ValueError, match="at least 2 characters"):
            user = User(
                email="test@example.com",
                full_name="A"
            )
    
    def test_full_name_whitespace_trimming(self, setup_database):
        """Test that full name whitespace is trimmed."""
        with get_db() as db:
            user = User(
                email="test@example.com",
                full_name="  Test User  "
            )
            user.set_password("ValidPass123!")
            db.add(user)
            db.commit()
            db.refresh(user)
            
            assert user.full_name == "Test User"


class TestLanguageValidation:
    """Test language preference validation."""
    
    def test_supported_languages(self, setup_database):
        """Test that supported languages are accepted."""
        supported_languages = ['en', 'hi', 'ta', 'te', 'bn', 'mr', 'gu', 'kn', 'ml', 'pa']
        
        for lang in supported_languages:
            with get_db() as db:
                user = User(
                    email=f"user_{lang}@example.com",
                    full_name="Test User",
                    preferred_language=lang
                )
                user.set_password("ValidPass123!")
                db.add(user)
                db.commit()
                db.refresh(user)
                
                assert user.preferred_language == lang
    
    def test_unsupported_language_rejected(self, setup_database):
        """Test that unsupported languages are rejected."""
        with pytest.raises(ValueError, match="Unsupported language"):
            user = User(
                email="test@example.com",
                full_name="Test User",
                preferred_language="fr"  # French not supported
            )
    
    def test_default_language_is_english(self, setup_database):
        """Test that default language is English."""
        with get_db() as db:
            user = User(
                email="test@example.com",
                full_name="Test User"
            )
            user.set_password("ValidPass123!")
            db.add(user)
            db.commit()
            db.refresh(user)
            
            assert user.preferred_language == "en"


class TestUserModelMethods:
    """Test User model methods."""
    
    def test_set_password_method(self, setup_database):
        """Test set_password method."""
        with get_db() as db:
            user = User(
                email="test@example.com",
                full_name="Test User"
            )
            
            password = "NewPassword123!"
            user.set_password(password)
            
            assert user.password_hash is not None
            assert user.verify_password(password) is True
    
    def test_repr_method(self, setup_database):
        """Test string representation of User."""
        with get_db() as db:
            user = User(
                email="test@example.com",
                full_name="Test User"
            )
            user.set_password("ValidPass123!")
            db.add(user)
            db.commit()
            db.refresh(user)
            
            repr_str = repr(user)
            assert "User" in repr_str
            assert user.email in repr_str
            assert user.full_name in repr_str
            assert str(user.id) in repr_str


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
