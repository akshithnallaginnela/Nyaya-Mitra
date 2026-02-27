"""
Verification script for Conversation and Message models.

This script validates the model structure, relationships, and validation
logic without requiring a database connection.
"""

import sys
from models.conversation import Conversation, Message
from models.user import User
from sqlalchemy import inspect


def verify_conversation_model():
    """Verify Conversation model structure."""
    print("=" * 60)
    print("Verifying Conversation Model")
    print("=" * 60)
    
    # Check table name
    assert Conversation.__tablename__ == "conversations", "Table name should be 'conversations'"
    print("✓ Table name: conversations")
    
    # Check columns
    mapper = inspect(Conversation)
    columns = {col.key for col in mapper.columns}
    
    required_columns = {'id', 'created_at', 'updated_at', 'user_id', 'title', 'language'}
    assert required_columns.issubset(columns), f"Missing columns: {required_columns - columns}"
    print(f"✓ Columns: {', '.join(sorted(columns))}")
    
    # Check relationships
    relationships = {rel.key for rel in mapper.relationships}
    assert 'user' in relationships, "Missing 'user' relationship"
    assert 'messages' in relationships, "Missing 'messages' relationship"
    print(f"✓ Relationships: {', '.join(sorted(relationships))}")
    
    # Check foreign keys
    user_id_col = mapper.columns['user_id']
    assert len(user_id_col.foreign_keys) > 0, "user_id should have foreign key"
    fk = list(user_id_col.foreign_keys)[0]
    assert 'users.id' in str(fk.target_fullname), "user_id should reference users.id"
    print("✓ Foreign key: user_id -> users.id")
    
    # Check cascade on user relationship
    user_rel = mapper.relationships['user']
    print(f"✓ User relationship back_populates: {user_rel.back_populates}")
    
    # Check cascade on messages relationship
    messages_rel = mapper.relationships['messages']
    assert 'delete-orphan' in str(messages_rel.cascade), "Messages should cascade delete"
    print(f"✓ Messages relationship cascade: {messages_rel.cascade}")
    
    # Test language validation
    try:
        conv = Conversation()
        conv.language = "fr"  # Invalid language
        assert False, "Should have raised ValueError for invalid language"
    except ValueError as e:
        assert "Unsupported language" in str(e)
        print("✓ Language validation works (rejects invalid languages)")
    
    # Test default language
    conv = Conversation()
    assert conv.language == "en", "Default language should be 'en'"
    print("✓ Default language: en")
    
    print("\n✅ Conversation model verification PASSED\n")


def verify_message_model():
    """Verify Message model structure."""
    print("=" * 60)
    print("Verifying Message Model")
    print("=" * 60)
    
    # Check table name
    assert Message.__tablename__ == "messages", "Table name should be 'messages'"
    print("✓ Table name: messages")
    
    # Check columns
    mapper = inspect(Message)
    columns = {col.key for col in mapper.columns}
    
    required_columns = {
        'id', 'created_at', 'updated_at', 'conversation_id', 
        'role', 'content', 'citations', 'confidence_score'
    }
    assert required_columns.issubset(columns), f"Missing columns: {required_columns - columns}"
    print(f"✓ Columns: {', '.join(sorted(columns))}")
    
    # Check relationships
    relationships = {rel.key for rel in mapper.relationships}
    assert 'conversation' in relationships, "Missing 'conversation' relationship"
    print(f"✓ Relationships: {', '.join(sorted(relationships))}")
    
    # Check foreign keys
    conv_id_col = mapper.columns['conversation_id']
    assert len(conv_id_col.foreign_keys) > 0, "conversation_id should have foreign key"
    fk = list(conv_id_col.foreign_keys)[0]
    assert 'conversations.id' in str(fk.target_fullname), "conversation_id should reference conversations.id"
    print("✓ Foreign key: conversation_id -> conversations.id")
    
    # Test role validation
    try:
        msg = Message()
        msg.role = "system"  # Invalid role
        assert False, "Should have raised ValueError for invalid role"
    except ValueError as e:
        assert "Invalid role" in str(e)
        print("✓ Role validation works (rejects invalid roles)")
    
    # Test valid roles
    for role in ['user', 'assistant']:
        msg = Message()
        msg.role = role
        assert msg.role == role
    print("✓ Valid roles accepted: user, assistant")
    
    # Test content validation
    try:
        msg = Message()
        msg.content = ""  # Empty content
        assert False, "Should have raised ValueError for empty content"
    except ValueError as e:
        assert "cannot be empty" in str(e)
        print("✓ Content validation works (rejects empty content)")
    
    try:
        msg = Message()
        msg.content = "   "  # Whitespace only
        assert False, "Should have raised ValueError for whitespace-only content"
    except ValueError as e:
        assert "cannot be empty" in str(e)
        print("✓ Content validation works (rejects whitespace-only content)")
    
    # Test confidence score validation
    try:
        msg = Message()
        msg.confidence_score = -0.1  # Below 0
        assert False, "Should have raised ValueError for negative confidence"
    except ValueError as e:
        assert "between 0.0 and 1.0" in str(e)
        print("✓ Confidence score validation works (rejects < 0.0)")
    
    try:
        msg = Message()
        msg.confidence_score = 1.5  # Above 1
        assert False, "Should have raised ValueError for confidence > 1"
    except ValueError as e:
        assert "between 0.0 and 1.0" in str(e)
        print("✓ Confidence score validation works (rejects > 1.0)")
    
    # Test valid confidence scores
    for score in [0.0, 0.5, 0.85, 1.0, None]:
        msg = Message()
        msg.confidence_score = score
        assert msg.confidence_score == score
    print("✓ Valid confidence scores accepted: 0.0-1.0 and None")
    
    print("\n✅ Message model verification PASSED\n")


def verify_user_relationship():
    """Verify User model has conversations relationship."""
    print("=" * 60)
    print("Verifying User-Conversation Relationship")
    print("=" * 60)
    
    mapper = inspect(User)
    relationships = {rel.key for rel in mapper.relationships}
    
    assert 'conversations' in relationships, "User should have 'conversations' relationship"
    print("✓ User has 'conversations' relationship")
    
    conv_rel = mapper.relationships['conversations']
    assert conv_rel.back_populates == 'user', "Should back_populate to 'user'"
    print("✓ Relationship back_populates: user")
    
    assert 'delete-orphan' in str(conv_rel.cascade), "Should cascade delete"
    print(f"✓ Cascade delete enabled: {conv_rel.cascade}")
    
    print("\n✅ User-Conversation relationship verification PASSED\n")


def verify_model_representations():
    """Verify __repr__ methods."""
    print("=" * 60)
    print("Verifying Model Representations")
    print("=" * 60)
    
    # Test Conversation repr
    conv = Conversation()
    conv.title = "Test Conversation"
    repr_str = repr(conv)
    assert "Conversation" in repr_str
    assert "Test Conversation" in repr_str
    print(f"✓ Conversation repr: {repr_str}")
    
    # Test Message repr
    msg = Message()
    msg.role = "user"
    msg.content = "This is a test message"
    repr_str = repr(msg)
    assert "Message" in repr_str
    assert "user" in repr_str
    assert "This is a test message" in repr_str
    print(f"✓ Message repr: {repr_str}")
    
    # Test Message repr truncation
    msg = Message()
    msg.role = "assistant"
    msg.content = "A" * 100
    repr_str = repr(msg)
    assert "..." in repr_str
    assert len(repr_str) < 200  # Should be truncated
    print(f"✓ Message repr truncates long content: {repr_str[:80]}...")
    
    print("\n✅ Model representation verification PASSED\n")


def main():
    """Run all verifications."""
    print("\n" + "=" * 60)
    print("CONVERSATION AND MESSAGE MODELS VERIFICATION")
    print("=" * 60 + "\n")
    
    try:
        verify_conversation_model()
        verify_message_model()
        verify_user_relationship()
        verify_model_representations()
        
        print("=" * 60)
        print("ALL VERIFICATIONS PASSED ✅")
        print("=" * 60)
        print("\nThe Conversation and Message models are correctly implemented with:")
        print("  • Proper table names and columns")
        print("  • Foreign key relationships")
        print("  • Cascade deletion")
        print("  • Field validation (language, role, content, confidence)")
        print("  • Bidirectional relationships with User")
        print("  • String representations")
        print("\nRequirement 1.6 (Conversation context preservation) is supported by:")
        print("  • Conversation model linking to User")
        print("  • Message model linking to Conversation")
        print("  • Messages ordered by created_at")
        print("  • One-to-many relationships preserving message history")
        print("\nTo run full database tests, start PostgreSQL with:")
        print("  docker compose up -d")
        print("Then run:")
        print("  pytest test_conversation_models.py -v")
        print()
        
        return 0
        
    except AssertionError as e:
        print(f"\n❌ VERIFICATION FAILED: {e}\n")
        return 1
    except Exception as e:
        print(f"\n❌ ERROR: {e}\n")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
