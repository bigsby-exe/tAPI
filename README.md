# tAPI — Todo API (minimal)

Lightweight FastAPI-based Todo backend intended for single-user use.

Quickstart (dev):

1. Create a virtualenv and install:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

2. Create a `.env` file with your configuration:
   - `API_KEY`: A strong secret key for API authentication (required)
   - `DATABASE_URL`: Database connection string (required)
   
   Example `.env` file:
   ```
   API_KEY=your-strong-secret-api-key-here
   DATABASE_URL=sqlite:///./dev.db
   ```
   
   For production, use a PostgreSQL connection string (e.g., Supabase).

3. Start the app:

```powershell
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

The API is protected by an API key using the `X-API-Key` header. All endpoints (except `/health`) require authentication:
- Missing API key: Returns `401 Unauthorized`
- Invalid API key: Returns `403 Forbidden`

API examples
------------

Make sure your `.env` contains a valid `API_KEY` (replace the placeholder in `.env.example`) and that you started the app with the `sqlite` dev DB for local testing.

Create a todo (curl):

```bash
curl -X POST "http://127.0.0.1:8000/todos/" \
	-H "Content-Type: application/json" \
	-H "X-API-Key: $API_KEY" \
	-d '{"title":"Pay bills","description":"Electricity","due_at":null,"estimated_minutes":30,"priority":2,"tags":["finance","monthly"]}'
```

Create a todo (PowerShell):

```powershell
#$env:API_KEY = "replace-with-your-api-key"
Invoke-RestMethod -Method Post -Uri http://127.0.0.1:8000/todos/ -Headers @{"X-API-Key"=$env:API_KEY} -Body (@{title="Pay bills"; description="Electricity"; estimated_minutes=30; priority=2; tags=@("finance","monthly")} | ConvertTo-Json) -ContentType "application/json"
```

List todos:

```bash
curl -H "X-API-Key: $API_KEY" "http://127.0.0.1:8000/todos/"
```

Get a todo by id:

```bash
curl -H "X-API-Key: $API_KEY" "http://127.0.0.1:8000/todos/<todo-id>"
```

Delete a todo:

```bash
curl -X DELETE -H "X-API-Key: $API_KEY" "http://127.0.0.1:8000/todos/<todo-id>"
```

Authentication
---------------
The API uses a single API key configured via the `API_KEY` environment variable in your `.env` file. All endpoints require API key authentication via the `X-API-Key` header:
- **401 Unauthorized**: Returned when the `X-API-Key` header is missing
- **403 Forbidden**: Returned when an invalid API key is provided

**Configuration:**
- Set `API_KEY` in your `.env` file to any strong secret string
- Use this same value in the `X-API-Key` header when making API requests
- The `/health` endpoint does not require authentication

Notes
- The dev environment uses `sqlite:///./dev.db` by default if you followed the quick fix; production should use your managed Postgres (Supabase) and the `DATABASE_URL` in `.env`.
- If you want me to run through creating a sample todo and show the exact responses, tell me and I'll create one via a small script or add a test that exercises the endpoints.

Docker
------
Build the production container and run it (it reads `.env`):

```bash
docker build -t tapi:local .
docker run -d --name tapi -p 8000:8000 --env-file .env tapi:local
```

Or use `docker-compose` for development:

```bash
docker-compose up --build
```

Deployment (Render)
--------------------

This project is configured for deployment on [Render](https://render.com) using native Python (no Docker required).

### Quick Setup

1. **Connect your repository:**
   - Sign up/login to [Render](https://render.com)
   - Click "New +" → "Web Service"
   - Connect your GitHub repository
   - Render will auto-detect the `render.yaml` configuration

2. **Set environment variables:**
   In the Render dashboard, add these environment variables:
   - `API_KEY`: A strong secret key for API authentication
   - `DATABASE_URL`: Your PostgreSQL connection string
     - For Supabase: `postgresql://user:password@db.supabase.co:5432/dbname`
     - For Render PostgreSQL: Create a PostgreSQL service first, then use the internal connection string

3. **Deploy:**
   - Render will automatically build and deploy using the `render.yaml` configuration
   - The service will be available at `https://your-service-name.onrender.com`

### Database Options

- **Supabase** (recommended for free tier): Create a free PostgreSQL database at [supabase.com](https://supabase.com)
- **Render PostgreSQL**: Create a PostgreSQL service in Render and use the provided connection string

### Configuration

The `render.yaml` file configures:
- Python 3.12 runtime
- Automatic dependency installation from `requirements.txt`
- Health check endpoint at `/health`
- Port configuration (uses Render's `$PORT` variable)

For manual configuration without `render.yaml`, use:
- **Build Command**: `pip install -r requirements.txt`
- **Start Command**: `PYTHONPATH=src uvicorn app.main:app --host 0.0.0.0 --port $PORT`

Database schema notes
---------------------

For local development the project uses `SQLModel.metadata.create_all()` to create tables automatically (SQLite dev DB). For production (Supabase) you can apply schema changes manually via the Supabase SQL editor or run SQL scripts as part of your deploy process. I removed Alembic from this repository to keep the project minimal; if you want versioned migrations later I can reintroduce Alembic or another migration tool.

