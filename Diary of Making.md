# Spotify Interface Data Pipeline

## _Table of Contents_

1. [Introduction](#1-introduction)

2. [Generating User Data](#2-generating-user-data)

    2.1 [Generating Random Data](#21-generating-random-data)

    - 2.1.1 [Original Implementation](#211-original-implementation)

    - 2.1.2 [Creating a Bash Script to Profile `data_utils.py`](#212-creating-a-bash-script-to-profile-data_utilspy)

    - 2.1.3 [Profiling and Analysing the Old Implementation](#213-profiling-and-analysing-the-old-implementation)

    - 2.1.4 [Optimising `data_utils.py`](#214-optimising-data_utilspy)

    - 2.1.5 [2.1.5 Profiling and Analysing `data_utils.py`](#215-profiling-and-analysing-data_utilspy)

## 1. Introduction


## 2. Generating User Data

<ins>__Overview__</ins> :

I will be generating a __JSON__ file containing random user data, this will be utilised in the source payload. I will performing unit and functional testing on the scripts, as well as profiling and analysing the profiles to understand how to improve the speed of execution.

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

### 2.1.3 Profiling and Analysing the Old Implementation
--------------------------------------------------------

To generate a profile for the [old implementation](https://github.com/kimiko-dev/Spotify-Interface-Data-Pipeline/blob/master/src/main/python/user_data_gen/data_utils_old.py), we simply run:

```
path\to\data_utils\profiling.sh old
```

Notice the added `old` at the end of the command (remember that we defined this parameter to be passed into the shell script so we can import the older implementation of the data_utils module).

After receiving a message in the terminal saying the profiling has been complete, we are free to open and analyse the [`.txt` file](https://github.com/kimiko-dev/Spotify-Interface-Data-Pipeline/blob/master/artifacts/profiling/user_data_gen/data_utils/2024-08-07_15-16-52-data_utils_old_profile.txt) generated.

- We can see that the total time taken for this function generate a list of 10,000 user data points is 12.154 seconds, which seems a bit slow.

- The number of function calls is 11119220

Let us take a deeper look into what function calls are the most time consuming, but first let me outline the key metrics:

1. `ncalls`: Number of calls to the function. 
2. `tottime`: Total time spent in the function (excluding sub-functions).
3. `percall`: Average time per call, calculated as `tottime / ncalls`.
4. `cumtime`: Cumulative time spent in the function AND its sub-functions.
5. `percall` (`cumtime`):  Average time per call including sub-functions calculated as `cumtime / ncalls`.

After establishing what these metrics mean, we seek functions with high `ncalls`, `tottime` and `cumtime`!

We can see:

- `generate_user_data` has the highest `tottime` and `cumtime`, but this is obviously to be expected since this is the function we are profiling!

- `random_element` and `random_elements` are frequently called and have high `cumtime`s. But this cannot be avoided due to the use of these in `Faker`, we can see it in the source code [here](https://github.com/joke2k/faker/blob/master/faker/providers/phone_number/__init__.py#L324).

- `{method 'sub' of 're.Pattern' objects}` also has a high `cumtime`, which points to a heavy use of regex. Again, we cannot really avoid this since it is used in `Faker` to validate the data it produces, we can see it [here](https://github.com/joke2k/faker/blob/master/faker/providers/__init__.py#L627)

This isn't really helpful for us since we cannot change any of the functions with the highest `cumtime` and `tottime` to optimise the process. However, employing `multiprocessing` to delegate tasks to different cores of the CPU may be the best bet in speed up the generation of the list of dictionaries containing random user data!

### 2.1.4 Optimising `data_utils.py`
------------------------------------

To implement `multiprocessing`, we need to refactor the old `generate_user_data` function into 2 parts. These are:

- Creating data chunks.
- Processing chunks in parallel.

Let us take a deeper look at both:

1. <ins>__Creating data chunks__</ins>

This step involves generating chunks of random data. It is similar to the [`generate_user_data`](https://github.com/kimiko-dev/Spotify-Interface-Data-Pipeline/blob/master/src/main/python/user_data_gen/data_utils_old.py#L40) in [`data_utils_old.py`](https://github.com/kimiko-dev/Spotify-Interface-Data-Pipeline/blob/master/src/main/python/user_data_gen/data_utils_old.py), the function is renamed to `generate_user_data_chunk`. One change here is that we generate the list of the countries (using keys from the `COUNTRY_CITY_MAP`) outside of the `for` loop, since we don't want to remake the list for each pass of the loop as this will slow the execution of the script down a bit. The function returns a chunk of random user data. The other main change we implement is by passing `start_index` and `end_index` into the function, this tells the cpu cores which range it should start and end from when generating data chunks - you will understand this more in:

2. <ins>__Processing chunks in parallel__</ins>

In this step, we generate the complete list of random user data - which is why we call the function `generate_user_data`. I will now proceed to break down the logic of this function:

```
num_workers = cpu_count()
chunk_size = num_users // num_workers
```
We find the number of workers we wish to make by using the `cpu_count()` function, which counts the number of cpu cores there are across the system. This step is neccesary since we wish you assign a worker to each of the available cores, to generate the chunks in parallel.

The `chunk_size` is used to tell the workers how many points of data they need to produce on each cpu core. We use `//` here since we require floor division to ensure an integer number is used for the range.

---
```
ranges = [(i * chunk_size, (i + 1) * chunk_size) for i in range(num_workers)]
ranges[-1] = (ranges[-1][0], num_users)
```
We then generate a list of tuples, using a list comprehension, to find the indices the workers should start and end from. The tuples in the list are of the form `(start_index, end_index)`. We simply cannot iterate over `range(chunk_size)` because the chunk size may not evenly divide the total number of random data points we wish to generate. Instead, we ensure that each worker processes a distinct portion of data.

The second line here ensures that last tuple in the list has an `end_index` of `num_users`. This is done since, as mentioned above, the total number of data points may not perfectly align with the chunk size. Let me show you an example where this could go wrong.

Suppose:

* `num_users = 102` (which is not evenly divisible by `num_workers`)
* `num_workers = 4`

In this case:

$$
\left\lfloor \frac{102}{4} \right\rfloor = 25
$$

Notice:

$$
25 \cdot 4 = 100 \neq 102
$$

Without the second line of code, the `ranges` would be:

$$
\text{ranges} = [(0, 25), (25, 50), (50, 75), (75, 100)]
$$

This results in only 100 data points being generated, but we need to generate 102 data points. By adjusting the last tuple to:

$$
(75, 102)
$$

We ensure that all 102 data points are generated!

Hopefully the above example makes it clear that if `num_workers` does not evenly divide `num_users`,  the second line ensures that the last chunk covers all remaining data points. Without this, you might generate fewer data points than intended.

---
```
with Pool(num_workers) as pool:
    results = pool.starmap(generate_user_data_chunk, ranges)
```

We use a context manager along side the `Pool` class used for `mulitiprocessing`, which creates a pool of workers, where `num_workers` specifies the number of worker processes to create. 

On the following line, `pool.starmap` is a method of the `Pool` object that maps a function (that we wish to parallelise) to a list of argument of tuples. So we wish to use the function `generate_user_data_chunk` on the list of tuples `ranges`.

It is important to note that `ranges` is a list of lists, the number of lists in `ranges` coincides with the number of workers there are (which is equal to the number of cores).

---
```
user_data = [item for sublist in results for item in sublist]
```

Here, we have a list comprehension to flatten the list of lists, i.e. combine all entries of each nested list into one list. We wish to do this since we have a number of lists equal to the number of cpu cores, and we wish to combine all of these lists into one list.

A more explicit, long form version would be as follows:
```
user_data = []

for sublist in results:
    for item in sublist:
        user_data.append(item)
```

---

Finally we `return user_data`, which is a list of dictionaries, ready to be sent to a JSON file.

### 2.1.5 Profiling and Analysing `data_utils.py`
-------------------------------------------------

Now it is time to test if the new improvements were worth it. 

We can still use the same shell script we saw in [2.1.2](#212-creating-a-bash-script-to-profile-data_utilspy). Recall, that I added functionality to test the new implementation by passing parameters into the shell script.

So, to profile `data_utils.py` we simply run:
```
path\to\data_utils\profiling.sh new
```

Once receiving a message of completion, we are able to check the [`.txt` file](https://github.com/kimiko-dev/Spotify-Interface-Data-Pipeline/blob/master/artifacts/profiling/user_data_gen/data_utils/2024-08-07_15-16-45-data_utils_new_profile.txt) generated by the shell script.

- We can see that the total time take for this function to generate a list of 10,000 user data points is 3.377 seconds, which is a massive improvement! 

- The number of function calls is 22365, again a drastic decrease from before!

Given that the time before was 12.154 seconds, we can calculate the efficiency gain by using the formula:

$$
\text{Efficiency Gain} (\%) = \left(\frac{T_{\text{old}} - T_{\text{new}}}{T_{\text{old}}}\right) \times 100
$$

So in this case, we can see that the efficiency gain is:

$$
\text{Efficiency Gain} = \left(\frac{12.154 - 3.377}{12.154}\right) \times 100 = 72.21490867 \%
$$

The main observations we can see from the profiling file are:

- `generate_user_data` has a high `cumtime` time, but this is to be expected since we are testing this function.

- `pool.py:_maintain_pool `and related functions are used heavily, which indicates that parallel processing is heavily utilised, which is what we want to see since we implemented this.

- `selectors.py:402(select)` and `select.poll` objects also have a high `cumtime` since the function is spending a lot of time waiting on I/O operations, likely due to being I/O-bound. (This means the performance is limited by the time spent on I/O operations, such as reading from or writing to files)
