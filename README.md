# AI QA Service

A modular, high-performance FastAPI REST API for managing Questions and Answers. Built with clean architecture principles, modern SQLAlchemy 2.0 async operations, and Pydantic validation.

## Architecture & Features
- **Clean Architecture**: Separated layers for API routing, business services, configuration, and data models.
- **Asynchronous DB Engine**: Utilizes `asyncpg` and SQLAlchemy's async connection pool to prevent event loop blocking.
- **Auto DDL Initialization**: Creates database tables on startup (lifespan) if they do not exist—perfect for local development.
- **Environment Variables Validation**: Configurations validated strictly using `pydantic-settings`.

---

## Directory Structure
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
│   │   └── qa.py        # SQLAlchemy database models
│   ├── schemas/
│   │   └── qa.py        # Pydantic request & response schemas
│   ├── routes/
│   │   ├── api.py       # Main router aggregating sub-routers
│   │   ├── health.py    # Service health and DB verification router
│   │   └── qa.py        # REST API endpoints for QA resources
│   └── services/
│       └── qa_service.py # Pure business logic decoupled from API handlers
├── .env.example         # Template for environment configuration
├── .gitignore           # Python development gitignore configurations
├── README.md            # Project documentation
└── requirements.txt     # Python requirements file
```

---

## Local Setup Instructions

### 1. Prerequisites
- Python 3.10 or higher.
- A running PostgreSQL database (or similar Postgres-compatible database).

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

### 4. Setup Environment Variables
Copy the template configuration to create your local `.env`:
```bash
cp .env.example .env
```
Ensure your `DATABASE_URL` in `.env` is updated to point to your PostgreSQL database.
Example:
```env
DATABASE_URL="postgresql+asyncpg://postgres:postgres@localhost:5432/ai_qa_db"
```

### 5. Run the Application
Start the FastAPI development server:
```bash
uvicorn app.main:app --reload
```

The server will start at `http://127.0.0.1:8000`.

---

## API Documentation

Once running, interactive API documentation is available at:
- **Swagger UI**: [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)
- **ReDoc**: [http://127.0.0.1:8000/redoc](http://127.0.0.1:8000/redoc)

### Key Endpoints

| Method | Endpoint | Description |
| :--- | :--- | :--- |
| **GET** | `/health` or `/api/v1/health` | Service health status and Database ping. |
| **POST** | `/ask` or `/api/v1/ask` | Contextual Q&A (RAG) using OpenAI completions + vector search. |
| **POST** | `/documents` or `/api/v1/documents` | Ingest and store a document with its vector embedding. |
| **GET** | `/documents/search` or `/api/v1/documents/search` | Search similar documents using cosine similarity. |
| **POST** | `/api/v1/qa` | Create a new manual question. |
| **GET** | `/api/v1/qa` | List all manual questions (paginated). |
| **GET** | `/api/v1/qa/{question_id}` | Retrieve details of a specific manual question. |
| **POST** | `/api/v1/qa/{question_id}/answers` | Add a manual answer to a specific question. |

---

## Seeding Sample Documents

To populate the database with tech/AI sample documents and their vector embeddings (using OpenAI), execute the following script from your virtual environment:

```bash
python scripts/seed_documents.py
```
*(Ensure `OPENAI_API_KEY` and `DATABASE_URL` are configured in your `.env` before running).*

---

## Deployment Instructions

### 1. Docker Compose (Quickstart Local Postgres + pgvector)
If you have Docker installed, you can spin up the full stack (FastAPI app + PostgreSQL with `pgvector` enabled) locally in one command:
```bash
# Set your OpenAI key in shell, then start the containers
export OPENAI_API_KEY="your-api-key-here"
docker-compose up --build
```
This automatically runs database migrations, enables the `vector` extension, and binds the API to `http://localhost:8000`.

### 2. Cloud Deployment (Render / Railway / GCP / AWS)
This application is fully containerized using the provided `Dockerfile` and is ready for cloud deployment.

#### Render Deployment Guide (Recommended)
1. **Host the Database**:
   - Create a new **PostgreSQL Database** on Render.
   - Once created, go to the database dashboard and enable the `vector` extension by executing `CREATE EXTENSION vector;` in the Render SQL interactive shell, or let the app lifespan handle it automatically.
   - Copy the database connection URL (External Database URL). Ensure it uses `postgresql+asyncpg://` as the driver protocol.

2. **Deploy the Web Service**:
   - Create a new **Web Service** on Render connected to your GitHub repository.
   - Choose **Docker** as the Runtime environment. Render will automatically detect the `Dockerfile` in the root.
   - Add the following environment variables in the Render dashboard:
     - `DATABASE_URL`: Set to your Render Postgres URL (prefixed with `postgresql+asyncpg://`).
     - `OPENAI_API_KEY`: Set to your OpenAI Secret API Key.
     - `OPENAI_MODEL`: `gpt-4o-mini`.
     - `APP_ENV`: `production`.
   - Click **Deploy Web Service**. Render will build and serve your app.

#### Railway Deployment Guide
1. Create a new project on Railway.
2. Add a **PostgreSQL** database service and an **empty service** connected to your GitHub repository.
3. Railway automatically builds the `Dockerfile` for your empty service.
4. Set your environment variables in the service dashboard (copying the Postgres database connection string and your `OPENAI_API_KEY`). The service will bind to port 8000 and deploy automatically.


