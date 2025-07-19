# AI Speaking Coach

This project is a web application with a Next.js frontend and a FastAPI backend.

## Features

- **Next.js Frontend**: A modern React framework for building user interfaces.
- **FastAPI Backend**: A high-performance Python web framework.
- **WebSocket Communication**: Real-time, two-way communication between the frontend and backend.
- **Connection Logging**: The backend logs when a client connects or disconnects from the WebSocket.

## Getting Started

### Prerequisites

- Node.js and npm
- Python 3.7+ and pip

### Installation and Running

**Backend (FastAPI)**

1.  Navigate to the `backend` directory:
    ```bash
    cd backend
    ```
2.  Create a virtual environment and activate it:
    ```bash
    python3 -m venv venv
    source venv/bin/activate
    ```
3.  Install the dependencies:
    ```bash
    pip install -r requirements.txt
    ```
4.  Run the development server:
    ```bash
    uvicorn main:app --reload
    ```
    The backend will be running at `http://localhost:8000`.

**Frontend (Next.js)**

1.  Navigate to the `frontend` directory:
    ```bash
    cd frontend
    ```
2.  Install the dependencies:
    ```bash
    npm install
    ```
3.  Run the development server:
    ```bash
    npm run dev
    ```
    The frontend will be running at `http://localhost:3000`.
