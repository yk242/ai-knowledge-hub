from datetime import UTC, datetime
from uuid import UUID, uuid4

from fastapi import FastAPI, HTTPException, Query
from pydantic import BaseModel, Field, field_validator

app = FastAPI(title="AI Knowledge Hub")


class DocumentCreate(BaseModel):
    title: str = Field(min_length=1, max_length=200)
    content: str = Field(min_length=1, max_length=50000)
    tags: list[str] = Field(default_factory=list, max_length=10)

    @field_validator("title")
    @classmethod
    def title_must_not_be_blank(cls, v: str) -> str:
        stripped = v.strip()
        if not stripped:
            raise ValueError("title must not be blank")
        return stripped

    @field_validator("tags")
    @classmethod
    def tags_trim_and_lower_and_unique(cls, tags: list[str]) -> list[str]:
        result = []
        for tag in tags:
            cleaned = tag.strip().lower()
            if cleaned:
                result.append(cleaned)
        return list(dict.fromkeys(result))


class DocumentUpdate(BaseModel):
    title: str | None = Field(default=None, min_length=1, max_length=200)
    content: str | None = Field(default=None, min_length=1, max_length=50000)
    tags: list[str] | None = Field(default=None, max_length=10)

    @field_validator("title")
    @classmethod
    def title_must_not_be_blank(cls, v: str | None) -> str | None:
        if v is None:
            return None
        stripped = v.strip()
        if not stripped:
            raise ValueError("title must not be blank")
        return stripped

    @field_validator("tags")
    @classmethod
    def tags_trim_and_lower_and_unique(cls, tags: list[str] | None) -> list[str] | None:
        if tags is None:
            return None
        result = []
        for tag in tags:
            cleaned = tag.strip().lower()
            if cleaned:
                result.append(cleaned)
        return list(dict.fromkeys(result))


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
def list_documents(
    tag: str | None = None,
    limit: int = Query(default=20, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
) -> list[DocumentResponse]:
    items = list(documents.values())
    if tag is not None:
        items = [d for d in items if tag.strip().lower() in d.tags]
    return items[offset : offset + limit]


@app.get("/api/v1/documents/{doc_id}", response_model=DocumentResponse)
def get_doc(doc_id: UUID) -> DocumentResponse:
    document = documents.get(doc_id)
    if document is None:
        raise HTTPException(status_code=404, detail="Document not found")
    return document


@app.delete("/api/v1/documents/{doc_id}", status_code=204)
def delete_doc(doc_id: UUID) -> None:
    if doc_id not in documents:
        raise HTTPException(status_code=404, detail="Document not found")
    del documents[doc_id]


@app.patch("/api/v1/documents/{doc_id}", response_model=DocumentResponse)
def update_doc(doc_id: UUID, body: DocumentUpdate) -> DocumentResponse:
    document = documents.get(doc_id)
    if document is None:
        raise HTTPException(status_code=404, detail="Document not found")
    updates = body.model_dump(exclude_unset=True, exclude_none=True)
    updates["updated_at"] = datetime.now(UTC)
    updated = document.model_copy(update=updates)
    documents[doc_id] = updated
    return updated


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}
