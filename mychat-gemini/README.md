# KingslakeBlue Assistant

This project is a voice-enabled chat assistant that can answer natural language questions about production line balancing data from a MariaDB database.

## Project Structure

- `app.py`: The main Gradio application file.
- `Dockerfile`: For containerizing the application for deployment.
- `requirements.txt`: The list of Python dependencies.
- `.env.example`: An example file for environment variables. You should rename this to `.env` and fill in your credentials.
- `.gitignore`: Specifies which files and directories to ignore for version control.
- `README.md`: This file.

## Setup Instructions

1.  **Clone the repository:**
    ```bash
    git clone <repository_url>
    cd kingslake-assistant
    ```

2.  **Create a Python virtual environment:**
    ```bash
    python3 -m venv venv
    source venv/bin/activate
    ```

3.  **Install the dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

4.  **Set up your environment variables:**
    -   Rename `.env.example` to `.env`.
    -   Open the `.env` file and add your OpenAI API key and your MariaDB database credentials.

5.  **Run the application:**
    ```bash
    python app.py
    ```
    The application will be available at `http://127.0.0.1:7860`.

## Deployment with Docker

1.  **Build the Docker image:**
    ```bash
    docker build -t kingslake-assistant .
    ```

2.  **Run the Docker container:**
    ```bash
    docker run -p 7860:7860 --env-file .env kingslake-assistant
    ```
    The application will be available at `http://localhost:7860`.
