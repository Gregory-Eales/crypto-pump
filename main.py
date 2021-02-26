"""

1. get account info BTC/USD

2. 
	

"""

import sys
from termcolor import colored, cprint
from binance.client import Client
import time
from datetime import datetime
from title import title
import asyncio
from prettytable import PrettyTable
from progress.spinner import Spinner
from binance.enums import *

cprint(title, "red", attrs=['bold'])

# api vars
KEY  = "ENTER PUBLIC KEY HERE"
SECRET = "ENTER SECRET KEY HERE"


MARGIN = 0.0
TICKER = ""
PRICE = 0
AMOUNT = 0

# printing vars
sell_txt = colored('sell', 'red', attrs=["bold"])
buy_txt = colored('buy', 'green', attrs=["bold"])
error_txt = colored('error', 'red', attrs=["bold"])
success_txt = colored('success', 'green', attrs=["bold"])

loop = asyncio.get_event_loop()


def get_time():
	now = datetime.now()
	return now.strftime("%H:%M:%S")


def print_buying(ticker, amount):

	order = client.create_test_order(
	symbol='BNBBTC',
	side=SIDE_BUY,
	type=ORDER_TYPE_MARKET,
	timeInForce=TIME_IN_FORCE_GTC,
	quantity=100,
	price='0.00001')

	print(order)

	print("[{}] {}: {} x {}".format(get_time(), buy_txt, amount, ticker))


def print_selling(ticker, amount):
	pass


def print_error():
	print("[{}] {}: {}".format(get_time(), error_txt, 'unable to perform action'))

def generate_client():
	print("")
	print("[{}] generating binance client...".format(get_time()))
	client = Client(KEY, SECRET)
	#client.API_URL = 'https://api.binance.us/api'
	print("[{}] {}: generated binance client".format(get_time(), success_txt))
	print("")
	return client

def get_account_info(client):
	print("")
	print("[{}] fetching account info...".format(get_time()))
	print("[{}] {}: fetched info".format(get_time(), success_txt))
	print("")
	balance = client.get_asset_balance(asset='BTC')
	k = ['BTC Balance']
	table = PrettyTable()
	#print(info.keys())
	table.field_names = k
	table.add_row([balance['free']])
	
	print(table)
	print("")

	print(client.get_asset_details()['assetDetail'].keys())
	


def get_desired_margin():
	print("")
	global MARGIN
	MARGIN = input("[{}] what is your desired margin: ".format(get_time()))
	MARGIN = float(MARGIN)
	marg_txt = colored("{}%".format(MARGIN*100), color='green', attrs=["bold"])
	print("[{}] set margin to {}".format(get_time(), marg_txt))
	print("")


def get_ticker():
	print("")
	global TICKER
	TICKER = input("[{}] which ticker is being pumped: ".format(get_time()))
	tick_txt = colored("{}".format(TICKER.upper()), color='green', attrs=["bold"])
	print("[{}] ticker is set to {}".format(get_time(), tick_txt))
	print("")
	


def place_order(client):
	print("")
	print("[{}] calculating order quantity...".format(get_time()))
	print("[{}] placing buy order...".format(get_time()))
	print("[{}] {}: buy order placed".format(get_time(), success_txt))
	print("")

	print("")
	print("[{}] placing sell order...".format(get_time()))
	print("[{}] {}: sell order placed".format(get_time(), success_txt))
	print("")


def show_ticker_info(client):
	info = client.get_ticker(symbol=TICKER+"USD")
	price = client.get_symbol_ticker(symbol=TICKER+"USD")
	global PRICE
	PRICE = float(price['price'])
	
	print("")
	k = ['symbol', 'priceChangePercent', 'lastPrice', 'volume']
	table = PrettyTable()
	table.field_names = k
	table.add_row([info[i] for i in k])
	print(table)
	print("")


def get_status_info(client):
	p = client.get_symbol_ticker(symbol=TICKER+"USD")['price']
	t = get_time()
	m = PRICE*(1+MARGIN)
	return t, p, m

def check_order_status(client):
	
	t, p, m = get_status_info(client)
	txt = "[{}] {}  price: {}  target: {}".format(t, TICKER, p, m)
	sys.stdout.write(txt)

	for i in range(100):
		#sys.stdout.flush()
		t, p, m = get_status_info(client)
		txt = "\r"+"[{}] {}  price: {}  target: {}".format(t, TICKER, p, m)
		sys.stdout.write(txt)

	print("")


def buy(client, ticker, amount):
	
	print_buying(ticker, amount)

	try:
		print(order)

	except:
		print_error()


def sell(ticker):
	print_selling(ticker, amount)

def main():

	# generate client
	client = generate_client()


	# get fee for one symbol
	print(client.get_trade_fee(symbol='BNBBTC'))


	order = client.create_test_order(
		symbol='BNBBTC',
		side=SIDE_BUY,
		type=ORDER_TYPE_MARKET,
		quantity=100,
		)

	print(order)


	"""
	# print account details
	#get_account_info(client)

	# ask for desired profit margin
	#get_desired_margin()

	# get ticker from user
	#get_ticker()
	
	# place ticker order
	#place_order(client)


	# show potential earnings
	#show_ticker_info(client)
	#check_order_status(client)
	"""

	print("")
	print("")
	print("")

if __name__ == "__main__":
	main()
