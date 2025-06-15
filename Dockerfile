# =========================================================================
#                 Dockerfile for the FastAPI States API
# =========================================================================

# 1. BASE IMAGE
# -------------------------------------------------------------------------
# Start from an official Python base image. Using a specific version and the
# 'slim' variant is a best practice for smaller, more reproducible images.
FROM python:3.11-slim

# 2. SET UP THE ENVIRONMENT
# -------------------------------------------------------------------------
# Set the working directory inside the container. All subsequent commands
# will run relative to this path.
WORKDIR /app

# 3. INSTALL SYSTEM DEPENDENCIES
# -------------------------------------------------------------------------
# Install system libraries needed by our Python packages. 'psycopg2' needs
# 'libpq-dev' and build tools to compile correctly. We clean up the apt
# cache afterwards to keep the final image small.
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# 4. INSTALL PYTHON DEPENDENCIES
# -------------------------------------------------------------------------
# Copy the requirements file first, then install packages. This is a key
# optimization. Docker caches this layer. If you later change your app code
# but not your requirements, Docker can reuse this cached layer, making
# subsequent builds much faster.
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 5. COPY APPLICATION CODE
# -------------------------------------------------------------------------
# With dependencies installed, now copy the rest of your application code
# into the working directory inside the container.
COPY . .

# 6. EXPOSE PORT
# -------------------------------------------------------------------------
# Inform Docker that the application inside the container will listen on
# port 8000.
EXPOSE 8000

# 7. DEFINE THE RUN COMMAND
# -------------------------------------------------------------------------
# This is the command that will be executed when the container starts. We use
# Gunicorn as a production-grade process manager to run our FastAPI app.
CMD ["gunicorn", "-w", "4", "-k", "uvicorn.workers.UvicornWorker", "api:app", "--bind", "0.0.0.0:8000"]
