import os
import json
import datetime
import sys
from collections import defaultdict

from plaid_handler import PlaidHandler
from config import REDIS_KEY, MESSENGER_ID
from utils import send_alert, send_image
import redis

budget_dict = defaultdict(float)

budget_dict = {
    'Food': 100,
    'Auto Loan': 230,
    'Mortgage': 2900,
    'Transfer': 20000,
    'Credit Card': 1000,
    'Hoa': 250,
    'electricity': 100
}

def track_expenses():
    r = redis.StrictRedis(host='localhost', port=6379, db=0)

    plaid = PlaidHandler()
    transactions = plaid.get_transactions(7)
    new_txns = []
    set_cnt = r.scard(REDIS_KEY)

    for tx in transactions:
        if tx['amount'] < 0:
            continue
        if not r.sismember(REDIS_KEY, tx['transaction_id']):
            new_txns.append(tx)
        r.sadd(REDIS_KEY, tx['transaction_id'])

    expenses_dict, total = plaid.categorize_txns(transactions)
    template = "The expense {name} ${amount} exceeds your weekly budget for {category}"
    if set_cnt > 0:
        for tx in new_txns:
            ct = plaid.find_category(tx['name'])
            if ct == 'Atm':
                continue
            if expenses_dict[ct] > budget_dict.get(ct, 100):
                msg = template.format(name=tx['name'].title(), amount=tx['amount'], category=ct)
                send_alert(msg, False)
                print msg


def send_chart(interval):
    plaid = PlaidHandler()
    result = plaid.get_summary(interval)
    send_image(MESSENGER_ID['arun'], 'plot.png', result, True)

def del_key():
    r = redis.StrictRedis(host='localhost', port=6379, db=0)
    r.delete(REDIS_KEY)

if __name__ == '__main__':
    action =  sys.argv[1]
    if action == 'del':
        del_key()
    elif action == 'track':
        track_expenses()
    elif action == 'weekly':
        send_chart(7)
    elif action == 'monthly':
        send_chart(30)
# J0azg6yLPqujZQ0xP8A7CZD6grJp1muqre9QQ
# srem plaid_txns J0azg6yLPqujZQ0xP8A7CZD6grJp1muqre9QQ
