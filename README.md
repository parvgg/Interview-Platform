Interview AI Coach 🚀
Interview AI Coach is a cloud-native, full-stack platform designed to help job seekers perfect their interview skills through real-time, AI-driven performance feedback. By capturing and analyzing user audio responses, the platform delivers instantaneous, actionable analytics covering text structure, filler word usage, and communication pacing.

🛠️ The Tech Stack & Architecture
The application is explicitly designed with a decoupled, stateless compute layer and a persistent cloud storage layer to maximize resource efficiency on cloud tiers.

Plaintext
 ┌────────────────┐       HTTP Requests       ┌───────────────┐
 │ Streamlit App  │ ────────────────────────> │  FastAPI API  │
 │   (Frontend)   │ <──────────────────────── │   (Backend)   │
 └────────────────┘       JSON Analytics      └───────────────┘
                                                      │
                            ┌─────────────────────────┼─────────────────────────┐
                            ▼                                                   ▼
                ┌───────────────────────┐                               ┌───────────────┐
                │   Google Gemini API   │                               │ Neon Serverless │
                │ (Cloud Transcription) │                               │ (PostgreSQL)  │
                └───────────────────────┘                               └───────────────┘
Frontend: Built an interactive data dashboard using Streamlit.

Backend: Engineered an asynchronous REST API using FastAPI.

Database & ORM: Managed application state and historical metrics with a serverless PostgreSQL (Neon) database mapped via SQLAlchemy ORM.

AI Engine: Powered by the official Google Gen AI SDK (gemini-2.5-flash) for cloud-native, multimodal audio-to-text processing.

Hosting & CI/CD: Hosted via automated build pipelines on Render (Compute) and Streamlit Cloud (Frontend).

✨ Features
Serverless Audio Processing: Uploads raw audio files directly into a cloud-native transcription pipeline, mitigating the need for heavy local dependencies (e.g., librosa, ffmpeg) and minimizing system memory footprint.

Communication Behavior Analytics: Dynamically scans transcripts using lightweight string-parsing matrix logic to locate and evaluate the density of filler words (um, uh, like, basically, etc.).

Custom NLP Assessment: Programmatically checks answers against conversational prompt parameters to evaluate depth, structure, and pacing.

Persistent Performance Tracking: Saves and displays interactive analytical charts of past mock interview scores across historical sessions using direct database relation indexing.

[!WARNING]
Free-Tier Resource Policy Notice: This platform is completely free to access and open-source. Because it relies on free-tier services (Render, Neon, and Google AI Studio), it operates under shared cloud compute restrictions and a standard limit of 20 free Gemini requests per day. If a processing request fails due to an API quota limit, the quota pool resets automatically on a rolling 24-hour cycle.

🚀 Local Installation & Setup
To run the entire ecosystem locally on your machine, follow these configurations:

1. Clone the Repository
Bash
git clone https://github.com/yourusername/interview-ai-coach.git
cd interview-ai-coach
2. Configure Your Environment Variables
Create a .env file in the root directory:

Code snippet
DATABASE_URL=postgresql://<user>:<password>@<host>/<dbname>?sslmode=require
GEMINI_API_KEY=your_google_ai_studio_api_key_here
3. Initialize the Virtual Environment & Dependencies
Bash
# Create and activate environment
python -m venv venv
source venv/bin/activate  # On Windows use: venv\Scripts\activate

# Install requirements
pip install -r requirements.txt
4. Provision the PostgreSQL Schema
Run the initialization script to force SQLAlchemy to compile your database tables directly inside your PostgreSQL instance:

Bash
python -c "from app.database import engine; from app.models.models import Base; Base.metadata.create_all(bind=engine); print('🎉 Tables created successfully!')"
5. Fire Up the Servers
Start the FastAPI Backend:

Bash
uvicorn app.main:app --reload --port 8000
Start the Streamlit Frontend:

Bash
streamlit run frontend/app.py
💡 Production Architecture Insights
Dynamic Metadata Registration: Bypassed traditional asynchronous startup race conditions by implementing on-demand schema mapping via direct Model.metadata.create_all(bind=engine) execution blocks, guaranteeing transactional table structure integrity even when cold-starting serverless containers.

Decoupled State: Implemented structural separation of stateless computing (Render instances) and persistent database storage (Neon endpoints) ensuring completely non-destructive code updates, hot reloads, and rebuild triggers.
