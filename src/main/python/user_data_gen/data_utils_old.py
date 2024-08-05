import uuid
import random

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


def generate_ip_address():
    """This function generates an returns a random ip address"""
    return (
        f"{random.randint(1, 255)}."
        f"{random.randint(1, 255)}."
        f"{random.randint(1, 255)}."
        f"{random.randint(1, 255)}"
    )


def generate_mac_address():
    """This function generates and returns a random MAC address"""
    return ':'.join(
        f'{random.randint(0, 255):02X}' for _ in range(6)
    )


def generate_system_triplet():
    """This function generates and returns a random system triplet"""
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


def generate_user_data(num_users):
    """This function generates a list of dictonaries which contain user data that has been generated randomly.

    Args:
        num_users (`int`): The number of users we want to randomly generate data for.

    Returns:
        `list` of `dict`: A list containing `num_users` dictionaries with random user data.
    
    """
    # init empty list to be insterted into
    user_data = []

    for i in range(num_users):
        # generates random country and city
        country = random.choice(list(COUNTRY_CITY_MAP.keys()))

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
                'city': random.choice(COUNTRY_CITY_MAP[country]),
                'country': country,
                'post_code': fake.postcode()
            },
            'email_address': fake.email(),
            'phone_number': fake.phone_number(),
            'device': {
                'ip_address': generate_ip_address(),
                'mac_address': generate_mac_address(),
                'UUID': str(uuid.uuid4()),
                'system_triplet': generate_system_triplet()
            }
        }

        # appending new data to user_data
        user_data.append(rand_user_data)

    return user_data
