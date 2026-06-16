# 1. Define a lightweight base image
FROM python:3.11-alpine

# 2. Set the working directory inside the container
WORKDIR /app

# 3. Copy application files from your machine into the container
COPY . /app

# 4. Execute commands to install dependencies during the build phase
RUN pip install --no-cache-dir -r requirements.txt

# 5. Document the port the application listens on
EXPOSE 5000

# 6. Specify the command to execute when the container starts
CMD ["python", "app.py"]
