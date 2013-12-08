#!/usr/bin/env python
import unittest
import os
from generate_completion_reports import *

loadconfig()


class MyTests(unittest.TestCase):
        # pylint: disable=R0904

    def setUp(self):
        self.db = jsondb.JsonDB('null')
        self.db.set('2013-11-01', (2.5, 2))
        self.db.set('2013-10-25', (2.5, 2))
        self.db.set('2013-10-18', (2.5, 2))
        self.db.set('2013-10-04', (2.5, 2))
        rt_user, rt_password, rt_queue = loadconfig()
        # override value from loadconfig so unit test tickets
        # won't effect our final output
        rt_queue = 'Bugs'
        self.rt = setup_rtobject(RT_URL, rt_user, rt_password)
        self.tc = TicketChecker(self.rt, rt_queue)
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
        result = self.tc._get_creation_time(self.ticket)
        self.assertEquals(result, expected_time)

    def test_get_history(self):
        history = self.tc._get_history(self.ticket)
        # use nosetests -s and uncomment the following 
        # to see what history looks like
        #for item in history:
        #    print item
        length = len(history)
        self.assertEquals(7, length)

    def test_get_completion_time(self):
        expected_time =  datetime.datetime.strptime("2013-11-17 01:55:46", "%Y-%m-%d %H:%M:%S")
        history = self.tc._get_history(self.ticket)
        result = get_completion_time(history)
        self.assertEquals(result, expected_time)

    def test_get_completion_time_reopened(self):
        expected_time =  datetime.datetime.strptime("2013-11-21 21:50:34", "%Y-%m-%d %H:%M:%S")
        history = self.tc._get_history(self.ticket_reopened)
        result = get_completion_time(history)
        self.assertEquals(result, expected_time)

    def test_get_days_to_complete(self):
        creation_time =  self.tc._get_creation_time(self.ticket)
        history = self.tc._get_history(self.ticket)
        completion_time = get_completion_time(history)
        result = get_days_to_complete(creation_time, completion_time)
        self.assertEquals(result, 1)

    def test_ticket_check(self):
        expect_completion_time =  datetime.datetime.strptime("2013-11-17 01:55:46", "%Y-%m-%d %H:%M:%S")
        (completion_time, days) = self.tc._ticket_check(self.ticket)
        self.assertEquals((expect_completion_time, 1), (completion_time, days))

    def test_check_tickets(self):
        tickets = [self.ticket]
        start = datetime.date(2013, 11, 10)
        end = datetime.date(2013, 11, 17)
        result = self.tc._check_tickets(tickets, (start, end))
        self.assertEquals(result, [1])


    def test_get_corrected_month_1(self):
        expected = (12, 2012)
        date = datetime.date(2013,01,01)
        month, year = get_corrected_month(date, 0)
        self.assertEquals(expected, (month, year))
    
    def test_get_corrected_month_2(self):
        expected = (11, 2012)
        date = datetime.date(2013,01,01)
        month, year = get_corrected_month(date,1)
        self.assertEquals(expected, (month, year))

    def test_get_monthrange(self):
        date = datetime.date(2013,01,01)
        expected_start = datetime.date(2012,12,01)
        expected_end= datetime.date(2012,12,31)
        month, year = get_corrected_month(date, 0)
        (start, end) = get_monthrange(month, year)
        self.assertEquals((start, end),(expected_start, expected_end))

    def test_get_db_averages(self):
        start = datetime.date(2013,11,01)
        expected = (2.5, 2)
        results = get_db_averages(self.db, (start))
        self.assertEquals(expected, results)

    def test_get_ticket_list(self):
        start = datetime.date(2013, 11, 20)
        end = datetime.date(2013, 11, 27)
        results = self.tc._get_ticket_list('pending', (start, end))
        self.assertEquals(len(results), 2)
 
    def test_gen_data(self):
        pass

    def test_TicketChecker_get_averages(self):
        pass

    def test_get_corrected_week0(self):
        expected = (datetime.date(2013,11,10), datetime.date(2013,11,16))
        date =  datetime.date(2013,11,20)
        start, end = get_corrected_week(date, 0)
        self.assertEquals(expected, (start, end))

    def test_get_corrected_week1(self):
        expected = (datetime.date(2013,10,27), datetime.date(2013,11,2))
        date =  datetime.date(2013,11,13)
        start, end = get_corrected_week(date, 1)
        self.assertEquals(expected, (start, end))

    def test_get_corrected_week_sunday(self):
        expected = (datetime.date(2013,11,10), datetime.date(2013,11,16))
        date =  datetime.date(2013, 11,17)
        start, end = get_corrected_week(date, 0)
        self.assertEquals(expected, (start, end))
if __name__ == "__main__":
    unittest.main()
