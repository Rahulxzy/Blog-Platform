# Blog Platform

A backend-focused blog platform built with FastAPI, featuring user authentication, post management, comments, and authorization.

## Overview

Blog Platform is a REST API built with FastAPI that allows users to register, authenticate, and manage blog posts. The project also includes authorization, comments, pagination, search, and sorting.

## Features

- User registration and login
- JWT-based authentication
- Authorization for post updates and deletion
- Create, read, update, and delete posts
- Pagination for posts
- Search posts by title
- Sort posts by latest or oldest
- Comments on posts

## Tech Stack

### Backend
- Python
- FastAPI
- SQLAlchemy
- Pydantic
- Pydantic Settings

### Authentication
- JWT
- OAuth2 Password Bearer
- Passlib
- python-jose

### Database
- SQLite

### Tooling
- uv

## Project Structure

```text
app/
├── auth.py          # User registration and login endpoints
├── comments.py      # Comment-related endpoints
├── config.py        # Application configuration and environment variables
├── database.py      # Database engine, session, and dependency setup
├── main.py          # FastAPI application entry point
├── models.py        # SQLAlchemy database models and relationships
├── posts.py         # Post-related endpoints
├── schemas.py       # Pydantic request and response schemas
├── security.py      # JWT token creation, verification, and authentication
├── utils.py         # Password hashing and verification utilities
└── __init__.py      # Python package initializer
```

## Getting Started

### Prerequisites

Make sure you have the following installed:

- Python 3.10 or higher
- uv

### Installation

Clone the repository:

```bash
git clone https://github.com/Rahulxzy/Blog-Platform.git
cd Blog-Platform
```

Install the project dependencies:

```bash
uv sync
```

### Environment Variables

Create a .env file in the project root directory and add:

```env
SECRET_KEY=your-secret-key
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
DATABASE_URL=sqlite:///./blog.db
```

> Keep your actual SECRET_KEY private and never commit the `.env` file to Git.

### Running the Application

Start the development server:

```bash
uv run fastapi dev app/main.py
```

The API will be available at:

`http://127.0.0.1:8000`

Interactive API documentation is available at:

`http://127.0.0.1:8000/docs`

## API Endpoints

### Authentication

| Method | Endpoint | Authentication | Description |
|--------|----------|----------------|-------------|
| POST | `/register` | No | Register a new user |
| POST | `/auth/login` | No | Authenticate a user and receive a JWT access token |
| GET | `/me` | Bearer Token | Get the currently authenticated user |

### Posts

| Method | Endpoint | Authentication | Description |
|--------|----------|----------------|-------------|
| POST | `/posts` | Bearer Token | Create a new post |
| GET | `/posts` | No | Get posts with pagination, title search, and sorting |
| GET | `/posts/{post_id}` | No | Get a post with its comments |
| PUT | `/posts/{post_id}` | Bearer Token | Update your own post |
| DELETE | `/posts/{post_id}` | Bearer Token | Delete your own post |

### Comments

| Method | Endpoint | Authentication | Description |
|--------|----------|----------------|-------------|
| POST | `/posts/{post_id}/comments` | Bearer Token | Add a comment to a post |
| GET | `/posts/{post_id}/comments` | No | Get comments for a post |
| PUT | `/comments/{comment_id}` | Bearer Token | Update your own comment |
| DELETE | `/comments/{comment_id}` | Bearer Token | Delete your own comment |

## Authentication

This API uses JWT (JSON Web Tokens) for authentication.

### Authentication Flow

1. Register a new user using `POST /register`.
2. Login using `POST /auth/login` with your email and password.
3. The login endpoint returns an access token.
4. Use the token in the `Authorization` header for protected endpoints.

Example:

```text
Authorization: Bearer <access_token>
```

Protected endpoints require a valid Bearer token.

### Example Login Response

```json
{
  "access_token": "<access_token>",
  "token_type": "bearer"
}
```

## Future Improvements

- Add PostgreSQL support
- Add database migrations with Alembic
- Add automated tests with Pytest
- Add Docker support
- Add CI/CD with GitHub Actions
- Add refresh token support
- Add user profile management

## Contributing

Contributions are welcome.

1. Fork the repository.
2. Create a new branch for your changes.
3. Make your changes and test them locally.
4. Commit your changes with a clear commit message.
5. Push your branch and open a pull request.