FROM python:3

# Create working directory
WORKDIR /app

# Copy and install dependencies
COPY requirements.txt .
RUN pip install --upgrade pip && pip install -r requirements.txt

# Copy application code
COPY . .

# Set port environment variable
ENV PORT=5000

# Expose the port
EXPOSE 5000

CMD ["python", "main.py"]
