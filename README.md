# Designer Panel

The Designer Panel is an internal tool to automate the process of specification projects for design engineers and firms. It allows users to configure a project setup, select parameters (e.g., number of pumps, motor power), visualize the design instantly via a dynamic Multi Line Diagram, and download a comprehensive asset package including data sheets, engineering specifications, and BIM objects (IFC).

## Technology Stack
- **Frontend**: React + Vite + Custom CSS
- **Backend**: Python + FastAPI + Uvicorn
- **Database**: PostgreSQL (Dockerized) + Alembic for migrations
- **Security Layer**: `bcrypt`, OWASP `HttpOnly` cross-domain JWTs, Strict HTTP Headers
- **Testing**: Pytest (Backend API), Vitest + React Testing Library (Frontend UI)
- **CI/CD**: GitHub Actions

## Prerequisites
- Node.js (v18+ recommended) and `npm`
- Python 3.10+
- Docker and Docker Compose
- WSL (if running on Windows)

---

## 1. Local Database Setup

The project uses a standard PostgreSQL container managed via Docker Compose. The database is persistent using local volumes.

1. From the project root, start the database service:
   ```bash
   docker-compose up -d
   ```
2. The database will listen to changes on host port `5433` (mapped to internal `5432`).
3. Connection details:
   - **Database**: `designer_panel`
   - **User**: `admin`
   - **Password**: `password`
   - **Host Port**: `5433`

---

## 2. Backend Setup & Execution

The backend logic and authentication are handled via FastAPI.

1. Navigate to the backend directory:
   ```bash
   cd back
   ```
2. Create and activate a Python virtual environment:
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   ```
3. Install the required dependencies:
   ```bash
   pip install -r requirements.txt
   ```
4. Run Alembic database migrations to create the necessary tables:
   ```bash
   alembic upgrade head
   ```
5. Seed the database with default user accounts, and populate the database with master data from the Excel sheets:
   ```bash
   python seed.py
   ```
6. Start the FastAPI development server:
   ```bash
   uvicorn app.main:app --reload --port 8000
   ```
   The backend API will now be available at `http://localhost:8000`. You can also view the auto-generated Swagger documentation at `http://localhost:8000/docs`.

---

## 3. Frontend Setup & Execution

The frontend is built with React and Vite. It consumes the API at `http://localhost:8000` to authenticate and allow users to configure projects.

1. Open a new terminal and navigate to the frontend directory:
   ```bash
   cd front
   ```
2. Install the necessary Node packages:
   ```bash
   npm install
   ```
3. Start the Vite development server:
   ```bash
   npm run dev
   ```
4. Access the web application:
   - Open your browser and navigate to `http://localhost:5174` (or `http://localhost:5173` depending on Vite's allocation).
5. The application is secured via a protected routing layer. You will be redirected to the login page.
6. Use one of the accounts seeded from Step 2 to log in.

---

## Design Flow

1. Enter your credentials on the login page.
2. Select either `Water` or `Buildings` from the Master Landing page.
3. Select an Application (e.g. `Booster Set`).
4. Configure the parameters within the layout panel to see the Multi Line diagram render dynamically in real-time.
5. Click `Select All` on the assets checklist and select `Download Package` to receive the zipped documentation and auto-generated image assets.

---

## 4. Testing

The repository enforces Continuous Integration (CI) via GitHub Actions workflows.

### Backend Tests (Pytest)
The backend tests rely on an injected, mocked SQLite in-memory database schema, completely abstracting the need for proprietary seed files or external data volumes to run successfully.
```bash
cd back
pytest tests/
```

### Frontend Tests (Vitest)
The frontend relies on Vitest to validate UI states, error handling boundaries, and mock component rendering natively.
```bash
cd front
npm test
```
