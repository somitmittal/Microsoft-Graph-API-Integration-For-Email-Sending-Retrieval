import pytest
from unittest.mock import Mock, patch

from app.repositories.email_repository import EmailRepository
from app.models.email import EmailDB

@pytest.fixture
def mock_collection():
    return Mock()

@pytest.fixture
def email_repository(mock_collection):
    with patch('app.repositories.email_repository.get_email_collection', return_value=mock_collection):
        repo = EmailRepository()
        return repo

def test_store_emails(email_repository, mock_collection):
    test_emails = [{
        "id": "test_id",
        "subject": "Test Subject",
        "sender": {"emailAddress": {"address": "sender@test.com"}},
        "toRecipients": [{"emailAddress": {"address": "recipient@test.com"}}],
        "ccRecipients": [],
        "bccRecipients": [],
        "body": {"content": "Test Body", "contentType": "text"},
        "receivedDateTime": "2023-01-01T00:00:00Z"
    }]
    # Test
    result = email_repository.store_emails(test_emails)
    # Assertions
    assert len(result) == 1
    mock_collection.insert_many.assert_called_once()

def test_store_emails_with_multiple_emails(email_repository, mock_collection):
    test_emails = [
        {
            "id": "test_id_1",
            "subject": "Test Subject 1",
            "sender": {"emailAddress": {"address": "sender1@test.com"}},
            "toRecipients": [{"emailAddress": {"address": "recipient1@test.com"}}],
            "body": {"content": "Test Body 1", "contentType": "text"},
            "receivedDateTime": "2023-01-01T00:00:00Z"
        },
        {
            "id": "test_id_2",
            "subject": "Test Subject 2",
            "sender": {"emailAddress": {"address": "sender2@test.com"}},
            "toRecipients": [{"emailAddress": {"address": "recipient2@test.com"}}],
            "body": {"content": "Test Body 2", "contentType": "text"},
            "receivedDateTime": "2023-01-01T00:00:00Z"
        }
    ]
    # Test
    result = email_repository.store_emails(test_emails)
    # Assertions
    assert len(result) == 2
    mock_collection.insert_many.assert_called_once()

def test_store_emails_failure(email_repository, mock_collection):
    mock_collection.insert_many.side_effect = Exception("Database error")
    test_emails = [{
        "id": "test_id",
        "subject": "Test Subject",
        "sender": {"emailAddress": {"address": "sender@test.com"}},
        "toRecipients": [{"emailAddress": {"address": "recipient@test.com"}}],
        "body": {"content": "Test Body", "contentType": "text"},
        "receivedDateTime": "2023-01-01T00:00:00Z"
    }]
    # Test and assert exception
    with pytest.raises(Exception) as exc_info:
        email_repository.store_emails(test_emails)
    assert "Database error" in str(exc_info.value)