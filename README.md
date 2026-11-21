# AI Knowledge Hub

Markdown の技術メモや議事録を管理し、生成 AI による自動要約・タグ抽出・RAG（引用元つき検索・SSE ストリーミング回答）を実現することを目指す、FastAPI ベースのバックエンドアプリケーションです。

## 技術スタック

- **Language**: Python 3.12
- **Framework**: FastAPI / Pydantic v2 / Uvicorn
- **Tooling**: uv / Ruff / Pyright / pytest
- **Planned**: PostgreSQL + `pgvector` / SQLAlchemy 2.0（非同期） / Alembic / JWT 認証 / LLM API（Structured Outputs・Embedding・SSE）

## 現在の実装状況

- [x] 開発・品質チェック基盤（`uv` / `ruff` / `pyright` / `pytest`）
- [ ] ドキュメント管理 REST API（インメモリ CRUD・タグ検索・ページネーション・Pydantic バリデーション）
- [ ] 自動テスト（`pytest` + `TestClient`）
- [ ] レイヤード設計への分割・DI（`Protocol` + `Depends`）・例外ハンドリング分離
- [ ] PostgreSQL + SQLAlchemy 2.0 + Alembic による永続化
- [ ] JWT 認証・認可・設定管理・構造化ログ
- [ ] 生成 AI 連携（自動要約・タグ抽出・`pgvector` RAG・SSE ストリーミング）

## セットアップ・起動

```bash
# 依存関係のインストール
uv sync

# 開発サーバー起動（Swagger UI: http://127.0.0.1:8000/docs）
uv run uvicorn practice.main:app --reload
```

## 静的解析

```bash
uv run ruff check .
uv run pyright
```
