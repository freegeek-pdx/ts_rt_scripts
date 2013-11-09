#!/usr/bin/env python
from __future__ import absolute_import, print_function, unicode_literals
import datetime
import  jsondb

'''
def date_check(ticket):
    get history
    get creation date
    get  contact -> pending -> resolved date
    return difference
        timedelta finished_date - creation_date

generate_list(week_start)
    list=[]
    get list of tickets in contact:
        check to see if we already have a result for for it
        completion_time = date_check(ticket)
        append completion time to list
        store_ticket

    repeat for tickets in pending

    repeat for ticket resolved in last week
        check to see if we already have a result for for it
            if so remove from db
        else
            completion_time = date_check(ticket)
            append completion time to list



generate_monthly_email(average, adjusted_average):
    generate email_body
    return email_body

send email(address, body):
    send email

get_week(week,weeklydb):
    week_list = generate_list(week)
    weekly_average, weekly_adjusted_average  = calculate_weekly_averages(week_list)
    return weekly_average, weekly_adjusted_average

get_previous_week(monthlydb):
    previous_week = 1st element of index list
    averages = monthlydb.get(previous_week)
    return averages[0], averages[1]

do_monthly(date, weeklydb, monthydb):
    last_week = calculate_week
    week_list = get_last_month(date)
    if  last_week != week_list[0]:
        last_week_list = generate_list(last_week)
        weekly_average, weekly_adjusted_average  = calculate_weekly_averages(last_week_list)
        store(last_week,(weekly_average, weekly_adjusted_average)
        week_list = get_last_month(db)
        monthy_average, monthly_adjusted_average  = calculate_monthly_averages(iweek_list)
        return monthy_average, monthly_adjusted_average 

def main():
    db = jsondb.JsonDB('dbfile')
    today = datetime.date.today()
    if monthly:
        monthy_average, monthly_adjusted_average = do_monthly((weeklydb, monthydb)
        msg = generate_monthly_email(monthy_average, monthly_adjusted_average)
        send_email(address, msg)
    elif weekly:
        this_week = calculate_week(today)
        weekly_average, weekly_adjusted_average = get_week(this_week, weeklydb)
        prev_weekly_average, prev_weekly_adjusted_average = get_previous_week(monthlydb)
         
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


def calculate_week(date):
    '''returns date for previous week'''
    return days_ago(date, 7)

def calculate_two_week(date):
    '''returns date for previous week + 1'''
    return days_ago(date, 14)

def days_ago(date, days):
    '''returns date n days ago from date,
    date is datetime.date object, days is int'''
    return date - datetime.timedelta(days)

def calculate_averages(wlist):
    '''return averages for list'''
    average = avg_list(wlist)
    adjusted_average=adjusted_avg_list(wlist)
    return average, adjusted_average

def get_calculated_averages(date, db):
    '''for a given date return average, adjusted_average from db)'''
    averages = db.get(str(date))
    return averages[0], averages[1]
if __name__ == "__main__":
    pass
