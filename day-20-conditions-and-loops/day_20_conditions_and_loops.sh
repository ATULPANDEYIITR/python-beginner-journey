#!/bin/bash
# Day 20: Run all implementations and tests

set -e

echo "========================================"
echo "Running Python Unit Tests..."
echo "========================================"
python3 -m unittest test_day_20_conditions_and_loops.py

echo "\n========================================"
echo "Running Python Implementation..."
echo "========================================"
python3 day_20_conditions_and_loops.py

echo "\n========================================"
echo "Running JavaScript Implementation..."
echo "========================================"
node day_20_conditions_and_loops.js

echo "\n========================================"
echo "Compiling and Running C++ Implementation..."
echo "========================================"
g++ -std=c++11 day_20_conditions_and_loops.cpp -o day_20_cpp_app
./day_20_cpp_app
rm day_20_cpp_app
