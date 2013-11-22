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
        # override value from loadconfig so unit test tickets
        # won't effect our final output
        RT_QUEUE=['bugs']
        self.rt = setup_rtobject()
        self.ticket = '38576'
        self.ticket_reopened =  '38618'

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

    def test_get_creation_time(self):
        expected_time =  datetime.datetime.strptime("Sat Nov 16 17:55:11 2013", "%c" )
        result = get_creation_time(self.rt, self.ticket)
        self.assertEquals(result, expected_time)

    def test_get_history(self):
        history = get_history(self.rt, self.ticket)
        # use nosetests -s and uncomment the following 
        # to see what history looks like
        #for item in history:
        #    print item
        length = len(history)
        self.assertEquals(5, length)

    def test_get_completion_time(self):
        expected_time =  datetime.datetime.strptime("2013-11-17 01:55:46", "%Y-%m-%d %H:%M:%S")
        history = get_history(self.rt, self.ticket)
        result = get_completion_time(history)
        self.assertEquals(result, expected_time)

    def test_get_completion_time_reopened(self):
        expected_time =  datetime.datetime.strptime("2013-11-21 21:50:34", "%Y-%m-%d %H:%M:%S")
        history = get_history(self.rt, self.ticket_reopened)
        result = get_completion_time(history)
        self.assertEquals(result, expected_time)

    def test_get_days_to_complete(self):
        creation_time =  get_creation_time(self.rt, self.ticket)
        history = get_history(self.rt, self.ticket)
        completion_time = get_completion_time(history)
        result = get_days_to_complete(creation_time, completion_time)
        self.assertEquals(result, 1)

    def test_ticket_check(self):
        expect_completion_time =  datetime.datetime.strptime("2013-11-17 01:55:46", "%Y-%m-%d %H:%M:%S")
        (completion_time, days) = ticket_check(self.rt, self.ticket)
        self.assertEquals((expect_completion_time, 1), (completion_time, days))

    def test_check_tickets(self):
        tickets = [self.ticket]
        start = datetime.date(2013, 11, 10)
        end = datetime.date(2013, 11, 17)
        result = check_tickets(self.rt, tickets, (start, end))
        self.assertEquals(result, [1])


    def test_get_corrected_date_1(self):
        expected = (12, 2012)
        date = datetime.date(2013,01,01)
        month, year = get_corrected_date(date, 1)
        self.assertEquals(expected, (month, year))
    
    def test_get_corrected_date_2(self):
        expected = (11, 2012)
        date = datetime.date(2013,01,01)
        month, year = get_corrected_date(date, 2)
        self.assertEquals(expected, (month, year))

    def test_get_last_month(self):
        date = datetime.date(2013,01,01)
        expected_start = datetime.date(2012,12,01)
        expected_end= datetime.date(2012,12,31)
        (start, end) = get_last_month(date)
        self.assertEqual((start, end),(expected_start, expected_end))

    def test_get_previous_months(self):
        date = datetime.date(2013,01,01)
        (expected1, expected2) = get_previous_months(date)
        self.assertEquals((expected1, expected2) , ('2012-11-01', '2012-10-01'))

if __name__ == "__main__":
    unittest.main()
