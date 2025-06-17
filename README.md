# States API and Streamlit Viewer

This project provides a simple FastAPI backend that serves data about US states from a PostgreSQL database. It is deployed via Docker and includes a CI/CD pipeline using GitHub Actions for automated deployment and data refreshes.

## About the Dataset

This project uses a classic dataset containing information about the 50 states of the USA, compiled around the year 1977. The data was originally sourced from the `state.x77` dataset, which is built into the R programming language, and includes the following information for each state:

* Population
* Per capita income
* Illiteracy rate
* Life expectancy
* Murder and non-negligent manslaughter rate
* Percentage of high school graduates
* Mean number of days with minimum temperature below freezing
* Land area

The initial data seeding in this project's database migration fetches a JSON version of this dataset.

## Architecture Overview

* **Backend API:** A Python FastAPI application (`api:app`).
* **Database:** PostgreSQL, managed by Docker.
* **Database Migrations:** Alembic handles schema changes and initial data seeding.
* **Deployment:** The entire stack is containerized using Docker and `docker-compose.yml`.
* **CI/CD:** GitHub Actions automatically deploys code changes (`deploy.yml`) and runs a scheduled data refresh (`refresh-data.yml`).

## Significant Files

* `docker-compose.yml`: Defines the services (`api`, `db`) and how they connect. The source of truth for the containerized environment.
* `Dockerfile`: Builds the Python application image, installing all necessary dependencies.
* `requirements.txt`: A list of all Python packages required by the project.
* `alembic.ini`: The main configuration file for the Alembic database migration tool.
* `migrations/env.py`: The crucial Python script that a anConfigures Alembic's connection to the database, reading the environment variable.
* `.github/workflows/deploy.yml`: The CI/CD pipeline that triggers on a `git push` to deploy application code changes.
* `.github/workflows/refresh-data.yml`: A second CI/CD pipeline that runs on a daily schedule (cron job) to refresh the database content.

## Key Challenges & Lessons Learned

This project served as a deep dive into full-stack deployment. Key friction points overcome include:

1.  **Server Port Conflicts:** Native services (PostgreSQL, old Python processes) were already using ports `5432` and `8000` on the host server.
    * **Lesson:** Always check for used ports with `sudo lsof -i :<port>` on a new server before deploying.
2.  **Docker Networking:** The API container could not connect to the database container using `localhost`.
    * **Lesson:** Containers in the same Docker Compose network must use the service name (e.g., `db`) as the hostname for communication.
3.  **CI/CD Secret Management:** A single typo in a large, opaque GitHub Secret (`DO_ENV_FILE`) caused cascading, hard-to-diagnose errors.
    * **Lesson:** It's best practice to use granular, individual secrets (e.g., `POSTGRES_USER`, `POSTGRES_PASSWORD`, `POSTGRES_HOST`) and build the connection string within the workflow. This makes debugging far easier.
4.  **Application Configuration Precedence:** The final bug was that the Python code in `migrations/env.py` was ignoring all environment variables and reading a hardcoded URL from `alembic.ini`.
    * **Lesson:** Understand the full configuration chain of your application and its libraries. The `.env` file is only useful if the application code is actually configured to read from it.

## Acknowledgements

The project relied upon a number of initiatives, some of which are listed below:

* **[SQLAlchemy](https://www.sqlalchemy.org/):** As the powerful Object Relational Mapper (ORM) for all database interactions.
* **[Alembic](https://alembic.sqlalchemy.org/):** For managing database schema migrations and the initial data seeding process.
* **[PostgreSQL](https://www.postgresql.org/):** As the world's most advanced open-source relational database, serving as the project's data persistence layer.

