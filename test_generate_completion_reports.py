#!/usr/bin/env python
import unittest
import os
from generate_completion_reports import *
class MyTests(unittest.TestCase):
        # pylint: disable=R0904

    def setUp(self):
        self.db = jsondb.JsonDB('null')
        self.db.set('2013-11-01', (2.5, 2))
        self.db.set('2013-10-25', (2.5, 2))
        self.db.set('2013-10-18', (2.5, 2))
        self.db.set('2013-10-04', (2.5, 2))

    def tearDown(self):
        os.remove('null')        

    def test_example(self):
        pass

    def test_avg_list(self):
        result = avg_list([1, 2, 3, 4])
        self.assertEquals(result, 2.5)

    def test_adjusted_avg_list(self):
        result = adjusted_avg_list([1, 2, 3, 4])
        self.assertEquals(result, 2)

    def test_days_ago(self):
        date = datetime.date(2013, 11, 01)
        expected = datetime.date(2013, 10, 25)
        result = days_ago(date, 7)
        self.assertEquals(result, expected)

    def test_calculate_week(self):
        date = datetime.date(2013, 11, 01)
        expected = datetime.date(2013, 10, 25)
        result = calculate_week(date)
        self.assertEquals(result, expected)

    def test_calculate_two_week(self):
        date = datetime.date(2013, 11, 01)
        expected = datetime.date(2013, 10, 18)
        result = calculate_two_week(date)
        self.assertEquals(result, expected)

    def test_get_last_4_weeks(self):
        date = datetime.date(2013, 11, 01)
        expected = [datetime.date(2013, 10, 25), datetime.date(2013, 10, 18), datetime.date(2013, 10, 11), datetime.date(2013, 10, 4)]
        result = get_last_4_weeks(date)
        self.assertEquals(result, expected)

    def test_calculate_averages(self):
        (result1, result2) = calculate_averages([1, 2, 3, 4])
        self.assertEquals((result1, result2), (2.5, 2))

    def test_get_calculated_averages(self):
        date = datetime.date(2013, 11, 01)
        (result1, result2) = get_calculated_averages(date, self.db)
        self.assertEquals((result1, result2), (2.5, 2))


if __name__ == "__main__":
    unittest.main()
