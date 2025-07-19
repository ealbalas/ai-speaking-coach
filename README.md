# AI Speaking Coach

This project is a web application with a React frontend and a FastAPI backend.

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
