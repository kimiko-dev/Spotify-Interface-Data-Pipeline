#!/bin/bash

DATE_TIME=$(date "+%Y-%m-%d_%H-%M-%S")
TEXT_FILE="/home/kimiko/spotify_interface_data_pipeline/artifacts/unit_testing/user_data_gen/data_utils/${DATE_TIME}-data_utils_unittest.txt"

export PYTHONPATH=/home/kimiko/spotify_interface_data_pipeline

cd /home/kimiko/spotify_interface_data_pipeline/tests/unit/user_data_gen || { echo "Failed to change directory"; exit 1; }

python3 test_data_utils.py > "$TEXT_FILE" 2>&1

echo "File has been created"