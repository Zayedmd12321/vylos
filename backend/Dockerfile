FROM python:3.13-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# 3. Directory - App root
WORKDIR /app

# 4. Dependencies
COPY backend/requirements.txt . 
RUN pip install --no-cache-dir -r requirements.txt

# 5. Code - Copy backend code into /app/backend
COPY backend/ ./backend/

# 6. Ensure the shared projects directory exists inside the container
RUN mkdir -p /app/projects

# Set working directory to where main.py lives
WORKDIR /app/backend

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]