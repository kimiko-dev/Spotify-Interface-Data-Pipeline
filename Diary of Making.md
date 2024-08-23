# Spotify Interface Data Pipeline

## _Table of Contents_

1. [Introduction](#1-introduction)

2. [Generating User Data](#2-generating-user-data)

    2.1 [Generating Random Data](#21-generating-random-data)

    - 2.1.1 [Original Implementation](#211-original-implementation)

    - 2.1.2 [Creating a Bash Script to Profile `data_utils.py`](#212-creating-a-bash-script-to-profile-data_utilspy)

    - 2.1.3 [Profiling and Analysing the Old Implementation](#213-profiling-and-analysing-the-old-implementation)

    - 2.1.4 [Optimising `data_utils.py`](#214-optimising-data_utilspy)

    - 2.1.5 [Profiling and Analysing `data_utils.py`](#215-profiling-and-analysing-data_utilspy)

    - 2.1.6 [Unit Testing `data_utils.py`](#216-unit-testing-data_utilspy)

    - 2.1.7 [Creating a Bash Script to Automate Unit Testing](#217-creating-a-bash-script-to-automate-unit-testing)

## 1. Introduction


## 2. Generating User Data

<ins>__Overview__</ins> :

I will be generating a __JSON__ file containing random user data, this will be utilised in the source payload. I will performing unit and integration testing on the scripts, as well as profiling and analysing the profiles to understand how to improve the speed of execution.

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

### 2.1.6 Unit Testing `data_utils.py`
--------------------------------------

Unit tests are an essential part of a script's lifecycle. They are used to validate that individual pieces of code function as expected. By running predefined tests, unit tests help ensure that any future changes to the code do not introduce new bugs or break existing functionality.

I will now walk you through the script for unit testing, which can be found [here](https://github.com/kimiko-dev/Spotify-Interface-Data-Pipeline/blob/master/tests/unit/user_data_gen/test_data_utils.py).

---

[Line 4](https://github.com/kimiko-dev/Spotify-Interface-Data-Pipeline/blob/master/tests/unit/user_data_gen/test_data_utils.py#L4) is an important one. Here, we import the functions from the script we wish we to test. In this case, we are testing `generate_system_triplet`, `generate_user_data_chunk`, and `generate_user_data` from, you guessed it, `data_utils.py`!

---

[Lines 8 and 9](https://github.com/kimiko-dev/Spotify-Interface-Data-Pipeline/blob/master/tests/unit/user_data_gen/test_data_utils.py#L8-L9) is used to configure and set up the logging system by creating a logging instance. This will be used to generate timestamped log messages at different levels, such as `INFO`, `ERROR` and `DEBUG`, to provide detailed insights into the testing process.

---

Now we will be creating a [class](https://github.com/kimiko-dev/Spotify-Interface-Data-Pipeline/blob/master/tests/unit/user_data_gen/test_data_utils.py#L11) to customise the test results to out liking, with the class being called `CustomTestResult`. This class will inherit from `unittest.TextTestResult`, allowing us to modify the behavior of the `TextTestResult` class provided by the `unittest` module.

First off, we define the [`startTest`](https://github.com/kimiko-dev/Spotify-Interface-Data-Pipeline/blob/master/tests/unit/user_data_gen/test_data_utils.py#L13-L16) method, which takes in `test` as an input. Here, `test` refers to all functions we define in our test class, which begin with `test_`. The first line is necessary since we wish to inherit the functionality from `unittest`'s `startTest`. This inheritance is denoted by the `super().` at the start! Now, we use the method `stream.write(...)` to change the output of `startTest`. Specifically, we write a seperator line to `STDOUT`, which is a line of `---` to visually separate the tests performed as this increases readability for me. Finally, we use the method `stream.flush()` to ensure that any buffered data in the stream is written out immediately, this ensures that the output is up to date and visible without any delay.

Now we define the [`stopTest`](https://github.com/kimiko-dev/Spotify-Interface-Data-Pipeline/blob/master/tests/unit/user_data_gen/test_data_utils.py#L18-L20) method, again taking in `test` as an input, which was explained above. Similar to above, we wish to inherit the functionality from `unittest`'s `stopTest`. There is no need for `stream.write()` here since we have already used a line seperator for `startTest`. Finally, we end the method with `stream.flush()`.

The [next three methods](https://github.com/kimiko-dev/Spotify-Interface-Data-Pipeline/blob/master/tests/unit/user_data_gen/test_data_utils.py#L22-L29) all serve similar functionality - they tell us information on the outcome of the test. We will be utilising `logger` for all of them, specifically `logger.info` for `addSuccess` - telling the user that the test was passed, alongside the test that was completed. And for the last two, `logger.error` is used to signify there is an error. I added a greater level of detail to these outputs by passing `{self._exc_info_to_string(err, test)}` to the `f` string inside `logger.error`', since this will convert the error into a readable format.

---

We then define the class [`CustomTestRunner`](https://github.com/kimiko-dev/Spotify-Interface-Data-Pipeline/blob/master/tests/unit/user_data_gen/test_data_utils.py#L31), which inherits the `TextTestRunner` method for the `unittest` module. This will be used to override specific methods of `TextTestRunner` to implement the customised behaviour outlined above.

Starting off, we define the [`__init__`](https://github.com/kimiko-dev/Spotify-Interface-Data-Pipeline/blob/master/tests/unit/user_data_gen/test_data_utils.py#L32-L3) method inside the class, which simply inherts `__init__` from `unittest.TextTestRunner`. We need to do this to initialise the class. By calling the superclass's `__init__` method, we ensure that the `CustomTestRunner` class is properly set up with the default initialisation behavior provided by `TextTestRunner`, allowing us to add or modify functionality as needed.

Up next is overriding the [`_makeResult`](https://github.com/kimiko-dev/Spotify-Interface-Data-Pipeline/blob/master/tests/unit/user_data_gen/test_data_utils.py#L35-L36) method. This method is intended to create and return a custom result class, in our case it is `CustomTestResult`, as in this class we have customised outputs for. To put it simply, this method is used to run tests with the customised result handling. The `return` of this method contains `CustomTestResult` with the following parameters:

- `self.stream`: The output stream where results are written (e.g., standard output).
- `self.descriptions`: A boolean that indicates whether to include test descriptions in the output.
- `self.verbosity`: An integer that controls the level of detail in the output.

In summary, overriding `_makeResult` ensures that our custom result class is used to handle and format the test results.

---

We will now be looking at the main class that is used for testing purposes, which is [`TestDataUtils`](https://github.com/kimiko-dev/Spotify-Interface-Data-Pipeline/blob/master/tests/unit/user_data_gen/test_data_utils.py#L38) class.

Some configuration is still required inside this class, just so we can ensure that the output is customised to our liking! 

First up, we define a class method, which is indicated by `@classmethod` above the definition of the [`setUpClass`](https://github.com/kimiko-dev/Spotify-Interface-Data-Pipeline/blob/master/tests/unit/user_data_gen/test_data_utils.py#L41) method. The function of this class method is to notify the user that the `TestDataUtils` tests are about to start, using `logger` to log the message.

Proceeding this, we define the method [`setUp`](https://github.com/kimiko-dev/Spotify-Interface-Data-Pipeline/blob/master/tests/unit/user_data_gen/test_data_utils.py#L44). This is used to 'set up' the test before it is executed. Namely, we will be logging a message which the user that the test has been started. 

- On [line 45](https://github.com/kimiko-dev/Spotify-Interface-Data-Pipeline/blob/master/tests/unit/user_data_gen/test_data_utils.py#L45) is sets up a logger instance specifically for this test class, which can be used to output the log messages for this class. 
- On [line 46](https://github.com/kimiko-dev/Spotify-Interface-Data-Pipeline/blob/master/tests/unit/user_data_gen/test_data_utils.py#L46), we log a message which indicates the start of the specific test method.

Next, we define the [`tearDown`](https://github.com/kimiko-dev/Spotify-Interface-Data-Pipeline/blob/master/tests/unit/user_data_gen/test_data_utils.py#L48) method. Similar to the `setUp` method, the `tearDown` method is executed after each test has finished. In this method, we log a message indicating the finish of the current test method.

---

We can now finally move onto looking at methods which will test functions in `data_utils.py`!!

We will start off by looking at [`test_generate_system_triplet`](https://github.com/kimiko-dev/Spotify-Interface-Data-Pipeline/blob/master/tests/unit/user_data_gen/test_data_utils.py#L52-L70). This test is really simple! Let me walk you through it:

1. We define `list_of_valid_outputs`, which is a list that contains all the accepted outputs for the function `generate_system_triplet`.

2. Then, we call the `generate_system_triplet` function, and set the variable `system_triplet` with this.

3. Next, we use `logger` to log the `system_triplet` in debug mode, just so we can cross reference the output it gave to us in case of failure (this may give us an understanding to why the function we are testing is not performing correctly.)

4. Finally, we use `assertIn` to see if the `system_triplet` we generated is actually in the `list_of_valid_outputs`.

Up next is another easy to understand test. In the method [`test_len_generate_user_data_chunk`](https://github.com/kimiko-dev/Spotify-Interface-Data-Pipeline/blob/master/tests/unit/user_data_gen/test_data_utils.py#L72-L76) we are simply checking that the `generate_user_data_chunk` outputs the correct number of results. This requires one line, which is:

```
assertEqual(len(generate_user_data_chunk(0,x)), x)
```

- `x` is the number of data points we expect the function to generate.

- We are asserting the length of the output matches `x`. 

To ensure the function behaves correctly, it's a good practice to test both small and large values for `x`:

1. __Small Value__: Testing with a small value of `x` ensures that the function works as expected in straightforward cases.

2. __Large Value__: Testing with a larger value of `x` checks that the function can handle a greater number of data points without performance issues or errors.

This approach validates both the correctness of the output for typical cases and the function’s ability to handle larger inputs efficiently.

Let us now move onto looking at the method [`test_structure_generate_user_data_chunk`](https://github.com/kimiko-dev/Spotify-Interface-Data-Pipeline/blob/master/tests/unit/user_data_gen/test_data_utils.py#L78-L149)

This method is an important once, since we wish to validate the structure of the dictionaries we generate. This ensures that they keys are indeed inside the dictionary, and the values generated are of the correct type! (We will also be checking that the country and city values are correct to the ones prescribed.)

But first, it is key to note the line:

```
@patch('src.main.python.user_data_gen.data_utils.generate_system_triplet', return_value='mocked_triplet')
```

We are using the `@patch` decorator here since we wish to suppress the output of the `generate_system_triplet` function from `data_utils.py`. This is crucial since we are unit testing, where we only wish to test one function in isolation, rather than any functions that are called interally. By patching `generate_system_triplet`, we replace its actual implementation with one that is mocked, with an output as `mocked_triplet`.

This ensures that the behaviour of `generate_user_data_chunk` is tested independently of the `generate_system_triplet` function. In fact, if we did not patch this function, we would actually be performing __integration testing__, where multiple componets (such as functions) are tested together.

With patching aside, we can now look at the meat and bones of this method in question.

On [line 81](https://github.com/kimiko-dev/Spotify-Interface-Data-Pipeline/blob/master/tests/unit/user_data_gen/test_data_utils.py#L81), we simply call `generate_user_data_chunk` and set it to the variable `results`, since this is the output data we wish to test.

Next, we define the [`CITY_COUNTRY_MAP`](https://github.com/kimiko-dev/Spotify-Interface-Data-Pipeline/blob/master/tests/unit/user_data_gen/test_data_utils.py#L84-L94), which is a dictionary with keys as countries and values as lists of cities corresponding to that country. This will be used when varifying the output data.

Following this, we define the list [`countries`](https://github.com/kimiko-dev/Spotify-Interface-Data-Pipeline/blob/master/tests/unit/user_data_gen/test_data_utils.py#L96) which is a list of the keys in `COUNTRY_CITY_MAP` (we do this to save on computation).

Now, we will be validating the structure of the data in the list, to do this we shall start a [`for` loop using `data in result`](https://github.com/kimiko-dev/Spotify-Interface-Data-Pipeline/blob/master/tests/unit/user_data_gen/test_data_utils.py#L98-L149). This is done to validate all dictionaries in `results`.

In the [first block (lines 100-116)](https://github.com/kimiko-dev/Spotify-Interface-Data-Pipeline/blob/master/tests/unit/user_data_gen/test_data_utils.py#L100-116) we are validating:

- that the data is indeed a dictionary using `assertIsInstance`.
- the top level keys where we use `assertIn` to check that the keys are present in the dictionary.
- the top level values for the keys are of correct type using `assertIsInstance`.

In the [second block (lines 119-130)](https://github.com/kimiko-dev/Spotify-Interface-Data-Pipeline/blob/master/tests/unit/user_data_gen/test_data_utils.py#L112-L123), we first set `address = data['address']` for brevity, and then check that the:

- `address` is indeed a dictionary using `assertIsInstance`.
- keys exist using `assertIn`.
- values for the keys are of correct type using `assertIsInstance`.

In the [third block (lines 132-133)](https://github.com/kimiko-dev/Spotify-Interface-Data-Pipeline/blob/master/tests/unit/user_data_gen/test_data_utils.py#L132-L133) we are validating that the `country` and `city` in address are in fact in `countries` and also the correct city in `COUNTRY_CITY_MAP`.

In the [fourth block (lines 136-147)](https://github.com/kimiko-dev/Spotify-Interface-Data-Pipeline/blob/master/tests/unit/user_data_gen/test_data_utils.py#L136-L147), similar to before, we set `device = data['device']` for brevity, and then check that the:

- `device` is indeed a dictionary using `assertIsInstance`.
- keys exist using `assertIn`.
- values for the keys are of correct type using `assertIsInstance`.

Which concludes `test_structure_generate_user_data`.

Now we move on to the final method of the test class, with that being [`test_generate_user_data`](https://github.com/kimiko-dev/Spotify-Interface-Data-Pipeline/blob/master/tests/unit/user_data_gen/test_data_utils.py#L150-L164). Unit testing `generate_user_data` is challenging due to the use of the `multiprocessing` module. To do so, we need to mock two things, `Pool` and `cpu_count` which can be seen [here](https://github.com/kimiko-dev/Spotify-Interface-Data-Pipeline/blob/master/tests/unit/user_data_gen/test_data_utils.py#L150-L151).

We mock `Pool` because `Pool` is responsible for managing a pool of worker processes. By mocking `Pool`, we can simulate how the pool distributes tasks across processes without actually spawning multiple processes, which can be difficult to control in a test environment. This also allows us to directly control the output of `starmap`, the method used to parallelise the execution of the function.

Similarly, we mock `cpu_count` to control the number of CPU cores the function thinks are available. This allows us to test how the function behaves under specific conditions (in our case, when 3 cores are available) regardless of the actual hardware the tests are running on.

You may be wondering what this is:

```
mock_pool_instance = mock_pool.return_value.__enter__.return_value
```

Simply put, it is used to mock the behaviour of the `multiprocessing.Pool` object when it is used as a context manager.

Let me explain what the `.__enter__` part signifies. When we enter the with block, the `__enter__` method of the context manager is called, which typically sets up the resource or environment the context manager is managing. In our case, when we use the `multiprocessing.Pool` object within a with statement, the `__enter__` method is responsible for initialising the pool of worker processes and returning the Pool instance.

I will break down the logic of the code snippet above:

- `mock_pool.return_value` provides a mock of the `Pool` object.

- `mock_pool.return_value.__enter__` mock the `__enter__` method of the `Pool` object.

- `mock_pool.return_value.__enter__.return_value` provides the mock instance that is actually used inside the `with` block, representing the `Pool` object.

Most of the heavy lifting is done, but we must do one more thing to finalise this specific mock, that is use `mock_pool_instance` so we can define what happens when the `starmap` object is called. Which is done by using:

```
mock_pool_instance.starmap.return_value = [
            [{'user_id': i} for i in range(10)],
            [{'user_id': i} for i in range(10, 20)],
            [{'user_id': i} for i in range(20, 25)],
        ]
```

(This is found on [line 154-158](https://github.com/kimiko-dev/Spotify-Interface-Data-Pipeline/blob/master/tests/unit/user_data_gen/test_data_utils.py#L154-158))

This last step ensures that when `starmap` is called on the `pool` object within the with block, it returns the predefined list, allowing the test to proceed with controlled and predictable behavior.

On [lines 160-161](https://github.com/kimiko-dev/Spotify-Interface-Data-Pipeline/blob/master/tests/unit/user_data_gen/test_data_utils.py#L160-161) we simply state the `num_users` we wish to use, and call the function we are testing, that is `generate_user_data`. 

Finally, on [lines 163-164](https://github.com/kimiko-dev/Spotify-Interface-Data-Pipeline/blob/master/tests/unit/user_data_gen/test_data_utils.py#L163-164) we are testing that the list of lists has been flattened correctly.

We have now made it to the end of the main testing class!!

---

Finally, to end this script off, we simply write:

```
if __name__ == '__main__':
    unittest.main(testRunner=CustomTestRunner(verbosity=1))
```

Which ensures the code in the script is executed directly, and it runs all unit tests using a custom test runner that we set up earlier for a customised output.

### 2.1.7 Creating a Bash Script to Automate Unit Testing
---------------------------------------------------------

I created the bash script [`unit_test.sh`](https://github.com/kimiko-dev/Spotify-Interface-Data-Pipeline/blob/master/scripts/user_data_gen/data_utils/unit_test.sh) to automate unit testing. The script runs the unit testing script, and stores the output in an appropriate text file.

Let me walk you though the bash script!

We start off by declaring: 

```
#!/bin/bash
```

Which is the shebang for bash, which tells the shell which shell language we intend to use.

Next, we have the lines:

```
DATE_TIME=$(date "+%Y-%m-%d_%H-%M-%S")
TEXT_FILE="/home/kimiko/spotify_interface_data_pipeline/artifacts/unit_testing/user_data_gen/data_utils/${DATE_TIME}-data_utils_unittest.txt"
```

Which sets the `DATE_TIME` to the current date and time, and sets the path for the `TEXT_FILE`s intended location - where we use `DATE_TIME` in the file name to signify when the test took place.

Then, we state:

```
export PYTHONPATH=/home/kimiko/spotify_interface_data_pipeline
```

Which `export`s the `PYTHONPATH` environment variable. This is used to tell Python to include this directory in the search path for modules - ensuring our unit testing script can be recognised and executed.

Next up, we have the following line:

```
cd /home/kimiko/spotify_interface_data_pipeline/tests/unit/user_data_gen || { echo "Failed to change directory"; exit 1; }
```

Which changes the directory to where the unit test script is located. We must bring attention to the `||` operator, it is in fact an OR operator, meaning that if the the first part fails (i.e. it cannot change to the specified directory), it executes the second part (in our case this will echo a message, telling the user that it "Failed to change directory" and then exits the shell script with an error code of `1`).

Following this, we execute the unit testing script by stating:

```
python3 test_data_utils.py > "$TEXT_FILE" 2>&1
```

Here:

- `python3` is the python interpreter we are using.

- `test_data_utils.py` is the script with all the unit tests we wish to execute.

- `> "$TEXT_FILE"` redirects the `STDOUT` of the unit testing script to be written to the specified `TEXT_FILE`, rather than being displayed in the terminal.

- `2>&1` redirects `STDERR` to `STDOUT`, meaning both standard output and standard error will be combined and sent to the same destination - `TEXT_FILE`.

Finally, we finish the shell script with:

```
echo "File has been created"
```

Which simply displays a message in the terminal telling the user that the text file has been created!

---

We are almost ready to execute the shell script. We need to give it the correct permissions to be executed, which can be done by running the following in a terminal:

```
chmod +x /path/to/unit_test.sh
```

Now, we can finally run the bash script by executing the command in the terminal:

```
/path/to/unit_test.py
```

We are greeted with a message of completion, meaning we can inspect the shell script - which can be found [here](https://github.com/kimiko-dev/Spotify-Interface-Data-Pipeline/blob/master/artifacts/unit_testing/user_data_gen/data_utils/2024-08-16_19-37-35-data_utils_unittest.txt)

We can see that putting in the work to customise the output for the unit test was worthwhile, since we have a neatly formatted and detailed output! 

Analysing the output for the unit test of `data_utils.py` shows us that all tests have been run without any errors, meaning the script has passed all checks.

Having this shell script enhances reusability because each time the `data_utils.py` script is modified, we can simply execute the shell script from the terminal to effortlessly run the tests. Additionally, the outputs are stored in text files that are differentiated by date and time, allowing us to review historical outputs and track changes across different iterations.