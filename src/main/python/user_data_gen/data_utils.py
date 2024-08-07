import uuid
import random
from multiprocessing import Pool, cpu_count

from faker import Faker


# init faker
fake = Faker()

# defines country and city dictionary map
COUNTRY_CITY_MAP = {
    'Germany': [
        'Göttingen', 'Berlin', 'Munich', 'Hamburg', 'Cologne'
    ],
    'Netherlands': [
        'Amsterdam', 'Rotterdam', 'The Hague', 'Utrecht', 'Eindhoven'
    ],
    'UK': [
        'London', 'Manchester', 'Nottingham', 'Liverpool', 'Edinburgh'
    ]
}


def generate_system_triplet():
    """Generates and returns a random system triplet"""
    return random.choice([
        'x86_64-pc-linux-gnu',
        'i686-pc-linux-gnu',
        'aarch64-pc-linux-gnu',
        'x86_64-pc-macosx',
        'x86_64-pc-win32',
        'x86_64-pc-win64',
        'x86_64-pc-android',
        'armv7l-pc-android',
        'x86_64-pc-freebsd',
        'i686-pc-freebsd'
    ])


def generate_user_data_chunk(start_index, end_index):
    """Generates a chunk of random user data.

    Args:
        start_index (int): The index the worker will start at.
        end_index (int): The index the worker will finish at.

    Returns:
        list of dict: A list containing `num_users / cpu_cores` dictionaries
        with random user data.

    """
    # init empty list to be insterted into
    user_data_chunk = []

    # precompute list of countries
    countries = list(COUNTRY_CITY_MAP.keys())

    for i in range(start_index, end_index):
        # generates random country city
        country = random.choice(countries)
        city = random.choice(COUNTRY_CITY_MAP[country])

        # adding random entries to dictionary
        rand_user_data = {
            'user_id': str(uuid.uuid4()),
            'user_name': fake.user_name(),
            'first_name': fake.first_name(),
            'last_name': fake.last_name(),
            'age': random.randint(18, 100),
            'address': {
                'house_number': fake.building_number(),
                'street_name': fake.street_name(),
                'city': city,
                'country': country,
                'post_code': fake.postcode()
            },
            'email_address': fake.email(),
            'phone_number': fake.phone_number(),
            'device': {
                'ipv4_address': fake.ipv4(),
                'ipv6_address': fake.ipv6(),
                'mac_address': fake.mac_address(),
                'UUID': str(uuid.uuid4()),
                'system_triplet': generate_system_triplet()
            }
        }

        # appending new data to user_data chunk
        user_data_chunk.append(rand_user_data)

    return user_data_chunk


def generate_user_data(num_users):
    """Generates user data using multiprocessing.

    Args:
        num_users (int): The number of data points for users you want
        to generate.

    Returns:
        list of dict: A list containing `num_users` dictionaries with
        random user data.

    """
    # finding the chunk size.
    num_workers = cpu_count()
    chunk_size = num_users // num_workers

    # creating ranges for each worker.
    ranges = [(i * chunk_size, (i + 1) * chunk_size) for i in range(num_workers)]
    ranges[-1] = (ranges[-1][0], num_users)  # ensure last chunk goes to the end.

    # creates a pool for the worker processes.
    with Pool(num_workers) as pool:
        results = pool.starmap(generate_user_data_chunk, ranges)

    # combining chunks
    user_data = [item for sublist in results for item in sublist]

    return user_data
