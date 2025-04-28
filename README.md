# Microsoft Graph API Integration for Email Sending and Retrieval

This project implements a Python-based service that integrates with Microsoft Graph API to send emails and periodically retrieve new emails, storing them in a MongoDB database.

## Features

- Send emails via Microsoft Graph API
- Automatically retrieve new emails from the past 24 hours
- Store email data in MongoDB
- Scheduled email retrieval without manual triggers

## Project Structure

```
.
├── README.md
├── .env.example
├── .gitignore
├── requirements.txt         # Python dependencies
├── main.py                  # Main application entry point
├── config.py                # Configuration and environment variables
├── exceptions.py            # Exception Handler
├── Dockerfile               # Dockerfile for containerization
├── docker-compose.yml       # Docker Compose configuration
└── app/
    ├── __init__.py
    ├── api/                # API endpoints
    │   ├── __init__.py
    │   └── routes.py       # API route definitions
    ├── db/                 # Database Setup
    │   ├── __init__.py
    │   └── mongodb.py      # MongoDB Setup 
    ├── models/             # Database models
    │   ├── __init__.py
    │   └── email.py        # Email model definition
    ├── repositories/       # Repositories
    │   ├── __init__.py
    │   └── email_repository.py   # Email Repository
    ├── schedulers/         # Schedulers
    │   ├── __init__.py
    │   └── scheduler.py    # Email retrieval scheduler
    └── services/           # Business logic
        ├── __init__.py
        ├── token_service.py # Microsoft Graph API token integration
        └── email_service.py # Microsoft Graph API email operations
```

## Setup Instructions

### Prerequisites

- Python 3.8+
- MongoDB (local installation or cloud instance) You can use [MongoDB Compass](https://www.mongodb.com/try/download/compass)
- Microsoft Outlook account
- Microsoft Entra ID app registration

### Microsoft Graph API Setup

1. Create a free Outlook account if you don't have one
2. Register an application in the Microsoft Entra ID portal:
   - Go to [Azure Portal](https://portal.azure.com)
   - Navigate to "Microsoft Entra ID" > "App registrations" > "New registration"
   - Name your application
   - Set the redirect URI to `http://localhost:8000/auth/callback`
   - Grant the following API permissions:
     - Mail.Read
     - Mail.Send
     - User.Read
   - Create a client secret

### Installation

1. Clone the repository
2. Create a virtual environment:
   ```
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```
3. Install dependencies:
   ```
   pip install -r requirements.txt
   ```
4. Copy `.env.example` to `.env` and fill in your credentials:
   ```
   cp .env.example .env
   ```

### Environment Variables

Create a `.env` file with the following variables:

```
MONGODB_URI=mongodb://mongodb:27017
CLIENT_ID=your_client_id
CLIENT_SECRET=your_client_secret
TENANT_ID=your_tenant_id
USER_EMAIL=your_outlook_email
SCHEDULE_INTERVAL=60  # Seconds between email retrievals
MAIL_SCOPES=User.Read Mail.Read Mail.Send
```

## Running the Application

1. Start the application:
   ```
   uvicorn main:app --reload
   ```
2. The API will be available at `http://localhost:8000`
3. The email retrieval scheduler will start automatically

## API Endpoints

### Send Email

```
POST /email/send
```

Request body:
```json
{
  "recipient": "recipient@example.com",
  "subject": "Test Email",
  "body": "This is a test email sent via Microsoft Graph API",
  "attachments": []  // Optional
}
```

### Manually Trigger Email Retrieval

```
POST /email/retrieve
```

<!-- ## How I Used AI Coding Tools

During the development of this project, I utilized several AI coding tools to enhance productivity and code quality:

1. **GitHub Copilot**: Used for code completion, especially for repetitive patterns in API routes and MongoDB schema definitions.

2. **ChatGPT**: Leveraged for:
   - Generating the initial project structure
   - Debugging authentication issues with Microsoft Graph API
   - Creating documentation templates
   - Optimizing MongoDB queries

3. **Cursor AI**: Used for refactoring code and suggesting improvements to error handling patterns.

These tools significantly accelerated development while maintaining code quality. All AI-generated code was reviewed and modified as needed to ensure it met project requirements and followed best practices. -->

## Testing

To test the application:

1. Send an email using the `/email/send` endpoint
2. Wait for the scheduled retrieval or manually trigger it with `/email/retrieve`
3. Check the MongoDB database for stored emails

## Security Considerations

- All sensitive information is stored in environment variables
- No credentials are committed to the repository
- Token cache and refresh is handled automatically

## Future Improvements

- Add unit and integration tests
- Add support for email filtering and search
- Improve error handling and retry mechanisms