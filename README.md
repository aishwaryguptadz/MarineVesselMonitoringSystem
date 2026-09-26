# Marine Smart Automation System

<p align="center">
  <strong>AI-Powered Marine Engineering & Vessel Operations Platform</strong>
</p>

<p align="center">
  <img src="https://img.shields.io/badge/Android-Kotlin-3DDC84?style=for-the-badge&logo=android&logoColor=white" alt="Android">
  <img src="https://img.shields.io/badge/Backend-FastAPI-009688?style=for-the-badge&logo=fastapi&logoColor=white" alt="FastAPI">
  <img src="https://img.shields.io/badge/AI-RAG%20%7C%20LangChain-FF6F00?style=for-the-badge" alt="AI">
  <img src="https://img.shields.io/badge/ML-Python-3776AB?style=for-the-badge&logo=python&logoColor=white" alt="Machine Learning">
  <img src="https://img.shields.io/badge/Database-SQL%20Server-CC2927?style=for-the-badge&logo=microsoftsqlserver&logoColor=white" alt="SQL Server">
  <img src="https://img.shields.io/badge/API-REST-02569B?style=for-the-badge" alt="REST API">
</p>

<p align="center">
  A modular marine intelligence platform combining native Android monitoring, machine learning, REST APIs, database management, RAG-based AI assistance, web dashboards, and edge deployment concepts.
</p>

---

## Demo Flow

```text
Marine / Vessel Data
        │
        ▼
Machine Learning Models
        │
        ▼
FastAPI Backend
        │
   ┌────┼─────────────┐
   │    │             │
   ▼    ▼             ▼
Android  Dashboard   AI Agent
 App       Web       RAG/LangChain
   │        │             │
   └────────┼─────────────┘
            ▼
      Decision Support
```

---

## Overview

The **Marine Smart Automation System** is a multidisciplinary software platform designed to improve marine engineering operations and vessel monitoring through data-driven intelligence.

Marine vessels generate large volumes of operational data. Traditional monitoring workflows can involve manual observation, delayed identification of abnormal conditions, difficult access to historical information, and heavy dependency on domain expertise.

This project proposes an integrated platform that combines:

* Native Android application development
* Machine Learning / Deep Learning
* Marine operational datasets
* REST APIs
* Database management
* RAG-based AI assistance
* Web-based monitoring dashboards
* Edge deployment concepts

The repository is organized as a modular system so that the mobile application, backend, AI agent, machine-learning pipeline, dashboard, and edge components can be developed independently while communicating through defined interfaces.

### Problem Statement

Marine vessel operations require continuous monitoring of operational parameters and engineering information.

Common challenges include:

* Manual monitoring of vessel information
* Large volumes of operational data
* Delayed detection of abnormal conditions
* Difficulty accessing historical information
* Limited decision-support capabilities
* Dependency on experienced marine personnel
* Lack of unified access to operational intelligence

### Proposed Solution

The system introduces an integrated software architecture in which machine-learning models, backend APIs, databases, mobile applications, dashboards, and AI-assisted information retrieval work together.

```text
┌───────────────────────────────┐
│      Marine Vessel Data       │
└───────────────┬───────────────┘
                │
                ▼
┌───────────────────────────────┐
│   Machine Learning Models     │
│       Python / ML / DL        │
└───────────────┬───────────────┘
                │
                ▼
┌───────────────────────────────┐
│       FastAPI Backend         │
│          REST APIs            │
└───────────────┬───────────────┘
                │
       ┌────────┼────────┐
       │        │        │
       ▼        ▼        ▼
   Android   Dashboard   AI Agent
     App        Web      RAG/LLM
       │        │        │
       └────────┼────────┘
                │
                ▼
       Marine Decision Support
```

---

## Features

### Android Application

* Native Android application built with Kotlin.
* XML-based Android UI.
* Vessel and marine information presentation.
* Application navigation and screen management.
* Backend API integration.
* JSON-based data communication.
* Application-side data handling.
* Mobile interface for marine monitoring.

### Machine Learning

* Maritime dataset processing.
* Machine-learning model development.
* Model evaluation.
* Model persistence.
* Model inference.
* Model compression.
* API integration support.
* Fuel-consumption prediction.
* ETA prediction.
* Route optimization.

The ML module contains trained artifacts including:

```text
fuel_model.pkl
eta_model.pkl
fuel_feature_cols.pkl
eta_feature_cols.pkl
label_encoders.pkl
scaler.pkl
```

### Fuel Prediction

The ML/API design supports prediction of voyage fuel consumption based on parameters such as:

* Deadweight tonnage
* Vessel age
* Distance
* Average speed
* Design speed
* Engine load
* RPM
* Shaft power
* SFOC
* Wind speed
* Wave height
* Current speed
* Hull fouling
* Propeller fouling
* Cargo utilization
* Draft
* Ship type
* Loading condition
* Fuel type

### ETA Prediction

The system can produce voyage-related ETA information alongside fuel prediction.

### Route Optimization

The route optimization component can recommend multiple routes between ports and provide information such as:

* Route ranking
* Route path
* Route type
* Total fuel consumption
* Total distance
* Voyage duration
* Fuel cost
* Risk score
* Overall score

### AI / RAG Assistant

* Marine-domain question answering.
* Retrieval-Augmented Generation.
* LangChain-based architecture.
* Marine knowledge retrieval.
* Context-aware response generation.
* Intelligent interaction with marine-domain information.

### Backend API

* FastAPI-based REST backend.
* Request validation.
* Database communication.
* ML service integration.
* JSON responses.
* Interactive Swagger/OpenAPI documentation.
* Centralized integration layer for application clients.

### Database Management

* Relational database architecture.
* SQL Server integration.
* Marine-domain data storage.
* Structured querying.
* Data retrieval for backend services.
* Database relationships and consistency management.

### Dashboard

The repository contains a dedicated React-based web dashboard module intended for monitoring and visualizing marine information.

### Edge Deployment

The repository also contains an edge-module intended for lightweight model deployment and optimization for resource-constrained environments.

---

## Tech Stack

### Mobile Application

| Technology     | Purpose                         |
| -------------- | ------------------------------- |
| Kotlin         | Android application development |
| Android SDK    | Native Android platform         |
| XML            | UI layouts                      |
| Gradle         | Build and dependency management |
| Android Studio | Android development environment |

### Backend

| Technology | Purpose                     |
| ---------- | --------------------------- |
| Python     | Backend and ML development  |
| FastAPI    | REST API framework          |
| Uvicorn    | ASGI server                 |
| REST API   | Client-server communication |

### Database

| Technology           | Purpose                        |
| -------------------- | ------------------------------ |
| Microsoft SQL Server | Relational database            |
| SQL                  | Data querying and management   |
| DBMS                 | Database design and management |

### Machine Learning

| Technology       | Purpose                   |
| ---------------- | ------------------------- |
| Python           | ML development            |
| Pandas           | Dataset processing        |
| NumPy            | Numerical computation     |
| Scikit-learn     | ML preprocessing/models   |
| XGBoost          | Fuel prediction           |
| Random Forest    | ETA prediction            |
| Joblib           | Model serialization       |
| Maritime Dataset | Model training/evaluation |

### AI

| Technology            | Purpose                              |
| --------------------- | ------------------------------------ |
| RAG                   | Retrieval-Augmented Generation       |
| LangChain             | AI/RAG orchestration                 |
| Information Retrieval | Marine knowledge retrieval           |
| AI Agent              | Intelligent marine-domain assistance |

### Web / Other

| Technology       | Purpose                |
| ---------------- | ---------------------- |
| React            | Web dashboard          |
| Git              | Version control        |
| GitHub           | Source-code management |
| VS Code          | Development            |
| SQL Server Tools | Database management    |

---

## Architecture

The project follows a **modular client-server architecture**.

Each major subsystem has a dedicated responsibility:

```text
                         ┌──────────────────────┐
                         │    Marine Dataset    │
                         └──────────┬───────────┘
                                    │
                                    ▼
                         ┌──────────────────────┐
                         │   ML / DL Pipeline   │
                         │       Python         │
                         └──────────┬───────────┘
                                    │
                                    ▼
                         ┌──────────────────────┐
                         │      FastAPI         │
                         │    Backend API       │
                         └──────────┬───────────┘
                                    │
              ┌─────────────────────┼─────────────────────┐
              │                     │                     │
              ▼                     ▼                     ▼
      ┌──────────────┐      ┌──────────────┐      ┌──────────────┐
      │ Android App  │      │ Web Dashboard│      │  AI / RAG    │
      │    Kotlin    │      │    React     │      │   Agent      │
      └──────┬───────┘      └──────┬───────┘      └──────┬───────┘
             │                     │                     │
             └─────────────────────┼─────────────────────┘
                                   │
                                   ▼
                         ┌──────────────────────┐
                         │     SQL Server       │
                         │      Database        │
                         └──────────────────────┘
```

### Android Architecture

The Android application acts as a client of the backend.

```text
┌───────────────┐
│     User      │
└───────┬───────┘
        │
        ▼
┌───────────────┐
│ Android UI    │
│ Kotlin + XML  │
└───────┬───────┘
        │
        ▼
┌───────────────┐
│ Application   │
│ Logic         │
└───────┬───────┘
        │
        │ HTTP / REST
        ▼
┌───────────────┐
│   FastAPI     │
│    Backend    │
└───────┬───────┘
        │
   ┌────┴───────────┐
   │                │
   ▼                ▼
Database          ML / AI
   │                │
   └───────┬────────┘
           ▼
     JSON Response
           │
           ▼
     Android UI
```

The Android client does not require direct access to the database. Database operations remain behind the backend API.

### ML Architecture

```text
Maritime Dataset
       │
       ▼
Data Preprocessing
       │
       ▼
Feature Engineering
       │
       ├───────────────┐
       ▼               ▼
Fuel Model         ETA Model
(XGBoost)       (Random Forest)
       │               │
       └───────┬───────┘
               ▼
         Model Inference
               │
               ▼
          Backend API
```

### RAG Architecture

```text
User Question
      │
      ▼
   AI Agent
      │
      ▼
 Information Retrieval
      │
      ▼
Marine Knowledge / Documents
      │
      ▼
 Retrieved Context
      │
      ▼
 Language Model
      │
      ▼
Generated Response
```

---

## API / Database

### Backend API

The backend is implemented using **FastAPI** and serves as the integration layer between the Android application, machine-learning components, and database.

The development server can be started with:

```bash
uvicorn app:app --reload --host 0.0.0.0 --port 8000
```

FastAPI's interactive documentation is then available at:

```text
http://localhost:8000/docs
```

### Machine Learning API

#### Fuel Prediction

```http
POST /api/predict/fuel
```

Example request:

```json
{
  "dwt": 287185,
  "vessel_age": 21,
  "distance_nm": 8278,
  "avg_speed_knots": 12.0,
  "design_speed_knots": 16.0,
  "engine_load_pct": 42.6,
  "rpm": 91,
  "shaft_power_kw": 5743.3,
  "sfoc_g_kwh": 186.7,
  "wind_speed_knots": 1.8,
  "wave_height_m": 2.16,
  "current_speed_knots": 2.3,
  "hull_fouling_pct": 15.6,
  "propeller_fouling_pct": 14.1,
  "cargo_utilization_pct": 0.833,
  "draft_m": 13.68,
  "ship_type": "Tanker",
  "loading_condition": "Laden",
  "fuel_type": "VLSFO"
}
```

Example response:

```json
{
  "predicted_fuel_tonnes": 739.6,
  "predicted_eta_hours": 689.8
}
```

#### Route Optimization

```http
POST /api/routes/optimize
```

Example request:

```json
{
  "origin": "Jebel Ali",
  "destination": "Guangzhou",
  "ship_type": "Tanker"
}
```

The route optimizer can return ranked route recommendations containing:

```text
Rank
Labels
Path
Route Type
Total Fuel
Total Distance
Voyage Days
Fuel Cost
Risk Score
Overall Score
```

#### Available Ports

```http
GET /api/ports
```

Returns available origin and destination ports from the maritime dataset.

### Database

The backend uses **Microsoft SQL Server** with the database configuration represented by:

```env
DB_SERVER=YOUR_SQL_SERVER
DB_NAME=MarineAI
DB_DRIVER=SQL Server
```

The Android application does not directly connect to SQL Server.

The intended request flow is:

```text
Android Application
        │
        ▼
     REST API
        │
        ▼
     FastAPI
        │
        ▼
   SQL Query
        │
        ▼
   SQL Server
        │
        ▼
   Query Result
        │
        ▼
 FastAPI Response
        │
        ▼
   JSON Response
        │
        ▼
 Android Application
```

### Database Responsibilities

* Persistent marine-domain data storage
* Structured data management
* SQL querying
* Data retrieval
* Entity relationships
* Backend data operations
* Data consistency

---

## Project Structure

```text
MajorProject/
│
├── AI-Agent (RAG + Langchain system) [Akhand]/
│   └── marine_ai_intelligence_module/
│
├── Backend-API (Fast API or Flask) [Shared (integration team)]/
│
├── Dashboard-Web (React frontend) [Anush]/
│
├── Data (Datasets or links)/
│
├── Docs (for documentation)/
│
├── Edge-Module (Edge deployment (Lite model))/
│
├── Mobile-App (Android app)/
│   └── Marine/
│       ├── app/
│       │   └── src/
│       │       └── main/
│       │
│       ├── gradle/
│       ├── .gitignore
│       ├── build.gradle.kts
│       ├── gradle.properties
│       ├── gradlew
│       ├── gradlew.bat
│       └── settings.gradle.kts
│
├── Scripts (Utility scripts)/
│
├── ml_model/
│   ├── data/
│   ├── evaluation/
│   ├── models/
│   │   ├── fuel_model.pkl
│   │   ├── eta_model.pkl
│   │   ├── fuel_feature_cols.pkl
│   │   ├── eta_feature_cols.pkl
│   │   ├── label_encoders.pkl
│   │   └── scaler.pkl
│   │
│   ├── src/
│   │   ├── predict.py
│   │   └── route_optimizer.py
│   │
│   ├── API_GUIDE.md
│   ├── compress_model.py
│   ├── main.py
│   └── new_maritime_dataset.csv
│
├── .gitignore
└── README.md
```

### Module Responsibilities

| Module          | Responsibility                                          |
| --------------- | ------------------------------------------------------- |
| `Mobile-App`    | Native Android application                              |
| `Backend-API`   | REST API and integration layer                          |
| `Dashboard-Web` | React-based monitoring dashboard                        |
| `AI-Agent`      | RAG + LangChain marine intelligence                     |
| `ml_model`      | ML models, training resources, evaluation and inference |
| `Data`          | Dataset/data resources                                  |
| `Edge-Module`   | Lightweight/edge deployment                             |
| `Docs`          | Project documentation                                   |
| `Scripts`       | Utility scripts                                         |

---

## Setup

### Prerequisites

Install:

* Android Studio
* Android SDK
* JDK compatible with the Android project
* Python 3.x
* Git
* Microsoft SQL Server
* SQL Server tools
* Android emulator or physical Android device

---

### 1. Clone the Repository

```bash
git clone <REPOSITORY_URL>
cd MajorProject
```

---

### 2. Backend Setup

Navigate to the backend:

```bash
cd "Backend-API (Fast API or Flask) [Shared (integration team)]"
```

Create a Python environment:

```bash
python -m venv venv
```

Activate it on Windows:

```bash
venv\Scripts\activate
```

Activate it on Linux/macOS:

```bash
source venv/bin/activate
```

Install dependencies:

```bash
pip install -r requirements.txt
```

---

### 3. Configure Database

Create a `.env` file in the backend module:

```env
DB_SERVER=YOUR_SQL_SERVER
DB_NAME=MarineAI
DB_DRIVER=SQL Server
```

Do not commit database credentials or other sensitive configuration values.

---

### 4. Start the Backend

```bash
uvicorn app:app --reload --host 0.0.0.0 --port 8000
```

Open the API documentation:

```text
http://localhost:8000/docs
```

---

### 5. Android Setup

Navigate to:

```text
Mobile-App (Android app)/
└── Marine/
```

Open the `Marine` directory in Android Studio.

Allow Android Studio to:

* Index the project.
* Download Gradle dependencies.
* Synchronize the Gradle project.
* Build the application.

Connect an Android device or start an emulator.

Then run:

```text
Run → Run 'app'
```

---

### 6. Machine Learning Setup

Navigate to:

```bash
cd ml_model
```

Install the ML dependencies:

```bash
pip install pandas numpy scikit-learn xgboost joblib
```

The repository contains trained model artifacts and supporting preprocessing files.

The ML API integration guide is available in:

```text
ml_model/API_GUIDE.md
```

---

## My Role

### Android Application Development

My primary responsibility in this project was **Native Android Application Development**.

I worked on:

* Native Android application development using Kotlin.
* Android UI implementation using XML.
* Application screens and navigation.
* Android-side application logic.
* Connecting the Android application with backend services.
* Consuming REST API responses.
* Displaying backend data inside the Android application.
* Handling application-side data flow.
* Testing Android functionality.
* Understanding the complete Android → API → Backend → Database communication flow.

### Database / DBMS

I also contributed to the **database and DBMS side** of the project.

My responsibilities included:

* Understanding the database schema.
* Structuring application-related data.
* Writing SQL queries.
* Retrieving data required by application features.
* Working with relational database concepts.
* Understanding relationships between marine-domain entities.
* Connecting backend functionality with stored data.
* Maintaining data consistency.
* Understanding how application requests map to database operations.

### Integration

A key part of my contribution was working with the integration between:

```text
┌──────────────────────┐
│   Android App        │
│      Kotlin          │
└──────────┬───────────┘
           │
           │ REST API
           ▼
┌──────────────────────┐
│    FastAPI Backend   │
└──────────┬───────────┘
           │
           │ SQL Queries
           ▼
┌──────────────────────┐
│     SQL Server       │
│      MarineAI        │
└──────────────────────┘
```

This architecture allowed the Android application to consume backend data without requiring direct database access.

---

## Future Improvements

### Android Application

* [ ] Add real-time vessel telemetry.
* [ ] Integrate live sensor data.
* [ ] Add real-time monitoring dashboards.
* [ ] Add push notifications for abnormal vessel conditions.
* [ ] Add offline support.
* [ ] Add local database caching.
* [ ] Improve application authentication.
* [ ] Add role-based access control.
* [ ] Improve UI responsiveness and accessibility.

### Backend

* [ ] Add production-grade authentication.
* [ ] Add authorization and role management.
* [ ] Add API rate limiting.
* [ ] Improve API validation.
* [ ] Add comprehensive API testing.
* [ ] Add centralized error handling.
* [ ] Deploy the backend to production infrastructure.
* [ ] Add automated CI/CD.

### Machine Learning

* [ ] Improve fuel prediction accuracy.
* [ ] Improve ETA prediction.
* [ ] Add real-time anomaly detection.
* [ ] Expand maritime datasets.
* [ ] Perform continuous model evaluation.
* [ ] Improve feature engineering.
* [ ] Optimize models for inference.
* [ ] Deploy optimized models to edge devices.

### AI / RAG

* [ ] Expand marine-domain knowledge sources.
* [ ] Improve retrieval quality.
* [ ] Add conversational memory.
* [ ] Add source citations to generated responses.
* [ ] Improve hallucination control.
* [ ] Integrate the AI agent directly with vessel operational data.
* [ ] Add domain-specific evaluation.

### Dashboard

* [ ] Add real-time telemetry visualization.
* [ ] Add vessel analytics.
* [ ] Add historical trend analysis.
* [ ] Add route visualization.
* [ ] Add fuel and ETA analytics.
* [ ] Add anomaly monitoring.
* [ ] Add role-specific dashboards.

### Infrastructure

* [ ] Containerize backend services.
* [ ] Add automated deployment.
* [ ] Add monitoring and logging.
* [ ] Add centralized configuration management.
* [ ] Implement HTTPS everywhere.
* [ ] Improve secrets management.
* [ ] Add comprehensive integration testing.

---

## License

No explicit open-source license is currently specified for this repository.

---

<p align="center">
  <strong>Marine Smart Automation System</strong>
</p>

<p align="center">
  AI • Android • Backend • Database • Machine Learning • RAG
</p>

<p align="center">
  Built as a collaborative engineering project for intelligent marine vessel operations.
</p>
