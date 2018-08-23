#!/usr/bin/env python3

from test_framework.authproxy import AuthServiceProxy, JSONRPCException
import os
import random
import sys
import time
import subprocess
import shutil

class Exchange:
	def __init__(self):
		self.users = []
		self.conf_liq_tx = []
		self.unconf_liq_tx = []
		self.conf_btc_tx = []
		self.unconf_btc_tx = []

class User:
	usr_ctr = 0
	def __init__(self, name, exchange):
		User.usr_ctr += 1
		self.uid = User.usr_ctr
		self.name = name
		self.conf_btc_txs = []
		self.unconf_btc_txs = []

		exchange.users.append(self);

	def __repr__(self):
		return str(self.__dict__)

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
	print("[Info] - Initializing bitcoind -datadir="+datadir)
	command = "bitcoind -datadir="+datadir
	print("Command to run: ", command)
	subprocess.Popen(command, shell=True, stdout=subprocess.PIPE)
	return AuthServiceProxy("http://"+conf["rpcuser"]+":"+conf["rpcpassword"]+"@127.0.0.1:"+conf["rpcport"])



print("[Info] Initializing environment...")

# Make data directories for each daemon
b_datadir_min="./tmp/btc-min"	
b_datadir_exc="./tmp/btc-exc"	
b_datadir_ali="./tmp/btc-ali"	
b_datadir_bob="./tmp/btc-bob"	

# Remove existing data


# folders = b_datadir_min, b_datadir_exc, b_datadir_ali, b_datadir_bob
# for f in folders:
try:
	shutil.rmtree("./tmp")
except FileNotFoundError:
	pass


os.makedirs(b_datadir_min)

# # Also configure the nodes by copying the configuration files from
shutil.copyfile("./src/bitcoin-miner.conf", b_datadir_min+"/bitcoin.conf")

bminconf = loadConfig(b_datadir_min+"/bitcoin.conf")
bmin = startbitcoind(b_datadir_min, bminconf)

# Need to copy an existing wallet.dat since bitcoind doesn't generate one
# shutil.copytree("./src/wallet-miner", b_datadir_min+"/regtest/wallets" )

time.sleep(2)


print(bmin.generate(101))
print("GETBALANCE:", bmin.getbalance())

print("GETBLOCKCHAININFO:", bmin.getblockchaininfo())
bmin.stop()


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
