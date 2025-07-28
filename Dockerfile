# Dockerfile

FROM python:3.10

# Install PyMuPDF
RUN pip install --no-cache-dir pymupdf

WORKDIR /app

# Copy our solution script
COPY solution.py .

# Create input/output directories
RUN mkdir -p /app/input /app/output

# Entrypoint processes all PDFs under /app/input
ENTRYPOINT ["python", "solution.py"]
