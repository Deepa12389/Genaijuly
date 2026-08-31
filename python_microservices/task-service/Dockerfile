FROM python:3.12-slim

WORKDIR /code

# Install dependencies first (better layer caching - only re-installs
# if requirements.txt changes, not on every code change)
COPY app/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY ./app ./app

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]