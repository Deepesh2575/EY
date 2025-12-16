# AI Loan Sales Platform

This project is a full-stack AI Loan Sales Platform designed to streamline the loan application process using a conversational AI, document processing, and a robust backend. The platform leverages a multi-agent system to guide users, process their documents via OCR, and manage the loan application workflow.

## Features

-   **Conversational AI**: A multi-agent system (MasterAgent, SalesAgent, UnderwritingAgent, etc.) guides users through the loan application process.
-   **Document Upload and OCR**: Users can upload necessary documents, which are then processed using OCR for data extraction.
-   **User Authentication**: Secure user login and registration.
-   **Loan Application Management**: Track the status and details of loan applications.
-   **Modular Backend**: Built with FastAPI, providing a clear separation of concerns.
-   **Modern Frontend**: Developed with Next.js and React for a dynamic user experience.

## Architecture

The project follows a client-server architecture:

-   **Frontend**: A Next.js application built with React, responsible for the user interface and interacting with the backend API.
-   **Backend**: A FastAPI application developed in Python, handling business logic, database interactions, AI agent orchestration, and document processing. It uses PostgreSQL as its database.
-   **Database**: PostgreSQL for storing application data.
-   **Containerization**: The backend services are containerized using Docker and managed with Docker Compose.

## Setup and Installation

Follow these steps to set up and run the project locally:

### Prerequisites

-   Docker and Docker Compose
-   Node.js and npm (for frontend)
-   Python 3.9+ (for backend development, though Docker is preferred for running)

### Backend Setup

1.  Navigate to the `backend` directory:
    ```bash
    cd loan-ai-app/backend
    ```
2.  Create a `.env` file based on `.env.example` and fill in the necessary environment variables, especially `ANTHROPIC_API_KEY`.
    ```bash
    cp .env.example .env
    ```
3.  Build and run the Docker containers:
    ```bash
    docker-compose up --build
    ```
    This will start the FastAPI backend and the PostgreSQL database. The backend will be accessible at `http://localhost:8000`.

### Frontend Setup

1.  Navigate to the `frontend` directory:
    ```bash
    cd loan-ai-app/frontend
    ```
2.  Install the dependencies:
    ```bash
    npm install
    ```
3.  Start the development server:
    ```bash
    npm run dev
    ```
    The frontend application will be accessible at `http://localhost:3000`.

## Usage

1.  Access the frontend application in your browser at `http://localhost:3000`.
2.  Register a new user account or log in if you already have one.
3.  Follow the conversational AI prompts to start a loan application.
4.  Upload required documents when prompted. The system will use OCR to extract information.
5.  Monitor the status of your loan application through the dashboard.

## Environment Variables

### Backend (`loan-ai-app/backend/.env`)

-   `ANTHROPIC_API_KEY`: Your API key for the Anthropic AI service, crucial for the conversational agents.
-   `DATABASE_URL`: Connection string for the PostgreSQL database (e.g., `postgresql://user:password@db:5432/dbname`).
-   Other variables as specified in `.env.example` for database credentials and application settings.

### Frontend (`loan-ai-app/frontend/.env.local` - or similar for Next.js)

-   `NEXT_PUBLIC_BACKEND_URL`: The URL of your backend API (e.g., `http://localhost:8000`).
