import pickle
import unittest

from app import _check_date


class SomeTest(unittest.TestCase):
    def test_check_date(self):
        delivery_hours = ["11:35-14:05", "09:00-11:00"]
        working_hours = ["11:35-14:05", "09:00-11:00"]
        assert _check_date(pickle.dumps(delivery_hours), pickle.dumps(working_hours))
        working_hours = ["14:05-21:05"]
        assert _check_date(pickle.dumps(delivery_hours), pickle.dumps(working_hours))
        working_hours = ["11:01-11:34"]
        assert not _check_date(pickle.dumps(delivery_hours), pickle.dumps(working_hours))

if __name__ == '__main__':
    unittest.main()
