import pytest
from fastapi.testclient import TestClient
from sqlalchemy.pool import StaticPool
from sqlalchemy import create_engine, inspect
from sqlalchemy.orm import sessionmaker

from protoapp.main import app, get_db_session
from protoapp.db import Base

engine = create_engine("sqlite:///:memory:", 
                        connect_args={"check_same_thread": False},
                        poolclass=StaticPool)

Base.metadata.create_all(bind=engine)

TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

@pytest.fixture
def test_db_session():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()

@pytest.fixture(scope="function")
def test_client(test_db_session):
    client = TestClient(app)
    app.dependency_overrides[get_db_session] = (lambda: test_db_session)
    
    return client