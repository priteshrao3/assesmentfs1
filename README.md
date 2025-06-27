# Book Review Service

A FastAPI service for managing books and reviews with Redis caching.

## Features
- REST API endpoints for books and reviews
- SQLite database with Alembic migrations
- Redis caching layer
- Automated testing

## Setup

### Prerequisites
- Docker and Docker Compose
- Python 3.13+

### Installation
1. Clone the repository:
   ```bash
    git clone git@github.com:priteshrao3/assesmentfs1.git

### Start services
  docker-compose up -d --build

### Run migrations
  docker-compose exec web alembic upgrade head

## API Documentation
  Access Swagger UI at http://localhost:8000/docs

Run tests with:
```bash
docker-compose exec web pytest
