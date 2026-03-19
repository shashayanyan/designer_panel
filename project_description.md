# Project Overview
**Last Synced:** March 19, 2026
The project aims to provide a panel for design engineers and design firms to automate the process of specification projects. It allows the users to configure a project setup using different forms and selections and choose different assets to download as a package in the end.


# Tech Stack (To be completed)
- **Frontend**: React + Vite (UI)
- **Backend**: Python + FastAPI + Uvicorn
- **Database**: Postgres + Alembic (Production) / SQLite (In-Memory for Testing)
- **BIM/CAD Generation**: `ifcopenshell` + `numpy`
- **Testing Infrastructure**: Pytest (Backend API), Vitest + React Testing Library (Frontend UI)
- **CI/CD Pipeline**: GitHub Actions (Automated verification on `main` branch pushes)
- **Security Layer**: `bcrypt`, OWASP `HttpOnly` cross-domain JWTs, Strict HTTP Headers
- **Deployment**: Vercel (Frontend), Google Cloud Run (Backend)
- **Infrastructure**: Docker


# Current Architectural State
*This section captures the active state of the application's core modules as of the last sync.*
- **Configuration Engine (`rule_resolver.py`)**: A dynamic ruleset processor that parses complex payload inputs to determine valid enclosure cabinets, logic components, and asset requirements (the "Digital Twin").
- **Asset Generators (`excel_gen.py`, `word_gen.py`, `bim_gen.py`)**: Dedicated programmatic generators that translate the Digital Twin JSON into Excel sheets, Word Spec Documents, and IFC4X3 compliant BIM objects.
- **Zip Packaging Service (`zip_service.py`)**: Centralized service that orchestrates all file generators into structured subdirectories (`/Neutral/`, `/Docs/`, `/BIM/`) and streams the final archive out to the user.
- **Authentication & Security (`auth.py`, `middleware`)**: A robust session lifecycle enforcing 60-minute JWT expiries via cross-domain `HttpOnly` cookies and strict OWASP frontend defenses.
- **Continuous Integration (`ci.yml`)**: An automated gating system ensuring that frontend dependency installations, vitest unit evaluations, and backend fast-sqlite mocked data validations pass cleanly before merging or deployment.
- **Database Orchestration (`models.py`)**: A connected SQLAlchemy ORM graph utilizing pre-fetched `relationship()` bindings to execute high-performance `joinedload` queries, eliminating database N+1 latencies.

# User Interface
This is the initial focus of the app for now. The goal is to have a responsive and user-friendly interface that allows users to easily configure their project setup and download the assets they need. Below is a description of pages needed.

## Landing Page
- The landing page should have a brief description of the app and its purpose. 
- It should then provide user with two choices between "Water" and "Buildings". Each choice is a square button with the an image background and the text "Water" or "Buildings" in the center. Upon clicking on either of the choices, the user should be redirected to the respective project setup page.


## Water Page
- The water page provide the user with buttons for 4 applications to choose from. These are: 
    1. Single Pump
    2. MCC Stand. Feeders
    3. Booster Set
    4. Tank level Control
- Upon clicking on any of the buttons, the user should be redirected to the respective application setup page.

## Booster Set Page
- The page should be divided into 4 sections as shown in the diagram below.
------------------------------------
|               1  header          |
------------------------------------
|config    |   single line diagram |
|          |                       |
|    2     |           3           |
|          |                       |
|          |                       |
|          -------------------------
|----------|                       |
|   4      |                       |
| assets   |                       |
------------------------------------
- Section 1, header, has the title "Motor Control Asset Library" and a brief description of the app. It also has a button "Back to Home" which redirects the user to the landing page.
- a figma prototype for this page is available [here](https://www.figma.com/make/BKivENvY8oK7KgoKNUErdY/Motor-Control-Asset-Library-Prototype?p=f)
- Section 2, Configuration, has these fields with the respective options:
    - Number of Incomers : 1, 2
    - Number of Pumps : 2, 3, 4
    - Motor Power Rate (kW) : 4, 7.5, 11, 15, 22.5, 30, 37, 45 kW
    - Type of Motor Start : DOL, Star-Delta, Soft Starter, Variable Speed Drive
    - IP Rating : IP23, IP54
    - Communication : No, ModbusTCP, ProfiNet
All fields are required, and they are all dropdowns.

- Section 3, Single Line Diagram, is a visual representation of the configuration selected in Section 2. It should be updated in real-time as the user changes the configuration in Section 2. 

- Section 4, Assets, is a checklist of all assets that the user can download. The checklist include :
    - Data Sheet
    - Single Line Diagram
    - Bill of Materials
    - Drawings
    - Specification
    - BIM Object

At the bottom of this section, there is a button "Download Package". Upon clicking this button, the user should be able to download all the assets in a zip file. The button is disabled until user completes all the fields in Section 2.

# Extension plan :
## Step 1 : Setup Backend + User Login
### Tasks : 
	1. create a postgres database and create a python (FastAPI) backend to integrate with the front
	2. create user table with username, password, email, role
		- role can be either Admin or User
	3. create 2 default users : (admin, admin@designer-panel.com, passwd=des!gnPanel321) (user, user@designer-panel.com) 
	4. create login page, and make the app accessible only for logged in users.

## Step 2: Dynamic Frontend-Backend Configuration Engine
### Purpose:
Transition the application from static, hard-coded React mockups (like `BoosterSetPage.jsx`) into a fully dynamic configurator. The backend will become the "Single Source of Truth" (SSOT) serving Master Data, cascading rule logic, and real-time document payload generation (The Digital Twin). The frontend will evolve to fetch parameters on-the-fly, rendering UI inputs dynamically based on what the backend dictates, and ultimately retrieving custom-generated `.zip` deliverables rather than fetching static `/public/documents/*` assets.

### Frontend-Backend Relationship Architecture:
1. **Master Data Sourcing:** Frontend dropdowns (Series, Power, etc.) should **not** exist in React state objects. When a user opens an application page, the frontend calls the backend `GET /api/v1/series`, `GET /api/v1/starter-options`, etc., to populate the UI.
2. **Cascading Constraints:** When a user selects a primary input (e.g., `Type of Motor Start: VFD`), the frontend must query the backend to filter subsequent inputs (e.g., only show `Motor Power` options that the DB confirms exist for VFDs).
3. **The Digital Twin Payload:** The frontend form state collapses into a single JSON `DigitalTwinRequest`. This is POSTed to the backend, which runs the engineering math (evaluating `Enclosure_Rules`, quantity multipliers, etc.).
4. **Dynamic Asset Generation:** The backend natively assembles Excel Documents (BOM, IO Params) and Word Documents (Specs) using `pandas` and `python-docx` strictly from the Twin DNA, grouping them via an in-memory `zipfile` stream. The frontend receives this binary stream and triggers the browser download, bypassing the static `public` folder entirely.

### Tasks to Execute:
1. **Purge Static Mock Data**: 
   - Delete the hardcoded `CONFIG_OPTIONS` dictionary inside `BoosterSetPage.jsx` and similarly structured pages.
   - Delete all static `.xlsx`, `.txt`, and `.docx` template files from the `public/documents/booster-set` folder.
2. **Hook up React `useEffect` Queries**:
   - Implement frontend data fetching using `axios` or `fetch` against the `master_data.py` FastAPI endpoints to populate the React Selection state.
   - Establish dependency checks (e.g., `useEffect` listening to `config.motorStart` to re-fetch/filter the `motorPower` dropdown).
3. **Refactor the Download API Call**:
   - Scrap the client-side `JSZip` logic in `BoosterSetPage`'s `handleDownload()`. 
   - Replace it with a `fetch` call pointing to `POST /api/v1/engine/generate-package`, passing the form inputs as the JSON body. Await the `application/x-zip-compressed` blob and trigger a standard anchor tag download.
4. **Abstract to a Universal Configurator Layout (Future phase)**:
   - Once Booster Sets are tested end-to-end, refactor the page into a generic `DynamicConfiguratorPage.jsx`.
   - The React page should take an `applicationType` prop to ask the backend, "What schema structure should I display to the user?" allowing for new apps (HVAC, Conveyor) to be added simply by inserting new rows into the Backend Master CSVs without writing new React pages!

### Required Master/Reference Files (To Be Added to Repo):
To make Universal configurator expansion possible in the long term, the backend needs mapping tables defining how different Apps consume rules:
- **`Applications.csv`:** A master sheet defining available App domains (e.g., ID: `APP-001`, Name: `Water Booster Set`, Root_Config_Requirements: `[motor_power, load_count, ats_included]`). 
- **`Application_Input_Schema.csv`:** A reference dictionary mapping which UI form options the frontend should render for each specific `Application_ID`. (e.g., Booster sets require "Pumps", while HVAC requires "Fans").
- **SVG Coordinate Maps (Optional):** If the Single Line Diagram remains dynamic, the backend may need a `DrawingTemplate.csv` outputting the specific SVG node structures coordinates/types to draw, letting React act strictly as a dumb SVG renderer.
