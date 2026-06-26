FROM python:3.10-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    postgresql-client \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python packages
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Install dbt
RUN pip install dbt-postgres

# Copy the rest of the application
COPY . .

# Create directories for data and logs
RUN mkdir -p data/raw logs

EXPOSE 8000 3000

CMD ["/bin/bash"]