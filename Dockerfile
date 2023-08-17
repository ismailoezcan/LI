# docker build -t ismailoezcan/python-ligainsider:latest .

# Use an official Python runtime as a parent image
FROM python:3.10-slim-buster

# Set the working directory to /app
WORKDIR /app

# Copy the current directory contents into the container at /app
COPY . /app

# Install any needed packages specified in requirements.txt
RUN pip install pandas numpy tqdm lxml requests beautifulsoup4 regex

# Run main.py when the container launches
CMD ["python", "main.py"]
