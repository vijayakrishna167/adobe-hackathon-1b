# ---- STAGE 1: The Builder ----
# This stage installs dependencies and downloads the model.
# It will be discarded after the build is complete.
FROM --platform=linux/amd64 python:3.11-slim as builder

WORKDIR /app

# Install the CPU-only version of torch first to avoid conflicts.
# This is the single most important step for reducing image size.
RUN pip install torch --index-url https://download.pytorch.org/whl/cpu

# Copy and install the rest of the dependencies.
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Download and cache the model within this builder stage.
RUN python -c "from sentence_transformers import SentenceTransformer; SentenceTransformer('all-MiniLM-L6-v2')"


# ---- STAGE 2: The Final Image ----
# This is the lean, final image that will be submitted.
FROM --platform=linux/amd64 python:3.11-slim

WORKDIR /app

# Copy the installed packages from the builder stage.
# This is much smaller than reinstalling everything.
COPY --from=builder /usr/local/lib/python3.11/site-packages /usr/local/lib/python3.11/site-packages

# Copy the pre-downloaded model cache from the builder stage.
# This ensures the final image is fully offline.
COPY --from=builder /root/.cache/huggingface /root/.cache/huggingface

# Copy our application code.
COPY src/ ./src/
COPY run.py .

# Set the default command to run our script.
CMD ["python", "run.py"]
