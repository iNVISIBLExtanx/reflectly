FROM python:3.9-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# First copy the AI modules from the parent directory
COPY ../ai /app/ai/

# Then copy the backend files
COPY . .

# Copy fix script
COPY docker_fix_unknown_emotions.py /app/

# Run the fix script
RUN python /app/docker_fix_unknown_emotions.py

# Create proper Python package structure
RUN touch /app/ai/__init__.py
RUN touch /app/ai/search/__init__.py
RUN touch /app/ai/probabilistic/__init__.py
RUN touch /app/ai/agent/__init__.py

EXPOSE 5002

CMD ["python", "-m", "flask", "run", "--host=0.0.0.0", "--port=5002"]
