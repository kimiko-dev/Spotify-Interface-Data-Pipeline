#!/bin/bash

# ensures correct number of arguments.
if [ "$#" -ne 1 ]; then
    echo "Usage: $0 <implementation>"
    exit 1
fi

IMPLEMENTATION=$1

NUM_USERS=10000

DATE_TIME=$(date "+%Y-%m-%d_%H-%M-%S")

PROFILE_FILE="/home/kimiko/spotify_interface_data_pipeline/artifacts/profiling/user_data_gen/data_utils/${DATE_TIME}-data_utils_${IMPLEMENTATION}_profile.prof"
TEXT_FILE="/home/kimiko/spotify_interface_data_pipeline/artifacts/profiling/user_data_gen/data_utils/${DATE_TIME}-data_utils_${IMPLEMENTATION}_profile.txt"

export PYTHONPATH=/home/kimiko/spotify_interface_data_pipeline

# profile the data_utils python script(s). this one script is able to generate profiles for the new and old data
python3 - <<EOF
import cProfile
import pstats


# dynamically import the appropriate module based on implementation
if "${IMPLEMENTATION}" == "old":
    from src.main.python.user_data_gen.data_utils_old import generate_user_data
elif "${IMPLEMENTATION}" == "new":
    from src.main.python.user_data_gen.data_utils import generate_user_data
else:
    raise ValueError("Unknown implementation specified. Use 'old' or 'new'. (BE MINDFUL OF CAPITALISATION!!)")

def profile_function(num_users):
    cProfile.run(f'generate_user_data({num_users})', '${PROFILE_FILE}')
    with open('${TEXT_FILE}', 'w') as f:
        stats = pstats.Stats('${PROFILE_FILE}', stream=f)
        stats.strip_dirs().sort_stats('cumulative').print_stats()

if __name__ == '__main__':
    profile_function($NUM_USERS)
    print("Profiling complete. Output saved to ${TEXT_FILE}.")
EOF

# removing .prof file.
rm -f "$PROFILE_FILE"