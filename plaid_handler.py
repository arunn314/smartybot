import os
import json
import datetime
from collections import defaultdict
import matplotlib
matplotlib.use('agg')
import matplotlib.pyplot as plt
from datetime import date
from datetime import timedelta
import plaid

PLAID_CLIENT_ID = 'xxx'
PLAID_SECRET = 'xxx'
PLAID_PUBLIC_KEY = 'xxx'
PLAID_ENV = 'development'
DATA_DIR = '/home/pi/projects/pi-bot/static/'

access_token = 'xxx'




category_map = {
    'restaurant': 'food',
    'cafe': 'food',
    'thai': 'food',
    'cuisine': 'food',
    'grill': 'food',
    'kebab': 'food',
    'pizza': 'food',
    'gyro': 'food',
    'subway': 'food',
    'chipotle': 'food',
    'chaat': 'food',
    'chillies': 'food',
    'walgreens': 'pharmacy',
    'cvs': 'pharmacy',
    'quickpay': 'transfer',
    'online transfer': 'transfer',
    'gas': 'fuel',
    'shell': 'fuel',
    'shell oil': 'fuel',
    'atm': 'atm',
    'walmart': 'walmart',
    'wal-mart': 'walmart',
    'costco': 'groceries',
    'keypoint': 'auto loan',
    'mortgage': 'mortgage',
    'theatre': 'movie',
    'cinemark': 'movie',
    'cinemas': 'movie',
    'auto insu': 'auto insurance',
    'india bazar': 'groceries',
    'groceries': 'groceries',
    'market': 'groceries',
    'supermarket': 'groceries',
    'safeway': 'groceries',
    'whole foods': 'groceries',
    'home depot': 'home depot',
    'paypal': 'paypal',
    'uber': 'uber',
    'amazon': 'amazon',
    'check': 'check'
}

def make_autopct(values):
    def my_autopct(pct):
        total = sum(values)
        val = int(round(pct*total/100.0))
        #'${v:d} ({p:.2f}%)'
        return '${v:d}'.format(v=val)
    return my_autopct


class PlaidHandler(object):
    def __init__(self):
        self.client = plaid.Client(client_id=PLAID_CLIENT_ID, secret=PLAID_SECRET,
                      public_key=PLAID_PUBLIC_KEY, environment=PLAID_ENV)


    def get_dates(self, interval):
        end_date = date.today()
        start_date = date.today() - timedelta(days=interval)
        return str(start_date), str(end_date)


    def get_transactions(self, interval=7):
        start_date, end_date = self.get_dates(interval)
        response = self.client.Transactions.get(access_token, start_date, end_date)
        expense_dict = defaultdict(float)
        title_str = 'Expenses Summary from '+start_date+' to '+end_date
        transactions = response['transactions']
        return transactions


    def find_category(self, name):
        name = name.lower()
        new_ct = 'misc'
        for k,v in category_map.iteritems():
            if k in name:
                new_ct = category_map[k]
        return new_ct.title()

    def categorize_txns(self, transactions):
        expense_dict = defaultdict(float)
        total = 0
        for tx in transactions:
            ct = tx['category']
            if tx['amount'] < 0:
                continue
            name = tx['name'].lower()
            new_ct = self.find_category(name)
            if new_ct == 'misc':
                print name, tx['amount']
            if new_ct not in ['Transfer', 'Mortgage', 'Credit Card', 'Investment']:
                expense_dict[new_ct.title()] += int(tx['amount'])
                total += int(tx['amount'])
        return expense_dict, total

    def txns_per_category(self, transactions, category):
        expense_dict = defaultdict(float)
        total = 0
        result = []
        category = category.title()
        for tx in transactions:
            ct = tx['category']
            if tx['amount'] < 0:
                continue
            name = tx['name'].lower()
            new_ct = self.find_category(name)
            if new_ct == 'misc':
                print name, tx['amount']
            if new_ct not in ['Transfer', 'Mortgage', 'Credit Card', 'Investment']:
                if new_ct == category:
                    result.append(name.title() + '  $'+ str(tx['amount']))
                    total += int(tx['amount'])
        txns = '\n'.join(result)
        if not txns:
            txns = 'No {0} expenses.'.format(category)
        return txns

    def get_txns_category(self, category, interval=7):
        start_date, end_date = self.get_dates(interval)
        response = self.client.Transactions.get(access_token, start_date, end_date)

        transactions = response['transactions']
        result = self.txns_per_category(transactions, category)
        return result

    def get_summary(self, interval=7):
        start_date, end_date = self.get_dates(interval)
        response = self.client.Transactions.get(access_token, start_date, end_date)

        transactions = response['transactions']
        expense_dict, total = self.categorize_txns(transactions)

        labels = expense_dict.keys()
        values = expense_dict.values()

        title_str = 'Expenses Summary from '+start_date+' to '+end_date
        title_str += '\nTotal = $'+ str(total)
        fig1, ax1 = plt.subplots()
        ax1.pie(values, labels=labels, autopct=make_autopct(values),
                shadow=False, startangle=90)
        ax1.axis('equal')
        ax1.set_title(title_str)
        plt.savefig(DATA_DIR + 'plot.png')

        return 'I have sent you expenses summary.'

# obj = PlaidHandler()
# obj.get_txns_category('food', interval=14)
# obj.get_summary(7)
