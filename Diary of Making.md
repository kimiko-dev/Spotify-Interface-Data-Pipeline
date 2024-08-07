# Spotify Interface Data Pipeline

## _Table of Contents_

1. [Introduction](#1-introduction)

2. [Generating User Data](#2-generating-user-data)

    2.1 [Generating Random Data](#21-generating-random-data)

    - 2.1.1 [Original Implementation](#211-original-implementation)

    - 2.1.2 [Creating a Bash Script to Profile `data_utils.py`](#212-creating-a-bash-script-to-profile-data_utilspy)

    - 2.1.3 [Profiling the Old Implementation](#213-profiling-the-old-implementation)

## 1. Introduction


## 2. Generating User Data

<ins>__Overview__</ins> :

I will be generating a __JSON__ file cointaining random user data, this will be utilised in the source payload. I will performing unit and functional testing on the scripts, as well as profiling and analysing the profiles to understand how to improve the speed of execution.

### 2.1 Generating Random Data
------------------------------

_N.B. I originally went for a slighlty different implementation to the final version of [data_utils.py](https://github.com/kimiko-dev/Spotify-Interface-Data-Pipeline/blob/master/src/main/python/user_data_gen/data_utils.py), so we will be discussing this first as most of it is relevant to the final version._

### 2.1.1 Original Implementation
---------------------------------

The main package used to generate random data for the user will be `Faker`. However, this doesn't randomly generate data points for __System Triplet__ and only gives fake city names. Later on, for batch analytics, I will be utilsing this data in queries, so it is best for it to be consistent.

After initialising the `Faker` class, I created a country and city dictonary map. It is a dictionary of lists, and will be used to randomly pick a country (using the keys) and a ramdom city based on the key chosen.

Next up, I created a function which randomly choses from a list of predefined system triplets.

Finally, we define the function that generates a list of dictionaries based on the number of users (`num_users`) we want to generate data for. Let us break down the logic of this function:

1. We initialise a list where the user data dictionary will be appended to.

2. We start a simple for loop, which will terminate when we have generated an amount of data equal to `num_users`. The logic of the loop is as follows: 

    2.1. We randomly select a key from the `COUNTRY_CITY_MAP` dictionary, which coincides with a country.

    2.2. Using this key, we randomly select an entry from the list corresponding to the keys value - this coincides with a valid city for that specific country.

    2.3. We then generate a dictionary of values using:

    - __Faker__ for the bulk of data (such as `user_name`, `phone_number`, etc.)

    - `uuid.uuid4()` is used to generate __UUIDs__ for the specifc user as well as for the users device.

    - `randint` is used to generate a random integer for age.

    -  `city` and `country`, as discussed before, are used to assign the user a country and city.

    - `generate_system_triplet` uses the function defined above to generate a random system triplet.

    2.4. The dictionary created is appended to the list `user_data`.

3. The function returns the list `user_data` when it has been filled with `num_users` amount of dictionaries. 

### 2.1.2 Creating a Bash Script to Profile `data_utils.py`
-----------------------------------------------------------

Considering this project has a heavy emphasis on optimisation, I wanted to profile the script to understand how to best increase efficiency. Admittedly, this is my first time encountering profiling, but I immediately understand its importance since it can: identify bottlenecks, understand the resource usage, as well as being able to compare implementations and measure improvements.

The approach I took to profile this script was to dynamically import the appropriate module based on if it is the old or new implementation, since this provides flexability. On top of this, I wrote a shell script for automated execution - enabling consistency.

Let's take a look at how the [`profiling.sh`](https://github.com/kimiko-dev/Spotify-Interface-Data-Pipeline/blob/master/scripts/user_data_gen/data_utils/profiling.sh) file works:

```
if [ "$#" -ne 1 ]; then
    echo "Usage: $0 <implementation>"
    exit 1
fi
```

Ensures that exactly one argument is passed into the script when it is run. If not, we provide the user with a message and exits with a status code of one, indicating an error.

---
```
IMPLEMENTATION=$1
```

Assigns the first parameter given to `IMPLEMENTATION`, which we be used later on. `$1` signifies that this is the first parameter given.

---
```
DATE_TIME=$(date "+%Y-%m-%d_%H-%M-%S")

PROFILE_FILE="/home/kimiko/spotify_interface_data_pipeline/artifacts/profiling/user_data_gen/data_utils/${DATE_TIME}-data_utils_${IMPLEMENTATION}_profile.prof"
TEXT_FILE="/home/kimiko/spotify_interface_data_pipeline/artifacts/profiling/user_data_gen/data_utils/${DATE_TIME}-data_utils_${IMPLEMENTATION}_profile.txt"
```

The first line here assigns the current date and time to `DATE_TIME`.

In the following lines we set the file paths for `PROFILE_FILE` amd `TEXT_FILE` using `DATE_TIME` and the `IMPLEMENTATION` variable. 

_N.B. I added the timestamp to the file name since this can be used to track the changes over time. However, this is rather redundant at the moment since I am using 2 files to showcase the new and old implementation. But this feature will be utilised for future scripts to discuss optimisation stratergies._

---
```
export PYTHONPATH=/home/kimiko/spotify_interface_data_pipeline
```

Sets the environment variable for `PYTHONPATH` since we want to tell python where to look for the python script I wish to test.

---
```
python3 - <<EOF
```

Lets break down the logic of the line:
- `python3` specifies that the `python3` interpreter is to be used.
- `-` tells `python3` to read the code from standard input (`STDIN`).
- `<<EOF` tells the shell to read read the following lines until it encounters `EOF` (which is an abbreviation for End Of File).

Now, lets bring it all together: We pass lines of code to the `python3` interpreter to run it as a script.

---
```
import cProfile
import pstats
```

These 2 lines import modules for python.

- `cProfile` is used for profiling.
- `pstats` is used for reading and processing data created by `cProfile`.

---
```
if "${IMPLEMENTATION}" == "old":
    from src.main.python.user_data_gen.data_utils_old import generate_user_data
elif "${IMPLEMENTATION}" == "new":
    from src.main.python.user_data_gen.data_utils import generate_user_data
else:
    raise ValueError("Unknown implementation specified. Use 'old' or 'new'. (BE MINDFUL OF CAPITALISATION!!)")
```

This conditional statement dynamically imports the function we wish to test based on the users input for `IMPLEMENTATION`. However, if the user didn't pass a valid parameter an error is shown, as well as terminating the script.

---
```
def profile_function(num_users):
    cProfile.run(f'generate_user_data({num_users})', '${PROFILE_FILE}')
    with open('${TEXT_FILE}', 'w') as f:
        stats = pstats.Stats('${PROFILE_FILE}', stream=f)
        stats.strip_dirs().sort_stats('cumulative').print_stats()
```

Here, we define a function that takes in the number of users as an input.

Next, we pass the arguments `f'generate_user_data({num_users})'` and`'${PROFILE_FILE}'` into `cProfile.run` as these specify the function we wish to profile, as well as the location for the `.prof` file to be written. 

Now using a context manager, we open the location for `TEXT_FILE` in write mode (this location doesn't exist, so the file is created first). On the following line, we use `pstats.Stats` (to create a `Stats` object) with the arguments `'${PROFILE_FILE}'` to speficty the profiling data, and `stream=f` to direct the output to the file object `f`.

On the last line, we use `stats.strip_dirs` to remove leading directory names from the filepaths in the profiling output, since this makes it easier to read. `.sort_stats('cumulative')` is used to sort the profiling statistics by cumulative time (since this will help indentify which functions are taking the most time). And lastly, `print_stats()` simply prints the formatted profiling statistics to the file object `f`.

---
```
if __name__ == '__main__':
    profile_function($NUM_USERS)
    print("Profiling complete. Output saved to ${TEXT_FILE}.")
```

We check that the script is being used directly by specifying `__name__ == '__main__'` in an if statement. Then we simply call the function `profile_function` (defined above) using `$NUM_USERS` as an argument. And finally, we print a statement telling the user where the profiling text file has been written. 

---
```
EOF 
```

Marks the end of the here document, signaling the end of the code block passed to python3.

---
```
rm -f "$PROFILE_FILE"
```

Finally, this line is provided to remove the `.prof` file since we don't need it anymore.

### 2.1.3 Profiling the Old Implementation