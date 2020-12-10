from typing import Dict, Generator

import pytest
from fastapi.testclient import TestClient

from app.core.config import settings
from app.main import app


@pytest.fixture(scope="module")
def client() -> Generator:
    with TestClient(app) as c:
        yield c


@pytest.fixture(scope="module")
def api_key_headers(client: TestClient) -> Dict[str, str]:
    return {"X-API-KEY": settings.SECRET_KEY}
