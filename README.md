# Advanced REST API with Elasticsearch Integration

A robust REST API implementation that handles structured JSON data with advanced features including Elasticsearch integration, message queuing, and security mechanisms.

## Features

### Core REST API Capabilities
- **CRUD Operations**: Full support for Create, Read, Update, and Delete operations
- **JSON Schema Validation**: Incoming payloads are validated against defined JSON schemas
- **Conditional Operations**: 
  - Conditional read support using ETags
  - Optimistic concurrency control
- **PATCH Support**: Partial updates with merge capabilities
- **Structured Data Handling**: Flexible handling of any structured JSON data

### Advanced Features
- **Elasticsearch Integration**:
  - Parent-Child relationship indexing
  - Advanced search capabilities
  - Document mapping and indexing
- **Message Queuing**:
  - Asynchronous processing with RabbitMQ
  - Event-driven architecture
  - Producer-Consumer pattern implementation
- **Security**:
  - Bearer token authentication
  - Request validation

### Data Storage
- **Key-Value Store**: Redis-based storage for high-performance data access
- **Elasticsearch**: Advanced search and indexing capabilities

## Technology Stack

- **Backend Framework**: Django with Django REST Framework
- **Primary Database**: Redis for high-performance key-value storage
- **Search Engine**: Elasticsearch
- **Message Queue**: RabbitMQ
- **Authentication**: Bearer token authentication
- **Containerization**: Docker & Docker Compose
- **API Documentation**: OpenAPI/Swagger

## Prerequisites

- Python 3.x
- Docker and Docker Compose
- Redis
- Elasticsearch
- RabbitMQ

## Setup Instructions

1. Clone the repository:
```bash
git clone <repository-url>
cd <repository-name>
```

2. Set up environment variables:
```bash
cp .env.example .env
# Edit .env with your configuration
```

3. Install dependencies:
```bash
pipenv install
```

4. Start the services using Docker Compose:
```bash
docker-compose up -d
```

## API Endpoints

### Plans
- `GET /api/plans/` - List all plans
- `POST /api/plans/` - Create a new plan
- `GET /api/plans/{id}/` - Retrieve a specific plan
- `PATCH /api/plans/{id}/` - Update a plan
- `DELETE /api/plans/{id}/` - Delete a plan

### Services
- `GET /api/services/` - List all services
- `POST /api/services/` - Create a new service
- `GET /api/services/{id}/` - Retrieve a specific service
- `PATCH /api/services/{id}/` - Update a service
- `DELETE /api/services/{id}/` - Delete a service

## Authentication

The API uses Bearer token authentication. To authenticate:

1. Obtain a valid token
2. Include the token in the Authorization header:
```
Authorization: Bearer <your-token>
```

## Elasticsearch Integration

The application implements parent-child relationships in Elasticsearch for efficient querying and searching. The document structure includes:

- Plans
- Services
- Member Cost Shares
- Plan Services

## Message Queueing

The application implements a producer-consumer pattern for asynchronous processing using RabbitMQ:

- **Producer**: Handles event generation and queue submission
- **Consumer**: Processes queued events asynchronously, particularly for Elasticsearch indexing

## Contributing

1. Fork the repository
2. Create your feature branch
3. Commit your changes
4. Push to the branch
5. Create a new Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- Django REST Framework
- Elasticsearch
- Redis
- RabbitMQ 
