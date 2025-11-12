FROM python:3.11-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy MCP server code
COPY config.py server.py ./

# Run with stdio transport
CMD ["python", "server.py"]
