from datetime import UTC, datetime
from uuid import UUID, uuid4

from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI(title="AI Knowledge Hub")


class DocumentCreate(BaseModel):
    title: str
    content: str
    tags: list[str] = []


class DocumentResponse(BaseModel):
    id: UUID
    title: str
    content: str
    tags: list[str]
    created_at: datetime
    updated_at: datetime


documents: dict[UUID, DocumentResponse] = {}


@app.post("/api/v1/documents", response_model=DocumentResponse, status_code=201)
def create_document(body: DocumentCreate) -> DocumentResponse:
    now = datetime.now(UTC)
    document = DocumentResponse(
        id=uuid4(),
        title=body.title,
        content=body.content,
        tags=body.tags,
        created_at=now,
        updated_at=now,
    )
    documents[document.id] = document
    return document


@app.get("/api/v1/documents", response_model=list[DocumentResponse])
def list_documents() -> list[DocumentResponse]:
    return list(documents.values())


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}
