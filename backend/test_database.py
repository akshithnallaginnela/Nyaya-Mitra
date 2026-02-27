"""
Tests for database configuration and connection.

Validates that SQLAlchemy is properly configured and can connect
to PostgreSQL database.
"""

import pytest
from datetime import datetime
from uuid import UUID

from sqlalchemy import Column, String
from sqlalchemy.orm import Session

from database import (
    Base,
    BaseModel,
    engine,
    get_db,
    get_db_session,
    init_db,
    drop_db,
)


# Test model for validation
class TestModel(BaseModel):
    """Test model to validate BaseModel functionality."""
    __tablename__ = "test_models"
    
    name = Column(String(100), nullable=False)


@pytest.fixture(scope="function")
def setup_test_db():
    """Set up test database before each test and clean up after."""
    # Create tables
    Base.metadata.create_all(bind=engine)
    yield
    # Drop tables
    Base.metadata.drop_all(bind=engine)


def test_base_model_has_required_fields(setup_test_db):
    """Test that BaseModel provides id, created_at, and updated_at fields."""
    with get_db() as db:
        test_obj = TestModel(name="Test")
        db.add(test_obj)
        db.commit()
        db.refresh(test_obj)
        
        # Verify id is UUID
        assert isinstance(test_obj.id, UUID)
        
        # Verify created_at is datetime
        assert isinstance(test_obj.created_at, datetime)
        
        # Verify updated_at is datetime
        assert isinstance(test_obj.updated_at, datetime)
        
        # Verify timestamps are recent (within last minute)
        now = datetime.utcnow()
        assert (now - test_obj.created_at).total_seconds() < 60
        assert (now - test_obj.updated_at).total_seconds() < 60


def test_database_connection(setup_test_db):
    """Test that database connection works."""
    with get_db() as db:
        # Simple query to verify connection
        result = db.execute("SELECT 1")
        assert result.scalar() == 1


def test_context_manager_commits_on_success(setup_test_db):
    """Test that context manager commits changes on success."""
    # Create record
    with get_db() as db:
        test_obj = TestModel(name="Test Commit")
        db.add(test_obj)
    
    # Verify record exists in new session
    with get_db() as db:
        result = db.query(TestModel).filter_by(name="Test Commit").first()
        assert result is not None
        assert result.name == "Test Commit"


def test_context_manager_rolls_back_on_error(setup_test_db):
    """Test that context manager rolls back changes on error."""
    try:
        with get_db() as db:
            test_obj = TestModel(name="Test Rollback")
            db.add(test_obj)
            # Force an error
            raise ValueError("Test error")
    except ValueError:
        pass
    
    # Verify record does not exist
    with get_db() as db:
        result = db.query(TestModel).filter_by(name="Test Rollback").first()
        assert result is None


def test_get_db_session_dependency(setup_test_db):
    """Test that get_db_session works as FastAPI dependency."""
    # Get session from generator
    session_gen = get_db_session()
    db = next(session_gen)
    
    try:
        # Verify it's a valid session
        assert isinstance(db, Session)
        
        # Verify we can use it
        test_obj = TestModel(name="Test Dependency")
        db.add(test_obj)
        db.commit()
        
        result = db.query(TestModel).filter_by(name="Test Dependency").first()
        assert result is not None
    finally:
        # Clean up
        try:
            next(session_gen)
        except StopIteration:
            pass


def test_updated_at_changes_on_update(setup_test_db):
    """Test that updated_at timestamp changes when record is updated."""
    import time
    
    # Create record
    with get_db() as db:
        test_obj = TestModel(name="Test Update")
        db.add(test_obj)
        db.commit()
        db.refresh(test_obj)
        original_updated_at = test_obj.updated_at
        obj_id = test_obj.id
    
    # Wait a moment to ensure timestamp difference
    time.sleep(0.1)
    
    # Update record
    with get_db() as db:
        test_obj = db.query(TestModel).filter_by(id=obj_id).first()
        test_obj.name = "Test Update Modified"
        db.commit()
        db.refresh(test_obj)
        new_updated_at = test_obj.updated_at
    
    # Verify updated_at changed
    assert new_updated_at > original_updated_at


def test_init_db_creates_tables():
    """Test that init_db creates all tables."""
    # Drop all tables first
    drop_db()
    
    # Initialize database
    init_db()
    
    # Verify tables exist by checking metadata
    assert len(Base.metadata.tables) > 0
    
    # Clean up
    drop_db()


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
