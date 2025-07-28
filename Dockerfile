# Dockerfile

FROM python:3.10

# Install PyMuPDF
RUN pip install --no-cache-dir pymupdf

WORKDIR /app

# Copy our solution script
COPY solution.py .

# Entrypoint processes all PDFs under /app/input
ENTRYPOINT ["python", "solution.py"]
