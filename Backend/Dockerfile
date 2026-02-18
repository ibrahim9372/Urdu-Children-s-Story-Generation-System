# Use a lightweight Python image
FROM python:3.11-slim

# Set the working directory inside the container
WORKDIR /app

# Copy the requirements first
COPY Backend/requirements.txt ./Backend/
RUN pip install --no-cache-dir -r ./Backend/requirements.txt

# Copy the folders while preserving the hierarchy
COPY Backend/ ./Backend/
COPY Tokenizer/ ./Tokenizer/
COPY Trigram_LM/ ./Trigram_LM/

# Run the application from the Backend directory to match local path resolution
WORKDIR /app/Backend

# Expose the port FastAPI runs on
EXPOSE 8000

# Start the application
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
