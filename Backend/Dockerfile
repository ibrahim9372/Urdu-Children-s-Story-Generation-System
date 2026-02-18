# Use a lightweight Python image
FROM python:3.11-slim

# Set the working directory inside the container
WORKDIR /app

# Copy the requirements first (to cache dependencies)
# We use COPY . . if you want to copy everything, but it's better to be specific
COPY Backend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the Backend code
COPY Backend/ .

# IMPORTANT: Copy the model logic and artifacts from parent directories
# Note: When building, the "context" should be the root of the project
COPY Tokenizer/ /app/Tokenizer/
COPY Trigram_LM/ /app/Trigram_LM/

# Expose the port FastAPI runs on
EXPOSE 8000

# Start the application
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
