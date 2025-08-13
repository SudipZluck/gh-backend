# Grateful Heart API

The Grateful Heart API is a comprehensive backend service for a modern blogging platform, designed to provide a seamless and engaging user experience. It is built with FastAPI and SQLModel, offering a robust and scalable architecture for managing users, journals, comments, and social interactions.

## Features

- **User Management**: Secure user registration, login, and profile management with JWT-based authentication.
- **Journaling**: Create, edit, and delete journal entries with rich content support.
- **Commenting**: Engage with the community by adding, updating, and deleting comments on journals.
- **Social Interactions**: Follow and block other users to customize your social experience.
- **Subscriptions and Payments**: Manage user subscriptions and payment methods with a flexible and secure system.
- **Prompts**: Inspire creativity with daily and user-generated prompts.
- **Content Moderation**: Report inappropriate journals and users to maintain a safe and positive community.

## Technology Stack

- **Backend**: FastAPI, Python 3.12
- **Database**: MySQL, SQLModel, Alembic
- **Authentication**: JWT (JSON Web Tokens)
- **Dependency Management**: pip

## Project Structure

```
.
├── alembic/
├── db/
├── middleware/
├── models/
├── routers/
├── schemas/
├── security/
├── main.py
├── requirements.txt
└── README.md
```

## Setup and Installation

1.  **Clone the repository**:

    ```bash
    git clone https://github.com/your-username/gh-backend.git
    cd gh-backend
    ```

2.  **Create and activate a virtual environment**:

    ```bash
    python3 -m venv grateful-heart
    source grateful-heart/bin/activate
    ```

3.  **Install the dependencies**:

    ```bash
    pip install -r requirements.txt
    ```

4.  **Set up the environment variables**:

    Create a `.env` file in the root of the project and add the following variables:

    ```env
    DB_HOST=127.0.0.1
    DB_PORT=3306
    DB_USER=root
    DB_PASSWORD=
    DB_NAME=grateful_heart
    SECRET_KEY=your-secret-key
    ALGORITHM=HS256
    ACCESS_TOKEN_EXPIRE_MINUTES=30
    ```

5.  **Run the application**:

    ```bash
    uvicorn main:app --reload
    ```

    The application will be available at `http://127.0.0.1:8000`.

## API Endpoints

The API is structured into the following modules:

-   **Auth**: `/user/signup`, `/user/login`
-   **Journals**: `/journals`
-   **Comments**: `/comments`
-   **Social**: `/social/follow`, `/social/block`
-   **Subscriptions**: `/subscriptions`, `/subscriptions/payment-methods`
-   **Prompts**: `/prompts`, `/prompts/user-prompts`
-   **Miscellaneous**: `/misc`

For detailed information about each endpoint, please refer to the auto-generated OpenAPI documentation at `/docs`.