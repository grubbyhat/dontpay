from asyncore import write
from signal import valid_signals
import requests
from matplotlib import pyplot as plt
import matplotlib
from bs4 import BeautifulSoup
import datetime
from email.message import EmailMessage
import smtplib
import time 
import sqlite3


conn = sqlite3.connect('tracker.db')
c = conn.cursor()
c.execute('''CREATE TABLE IF NOT EXISTS tracker (
            email text, 
            thresh integer)''')
conn.commit()
conn.close()

def add_user(email, thresh):
    conn = sqlite3.connect('tracker.db')
    c = conn.cursor()
    c.execute("INSERT INTO tracker VALUES (?, ?)", (email, thresh))
    conn.commit()
    conn.close()

def search_db(final):
    conn = sqlite3.connect('tracker.db')
    c = conn.cursor()
    c.execute('SELECT * FROM tracker')
    for row in c.fetchall():
        if row[1] < final:
            send_mail(final, row[0])
            print('Email sent')
    c.execute('DELETE FROM tracker WHERE thresh < ?', (final,))
    conn.commit()
    conn.close()



def resps():
    link = 'https://dontpay.uk/'
    number = []
    now = str(datetime.datetime.now())
    response = requests.get(link)
    soup = BeautifulSoup(response.text, 'html.parser')
    parent_div = soup.find('div', {'class': 'pb-4'})
    result = parent_div.findAll('span')
    nums = ['1', '2', '3', '4', '5', '6', '7', '8', '9', '0']
    for a in str(result[0]):
        if a in nums:
            number.append(a)
    finals = ''.join(number)
    final = int(finals)
    return now, final


def write_to_file(now, final):
    with open ('tracker.txt', 'a') as f:
        f.write(now)
        f.write(',')
        f.write(str(final))
        f.write('\n')
        f.close()


def read_text():
    with open ('tracker.txt', 'r') as f:
        time = []
        value = []
        for line in f.readlines():
            tme, val = line.split(',')
            vals = int(val)
            time.append(tme)
            value.append(vals)
        return time, value




def send_mail(final,email_choice):
    email_sender = 'pythonscriptjakeludlam@gmail.com'
    email_password = 'rzylvmqogzvddbwu'

    email_subject = 'dontpay.uk update'
    email_body ='Your threshold has been broken and now' + str(final) + ' people have signed up to the dontpay.uk campaign'
    
    em = EmailMessage()

    em['From'] = email_sender
    em['To'] = email_choice
    em['Subject'] = email_subject
    em.set_content(email_body)
    with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
        smtp.login(email_sender, email_password)
        smtp.sendmail(email_sender, email_choice, em.as_string())


# def should_send(threshold, email_choice):
#     now, final = resps()
#     if final > threshold:
#         send_mail(final, email_choice)
#     else:
#         time.sleep(60)
#         should_send(threshold, email_choice)



def let_run():
    now, final = resps()
    search_db(final)
    time.sleep(60)
    let_run()




def plot(time, value):
    dates = []
    for  i in range(len(time)):
        date = time[i].split(' ')[0]
        hours = time[i].split(' ')[1]
        hour = hours.split(':')[0]
        days = date.split('-')[1:3]
        dayss = '-'.join(days)
        timedate = dayss + '-' + hour
        dates.append(timedate)
    
    plt.ylabel('Number of people signed up')
    plt.xlabel('Date, Hour')
    plt.plot(dates, value)
    plt.legend()
    plt.show()



####################


def main():
    print('''Welcome to dontpay.uk tracker.
    This script will tell you the current amount of people signed up to a campaign in the UK where on October 1st they will cancel their direct debit to their energy provider.
    This is to help the UK government to negotiate better deals with energy providers. 
    1. To print the number of people signed up to the campaign
    2. Recieve an email if the number of people signed up to the campaign has broken a threshold that you set 
    3. To plot the number of people signed up to the campaign over time
    ''')

    now, final = resps()
    search_db(final)
    write_to_file(now, final)

    choice = input('Please enter your choice: ')
    if choice == '1':
        print(final)
    elif choice == '2':
        threshold = int(input('Please enter the threshold you would like to be notified at: '))
        email_choice = input('What email would you like to be notified at? ')
        add_user(email_choice, threshold)
        print('You have been added ')

    elif choice == '3':
        time, value = read_text()
        plot(time, value)
        plt.show()
    elif choice == '4':
        let_run()

    else:
        print('Please enter a valid choice')
        main()

main()

    

