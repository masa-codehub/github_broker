# Getting Started Guide for New Contributors

## 1. Introduction

Welcome to the project! This guide will help you set up your development environment and understand the basic workflow of the `github_broker` project. By following these steps, you'll be able to run the core components locally and start contributing.

## 2. Prerequisites

Before you begin, ensure you have the following tools installed on your system:

*   **Python 3.9+**: We recommend using `pyenv` or `conda` for managing Python versions.
    *   [Python Official Website](https://www.python.org/downloads/)
*   **Docker & Docker Compose**: Essential for running Redis and other services.
    *   [Docker Desktop](https://www.docker.com/products/docker-desktop)
*   **Git**: For version control.
    *   [Git Official Website](https://git-scm.com/downloads)

## 3. Environment Setup

### 3.1. Clone the Repository

First, clone the project repository to your local machine:

```bash
git clone https://github.com/masa-codehub/github_broker.git
cd github_broker
```

### 3.2. Set up `.env` File

The project uses environment variables for configuration. You'll need to create a `.env` file in the root directory. You can use the sample files in the `.build/context/secrets/` directory as a reference.

1.  Create a `.env` file in the root directory of the project:
    ```bash
    touch .env
    ```
2.  Open `.env` and add the necessary environment variables. At a minimum, you'll need:
    *   `GITHUB_TOKEN`: Your GitHub Personal Access Token with appropriate permissions (repo, workflow).
    *   `GEMINI_API_KEY`: Your Google Gemini API Key.

    Refer to `.build/context/secrets/github_token.sample` and `.build/context/secrets/gemini_api_key.sample` for the expected format.

    **Example `.env` content:**
    ```
    GITHUB_TOKEN=your_github_token_here
    GEMINI_API_KEY=your_gemini_api_key_here
    ```

### 3.3. Install Dependencies

Install the Python dependencies using `pip`:

```bash
pip install -r requirements.txt
```

## 4. Running Core Components Locally

The `github_broker` project consists of two main components: `broker_main.py` (the broker) and `agents_main.py` (the agent runner).

### 4.1. Start Dependent Services (Redis)

The project uses Redis for task queuing. Start Redis using Docker Compose:

```bash
docker-compose -f .build/context/docker-compose.yml up -d redis
```

### 4.2. Run the Broker

The broker is responsible for fetching tasks from GitHub and pushing them to Redis.

```bash
python broker_main.py
```

### 4.3. Run the Agent Runner

The agent runner pulls tasks from Redis, executes the agents, and updates GitHub.

```bash
python agents_main.py
```

## 5. Verifying Basic Task Processing Flow

To verify that the broker and agent runner are working correctly:

1.  Ensure both `broker_main.py` and `agents_main.py` are running in separate terminals.
2.  Create a new issue in a GitHub repository that the `GITHUB_TOKEN` has access to.
3.  Observe the logs of `broker_main.py` and `agents_main.py`. You should see the broker fetching the issue and the agent runner processing it.
4.  The agent runner should eventually add a comment to the GitHub issue, indicating that it has processed the task.

## 6. Troubleshooting

*   **`GITHUB_TOKEN` or `GEMINI_API_KEY` not found**: Ensure your `.env` file is correctly set up in the root directory and contains the required keys.
*   **Redis connection issues**: Make sure Docker is running and the Redis container is up (`docker ps`).
*   **Dependency errors**: Double-check that all Python dependencies are installed (`pip install -r requirements.txt`).
*   **Agent not processing tasks**: Verify that both the broker and agent runner are running, and that new issues are being created in the monitored GitHub repository. Check the logs for any error messages.

If you encounter persistent issues, please refer to the existing documentation in `docs/guides/` or open a new issue on GitHub.
