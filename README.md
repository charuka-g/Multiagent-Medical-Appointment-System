# AgenticAI Medical Appointment System

A sophisticated multi-agent AI system for managing medical appointments and lab tests and diagnostics. Built with LangGraph, FastAPI, and Next.js, this system uses an agentic architecture to intelligently route and handle patient requests through specialized agents.

## 🏗️ Architecture

This system implements a **supervisor-agent pattern** using LangGraph, where a supervisor agent intelligently routes patient queries to specialized agents:

- **Supervisor Agent**: Routes queries to appropriate specialized agents
- **Doctor Appointment Agent**: Handles appointment scheduling, doctor selection, and booking management
- **Lab & Diagnostics Agent**: Manages lab test requests and diagnostic appointments

## 🚀 Features

- **Multi-Agent System**: Intelligent routing and orchestration of patient requests
- **Conversation Memory**: Persistent memory system that maintains context across conversations
- **Doctor Scheduling**: Real-time availability checking and appointment booking
- **Lab Test Management**: Request and schedule lab tests and diagnostics
- **Patient Profiles**: Personalized experience based on patient history
- **Insurance Integration**: Insurance plan verification and coverage checking
- **Modern UI**: Clean, responsive Next.js frontend with real-time chat interface

## 📁 Project Structure

```
AgenticAI-Medical-Appointment-System/
├── backend/                 # FastAPI backend with agent system
│   ├── agents/             # Agent implementations
│   │   ├── supervisor_agent.py
│   │   ├── doctor_appointment_agent.py
│   │   └── lab_agent.py
│   ├── data/               # Data files (profiles, availability, etc.)
│   ├── data_models/        # Pydantic models
│   ├── db/                 # Database connection and schema
│   ├── prompt_library/     # Agent prompts
│   ├── toolkit/            # Agent tools and toolkits
│   ├── utils/              # Utilities (LLM, memory, data access)
│   ├── scripts/             # Data seeding and utility scripts
│   ├── main.py             # FastAPI application entry point
│
└── frontend/               # Next.js frontend
    ├── app/                # Next.js app directory
    ├── components/         # React components
    │   ├── ChatInterface.tsx
    │   ├── ChatWidget.tsx
    │   ├── BookingConfirmationTile.tsx
    │   └── PaymentGatewayTile.tsx
    └── package.json        # Node.js dependencies
```

## 🛠️ Prerequisites

- **Python 3.10+**
- **Node.js 18+**
- **PostgreSQL** (for database)
- **OpenAI API Key** (or compatible LLM provider)

## 📦 Installation

### Backend Setup

1. Navigate to the backend directory:
```bash
cd backend
```

2. Create a virtual environment (recommended):
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Set up environment variables:
Create a `.env` file in the `backend/` directory:
```env
OPENAI_API_KEY=your_openai_api_key_here
DATABASE_URL=postgresql://user:password@localhost:5432/medical_appointments
```

5. Set up the database:
```bash
# Create database and run schema
psql -U postgres -c "CREATE DATABASE medical_appointments;"
psql -U postgres -d medical_appointments -f db/schema.sql
```

6. Seed initial data (optional):
```bash
python scripts/seed_dummy_data.py
python scripts/seed_medical_appointments.py
```

### Frontend Setup

1. Navigate to the frontend directory:
```bash
cd frontend
```

2. Install dependencies:
```bash
npm install
```

## 🚀 Running the Application

### Start the Backend

From the `backend/` directory:
```bash
uvicorn main:app --reload --port 8000
```

The API will be available at `http://localhost:8000`

### Start the Frontend

From the `frontend/` directory:
```bash
npm run dev
```

The frontend will be available at `http://localhost:3000`

## 📡 API Endpoints

### POST `/execute`

Execute a query through the agent system.

**Request Body:**
```json
{
  "id_number": 12345,
  "messages": "I need to book an appointment with a cardiologist"
}
```

**Response:**
```json
{
  "messages": [
    {
      "type": "ai",
      "content": "I'll help you book an appointment..."
    }
  ]
}
```

## 🔧 Configuration

### Backend Configuration

- LLM Model: Configured in `backend/utils/llms.py`
- Database: Connection settings in `backend/db/db_connection.py`
- Memory: Conversation memory stored in `backend/data/conversation_memory.json`

### Frontend Configuration

- API Proxy: Configured in `frontend/next.config.js`
- Backend URL: Defaults to `http://localhost:8000`

## 🧪 Development

### Running Scripts

- **Visualize Agent Graph**: `python scripts/visualize_agent_graph.py`
- **Seed Data**: `python scripts/seed_dummy_data.py`
- **Seed Appointments**: `python scripts/seed_medical_appointments.py`

### Testing

The system includes:
- Jupyter notebooks for experimentation (`backend/notebooks/`)
- Agent graph visualization (`backend/agent_graph.mmd`)

## 📚 Key Technologies

- **LangGraph**: Multi-agent orchestration and state management
- **LangChain**: LLM integration and tooling
- **FastAPI**: High-performance Python web framework
- **Next.js 14**: React framework with App Router
- **PostgreSQL**: Relational database
- **TypeScript**: Type-safe frontend development
- **Tailwind CSS**: Utility-first CSS framework

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📝 License

This project is licensed under the MIT License.

## 👤 Author

**Charuka Gunawardhane**
- Email: charukagunawardhane999@gmail.com

## 🙏 Acknowledgments

- Built with LangChain and LangGraph
- OpenAI for LLM capabilities
- FastAPI and Next.js communities

---

For more detailed information, see the README files in the `backend/` and `frontend/` directories.

