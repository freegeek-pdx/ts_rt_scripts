#!/usr/bin/env python
from __future__ import absolute_import, print_function, unicode_literals
import datetime
import calendar
import  jsondb
from request_tracker import RT, RT_URL, send_email, load_config, get_id_list

# CONFIG
EMAIL = ['paulm@freegeek.org']
MONTHLDB = 'monthlydb.json'
WEEKLYDB = 'weeklydb.json'

def loadconfig():
    '''load config into global variables to make setting up rt object easy'''
    config = load_config('/etc/rt.cfg')
    rtconf = config['rt']
    mail = config['mail']
    global RT_HOST, RT_USER, RT_PASSWORD, RT_QUEUE, RT_FROM, RT_TO, MAILHOST, tickets
    tickets = config['tickets']
    RT_HOST = 'todo.freegeek.org'
    RT_USER = rtconf['rt_user']
    RT_PASSWORD = rtconf['rt_password']
    RT_QUEUE = rtconf['rt_queue']
    RT_FROM = mail['rt_from']
    RT_TO= mail['rt_to']
    MAILHOST = mail['mail_host']


def setup_rtobject():
    '''set up rt object'''
    rtobject = RT(RT_URL, RT_USER, RT_PASSWORD)
    rtobject.login()
    return rtobject


'''

def main():
    loadconfig()
    rtobject = setup_rtobject()  
    now = datetime.date.today()

    if monthly:
        db = jsondb.JsonDB(MONTHLYDB)
        start, end = get_last_month(now)
        monthy_average, monthly_adjusted_average = gen_data(start, end) 
        db.set(start, (monthy_average, monthly_adjusted_average))
        db.dump()
        data = [(str(start), (monthy_average, monthly_adjusted_average))]
        pstart1, pstart2 = get_previous_months(now)
        data += [ (pstart1, db.get(pstart1)), (pstart2, db.get(pstart2)) ]
        msg = generate_email_body(data,'month')
        for adress in EMAIL:
            send_email(address, msg)
    elif weekly:
        db = jsondb.JsonDB(WEEKLYDB)
        end = get_week_end(now) #WRITE THIS
        start = days_ago(end, 7)
        weekly_average, weekly_adjusted_average = gen_data(start, end)
        db.set(start, (weekly_average, weekly_adjusted_average)
        db.dump()
        data = [(str(start), (weeky_average, weekly_adjusted_average))]
        pstart1, pstart2 = get_previous_weeks(now) #WRITE THIS
        data += [ (pstart1, db.get(pstart1)), (pstart2, db.get(pstart2)) ]
        msg = generate_email_body(data,'week')
        for adress in EMAIL:
            send_email(address, msg)


'''
class LocalError(Exception):
    pass

def avg_list(list):
    '''returns the average of a list of numbers'''
    return float(sum(list)) / len(list)

def adjusted_avg_list(list):
    '''returns the average of a list of numbers ignoring the highest number'''
    return  (float(sum(list)) - max(list)) / (len(list) - 1)   


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

def get_corrected_date(date, span):
    '''returns month and year for span months previous to date'''
    if date.month - span <= 0:
        return date.month - span + 12, date.year - 1
    else:
        return date.month - span, date.year


def get_last_month(date):
    '''returns the start and end of a full month as 
    datetime.date objects'''
    month, year = get_corrected_date(date, 1)
    daterange = calendar.monthrange(year, month)
    start = datetime.date(year, month, 1)
    end = datetime.date(year, month, daterange[1])
    return start, end

def get_previous_months(date):
    '''returns the start dates for the previous two months as strings'''
    dates = []
    for i in [2,3]:
        month, year = get_corrected_date(date, i)
        dates.append("%s-%s-%s" %(year, month, '01'))
    return dates[0], dates[1]



def calculate_averages(wlist):
    '''return averages for list'''
    average = avg_list(wlist)
    adjusted_average=adjusted_avg_list(wlist)
    return average, adjusted_average

def get_calculated_averages(date, db):
    '''for a given date return average, adjusted_average from db)'''
    averages = db.get(str(date))
    if not averages:
        raise LocalError('incorrect date, could not get averages')
    else:
        return averages[0], averages[1]

def get_creation_time(rtobject, ticket):
    '''returns creation time as datetime object'''
    ctime = datetime.datetime.strptime(rtobject.get_creation_date(ticket), '%c')
    return ctime

def get_history(rtobject, ticket):
    '''returns ticket history as list'''
    history = rtobject.get_history(ticket)
    return history

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
        elif  entry['NewValue'] == 'pending' and completed is False:
            datestr = entry['Created']
            completed = True
        elif  entry['NewValue'] == 'resolved'and completed is False:
            datestr = entry['Created']
            completed = True
    return  datetime.datetime.strptime(datestr, "%Y-%m-%d %H:%M:%S")

def get_days_to_complete(creation_date, completion_date):
    '''returns the difference in days 
    between creation_date and completion_date'''
    timedelta =  completion_date.date() - creation_date.date()
    return timedelta.days

def ticket_check(rt, ticket):
    '''for a given ticket return the time it was completed 
    i.e. finally moved to contact etc. and the time in days it took
    returns datetime object, integer'''
    creation_time = get_creation_time(rt, ticket)
    history = get_history(rt, ticket)
    completion_time= get_completion_time(history)
    days_to_complete =  get_days_to_complete(creation_time, completion_time)
    return completion_time, days_to_complete


def check_tickets(rtobject, ticket_list, (start, end)):
    results = []
    for ticket in ticket_list:
        completion_time, days_to_complete = ticket_check(rtobject, ticket)
        # if status change was within time period add to results
        if check_date((start, end), completion_time.date()):
            results.append(days_to_complete)
    return results

def get_ticket_list(rtobject, status, (start, end)):
    '''reurns a list of tickets matching status
    between start and today (as datetime.date objects)'''
    # not unit tested as unpredictable due to following. 
    # last_updated_by_status from request_tracker only takes a number of 
    # days before today, not a date range, so we set end to be today.
    # Since we check the date range elsewhere it won't have any side effects
    # other than possibly making the list a little larger than necesary
    # it most cases end will equal today anyway. Taking (start, end) 
    # as argument  means this can be fixed later without side effects.
    end = datetime.date.today()
    days = (end - start).days 
    return rtobject.last_updated_by_status(RT_QUEUE, status, days)


def generate_completion_list(rtobject,(start, end)):
    '''generate a list of how long it took to complete tickets''' 
    # not unit tested as covered by other tests
    completed=[]
    status_list = ['contact', 'pending', 'resolved']
    # get completion times of appropriate tickets
    # Note we can assume any ticket that hasn't been updated since
    # the start date should not be counted, but we can't assume it
    # should be.
    for status in status_list:
        ticket_list = get_ticket_list(rtobject, status, (start, end))
        completed.extend(check_tickets(rtobject, ticket_list, (start, end)))
    return completed


def gen_data(rtobject, (start, end)):
    '''given a date range return the average and adjusted average
    completion times for tickets'''
    # not unit tested as covered by other tests
    glist = generate_completion_list(rtobject, (start,end)) 
    average, adjusted_average  = calculate_averages(glist)
    return average, adjusted_average

def generate_email_body(data, typeof):
    title = "Completion Time %sly Report\n" %(typeof.capitalize())
    msg = title
    for i in len(title):
        msg += '='
    msg += "\n\n%s starting\tAverage\tAdjusted Average\n" %(typeof.capitalize())
    for datum in data:
        date=datum[0]
        avg, adj_avg = datum[1]
        msg += "%s\t\t%s\t%s\n" %(date, avg, adj_avg)
    return msg



if __name__ == "__main__":
    pass
