import os
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from fastapi.testclient import TestClient

from app.main import app
from app.db.base import Base
from app.db.session import get_db


# Use an in-memory SQLite database for testing
SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


# Override the get_db dependency to use the test database
@pytest.fixture
def db():
    # Create the database
    Base.metadata.create_all(bind=engine)
    
    # Create a connection to use for testing
    connection = engine.connect()
    transaction = connection.begin()
    
    # Bind an individual Session to the connection
    db = TestingSessionLocal(bind=connection)
    
    yield db
    
    # Clean up after the test
    db.close()
    transaction.rollback()
    connection.close()
    
    # Remove the test database
    Base.metadata.drop_all(bind=engine)


@pytest.fixture
def client(db):
    # Override the get_db dependency to use the test database
    def override_get_db():
        try:
            yield db
        finally:
            pass
    
    app.dependency_overrides[get_db] = override_get_db
    
    with TestClient(app) as client:
        yield client
    
    # Reset the dependency override
    app.dependency_overrides = {} 