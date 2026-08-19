# Use official lightweight Python base image
FROM python:3.10-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV DEBIAN_FRONTEND=noninteractive

# Install system dependencies & LaTeX compiler
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    curl \
    git \
    texlive-latex-base \
    texlive-latex-extra \
    texlive-fonts-recommended \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Install Playwright Firefox browser binary
RUN playwright install firefox
RUN playwright install-deps firefox

# Copy application source code & main entrypoint
COPY app ./app
COPY main.py .

# Create data directories
RUN mkdir -p data/uploads data/output data/chrome_user_profile data/firefox_user_profile data/brave_user_profile

# Expose Streamlit default port 8501
EXPOSE 8501

# Healthcheck endpoint
HEALTHCHECK CMD curl --fail http://localhost:8501/_stcore/health || exit 1

# Launch Streamlit Dashboard
CMD ["streamlit", "run", "app/ui/dashboard.py", "--server.port=8501", "--server.address=0.0.0.0"]
