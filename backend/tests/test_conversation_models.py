"""
Unit tests for Conversation and Message models.

Tests cover:
- Conversation model creation with user relationship
- Message model creation with conversation relationship
- Foreign key relationships and cascade deletion
- Language validation
- Role validation
- Content validation
- Confidence score validation
- Conversation context preservation

Requirements: 1.6 (Conversation context preservation)
"""

import pytest
from sqlalchemy.exc import IntegrityError

from database import Base, engine, get_db
from models.user import User
from models.conversation import Conversation, Message


@pytest.fixture(scope="function")
def setup_database():
    """Create tables before each test and drop after."""
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


@pytest.fixture
def test_user(setup_database):
    """Create a test user for conversation tests."""
    with get_db() as db:
        user = User(
            email="testuser@example.com",
            full_name="Test User"
        )
        user.set_password("TestPass123!")
        db.add(user)
        db.commit()
        db.refresh(user)
        return user.id


class TestConversationModelCreation:
    """Test Conversation model creation and field validation."""
    
    def test_create_conversation_with_all_fields(self, test_user):
        """Test creating a conversation with all fields."""
        with get_db() as db:
            conversation = Conversation(
                user_id=test_user,
                title="Legal Query about Defamation",
                language="en"
            )
            
            db.add(conversation)
            db.commit()
            db.refresh(conversation)
            
            assert conversation.id is not None
            assert conversation.user_id == test_user
            assert conversation.title == "Legal Query about Defamation"
            assert conversation.language == "en"
            assert conversation.created_at is not None
            assert conversation.updated_at is not None
    
    def test_create_conversation_without_title(self, test_user):
        """Test creating a conversation without optional title."""
        with get_db() as db:
            conversation = Conversation(
                user_id=test_user,
                language="hi"
            )
            
            db.add(conversation)
            db.commit()
            db.refresh(conversation)
            
            assert conversation.id is not None
            assert conversation.title is None
            assert conversation.language == "hi"
    
    def test_conversation_default_language(self, test_user):
        """Test that default language is English."""
        with get_db() as db:
            conversation = Conversation(
                user_id=test_user
            )
            
            db.add(conversation)
            db.commit()
            db.refresh(conversation)
            
            assert conversation.language == "en"
    
    def test_conversation_requires_user_id(self, setup_database):
        """Test that conversation requires a user_id."""
        with pytest.raises(IntegrityError):
            with get_db() as db:
                conversation = Conversation(
                    title="Test Conversation"
                )
                db.add(conversation)
                db.commit()


class TestConversationLanguageValidation:
    """Test conversation language validation."""
    
    def test_supported_languages(self, test_user):
        """Test that supported languages are accepted."""
        supported_languages = ['en', 'hi', 'ta', 'te', 'bn', 'mr', 'gu', 'kn', 'ml', 'pa']
        
        for lang in supported_languages:
            with get_db() as db:
                conversation = Conversation(
                    user_id=test_user,
                    language=lang
                )
                db.add(conversation)
                db.commit()
                db.refresh(conversation)
                
                assert conversation.language == lang
    
    def test_unsupported_language_rejected(self, test_user):
        """Test that unsupported languages are rejected."""
        with pytest.raises(ValueError, match="Unsupported language"):
            conversation = Conversation(
                user_id=test_user,
                language="fr"  # French not supported
            )


class TestMessageModelCreation:
    """Test Message model creation and field validation."""
    
    def test_create_user_message(self, test_user):
        """Test creating a user message."""
        with get_db() as db:
            conversation = Conversation(user_id=test_user)
            db.add(conversation)
            db.commit()
            db.refresh(conversation)
            
            message = Message(
                conversation_id=conversation.id,
                role="user",
                content="What are my rights if falsely accused?"
            )
            
            db.add(message)
            db.commit()
            db.refresh(message)
            
            assert message.id is not None
            assert message.conversation_id == conversation.id
            assert message.role == "user"
            assert message.content == "What are my rights if falsely accused?"
            assert message.citations is None
            assert message.confidence_score is None
            assert message.created_at is not None
    
    def test_create_assistant_message_with_citations(self, test_user):
        """Test creating an assistant message with citations and confidence."""
        with get_db() as db:
            conversation = Conversation(user_id=test_user)
            db.add(conversation)
            db.commit()
            db.refresh(conversation)
            
            citations = [
                {"source": "IPC Section 499", "text": "Defamation definition"},
                {"source": "IPC Section 500", "text": "Punishment for defamation"}
            ]
            
            message = Message(
                conversation_id=conversation.id,
                role="assistant",
                content="Based on IPC Section 499, defamation is...",
                citations=citations,
                confidence_score=0.85
            )
            
            db.add(message)
            db.commit()
            db.refresh(message)
            
            assert message.role == "assistant"
            assert message.citations == citations
            assert message.confidence_score == 0.85
    
    def test_message_requires_conversation_id(self, setup_database):
        """Test that message requires a conversation_id."""
        with pytest.raises(IntegrityError):
            with get_db() as db:
                message = Message(
                    role="user",
                    content="Test message"
                )
                db.add(message)
                db.commit()


class TestMessageRoleValidation:
    """Test message role validation."""
    
    def test_valid_roles(self, test_user):
        """Test that valid roles are accepted."""
        valid_roles = ['user', 'assistant']
        
        with get_db() as db:
            conversation = Conversation(user_id=test_user)
            db.add(conversation)
            db.commit()
            db.refresh(conversation)
            
            for role in valid_roles:
                message = Message(
                    conversation_id=conversation.id,
                    role=role,
                    content=f"Test message from {role}"
                )
                db.add(message)
                db.commit()
                db.refresh(message)
                
                assert message.role == role
    
    def test_invalid_role_rejected(self, test_user):
        """Test that invalid roles are rejected."""
        with get_db() as db:
            conversation = Conversation(user_id=test_user)
            db.add(conversation)
            db.commit()
            
            with pytest.raises(ValueError, match="Invalid role"):
                message = Message(
                    conversation_id=conversation.id,
                    role="system",  # Invalid role
                    content="Test message"
                )


class TestMessageContentValidation:
    """Test message content validation."""
    
    def test_empty_content_rejected(self, test_user):
        """Test that empty content is rejected."""
        with get_db() as db:
            conversation = Conversation(user_id=test_user)
            db.add(conversation)
            db.commit()
            
            with pytest.raises(ValueError, match="cannot be empty"):
                message = Message(
                    conversation_id=conversation.id,
                    role="user",
                    content=""
                )
    
    def test_whitespace_only_content_rejected(self, test_user):
        """Test that whitespace-only content is rejected."""
        with get_db() as db:
            conversation = Conversation(user_id=test_user)
            db.add(conversation)
            db.commit()
            
            with pytest.raises(ValueError, match="cannot be empty"):
                message = Message(
                    conversation_id=conversation.id,
                    role="user",
                    content="   "
                )
    
    def test_long_content_accepted(self, test_user):
        """Test that long content is accepted."""
        with get_db() as db:
            conversation = Conversation(user_id=test_user)
            db.add(conversation)
            db.commit()
            db.refresh(conversation)
            
            long_content = "A" * 10000  # 10,000 characters
            message = Message(
                conversation_id=conversation.id,
                role="user",
                content=long_content
            )
            
            db.add(message)
            db.commit()
            db.refresh(message)
            
            assert len(message.content) == 10000


class TestConfidenceScoreValidation:
    """Test confidence score validation."""
    
    def test_valid_confidence_scores(self, test_user):
        """Test that valid confidence scores are accepted."""
        valid_scores = [0.0, 0.5, 0.85, 1.0]
        
        with get_db() as db:
            conversation = Conversation(user_id=test_user)
            db.add(conversation)
            db.commit()
            db.refresh(conversation)
            
            for score in valid_scores:
                message = Message(
                    conversation_id=conversation.id,
                    role="assistant",
                    content="Test response",
                    confidence_score=score
                )
                db.add(message)
                db.commit()
                db.refresh(message)
                
                assert message.confidence_score == score
    
    def test_confidence_score_below_zero_rejected(self, test_user):
        """Test that confidence scores below 0.0 are rejected."""
        with get_db() as db:
            conversation = Conversation(user_id=test_user)
            db.add(conversation)
            db.commit()
            
            with pytest.raises(ValueError, match="between 0.0 and 1.0"):
                message = Message(
                    conversation_id=conversation.id,
                    role="assistant",
                    content="Test response",
                    confidence_score=-0.1
                )
    
    def test_confidence_score_above_one_rejected(self, test_user):
        """Test that confidence scores above 1.0 are rejected."""
        with get_db() as db:
            conversation = Conversation(user_id=test_user)
            db.add(conversation)
            db.commit()
            
            with pytest.raises(ValueError, match="between 0.0 and 1.0"):
                message = Message(
                    conversation_id=conversation.id,
                    role="assistant",
                    content="Test response",
                    confidence_score=1.5
                )
    
    def test_null_confidence_score_accepted(self, test_user):
        """Test that null confidence score is accepted."""
        with get_db() as db:
            conversation = Conversation(user_id=test_user)
            db.add(conversation)
            db.commit()
            db.refresh(conversation)
            
            message = Message(
                conversation_id=conversation.id,
                role="user",
                content="Test message",
                confidence_score=None
            )
            
            db.add(message)
            db.commit()
            db.refresh(message)
            
            assert message.confidence_score is None


class TestRelationships:
    """Test relationships between User, Conversation, and Message models."""
    
    def test_user_to_conversations_relationship(self, test_user):
        """Test one-to-many relationship from User to Conversations."""
        with get_db() as db:
            user = db.query(User).filter(User.id == test_user).first()
            
            # Create multiple conversations
            conv1 = Conversation(user_id=user.id, title="Conversation 1")
            conv2 = Conversation(user_id=user.id, title="Conversation 2")
            
            db.add_all([conv1, conv2])
            db.commit()
            
            # Refresh user to load relationships
            db.refresh(user)
            
            assert len(user.conversations) == 2
            assert conv1 in user.conversations
            assert conv2 in user.conversations
    
    def test_conversation_to_messages_relationship(self, test_user):
        """Test one-to-many relationship from Conversation to Messages."""
        with get_db() as db:
            conversation = Conversation(user_id=test_user)
            db.add(conversation)
            db.commit()
            db.refresh(conversation)
            
            # Create multiple messages
            msg1 = Message(
                conversation_id=conversation.id,
                role="user",
                content="First message"
            )
            msg2 = Message(
                conversation_id=conversation.id,
                role="assistant",
                content="Response to first message"
            )
            msg3 = Message(
                conversation_id=conversation.id,
                role="user",
                content="Follow-up question"
            )
            
            db.add_all([msg1, msg2, msg3])
            db.commit()
            
            # Refresh conversation to load relationships
            db.refresh(conversation)
            
            assert len(conversation.messages) == 3
            assert msg1 in conversation.messages
            assert msg2 in conversation.messages
            assert msg3 in conversation.messages
    
    def test_message_to_conversation_relationship(self, test_user):
        """Test many-to-one relationship from Message to Conversation."""
        with get_db() as db:
            conversation = Conversation(user_id=test_user, title="Test Conversation")
            db.add(conversation)
            db.commit()
            db.refresh(conversation)
            
            message = Message(
                conversation_id=conversation.id,
                role="user",
                content="Test message"
            )
            db.add(message)
            db.commit()
            db.refresh(message)
            
            assert message.conversation is not None
            assert message.conversation.id == conversation.id
            assert message.conversation.title == "Test Conversation"


class TestCascadeDeletion:
    """Test cascade deletion behavior."""
    
    def test_delete_user_cascades_to_conversations(self, test_user):
        """Test that deleting a user deletes their conversations."""
        with get_db() as db:
            # Create conversations
            conv1 = Conversation(user_id=test_user, title="Conv 1")
            conv2 = Conversation(user_id=test_user, title="Conv 2")
            db.add_all([conv1, conv2])
            db.commit()
            
            conv1_id = conv1.id
            conv2_id = conv2.id
        
        # Delete user
        with get_db() as db:
            user = db.query(User).filter(User.id == test_user).first()
            db.delete(user)
            db.commit()
        
        # Verify conversations are deleted
        with get_db() as db:
            conversations = db.query(Conversation).filter(
                Conversation.id.in_([conv1_id, conv2_id])
            ).all()
            assert len(conversations) == 0
    
    def test_delete_conversation_cascades_to_messages(self, test_user):
        """Test that deleting a conversation deletes its messages."""
        with get_db() as db:
            conversation = Conversation(user_id=test_user)
            db.add(conversation)
            db.commit()
            db.refresh(conversation)
            
            # Create messages
            msg1 = Message(conversation_id=conversation.id, role="user", content="Msg 1")
            msg2 = Message(conversation_id=conversation.id, role="assistant", content="Msg 2")
            db.add_all([msg1, msg2])
            db.commit()
            
            msg1_id = msg1.id
            msg2_id = msg2.id
            conversation_id = conversation.id
        
        # Delete conversation
        with get_db() as db:
            conversation = db.query(Conversation).filter(
                Conversation.id == conversation_id
            ).first()
            db.delete(conversation)
            db.commit()
        
        # Verify messages are deleted
        with get_db() as db:
            messages = db.query(Message).filter(
                Message.id.in_([msg1_id, msg2_id])
            ).all()
            assert len(messages) == 0
    
    def test_delete_user_cascades_to_messages(self, test_user):
        """Test that deleting a user deletes all conversations and messages."""
        with get_db() as db:
            # Create conversation with messages
            conversation = Conversation(user_id=test_user)
            db.add(conversation)
            db.commit()
            db.refresh(conversation)
            
            msg1 = Message(conversation_id=conversation.id, role="user", content="Msg 1")
            msg2 = Message(conversation_id=conversation.id, role="assistant", content="Msg 2")
            db.add_all([msg1, msg2])
            db.commit()
            
            msg1_id = msg1.id
            msg2_id = msg2.id
        
        # Delete user
        with get_db() as db:
            user = db.query(User).filter(User.id == test_user).first()
            db.delete(user)
            db.commit()
        
        # Verify messages are deleted
        with get_db() as db:
            messages = db.query(Message).filter(
                Message.id.in_([msg1_id, msg2_id])
            ).all()
            assert len(messages) == 0


class TestConversationContextPreservation:
    """Test conversation context preservation (Requirement 1.6)."""
    
    def test_messages_ordered_by_creation_time(self, test_user):
        """Test that messages are ordered by creation time."""
        with get_db() as db:
            conversation = Conversation(user_id=test_user)
            db.add(conversation)
            db.commit()
            db.refresh(conversation)
            
            # Create messages in order
            msg1 = Message(conversation_id=conversation.id, role="user", content="First")
            db.add(msg1)
            db.commit()
            
            msg2 = Message(conversation_id=conversation.id, role="assistant", content="Second")
            db.add(msg2)
            db.commit()
            
            msg3 = Message(conversation_id=conversation.id, role="user", content="Third")
            db.add(msg3)
            db.commit()
            
            # Refresh conversation to load messages
            db.refresh(conversation)
            
            # Verify messages are in correct order
            assert len(conversation.messages) == 3
            assert conversation.messages[0].content == "First"
            assert conversation.messages[1].content == "Second"
            assert conversation.messages[2].content == "Third"
    
    def test_retrieve_full_conversation_history(self, test_user):
        """Test retrieving full conversation history with all messages."""
        with get_db() as db:
            conversation = Conversation(user_id=test_user, title="Legal Consultation")
            db.add(conversation)
            db.commit()
            db.refresh(conversation)
            
            # Simulate a multi-turn conversation
            messages_data = [
                ("user", "What is defamation?"),
                ("assistant", "Defamation is defined in IPC Section 499...", 0.9),
                ("user", "What are the penalties?"),
                ("assistant", "IPC Section 500 prescribes punishment...", 0.85),
                ("user", "Can I file a counter-case?"),
                ("assistant", "Yes, you can file a counter-case if...", 0.75)
            ]
            
            for msg_data in messages_data:
                if len(msg_data) == 2:
                    role, content = msg_data
                    message = Message(
                        conversation_id=conversation.id,
                        role=role,
                        content=content
                    )
                else:
                    role, content, confidence = msg_data
                    message = Message(
                        conversation_id=conversation.id,
                        role=role,
                        content=content,
                        confidence_score=confidence
                    )
                db.add(message)
            
            db.commit()
            db.refresh(conversation)
            
            # Verify all messages are preserved
            assert len(conversation.messages) == 6
            
            # Verify conversation context is maintained
            assert conversation.messages[0].role == "user"
            assert conversation.messages[1].role == "assistant"
            assert conversation.messages[1].confidence_score == 0.9
            assert conversation.messages[2].role == "user"
            assert "penalties" in conversation.messages[2].content


class TestModelRepresentations:
    """Test string representations of models."""
    
    def test_conversation_repr(self, test_user):
        """Test Conversation string representation."""
        with get_db() as db:
            conversation = Conversation(
                user_id=test_user,
                title="Test Conversation"
            )
            db.add(conversation)
            db.commit()
            db.refresh(conversation)
            
            repr_str = repr(conversation)
            assert "Conversation" in repr_str
            assert str(conversation.id) in repr_str
            assert str(test_user) in repr_str
            assert "Test Conversation" in repr_str
    
    def test_message_repr(self, test_user):
        """Test Message string representation."""
        with get_db() as db:
            conversation = Conversation(user_id=test_user)
            db.add(conversation)
            db.commit()
            db.refresh(conversation)
            
            message = Message(
                conversation_id=conversation.id,
                role="user",
                content="This is a test message with some content"
            )
            db.add(message)
            db.commit()
            db.refresh(message)
            
            repr_str = repr(message)
            assert "Message" in repr_str
            assert str(message.id) in repr_str
            assert "user" in repr_str
            assert "This is a test message" in repr_str
    
    def test_message_repr_truncates_long_content(self, test_user):
        """Test that Message repr truncates long content."""
        with get_db() as db:
            conversation = Conversation(user_id=test_user)
            db.add(conversation)
            db.commit()
            db.refresh(conversation)
            
            long_content = "A" * 100
            message = Message(
                conversation_id=conversation.id,
                role="user",
                content=long_content
            )
            db.add(message)
            db.commit()
            db.refresh(message)
            
            repr_str = repr(message)
            # Should be truncated to 50 chars + "..."
            assert len(repr_str) < len(long_content) + 50
            assert "..." in repr_str


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
