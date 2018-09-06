#!/usr/bin/env python3

from test_framework.authproxy import AuthServiceProxy, JSONRPCException
import os
import random
import sys
import time
import subprocess
import shutil
import json
import threading

CONFS = 3		# Number of confirmations required to move a tx from unconfirmed to confirmed

# This thread purpose is to monitor listtransactions() and check if a new transaction has been recieved.
class DaemonTx(threading.Thread):
	def __init__(self, tid, exc, bexc, chain):
		assert((chain is not None) and (chain == "BTC" or chain == "LIQ"))
		threading.Thread.__init__(self)
		self.exc = exc 
		self.tid = tid
		self.bexc = bexc
		self.chain = chain

	def run(self):
		print("[Info] Initializing "+str(self.tid)+" thread...")
		print("[Info] Thread "+self.tid+" - Monitoring "+self.chain+" address list...")

		# Creating a new btc transaction 
		while (True):
			time.sleep(1)
			try:
				data = self.bexc.listtransactions()
			except:
				continue
			if (len(data) == 0  ): #Need to add the case for when there are no new transactions
				continue
			else:
				for tx in data:
					for item in tx:
						# Unconfirmed transactions
						if ((self.chain == "BTC") and (tx["confirmations"] < CONFS) and (tx["txid"] not in self.exc.btc_tx_set)):
							print("[Debug] - "+self.chain+" tx is UNCONFIRMED and NOT in btc_tx_set - txid: "+tx["txid"])
							new_tx = BtcTx(tx["account"], tx["address"], tx["category"], tx["amount"], tx["label"], tx["vout"], tx["confirmations"], tx["txid"], tx["time"], 0)
							self.exc.unconf_btc_tx.append(new_tx)
							self.exc.btc_tx_set.add(tx["txid"])
							# For confirmed transactions

							print("\n-=-=-= Set =-=-=-")
							print(self.exc.btc_tx_set)
							print("-=-=-=-=-=-=-=-=-=-")
						else:
							continue
		



class Exchange:
	def __init__(self, name):
		self.name = name
		self.user_ctr = 0
		self.users = []
		self.conf_liq_tx = []		# 3 confirmations required
		self.unconf_liq_tx = []
		self.conf_btc_tx = []
		self.unconf_btc_tx = []
		self.btc_tx_set = set()


	def getUser(self, name):
		for u in self.users:
			if u.name == name:
				# print("[Debug] getUser() - name:"+name+"\t return:"+str(u.uid)+" "+u.name)
				return u
		# print("[Debug] getUser() - name:"+name+"\t return:-1")
		return -1

	def getUserID(self, name):
		for u in self.users:
			if u.name == name:
				# print("[DEBUG] getUserID() - Returning user_name:"+name+"\tuid:"+str(u.uid))
				return u.uid
		# print("[DEBUG] getUserID() - Returning -1 for user_name:"+name)
		return -1 

	def generateBtcAddr(self, user_name, bexc):
		address = bexc.getnewaddress()	
		if (user_name is None):
			print("[Info] - generateBtcAddr() - No user given, pubkey:"+address+"\t")
			return bexc.getnewaddress()
		# Add new address to user used btc address list and monitored address list for exchange
		user = self.getUser(user_name)
		if (user is not -1):
			user.addBtcAddress(address)
			print("[Info] - generateBtcAddr() pubkey:"+address+" \t | User:"+user_name)
			return address
		else:
			sys.exit('getUser() returned -1, Is the user "%s" is registered in the exchange "%s"?'%(user_name, self.name))

	def printUsers(self):
		print("\n-=-=-= Exchange: "+self.name+" User List=-=-=-")
		print('{0:<3} {1:<10} {2:<10}'.format("ID", "User_Name", "BTC_balance"))
		for u in self.users:

			print('{0:3d} {1:<10} {2:10d}'.format(u.uid, u.name, 0))
			# print("ID: "+str(u.uid)+" \tUser_name: "+u.name+"\t\t"+"BTC_balance: ")
		print("Total users:", self.user_ctr)
		print("-=-=-= End of List =-=-=-")

class User:
	def __init__(self, name, exchange):
		self.uid = exchange.user_ctr
		self.name = name  	#TODO: name must be unique
		self.conf_btc_txs = []
		self.unconf_btc_txs = []
		self.btc_addr = []
		exchange.users.append(self);
		exchange.user_ctr += 1

	def __repr__(self):
		return str(self.__dict__)

	def addBtcAddress(self, address):
		self.btc_addr.append(address)

	def printBtcAddresses(self):
		print("\n-=-=-= PubKeys: "+self.name+" =-=-=-")
		for p in self.btc_addr:
			print('{0:<6}'.format(p))
		print("-=-=-= End of List =-=-=-")


class BtcTx:
	def __init__ (self, account, address, category, amount, label, vout, confirmations, txid, time, status):
		self.account = account
		self.address = address
		self.category = category
		self.amount = amount
		self.label = label
		self.vout = vout
		self.confirmations = confirmations
		self.txid = txid
		self.time = time
		self.status = status # 0: unconfirmed, 1: confirmed

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

def sendBtcTx(server, address, amount):	
	server.sendtoaddress(address, amount)


# if __name__ == '__main__':