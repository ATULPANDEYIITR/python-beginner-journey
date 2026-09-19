# Use official lightweight Python image
FROM python:3.10-slim

# Set working directory
WORKDIR /app

# Copy all project files into the container
COPY . /app

# Install Node.js and G++ to run JS and C++ examples
RUN apt-get update && apt-get install -y \
    nodejs \
    g++ \
    && rm -rf /var/lib/apt/lists/*

# Compile C++ implementation
RUN g++ -O3 day_20_conditions_and_loops.cpp -o day_20_cpp_app

# Default command to run tests and execute all implementations
CMD ["sh", "-c", "python -m unittest test_day_20_conditions_and_loops.py && python day_20_conditions_and_loops.py && node day_20_conditions_and_loops.js && ./day_20_cpp_app"]
