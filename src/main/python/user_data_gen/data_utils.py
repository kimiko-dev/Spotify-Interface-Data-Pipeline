import uuid
import random

from faker import faker


# init faker
fake = Faker()

# defines country and city dictionary map
COUNTRY_CITY_MAP = {
    'Germany': ['Göttingen', 'Berlin', 'Munich', 'Hamburg', 'Cologne'],
    'Netherlands': ['Amsterdam', 'Rotterdam', 'The Hague', 'Utrecht', 'Eindhoven'],
    'UK': ['London', 'Manchester', 'Nottingham', 'Liverpool', 'Edinburgh']
}

# lambda functions for generating random values
generate_ip_address = lambda: f"{random.randint(1, 255)}.{random.randint(1, 255)}.{random.randint(1, 255)}.{random.randint(1, 255)}"
generate_mac_address = lambda: ':'.join(['{:02X}'.format(random.randint(0, 255)) for _ in range(6)])
generate_system_triplet = lambda: random.choice([
    'x86_64-pc-linux-gnu',          # Linux 64-bit
    'i686-pc-linux-gnu',            # Linux 32-bit
    'aarch64-pc-linux-gnu',         # Linux ARM64
    'x86_64-pc-macosx',             # macOS 64-bit
    'x86_64-pc-win32',              # Windows 32-bit
    'x86_64-pc-win64',              # Windows 64-bit
    'x86_64-pc-android',            # Android 64-bit
    'armv7l-pc-android',            # Android ARMv7
    'x86_64-pc-freebsd',            # FreeBSD 64-bit
    'i686-pc-freebsd'               # FreeBSD 32-bit
])

def generate_user_data(num_users):

    #init empty list to be insterted into
    user_data = []

    for i in range(num_users):
        
        #generates random country and city
        country = random.choice(list(COUNTRY_CITY_MAP.keys()))
        city = random.choice(COUNTRY_CITY_MAP[country])

        # adding random entries to dictionary
        rand_user_data = {
            'user_id' : str(uuid.uuid4()),
            'user_name' : fake.user_name(),
            'first_name' : fake.first_name(),
            'last_name' : fake.last_name(),
            'age' : random.randint(18,100),
            'address' : {
                'house_number' : fake.building_number(),
                'street_name' : fake.street_name(),
                'city' : city,
                'country' : country,
                'post_code' : fake.post_code()
            },
            'email_address' : fake.email(),
            'phone_number' : fake.phone_number(),
            'device' : {
                'ip_address' : generate_ip_address(),
                'mac_address' : generate_mac_address(),
                'UUID' : str(uuid.uuid4()),
                'system_triplet' : generate_system_triplet()
            }
        }

        # appending new data to user_data
        user_data.append(rand_user_data)

    return user_data