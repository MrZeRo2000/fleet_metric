
from unittest import TestCase
import time
import concurrent.futures


class ParallelTestCase(TestCase):

    def test_delay(self):
        delay_list = [4, 6, 2, 8, 1, 5, 9, 3, 8]

        with concurrent.futures.ThreadPoolExecutor(max_workers=4) as executor:
            executor.map(self.run_delay, delay_list)

    def run_delay(self, delay):
        print("test_delay start with {0}".format(delay))
        time.sleep(delay)
        print("test_delay end with {0}".format(delay))
