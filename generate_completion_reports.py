#!/usr/bin/env python
from __future__ import absolute_import, print_function, unicode_literals
import datetime
import  jsondb
from request_tracker import RT, RT_URL, format_results, email_results, send_email, load_config, get_id_list

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
def ticket_check(rt, ticket, (start, end)):
    # get history (python-rt method), returned as list
    history = rt.get_history(ticket)
    # get creation date python-requestracker method
    creation_date = get_creation_date(ticket)
    get  contact -> pending -> resolved date
    return date_of_change, difference
        timedelta finished_date - creation_date
    (repeat for any status change if new status = open)

gen_list((start, end))
    rtobject = setup_rtobject()  
    completion_list=[]
    #get list of tickets in contact:
    ticket_list = get_ticket_list(contact)
    completion_list.extend(check_tickets(rtobject, ticket_list, (start, end)))
    #repeat for tickets in pending
    ticket_list = get_ticket_list(pending)
    completion_list.extend(check_tickets(rtobject, ticket_list, (start, end)))
    #repeat for ticket resolved in timeperiod
    ticket_list = get_resolved_ticket_list(start, end)
    completion_list.extend(check_tickets(rtobject, ticket_list, (start, end)))   
    return completion_list

def check_tickets(rtobject, ticket_list, (start, end)):
    results = []
    for ticket in ticket_list:
        date_of_change, difference = ticket_check(rtobject, ticket, (start, end))
        # if status change was within time period add to results
        if check_date((start, end), date_of_change):
            #append completion time to list
            results.append(completion_time)
    return results

def get_resolved_ticket_list(start, end):
    get a list of resolved tickets where start <= last_updated <= end
    return list

generate_monthly_email(average, adjusted_average):
    generate email_body
    return email_body

send email(address, body):
    send email

gen_data((start, end)):
    glist = gen_list((start,end)) 
    average, adjusted_average  = calculate_averages(glist)
    return average, adjusted_average

get_previous_week(date, weeklydb):
    previous_week = days_ago(date, 14)
    average, adj_average = get_calculated_averages(previous_week, weeklydb)
    return average, adj_average


do_monthly(date, weeklydb, monthydb):
        last_week_list = generate_list(last_week)
        weekly_average, weekly_adjusted_average  = calculate_weekly_averages(last_week_list)
        store(last_week,(weekly_average, weekly_adjusted_average)
        week_list = get_last_month(db)
        monthy_average, monthly_adjusted_average  = calculate_monthly_averages(iweek_list)
        return monthy_average, monthly_adjusted_average 

def main():
    loadconfig()
    db = jsondb.JsonDB('dbfile')
    if monthly:
        monthy_average, monthly_adjusted_average = gen_data(start_of_month,end_of_month) 
        msg = generate_monthly_email(monthy_average, monthly_adjusted_average)
        send_email(address, msg)
    elif weekly:
        start =
        end = days_ago(start, 7)
        weekly_average, weekly_adjusted_average = gen_data(start, end)
        prev_weekly_average, prev_weekly_adjusted_average = get_previous_week(start, weeklydb)
         store(this_week,(weekly_average, weekly_adjusted_average)
        msg = gen_weekly_email((weekly_average, weekly_adjusted_average),(prev_weekly_average, prev_weekly_adjusted_average))
         send_email(address, msg)
    weeklydb.dump()
    monthlydb.dump()


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

def get_creation_date(rtobject, ticket):
    '''returns creation date as datetime date object'''
    ctime = datetime.datetime.strptime(rtobject.get_creation_date(ticket), '%c')
    return ctime.date()


if __name__ == "__main__":
    pass
