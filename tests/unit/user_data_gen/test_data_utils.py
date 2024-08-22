import logging
import unittest
from unittest.mock import patch, MagicMock

from src.main.python.user_data_gen.data_utils import generate_system_triplet, generate_user_data_chunk, generate_user_data


logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class CustomTestResult(unittest.TextTestResult):

    def startTest(self, test):
        super().startTest(test)
        self.stream.write(f"----------------------------------------------------------------------\n")
        self.stream.flush()

    def stopTest(self, test):
        super().stopTest(test)
        self.stream.flush()

    def addSuccess(self, test):
        logger.info(f"Test passed: {test}")

    def addFailure(self, test, err):
        logger.error(f"Test failed: {test} - {self._exc_info_to_string(err, test)}")

    def addError(self, test, err):
        logger.error(f"Test error: {test} - {self._exc_info_to_string(err, test)}")

class CustomTestRunner(unittest.TextTestRunner):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
    
    def _makeResult(self):
        return CustomTestResult(self.stream, self.descriptions, self.verbosity)

class TestDataUtils(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        logger.info("Starting TestDataUtils")

    def setUp(self):
        self.logger = logging.getLogger(self.__class__.__name__)
        self.logger.info(f"Starting test: {self._testMethodName}")

    def tearDown(self):
        self.logger.info(f"Finished test: {self._testMethodName}")


    def test_generate_system_triplet(self):

        list_of_valid_outputs = [
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
        ]

        system_triplet = generate_system_triplet()
        self.logger.debug(f"Generated system triplet: {system_triplet}")

        self.assertIn(system_triplet, list_of_valid_outputs)

    def test_len_generate_user_data_chunk(self):
        # testing length of output list, starting with: small
        self.assertEqual(len(generate_user_data_chunk(0,4)), 4)
        # now testing large
        self.assertEqual(len(generate_user_data_chunk(0,5000)), 5000)

    @patch('src.main.python.user_data_gen.data_utils.generate_system_triplet', return_value='mocked_triplet')
    def test_structure_generate_user_data_chunk(self, mock_generate_system_triplet):
        # now, we shall begin testing the structure of the data produced
        result = generate_user_data_chunk(0,10)

        # defining country city map for validation use
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

        countries = list(COUNTRY_CITY_MAP.keys())

        for data in result:
            # validating top-level keys
            self.assertIsInstance(data, dict)
            self.assertIn('user_id', data)
            self.assertIn('user_name', data)
            self.assertIn('first_name', data)
            self.assertIn('last_name', data)
            self.assertIn('age', data)
            self.assertIn('address', data)
            self.assertIn('email_address', data)
            self.assertIn('phone_number', data)
            self.assertIn('device', data)
            self.assertIsInstance(data['user_id'], str)
            self.assertIsInstance(data['user_name'], str)
            self.assertIsInstance(data['first_name'], str)
            self.assertIsInstance(data['last_name'], str)
            self.assertIsInstance(data['age'], int)
            self.assertIsInstance(data['email_address'], str)
            self.assertIsInstance(data['phone_number'], str)

            # validating `address` dictionary
            address = data['address']
            self.assertIsInstance(address, dict)
            self.assertIn('house_number', address)
            self.assertIn('street_name', address)
            self.assertIn('city', address)
            self.assertIn('country', address)
            self.assertIn('post_code', address)
            self.assertIsInstance(address['house_number'], str)
            self.assertIsInstance(address['street_name'], str)
            self.assertIsInstance(address['city'], str)
            self.assertIsInstance(address['country'], str)
            self.assertIsInstance(address['post_code'], str)

            self.assertIn(address['country'], countries)
            self.assertIn(address['city'], COUNTRY_CITY_MAP[address['country']])

            # validating `device` dictionary
            device = data['device']
            self.assertIsInstance(device, dict)
            self.assertIn('ipv4_address', device)
            self.assertIn('ipv6_address', device)
            self.assertIn('mac_address', device)
            self.assertIn('UUID', device)
            self.assertIn('system_triplet', device)
            self.assertIsInstance(device['ipv4_address'], str)
            self.assertIsInstance(device['ipv6_address'], str)
            self.assertIsInstance(device['mac_address'], str)
            self.assertIsInstance(device['UUID'], str)
            self.assertIsInstance(device['system_triplet'], str)


    @patch('src.main.python.user_data_gen.data_utils.Pool')
    @patch('src.main.python.user_data_gen.data_utils.cpu_count', return_value=3)
    def test_generate_user_data(self, mock_cpu_count, mock_pool):
        mock_pool_instance = mock_pool.return_value.__enter__.return_value
        mock_pool_instance.starmap.return_value = [
            [{'user_id': i} for i in range(10)],
            [{'user_id': i} for i in range(10, 20)],
            [{'user_id': i} for i in range(20, 25)],
        ]
        
        num_users = 25
        result = generate_user_data(num_users)
        
        self.assertEqual(len(result), num_users)
        self.assertEqual(result, [{'user_id': i} for i in range(num_users)])

if __name__ == '__main__':
    unittest.main(testRunner=CustomTestRunner(verbosity=1))
