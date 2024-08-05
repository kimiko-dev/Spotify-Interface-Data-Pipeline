#!/bin/bash

# defining the number of users to generate
NUM_USERS=10000

# defining output file names
PROFILE_FILE="/home/kimiko/spotify_interface_data_pipeline/artifacts/profiling/data_utils_old_profile.prof"
TEXT_FILE="/home/kimiko/spotify_interface_data_pipeline/artifacts/profiling/data_utils_old_profile.txt"

export PYTHONPATH=/home/kimiko/spotify_interface_data_pipeline

# run the Python profiling command using a here-doc
python3 - <<EOF
import cProfile
import os
import pstats

from src.main.python.user_data_gen.data_utils_old import generate_user_data


def profile_function(num_users):
    # profiling the generate_user_data function.
    cProfile.run(f'generate_user_data({num_users})', '${PROFILE_FILE}')
    
    # writing profiling stats to the output file.
    with open('${TEXT_FILE}', 'w') as f:
        stats = pstats.Stats('${PROFILE_FILE}', stream=f)
        stats.strip_dirs().sort_stats('cumulative').print_stats()

if __name__ == '__main__':
    profile_function($NUM_USERS)
EOF

# removes .prof file
rm -f "$PROFILE_FILE"

echo "profiling complete. output saved to $TEXT_FILE."