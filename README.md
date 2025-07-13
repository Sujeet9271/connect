# User Connection Platform

A Django-based platform for user registration, authentication, real-time connection requests, and asynchronous notifications. The system supports JWT-based login, Redis caching, Celery background tasks, and PostgreSQL for data persistence.

## ✨ Features

- User Registration and JWT Authentication
- 15-minute inactivity timeout for login sessions
- User-to-user connection request system:
  - Send, Accept, Reject requests
  - Prevent duplicate or pending requests
- Asynchronous notification system using Celery
- Real-time updates and background job handling
- Redis for caching and Celery message brokering

## 🚀 Tech Stack

- **Backend**: Django 5.2, Django REST Framework
- **Authentication**: JWT (via SimpleJWT)
- **Task Queue**: Celery
- **Broker**: Redis
- **Database**: Sqlite
- **Deployment**: Docker, Docker Compose

## ⚙️ Installation

```bash
# Clone the repository
git clone https://github.com/Sujeet/connect.git
cd connect

# first of all install uv
pip install uv

# Create a virtual environment
uv venv venv
source venv/bin/activate

# Install dependencies
uv pip compile requirements.txt --output-file=requirements.lock
uv pip sync requirements.lock

# Configure your .env from .env.example

# Run migrations
python manage.py makemigrations
python manage.py migrate

# Create a superuser
python manage.py createsuperuser

# Start the development server
python manage.py runserver


# If using docker, simply build the containers after configuring .env
docker compose up -d --build
