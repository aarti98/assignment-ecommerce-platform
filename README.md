# E-Commerce Platform RESTful API

A production-grade RESTful API for an e-commerce platform built with FastAPI, SQLAlchemy, and Docker.

## Features

- Product management (create, read)
- Order processing with stock validation
- Comprehensive error handling
- Unit and integration tests
- Dockerized for easy deployment

## Tech Stack

- **FastAPI**
- **SQLAlchemy**
- **Pydantic**
- **Pytest**
- **Docker**

## Project Structure

```
.
├── app/
│   ├── api/                # API endpoints
│   ├── core/               # Core functionality
│   ├── db/                 # Database models and sessions
│   ├── schemas/            # Pydantic models
│   ├── services/           # Business logic
│   └── main.py             # Application entry point
├── tests/                  # Test suite
├── .env                    # Environment variables (not in repo)
├── .gitignore              # Git ignore file
├── Dockerfile              # Docker configuration
├── docker-compose.yml      # Docker Compose configuration
├── requirements.txt        # Python dependencies
└── README.md               # Project documentation
```

## Getting Started

### Database Setup

This application uses SQLite for its database. The database files are not included in the repository and need to be created locally.

1. To create the main database:
   ```
   python -c "from app.db.init_db import create_tables; create_tables()"
   ```

2. This will create `ecommerce.db` in the project root directory.

3. For testing, a separate test database will be created automatically when running the tests.

**Note**: Database files (*.db) are intentionally excluded from version control for security and collaboration reasons.

### Running with Docker

1. Clone the repository:
   ```
   git clone https://github.com/yourusername/e-commerce-platform.git
   cd e-commerce-platform
   ```

2. Build and run the Docker container:
   ```
   docker-compose up --build
   ```

3. Access the API at http://localhost:8000

4. API documentation is available at http://localhost:8000/docs

### Running Locally (Development)

1. Create a virtual environment:
   ```
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

2. Install requirements:
   ```
   pip install -r requirements.txt
   ```

3. Install the package in development mode:
   ```
   pip install -e .
   ```

4. Create the database (as described in the Database Setup section)

5. Run the application:
   ```
   uvicorn app.main:app --reload --port 8001
   ```

## API Endpoints

### Products

- `GET /products` - Retrieve all products
- `POST /products` - Create a new product

### Orders

- `POST /orders` - Place a new order
- `GET /orders/{order_id}` - Get order details

## Testing

Run tests with pytest:

```
pytest
```

For coverage report:

```
pytest --cov=app tests/
```

## Environment Variables

The following environment variables can be configured:

- `DATABASE_URL`: Database connection string
- `TESTING`: Set to "True" for testing environment
- `DEBUG`: Set to "True" for debug mode

## License

MIT