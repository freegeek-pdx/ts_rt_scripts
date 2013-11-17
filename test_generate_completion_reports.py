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
        loadconfig()
        self.rt = setup_rtobject()
        self.ticket = '38576'

    def tearDown(self):
        os.remove('null')     
        self.rt.logout()

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

    def test_check_date_true(self):
        start = datetime.date(2013, 10, 25)
        end = datetime.date(2013, 11, 01)
        test_date =  datetime.date(2013, 10, 27)
        self.assertTrue(check_date((start, end), test_date))
    
    def test_check_date_false(self):
        start = datetime.date(2013, 10, 25)
        end = datetime.date(2013, 11, 01)
        test_date =  datetime.date(2013, 9, 27)
        self.assertFalse(check_date((start, end), test_date))
    
    def test_check_date_start_is_true(self):
        start = datetime.date(2013, 10, 25)
        end = datetime.date(2013, 11, 01)
        test_date =  datetime.date(2013, 10, 25)
        self.assertTrue(check_date((start, end), test_date))

    def test_check_date_end_is_true(self):
        start = datetime.date(2013, 10, 25)
        end = datetime.date(2013, 11, 01)
        test_date =  datetime.date(2013, 11, 01)
        self.assertTrue(check_date((start, end), test_date))

    def test_calculate_averages(self):
        (result1, result2) = calculate_averages([1, 2, 3, 4])
        self.assertEquals((result1, result2), (2.5, 2))

    def test_get_calculated_averages(self):
        date = datetime.date(2013, 11, 01)
        (result1, result2) = get_calculated_averages(date, self.db)
        self.assertEquals((result1, result2), (2.5, 2))


    def test_get_calculated_averages_fails(self):
        date = datetime.date(2013, 11, 11)
        self.assertRaises(LocalError, get_calculated_averages, date, self.db)

    def test_get_creation_date(self):
        fdate =  datetime.datetime.strptime("Sat Nov 16 17:55:11 2013", "%c" )
        expected_date = fdate.date()
        result = get_creation_date(self.rt, self.ticket)
        self.assertEquals(result, expected_date)

    def test_get_history(self):
        history = get_history(self.rt, self.ticket)
        for item in history:
            print item
        length = len(history)
        self.assertEquals(4, length)

if __name__ == "__main__":
    unittest.main()
