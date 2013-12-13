#!/usr/bin/env python
'''Generate reports on completion times of Tech Support Tickets
based on the time they hit contacy/pending etc'''
from __future__ import absolute_import, print_function, unicode_literals
import datetime
import calendar
import jsondb
from request_tracker import RT, RT_URL, send_email, load_config #, get_id_list

# CONFIG
EMAIL = ['paulm@freegeek.org']
MONTHLDB = 'monthlydb.json'
WEEKLYDB = 'weeklydb.json'

def loadconfig():
    '''load config into global variables to make setting up rt object easy'''
    config = load_config('/etc/rt.cfg')
    rtconf = config['rt']
    rt_user = rtconf['rt_user']
    rt_password = rtconf['rt_password']
    rt_queue = rtconf['rt_queue']
    return rt_user, rt_password, rt_queue

def setup_rtobject(rt_url, rt_user, rt_password):
    '''set up rt object'''
    rtobject = RT(rt_url, rt_user, rt_password)
    rtobject.login()
    return rtobject


class LocalError(Exception):
    '''could do with a better name '''
    pass

class TicketChecker:
    def __init__(self, rtobject, rtqueue):
        self.rtobject = rtobject
        self.rtqueue = rtqueue
        self.initialized = False
        # self.ticket_data = []

        # Public Method
    def get_averages(self, start, end):    # was gen_data
        if not self.initialized:
            self.ticket_data = self._gen_data(start, end)              # was get_completion_list
            self.initialized = True
        valid_tickets = self._check_tickets(self.ticket_list, (start, end))
        average, adjusted_average  = calculate_averages(valid_tickets)
        return average, adjusted_average

        # Private Methods
    def _get_creation_time(self, ticket):
        '''returns creation time as datetime object'''
        return datetime.datetime.strptime(ticket['Created'], '%c')

    def _get_history(self, ticket):
        '''returns ticket history as list'''
        history = self.rtobject.get_history(ticket)
        return history

    def _get_ticketid(self, ticket):
        '''for a set of ticket results return the ticket id'''
        return ticket['id'].split('/')[1]

    def _ticket_check(self, ticket):
        '''for a given ticket return the time it was completed
        i.e. finally moved to contact etc. and the time in days it took
        returns datetime object, integer'''
        creation = self._get_creation_time(ticket)
        ticket_no = self._get_ticketid(ticket)
        history = self._get_history(ticket_no)
        completion = get_completion_time(history)
        days_to_complete = get_days_to_complete(creation, completion)
        return completion, days_to_complete

    def _get_ticket_list(self, status, (start, end)):
        '''returns a list of tickets matching status
        between start and today (as datetime.date objects).
        Contains all ticket properties'''
        return self.rtobject.updated_by_status_daterange(self.rtqueue, status, start, end)

    def _check_tickets(self, tickets,  (start, end)):
        '''return list of times to complete between start and end'''
        results = []
        for ticket in tickets:
            # if status change was within time period add to results
            completion_time, days_to_complete = self._ticket_check(ticket)
            if check_date((start, end), completion_time.date()):
                results.append(days_to_complete)
        return results
 
    def _gen_data(self, start, end):
        '''generate dict of completed tickets, doesn't
        check tickets for validity, _check tickets is used for this'''
        completed = []
        status_list = ['contact', 'pending', 'resolved']
        for status in status_list:
            ticket_list = self._get_ticket_list( status, (start, end))
            completed.extend(ticket_list)
        ticket_data = {}
        for ticket in completed:
            ticket_no = self._get_ticketid(ticket)
            completion_time, days_to_complete = self._ticket_check(ticket)
            ticket_data[ticket_no] = (completion_time, days_to_complete)
        return ticket_data


def get_completion_time(history):
    '''returns a datetime object indication when a ticket was moved
    to contact or pending'''
    completed = False
    # check for changed status in each entry in a tickets history
    for entry in history:
        # checks to see if a ticket has been reopened
        if entry['NewValue'] == 'open' and completed is True:
            completed = False
        # set the completion date and status
        elif entry['NewValue'] == 'contact' and completed is False:
            datestr = entry['Created']
            completed = True
        elif entry['NewValue'] == 'pending' and completed is False:
            datestr = entry['Created']
            completed = True
        elif entry['NewValue'] == 'resolved'and completed is False:
            datestr = entry['Created']
            completed = True
    return datetime.datetime.strptime(datestr, "%Y-%m-%d %H:%M:%S")
 
def avg_list(alist):
    '''returns the average of a list of numbers'''
    return round(float(sum(alist)) / len(alist), 1)

def adjusted_avg_list(alist):
    '''returns the average of a list of numbers ignoring the highest number'''
    return  round((float(sum(alist)) - max(alist)) / (len(alist) - 1), 1)  


def days_ago(date, days):
    '''returns date n days ago from date,
    date is datetime.date object, days is int'''
    return date - datetime.timedelta(days)

def check_date((start, end), date):
    '''checks to see if date is between start and end and returns boolean'''
    if start <= date <= end:
        return True
    else:
        return False

def get_corrected_week(date, weekno):
    '''returns datetime.date object representing the Sunday at the
    beginning of the last full week'''
    correction = (weekno * 7) + 7  +( date.isoweekday() % 7)
    # if its sunday we want the previous sunday
    start =  date - datetime.timedelta(correction)
    end = start + datetime.timedelta(6)
    return start, end

def get_corrected_month(date, span):
    '''returns month and year for span + 1 months previous to date.
    This return the last *full* month for span 0. So (2013-12-31, 0)
    will return 11, 2013. This returns correctly for now() as it does 
    not assume the month is over. '''
    span += 1
    if date.month - span <= 0:
        return date.month - span + 12, date.year - 1
    else:
        return date.month - span, date.year


def get_monthrange(month, year):
    '''returns the start and end of a month as datetime.date objects'''
    daterange = calendar.monthrange(year, month)
    start = datetime.date(year, month, 1)
    end = datetime.date(year, month, daterange[1])
    return start, end

def calculate_averages(wlist):
    '''return averages for list'''
    average = avg_list(wlist)
    adjusted_average = adjusted_avg_list(wlist)
    return average, adjusted_average

def get_calculated_averages(date, db):
    '''for a given date return average, adjusted_average from db)'''
    averages = db.get(str(date))
    if not averages:
        raise LocalError('incorrect date, could not get averages')
    else:
        return averages[0], averages[1]

def get_days_to_complete(creation_date, completion_date):
    '''returns the difference in days 
    between creation_date and completion_date'''
    timedelta =  completion_date.date() - creation_date.date()
    return timedelta.days

def get_db_averages(db, date):
    '''return averages from db if present, else none when given
    datetime object'''
    averages = db.get(str(date))
    return averages


def generate_email_body(data, typeof):
    '''Generate the bofy of a message'''
    title = "Completion Time %sly Report\n" % (typeof.capitalize())
    msg = title
    msg += '=' * len(title)
    msg += "\n\n%s starting\tAverage\tAdjusted Average\n" % (typeof.capitalize())
    for datum in data:
        date = datum[0]
        avg, adj_avg = datum[1]
        msg += "%s\t\t%s\t%s\n" % (date, avg, adj_avg)
    return msg


def main():
    rt_user, rt_password, rt_queue = loadconfig()
    rtobject = setup_rtobject(RT_URL, rt_user, rt_password) 
    date = datetime.date.today()

    if monthly:
        db = jsondb.JsonDB(MONTHLYDB)
        try:
            daterange = daterange
        except NameError:
            daterange = 3
        # TODO start = 
        # TODO end = 
        data = []
        tc = TicketChecker(rtobject, rt_queue)
        for i in range(daterange):
            get_db_averages(db, start)
            if not averages:
                average, adjusted_average = tc.get_averages(start, end)
                db.set(str(start), (average, adjusted_average))
            data.append(results)
        db.dump()
        msg = generate_email_body(data,'month')
        for address in EMAIL:
            send_email(address, msg)
    elif weekly:
        db = jsondb.JsonDB(WEEKLYDB)
        try:
            daterange = daterange
        except NameError:
            daterange = 3
        data = []
        tc = TicketChecker(rtobject, rt_queue)
        for i in range(daterange):
            get_db_averages(db, start)
            if not averages:
                average, adjusted_average = tc.get_averages(start, end)
                db.set(str(start), (average, adjusted_average))
            data.append(results)
        db.dump()


if __name__ == "__main__":
    pass
