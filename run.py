
from termcolor import colored, cprint
from progress.spinner import Spinner
from prettytable import PrettyTable
from binance.client import Client
from datetime import datetime
from binance.enums import *
import time
import sys

from title import title



# api key + secret
KEY  = "ENTER PUBLIC KEY HERE"
SECRET = "ENTER SECRET KEY HERE"

# printing vars
sell_txt = colored('sell', 'red', attrs=["bold"])
buy_txt = colored('buy', 'green', attrs=["bold"])
error_txt = colored('error', 'red', attrs=["bold"])
success_txt = colored('success', 'green', attrs=["bold"])

# print title
cprint(title, "red", attrs=['bold'])


def space_it(f):
	def func(*args, **kwargs):
		print("")
		out = f(*args, **kwargs)
		print("")
		return out
	return func


def get_time():
	now = datetime.now()
	return now.strftime("%H:%M:%S")


@space_it
def print_table(fields, row):
	table = PrettyTable()
	table.field_names = fields
	table.add_row(row)
	print(table)


@space_it
def generate_client():
	print("[{}] generating binance client...".format(get_time()))

	try:
		client = Client(KEY, SECRET)
		print("[{}] {}: generated binance client".format(get_time(), success_txt))
		return client
	
	except:
		print("[{}] {}: failed to generate client".format(get_time(), error_txt))
		return None

@space_it
def get_account_info(client):

	print("[{}] fetching account info...".format(get_time()))

	try:

		balance = client.get_asset_balance(asset='BTC')
		value = float(client.get_symbol_ticker(symbol="BTCUSDT")['price'])
		f = ['BTC Balance', "Account Value"]
		accnt_value = round(value*float(balance['free']), 2)
		r = [balance['free'], "${}".format(accnt_value)]
		print("[{}] {}: fetched info".format(get_time(), success_txt))
		print_table(f, r)

		return float(r[0])
		
	except:
		print("[{}] {}: failed to fetch info".format(get_time(), error_txt))
		return None

@space_it
def get_ticker():
	tick = input("[{}] which ticker is being pumped: ".format(get_time()))
	txt = colored("{}".format(tick.upper()), color='green', attrs=["bold"])
	print("[{}] ticker is set to {}".format(get_time(), txt))
	return tick


@space_it
def get_ticker_info(client, tick):
	info = client.get_ticker(symbol=tick+"BTC")
	precision = client.get_symbol_info(symbol=tick+"BTC")['quoteAssetPrecision']
	price = client.get_symbol_ticker(symbol=tick+"BTC")
	price = float(price['price'])

	t = ['symbol', 'priceChangePercent', 'lastPrice', 'volume']
	print_table(t, [info[i] for i in t])
	return price, precision


@space_it
def get_max_quantity(client, balance, value, tick, precision):
	print("[{}] calculating order quantity...".format(get_time()))
	qty = balance/value

	s = client.get_symbol_info('{}BTC'.format(tick))['filters'][2]['stepSize']
	qty = round(step(float(s), qty), precision)

	print(
		"[{}] calculated purchasing power: {} x {}".format(
			get_time(),
			qty,
			tick
			)
		)

	return qty

@space_it
def place_buy_order(client, ticker, qty):

	print("[{}] placing buy order...".format(get_time()))

	if True:
		
		order =  client.order_market_buy(
			symbol=ticker+"BTC",
			quantity=qty
			)

		print("[{}] {}: buy order placed".format(get_time(), success_txt))

		return order['orderId']

	#except: pass

@space_it
def place_sell_order(client, tick, qty, margin):
	print("[{}] placing sell order...".format(get_time()))

	try:
		print("[{}] {}: sell order placed".format(get_time(), success_txt))
		order = client.order_market_sell(symbol=tick+"BTC", quantity=qty)
		return order['orderId']

	except:
		pass
	

def get_order_status(client, tick, orderID):
	p = get_order_fill(client, tick, orderID)
	return colored("{}%".format(p), 'green', attrs=["bold"])
	

def get_order_fill(client, tick, orderID):
	order = client.get_order(symbol=tick+"BTC", orderId=orderID)
	s = order.keys()
	exec_qty = float(order["executedQty"])
	orig_qty = float(order["origQty"])
	return 100*exec_qty/orig_qty


@space_it
def check_buy_status(client, ticker, orderID):
	s = get_order_fill(client, ticker, orderID)
	txt = "[{}] percent filled: {}%".format(get_time(), s)
	sys.stdout.write(txt)

	while s < 100:
		s = get_order_fill(client, ticker, orderID)
		txt = "\r"+"[{}] percent filled: {}%".format(get_time(), s)
		sys.stdout.write(txt)


@space_it
def check_sell_status(client, ticker, orderID):
	s = get_sell_status(client, ticker, orderID)
	txt = "[{}] percent filled: {}%".format(get_time(), s)
	sys.stdout.write(txt)

	while s < 100:
		s = get_buy_status(client, ticker, orderID)
		s = next(gen)
		txt = "\r"+"[{}] percent filled: {}%".format(get_time(), s)
		sys.stdout.write(txt)


def get_status_info(client, ticker, value, margin):
	p = client.get_symbol_ticker(symbol=ticker+"BTC")['price']
	t = get_time()
	m = value*(1+margin)
	return t, p, m


@space_it
def await_margin_criterion(client, ticker, value, margin=0.4):
	t, p, m = get_status_info(client, ticker, value, margin)
	txt = "[{}] {}  price: {}  target: {}".format(t, ticker, p, m)
	sys.stdout.write(txt)

	for i in range(10):
		t, p, m = get_status_info(client, ticker, value, margin)
		txt = "\r"+"[{}] {}  price: {}  target: {}".format(t, ticker, p, m)
		sys.stdout.write(txt)


def get_status(client, tick, buy_id, sell_id, orig_value):
	p = client.get_symbol_ticker(symbol=tick+"BTC")['price']
	p = get_profit_txt(orig_value, p)
	b = get_order_status(client, tick, buy_id)
	s = get_order_status(client, tick, sell_id)
	t = get_time()
	return p, s, b, t 


def get_profit_txt(orig_value, price):

	r = round(((float(price)/float(orig_value))-1)*100, 3)

	print(r)

	if r > 0:
		return colored("{}%%".format(r), 'green', attrs=["bold"])

	else:
		return colored("{}%%".format(r), 'red', attrs=["bold"])


@space_it
def show_status(client, tick, buy_id, sell_id, orig_value, margin):
	p, s, b, t = get_status(client, tick, buy_id, sell_id, orig_value)
	txt = "[{}] buy status: {}  sell status: {} coin increase: {}".format(t, b, s, p)
	sys.stdout.write(txt)

	while s < 100:
		p, s, b, t = get_status(client, tick, buy_id, sell_id, orig_value)
		txt = "\r"+"[{}] buy fill: {}  sell fill: {} coin increase: {}% ".format(t, b, s, p)
		sys.stdout.write(txt)


@space_it
def get_desired_margin():
	margin = input("[{}] what is your desired margin: ".format(get_time()))
	margin= float(margin)
	marg_txt = colored("{}%".format(margin*100), color='green', attrs=["bold"])
	print("[{}] set margin to {}".format(get_time(), marg_txt))
	return margin


def step(step_sz, quantity):
	return (quantity//step_sz)*step_sz


def main():

	# generate client
	client = generate_client()
	
	# get account info
	accnt_balance = get_account_info(client)*0.05

	# get desired margin
	margin = get_desired_margin()

	# get ticker
	tick = get_ticker()

	# get ticker value
	orig_value, precision = get_ticker_info(client, tick)

	# get max quanity
	qty = get_max_quantity(client, accnt_balance, orig_value, tick, precision)
	
	# place buy order
	buy_id = place_buy_order(client, tick, qty)

	# wait for buy to fill
	check_buy_status(client, tick, buy_id)

	# place sell order
	sell_id = place_sell_order(client, tick, qty, margin)

	# wait for sell off
	show_status(client, tick, buy_id, sell_id, orig_value, margin)


if __name__ == "__main__":
	main()