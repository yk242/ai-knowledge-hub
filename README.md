# AI Knowledge Hub

Markdown の技術メモや議事録を管理し、生成 AI による自動要約・タグ抽出・RAG（引用元つき検索・SSE ストリーミング回答）を実現することを目指す、FastAPI ベースのバックエンドアプリケーションです。

## 技術スタック

- **Language**: Python 3.12
- **Framework**: FastAPI / Pydantic v2 / Uvicorn
- **Tooling**: uv / Ruff / Pyright / pytest
- **Planned**: PostgreSQL + `pgvector` / SQLAlchemy 2.0（非同期） / Alembic / JWT 認証 / LLM API（Structured Outputs・Embedding・SSE）
