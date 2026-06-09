# AI QA Service 🚀

A modular, high-performance **FastAPI REST API** for managing Questions and Answers, integrated with Retrieval-Augmented Generation (RAG). Built using clean architecture principles, modern SQLAlchemy 2.0 async operations, and Pydantic validation.

This repository serves as the technical assessment submission for the **AI Developer Trainee / Junior AI Engineer** role.

---

## 🏗️ Architecture & Features

- **Clean Architecture & Decoupled Layers**: Clearly separated layers for API routing, business services, configuration, and data models to ensure high maintainability and testability.
- **Retrieval-Augmented Generation (RAG)**: Integrates OpenAI's `text-embedding-3-small` embeddings and `gpt-4o-mini` chat completion model to deliver contextual, high-quality answers.
- **Asynchronous DB Operations**: Built with `asyncpg` and SQLAlchemy's async connection pool to prevent blocking of the FastAPI event loop during high-throughput workloads.
- **Flexible Vector Similarity Search**: Backed by PostgreSQL's `pgvector` extension. In local development or testing environments, the service includes a seamless **SQLite fallback** calculating cosine similarity in Python, allowing full out-of-the-box operation without requiring pgvector local installations.
- **Auto DDL Initialization**: Automatically creates tables and enables required database extensions (e.g. pgvector) during lifespan startup events.
- **Environment Variables Validation**: Configurations validated strictly at startup using `pydantic-settings`.

---

## 📁 Directory Structure

```
ai-qa-service/
├── app/
│   ├── main.py          # Application entrypoint & lifespan events
│   ├── core/
│   │   └── config.py    # Environment variables loading & validation
│   ├── db/
│   │   ├── base.py      # SQLAlchemy 2.0 DeclarativeBase class
│   │   └── session.py   # Async DB session maker & dependency get_db
│   ├── models/
│   │   ├── document.py  # SQLAlchemy database models for vector documents
│   │   └── qa.py        # SQLAlchemy database models for QA entries
│   ├── schemas/
│   │   ├── document.py  # Pydantic validation schemas for documents
│   │   └── qa.py        # Pydantic validation schemas for QA resources
│   ├── routes/
│   │   ├── api.py       # Main router aggregating sub-routers
│   │   ├── ask.py       # RAG-based ask router
│   │   ├── document.py  # Document upload and search router
│   │   ├── health.py    # Service health and DB verification router
│   │   └── qa.py        # Manual QA pairs router
│   └── services/
│       ├── document_service.py # Core logic for document embeddings and similarity search
│       └── qa_service.py       # Pure business logic decoupled from API handlers
├── scripts/
│   └── seed_documents.py       # Database seeding script
├── .env.example         # Template for environment configuration
├── .gitignore           # Git ignore rules
├── Dockerfile           # Docker configuration for deployment
├── docker-compose.yml   # Multi-container local orchestration (App + Postgres with pgvector)
├── README.md            # Project documentation (this file)
└── requirements.txt     # Python requirements file
```

---

## 💾 Database Schema

The service operates on three primary relational tables:

1. **`documents`**:
   - `id` (Integer, Primary Key)
   - `content` (String, Non-Nullable): Text content of the ingested knowledge segment.
   - `embedding` (Vector(1536), Nullable): Vector embedding generated from the content.

2. **`questions`**:
   - `id` (Integer, Primary Key)
   - `text` (String, Non-Nullable): Text of the question asked.
   - `created_at` (DateTime, Default: UTC Now)
   - `answers` (Relationship): Linked answers for manual QA flows.

3. **`answers`**:
   - `id` (Integer, Primary Key)
   - `question_id` (Integer, Foreign Key pointing to `questions.id`)
   - `text` (String, Non-Nullable): Generated or manually input response.
   - `created_at` (DateTime, Default: UTC Now)

---

## 🛠️ Local Setup Instructions

### 1. Prerequisites
- Python 3.10 or higher.
- A running PostgreSQL instance with the `pgvector` extension (optional; SQLite fallback works out-of-the-box for local testing).

### 2. Set Up Virtual Environment

**On Windows (PowerShell):**
```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
```

**On macOS/Linux:**
```bash
python3 -m venv venv
source venv/bin/activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Configure Environment Variables
Copy the template configuration to create your local `.env`:
```bash
cp .env.example .env
```
Ensure your `.env` contains valid configurations:
```env
# Application Configuration
APP_NAME="AI QA Service"
APP_ENV="development"
API_V1_STR="/api/v1"

# SQLite Connection for Local Setup (no pgvector required)
DATABASE_URL="sqlite+aiosqlite:///./local_dev.db"

# Or use PostgreSQL + pgvector Connection
# DATABASE_URL="postgresql+asyncpg://postgres:postgres@localhost:5432/ai_qa_db"

# OpenAI API Integration
OPENAI_API_KEY="your-openai-api-key-here"
OPENAI_MODEL="gpt-4o-mini"
```

### 5. Seed Sample Documents
Populate the database with contextual technical documentation:
```bash
python scripts/seed_documents.py
```
*(Make sure to specify a valid `OPENAI_API_KEY` to successfully generate embeddings).*

### 6. Run the Application
Start the development server using Uvicorn:
```bash
uvicorn app.main:app --reload
```
The server will start at `http://127.0.0.1:8000`.

---

## 🐳 Docker Compose (Recommended Local PostgreSQL + pgvector Setup)

Spin up the complete infrastructure—the FastAPI application and PostgreSQL with the `pgvector` extension—with a single command:

```bash
# Set your OpenAI API key in the current environment
# On Windows PowerShell:
$env:OPENAI_API_KEY="your-api-key"
docker-compose up --build

# On macOS/Linux:
export OPENAI_API_KEY="your-api-key"
docker-compose up --build
```
The application will automatically initialize the database extension, create all required tables, and start listening on `http://localhost:8000`.

---

## 📡 API Endpoints & Usage

Once running, interactive API documentation is available at:
- **Swagger UI**: `http://127.0.0.1:8000/docs`
- **ReDoc**: `http://127.0.0.1:8000/redoc`

### Key Endpoints

| Method | Endpoint | Description |
| :--- | :--- | :--- |
| **GET** | `/health` | Application status & Database ping. |
| **POST** | `/api/v1/documents` | Ingest and store a text document (generates OpenAI embedding). |
| **GET** | `/api/v1/documents/search` | Query similar documents based on cosine similarity. |
| **POST** | `/api/v1/ask` | Contextual Q&A (RAG) using vector search and OpenAI completion. |
| **POST** | `/api/v1/qa` | Save a new question manually. |
| **GET** | `/api/v1/qa` | List saved questions (paginated). |
| **GET** | `/api/v1/qa/{question_id}` | Fetch a question with all its answers. |
| **POST** | `/api/v1/qa/{question_id}/answers` | Add a manual answer to a question. |

---

### Request & Response Examples

#### 1. Ingest a Document (`POST /api/v1/documents`)
**Request:**
```bash
curl -X POST "http://127.0.0.1:8000/api/v1/documents" \
     -H "Content-Type: application/json" \
     -d '{"content": "Retrieval-Augmented Generation (RAG) combines search indexing with generative completions."}'
```
**Response:**
```json
{
  "id": 1,
  "content": "Retrieval-Augmented Generation (RAG) combines search indexing with generative completions."
}
```

#### 2. Search Similar Documents (`GET /api/v1/documents/search`)
**Request:**
```bash
curl -G "http://127.0.0.1:8000/api/v1/documents/search" \
     --data-urlencode "query=What is RAG?" \
     --data-urlencode "limit=2"
```
**Response:**
```json
[
  {
    "id": 1,
    "content": "Retrieval-Augmented Generation (RAG) combines search indexing with generative completions.",
    "similarity": 0.8924
  }
]
```

#### 3. Ask a Question with RAG (`POST /api/v1/ask`)
This endpoint performs vector similarity search on ingested documents, builds a contextual prompt, queries OpenAI's completion endpoint, logs the question and answer to the database, and returns the response:
**Request:**
```bash
curl -X POST "http://127.0.0.1:8000/api/v1/ask" \
     -H "Content-Type: application/json" \
     -d '{"question": "How does RAG work?"}'
```
**Response:**
```json
{
  "question": "How does RAG work?",
  "answer": "Retrieval-Augmented Generation (RAG) works by retrieving relevant information from a vector database (context) and appending it to the user query before passing it to the language model to generate a factually grounded response.",
  "sources": [
    "Retrieval-Augmented Generation (RAG) combines search indexing with generative completions."
  ]
}
```

#### 4. Service Health Check (`GET /health`)
**Request:**
```bash
curl "http://127.0.0.1:8000/health"
```
**Response:**
```json
{
  "status": "healthy",
  "database": "connected"
}
```

---

## 🚀 Cloud Deployment Instructions

The application is containerized and ready for cloud deployment to platforms such as **Render** or **Railway**.

### Render Deployment (Recommended)

1. **Deploy a Managed PostgreSQL Database**:
   - Create a new **PostgreSQL Database** on Render.
   - Once provisioned, copy the **External Database URL**. Ensure you change the scheme to `postgresql+asyncpg://` for compatibility with SQLAlchemy's async driver.
   
2. **Deploy the Web Service**:
   - Create a new **Web Service** on Render, connecting it to your GitHub repository.
   - Select **Docker** as the Runtime environment. Render will automatically detect the root `Dockerfile`.
   - Add the following variables under **Environment Variables**:
     - `DATABASE_URL`: Set to your Render Postgres URL (using `postgresql+asyncpg://` scheme).
     - `OPENAI_API_KEY`: Set to your OpenAI API Key.
     - `OPENAI_MODEL`: `gpt-4o-mini`.
     - `APP_ENV`: `production`.
   - Click **Deploy Web Service**. Render will build the Docker container and start serving the API.

### Railway Deployment

1. **Create Project**:
   - Create a new project on Railway.
   - Click **Add Service** -> **PostgreSQL**.
   
2. **Deploy Service**:
   - Select **Deploy from GitHub repo** and connect to your repository.
   - Railway will detect the `Dockerfile` and build it automatically.
   - Set the service variables:
     - `DATABASE_URL`: Set to `postgresql+asyncpg://${{ Postgres.DATABASE_URL }}` (replacing the standard postgresql scheme with the asyncpg driver protocol).
     - `OPENAI_API_KEY`: Set to your OpenAI API Key.
     - `OPENAI_MODEL`: `gpt-4o-mini`.
     - `APP_ENV`: `production`.
   - Railway will trigger an automatic build and deploy the web service.

---

## 📝 Satisfying Assessment Requirements

This implementation directly meets all requirements of the Stage 1 Technical Assessment:

- **FastAPI REST API**: Configured with proper CORS middleware, API routers, OpenAPI schemas, and path validation.
- **LLM Integration**: Seamless connection to OpenAI with asynchronous client configuration (`AsyncOpenAI`) to avoid locking threads during network calls, featuring graceful mock fallbacks for safe testing when API keys are unconfigured.
- **Embeddings-based Retrieval**: PostgreSQL + `pgvector` implementation for indexing high-dimensional embeddings with cosine similarity. Includes SQLite fallback to facilitate development on systems lacking Postgres.
- **Software Engineering Best Practices**: Clean architecture, asynchronous handling for web endpoints and database queries, comprehensive input validation, strict environment variables validation using `pydantic-settings`, and extensive API documentation.
- **Deployment-Ready**: Ready to deploy via Docker, Docker Compose, Render, or Railway with database migration, extensions setup, and containerized configuration automated out-of-the-box.
