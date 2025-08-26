# Social Media Analysis API

This project is a FastAPI application that provides user authentication, runs social media analysis, and generates PDF reports.

## Setup

1.  **Install dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

2.  **Run the application:**
    ```bash
    uvicorn app.main:app --reload
    ```

## API Endpoints

-   `/auth/register`: Register a new user.
-   `/auth/login`: Log in to get a JWT token.
-   `POST /api/analyze/`: Upload a CSV file to run analysis. This creates a report record and returns its metadata.
-   `GET /api/reports/`: Get a list of all reports you have generated.
-   `GET /api/reports/{report_id}`: Download a specific PDF report by its ID.
