from collections.abc import Iterator
from datetime import datetime
from typing import Any
from uuid import uuid4

import pytest
from fastapi.testclient import TestClient

from practice.main import app, documents


@pytest.fixture(autouse=True)
def clear_documents() -> None:
    documents.clear()


@pytest.fixture
def client() -> Iterator[TestClient]:
    with TestClient(app) as client:
        yield client


def test_health(client: TestClient) -> None:
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"


def test_create_document(client: TestClient) -> None:
    data = _create_document(
        client,
        title=" Test doc ",
        content="This is test doc",
        tags=[" Test ", "test", " "],
    )
    required_fields = ["id", "created_at", "updated_at"]
    for field in required_fields:
        assert field in data
    assert data["title"] == "Test doc"
    assert data["tags"] == ["test"]


def test_get_document(client: TestClient) -> None:
    data = _create_document(client)
    doc_id = data["id"]
    response = client.get(f"/api/v1/documents/{doc_id}")
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == doc_id
    assert data["title"] == "Test doc"
    assert data["content"] == "This is test doc"
    assert data["tags"] == ["test"]


def test_search_documents(client: TestClient) -> None:
    _create_document(
        client, title="Test1", content="This is first doc", tags=["java", "python"]
    )
    _create_document(
        client, title="Test2", content="This is second doc", tags=["api", "web"]
    )
    _create_document(
        client, title="Test3", content="This is third doc", tags=["java", "rust"]
    )
    _create_document(
        client, title="Test4", content="This is fourth doc", tags=["c++", "java"]
    )
    response = client.get(
        "/api/v1/documents", params={"tag": " Java", "limit": "1", "offset": "1"}
    )
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["title"] == "Test3"
    assert data[0]["content"] == "This is third doc"
    assert data[0]["tags"] == ["java", "rust"]


def test_update_document(client: TestClient) -> None:
    data = _create_document(client)
    doc_id = data["id"]
    created_at = data["created_at"]
    response = client.patch(f"/api/v1/documents/{doc_id}", json={"title": "New doc"})
    assert response.status_code == 200
    updated = response.json()
    assert updated["title"] == "New doc"
    assert updated["content"] == "This is test doc"
    assert updated["tags"] == ["test"]
    assert updated["created_at"] == created_at
    assert datetime.fromisoformat(updated["updated_at"]) > datetime.fromisoformat(
        created_at
    )

    response = client.patch(f"/api/v1/documents/{doc_id}", json={"tags": []})
    assert response.status_code == 200
    updated = response.json()
    assert updated["tags"] == []


def test_delete_document(client: TestClient) -> None:
    data = _create_document(client)
    doc_id = data["id"]
    response = client.delete(f"/api/v1/documents/{doc_id}")
    assert response.status_code == 204
    response = client.get(f"/api/v1/documents/{doc_id}")
    assert response.status_code == 404


@pytest.mark.parametrize(
    ("method", "json_body"),
    [
        ("GET", None),
        ("PATCH", {"title": "New Title"}),
        ("DELETE", None),
    ],
    ids=["GET", "PATCH", "DELETE"],
)
def test_nonexistent_id(
    client: TestClient,
    method: str,
    json_body: dict[str, object] | None,
) -> None:
    response = client.request(method, f"/api/v1/documents/{uuid4()}", json=json_body)
    assert response.status_code == 404


@pytest.mark.parametrize(
    ("method", "json_body"),
    [
        ("GET", None),
        ("PATCH", {"title": "New Title"}),
        ("DELETE", None),
    ],
    ids=["GET", "PATCH", "DELETE"],
)
def test_invalid_id(
    client: TestClient,
    method: str,
    json_body: dict[str, object] | None,
) -> None:
    response = client.request(method, "/api/v1/documents/not-a-uuid", json=json_body)
    assert response.status_code == 422


@pytest.mark.parametrize(
    "params",
    [{"limit": 0}, {"limit": 101}, {"offset": -1}],
)
def test_search_documents_validation_error(
    client: TestClient, params: dict[str, int]
) -> None:
    response = client.get("/api/v1/documents", params=params)
    assert response.status_code == 422


@pytest.mark.parametrize(
    "payload",
    [
        {"title": "", "content": "test doc", "tags": ["test"]},
        {"title": " ", "content": "test doc", "tags": ["test"]},
        {"title": "a" * 201, "content": "test doc", "tags": ["test"]},
        {"title": "test", "content": "", "tags": ["test"]},
        {"title": "test", "content": "a" * 50001, "tags": ["test"]},
        {"title": "test", "content": "test doc", "tags": ["test"] * 11},
    ],
)
def test_create_document_validation_error(
    client: TestClient, payload: dict[str, object]
) -> None:
    response = client.post("/api/v1/documents", json=payload)
    assert response.status_code == 422


@pytest.mark.parametrize(
    "payload",
    [
        {"title": ""},
        {"title": " "},
        {"title": "a" * 201},
        {"content": ""},
        {"content": "a" * 50001},
        {"tags": ["test"] * 11},
    ],
)
def test_update_document_validation_error(
    client: TestClient, payload: dict[str, object]
) -> None:
    data = _create_document(client)
    doc_id = data["id"]

    response = client.patch(f"/api/v1/documents/{doc_id}", json=payload)
    assert response.status_code == 422


def _create_document(
    client: TestClient,
    *,
    title: str = "Test doc",
    content: str = "This is test doc",
    tags: list[str] | None = None,
) -> dict[str, Any]:
    response = client.post(
        "/api/v1/documents",
        json={
            "title": title,
            "content": content,
            "tags": ["test"] if tags is None else tags,
        },
    )
    assert response.status_code == 201
    return response.json()
