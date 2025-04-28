import pytest
from unittest.mock import Mock, patch
from app.services.email_service import EmailService
from app.models.email import EmailSendRequest
from config import settings

@pytest.fixture
def email_service():
    with patch("app.services.email_service.EmailRepository") as MockRepo:
        mock_repo_instance = MockRepo.return_value
        mock_repo_instance.store_emails.return_value = []
        email_service = EmailService()
        email_service.token_service = Mock()
        email_service.token_service.get_access_token.return_value = "mock_token"
        return email_service

@pytest.fixture
def mock_email_request():
    return EmailSendRequest(
        to_recipients=["test@example.com"],
        subject="Test Subject",
        body="Test Body",
        is_html=False,
        cc_recipients=[],
        bcc_recipients=[]
    )

@patch('app.services.email_service.requests')
@patch('app.services.email_service.token_cache')
def test_send_email_success(mock_token_cache, mock_requests, email_service, mock_email_request):
    # Setup token and requests mock
    mock_token_cache.get_access_token.return_value = "mock_token"
    mock_response = Mock()
    mock_response.status_code = 202
    mock_requests.post.return_value = mock_response

    # Act
    result = email_service.send_email(mock_email_request)

    # Assert
    assert result == "email_sent_successfully"

@patch('app.services.email_service.requests')
@patch('app.services.email_service.token_cache')
def test_send_email_failure(mock_token_cache, mock_requests, email_service, mock_email_request):
    # Setup mocks
    mock_token_cache.get_access_token.return_value = "mock_token"
    mock_response = Mock()
    mock_response.status_code = 500
    mock_response.text = "Internal Server Error"
    mock_requests.post.return_value = mock_response

    # Act & Assert
    with pytest.raises(Exception) as exc_info:
        email_service.send_email(mock_email_request)
    assert "Failed to send email" in str(exc_info.value)

@patch('app.services.email_service.requests')
@patch('app.services.email_service.token_cache')
def test_retrieve_emails_success(mock_token_cache, mock_requests, email_service):
    # Setup mocks
    mock_token_cache.get_access_token.return_value = "mock_token"
    mock_response = Mock()
    mock_response.status_code = 200
    mock_response.json.return_value = {"value": []}
    mock_requests.get.return_value = mock_response

    # Act
    result = email_service.retrieve_emails()

    # Assert
    assert result == []
    mock_requests.get.assert_called_once()

@patch('app.services.email_service.requests')
@patch('app.services.email_service.token_cache')
def test_retrieve_emails_failure(mock_token_cache, mock_requests, email_service):
    # Setup mocks
    mock_token_cache.get_access_token.return_value = "mock_token"
    mock_response = Mock()
    mock_response.status_code = 500
    mock_response.text = "Internal Server Error"
    mock_requests.get.return_value = mock_response

    # Act & Assert
    with pytest.raises(Exception) as exc_info:
        email_service.retrieve_emails()
    assert "Failed to retrieve emails" in str(exc_info.value)
