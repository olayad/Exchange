#!/usr/bin/env python3

from test_framework.authproxy import AuthServiceProxy, JSONRPCException
import os
import random
import sys
import time
import subprocess
import shutil

class Exchange:
	def __init__(self, name):
		self.name = name
		self.user_ctr = 0
		self.users = []
		self.conf_liq_tx = []
		self.unconf_liq_tx = []
		self.conf_btc_tx = []
		self.unconf_btc_tx = []
		
	def printUsers(self):
		print("-=-=-= Exchange: "+self.name+" users=-=-=-")
		for u in self.users:
			print("ID: "+str(u.uid)+" \tName: "+u.name+" \tBTC Balance: ")
		print("Total users:", self.user_ctr)
		print("-=-=-= End of List =-=-=-")

class User:
	def __init__(self, name, exchange):
		self.uid = exchange.user_ctr
		self.name = name
		self.conf_btc_txs = []
		self.unconf_btc_txs = []
		self.btc_addresses = []

		exchange.users.append(self);
		exchange.user_ctr += 1

	def __repr__(self):
		return str(self.__dict__)

	def addBtcAddress(self, address):
		self.btc_addresses.append(address)

class BtcTx:
	def __init__ (self, txid, vout, address, amount, status):
		self.txid = txid
		self.vout = vout
		self.address = address
		self.amount = amount
		self.status = status	# 0: unconfirmed, 1: confirmed

	def __repr__(self):
		return str(self.txid)

class LiqTx(BtcTx):
	def __init__ (self, txid, vout, address, amount, status, blinder, assetblinder):
		super().__init__(txid, vout, address, amount, status)
		self.blinder = blinder
		self.assetblinder = assetblinder


def loadConfig(filename):
	conf = {}
	with open(filename) as f:
		for line in f:
			if len(line) == 0 or line[0] == "#" or len(line.split("=")) != 2:
				continue
			conf[line.split("=")[0]] = line.split("=")[1].strip()
	conf["filename"] = filename
	return conf

def startbitcoind(datadir, conf, args=""):
	command = "bitcoind -datadir="+datadir+" -conf=./bitcoin.conf"
	print("[Info] - Initializing "+command)
	subprocess.Popen(command, shell=True, stdout=subprocess.PIPE)
	# print("[Debug] startbitcoind - Initilizing bitcoind with command: ", command)
	# print("[DEBUG] startbitcoind - http://"+conf["rpcuser"]+":"+conf["rpcpassword"]+"@127.0.0.1:"+conf["rpcport"])

	return AuthServiceProxy("http://"+conf["rpcuser"]+":"+conf["rpcpassword"]+"@127.0.0.1:"+conf["rpcport"])

def generateBtcDepositAddr(user):
	pass



print("[Info] Initializing environment...")
subprocess.call("./src/killdaemon.sh") 		# Kill all bitcoind and liquidd that are currently runniewng

# Make data directories for each daemon
b_datadir_min="./tmp/btc-min"	
b_datadir_exc="./tmp/btc-exc"	
b_datadir_ali="./tmp/btc-ali"	
b_datadir_bob="./tmp/btc-bob"	

# Remove pre-existing data
try:
	shutil.rmtree("./tmp")
except FileNotFoundError:
	pass

#Create new data folders
os.makedirs(b_datadir_min)
os.makedirs(b_datadir_exc)
# os.makedirs(b_datadir_ali)
# os.makedirs(b_datadir_bob)

# Configure the nodes by copying the configuration files from /src/
shutil.copyfile("./src/bitcoin-miner.conf", b_datadir_min+"/bitcoin.conf")
shutil.copyfile("./src/bitcoin-exchange.conf", b_datadir_exc+"/bitcoin.conf")
time.sleep(.5)
bminconf = loadConfig(b_datadir_min+"/bitcoin.conf")
bexcconf = loadConfig(b_datadir_exc+"/bitcoin.conf")

# Initialize bitcoind servers
bmin = startbitcoind(b_datadir_min, bminconf)
bexc = startbitcoind(b_datadir_exc, bexcconf)
time.sleep(2)

print("[Info] bitcoind servers initialized...")

print("[Info] Initializing exchange and user instances...")
excA = Exchange("A")
excB = Exchange("B")
alice = User("Alice", excA)
bob = User("Bob", excB)
print("Print excA user list:", excA.printUsers())

# Generating some coins to spend
bmin.generate(101)
print("bmin.getnewaddress", bmin.getnewaddress())
print("bmin.getbalance():", bmin.getbalance())
time.sleep(.5)
print()


print("[Info] bexc.getbalance: ", bexc.getbalance())

bmin.stop()
bexc.stop()


# print("[Info] Starting exchange.py...")

# exc_a = Exchange()
# exc_b = Exchange()

# alice = User("Alice", exc_a)
# bob = User("Bob", exc_b)

# btctx1 = BtcTx("b1aaa", 0, "2dmwiWt9r", 0.8999, 1)
# lqtx1 = LiqTx("l1aaa", 0, "2dmwiWt9r", 0.9 , 1, "blinderblinder", "assetblinderassetblinder")

# print("-=-=-= [Printing Transactions] =-=-=-")
# print("Lqtx1", lqtx1)
# print("Tx1: ", btctx1)

# print("-=-=-= [Printing users in Exchange A] =-=-=-")
# for user in exc_a.users:
# 	print(user.uid, user.name)
# print("-=-=-= [Printing users in Exchange B] =-=-=-")
# for user in exc_b.users:
# 	print(user.uid, user.name)
