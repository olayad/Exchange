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

CONFS = 3		# Number of confirmations required to have a confirmed tx

# Thread that monitors listtransactions() to check if a new transaction has been recieved. 
# If a new transaction has been received, it appends to the exchange list of conf/unconf transaction.
class NewTxDaemon(threading.Thread):
	def __init__(self, tid, exc, bexc, chain):
		assert((chain is not None) and (chain == "BTC" or chain == "LIQ"))
		threading.Thread.__init__(self)
		self.exc = exc 
		self.tid = tid
		self.bexc = bexc
		self.chain = chain

	def run(self):
		# TODO: What happens if I get a transaction without user?

		print("[Info] Initializing "+str(self.tid)+" thread, monitoring address list...")
		# Checks if the recieved tx is alred included in the exchange btc_tx_set, if not,
		# it creates a new tx instance and adds it to exchange list of conf and unconf txs
		while (True):
			time.sleep(1)
			try:
				if (self.chain == "BTC"):
					data = self.bexc.listtransactions()
				else:
					# TODO
					print("This is for Liquid transactions")
			except:
				continue
			if (len(data) == 0): 		# Case for when there are no new transactions
				continue
			else:
				for tx in data:

					# Find user from the recepient adddress
					user = self.exc.address_user[tx["address"]]
					# New unconfirmed transaction found
					if ((self.chain == "BTC") and (tx["txid"] not in self.exc.btc_tx_set) and (tx["confirmations"] < CONFS)):
						print("[Debug] - "+self.chain+" tx is UNCONFIRMED and NOT in btc_tx_set - txid: "+tx["txid"])
						new_tx = BtcTx(tx["account"], tx["address"], tx["category"], tx["amount"], tx["label"], tx["vout"], tx["confirmations"], tx["txid"], tx["time"], 0)

						print("[Debug] NewTxDaemon - User of the deposit address is:"+ user.name+" ,  address:"+tx["address"])
						# Add the transaction to user
						if (user is not None):
							user.unconf_btc_txs[tx["txid"]] = new_tx
						self.exc.btc_tx_set.add(tx["txid"])		# Adds to the set monitored by NewTxDaemon
						print("+++++++++++++++++unconf_btc_tx:")
						for m in user.unconf_btc_txs:
							print(m)

					# New confirmed transaction found
					elif ((self.chain == "BTC") and (tx["txid"] not in self.exc.btc_tx_set) and (tx["confirmations"] >= CONFS)):
						print("[Debug] - "+self.chain+" tx is CONFIRMED and NOT in btc_tx_set - txid: "+tx["txid"])
						new_tx = BtcTx(tx["account"], tx["address"], tx["category"], tx["amount"], tx["label"], tx["vout"], tx["confirmations"], tx["txid"], tx["time"], 0)
						
						print("[Debug] NewTxDaemon - User of the deposit address is:"+ user.name+" ,  address:"+tx["address"])
						# Add the transaction to user
						if (user is not None):
							user.conf_btc_txs[tx["txid"]] = new_tx
						self.exc.btc_tx_set.add(tx["txid"])		# Adds to the set monitored by NewTxDaemon



						# self.printTxSet()
						pass
					else:
						continue

					print()

	def printTxSet(self):
			print("-=-=-= Printing "+self.chain+"_tx_set =-=-=-")
			if (self.chain == "BTC"):
				print(self.exc.btc_tx_set)
			else:
				print("TODO, LIQ tx set")
			print("-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-")
		

# Thread that is checking for new confirmations in the conf/unconf exchange tx list
class CheckConfsDaemon(threading.Thread):
	def __init__(self, tid, exc, bexc, chain):
		assert((chain is not None) and (chain == "BTC" or chain == "LIQ"))
		threading.Thread.__init__(self)
		self.tid = tid
		self.exc = exc
		self.bexc = bexc
		self.chain = chain

	def run(self):
		print("[Info] Initializing "+str(self.tid)+" thread, updating confirmations in txs list...")
		while(True):
			time.sleep(1)
			# Updating unconfirmed txs
			# for tx in self.exc.unconf_btc_tx:
			# 	try:
			# 		tx = self.bexc.gettransaction(tx.txid)
			# 		# print(tx)
			# 	except:
			# 		continue
			


class Exchange:
	def __init__(self, name):
		self.name = name
		self.user_ctr = 0
		self.users = []

		self.address_user = {}		# Retuns a user for a given deposit address
		self.btc_tx_set = set()


	# def getUser(self, name):
	# 	for u in self.users:
	# 		if u.name == name:
	# 			# print("[Debug] getUser() - name:"+name+"\t return:"+str(u.uid)+" "+u.name)
	# 			return u
	# 	# print("[Debug] getUser() - name:"+name+"\t return:-1")
	# 	return -1

	# def getUserID(self, name):
	# 	for u in self.users:
	# 		if u.name == name:
	# 			# print("[DEBUG] getUserID() - Returning user_name:"+name+"\tuid:"+str(u.uid))
	# 			return u.uid
	# 	# print("[DEBUG] getUserID() - Returning -1 for user_name:"+name)
	# 	return -1 

	def generateBtcAddr(self, user, bexc):
		assert(isinstance(user, User) or None)

		address = bexc.getnewaddress()	
		if (user is None):
			print("[Debug] generateBtcAddr() - No user given, pubkey:"+address+"\t")
			return bexc.getnewaddress()
		# Add new address to user used btc address list and monitored address list for exchange
		# user = self.getUser(user)

		else:
			user.btc_addr.add(address) 			# Adds new adddress to the user set of address 
			self.address_user[address] = user 	# Adds new address to the exchange dict Address:User
			print("[Debug] generateBtcAddr() pubkey:"+address+" \t | User:"+user.name)
			return address
		# else:
		# 	sys.exit('getUser() returned -1, Is the user "%s" is registered in the exchange "%s"?'%(user, self.name))

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
		self.conf_btc_txs = {} 			
		self.unconf_btc_txs = {}
		self.conf_liq_txs = {}		
		self.unconf_liq_txs = {}
		self.btc_addr = set()
		exchange.users.append(self);
		exchange.user_ctr += 1

	def __repr__(self):
		return str(self.__dict__)

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
		return str("BtcTx: "+self.txid)

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
	print("[Info] Initializing "+command)
	subprocess.Popen(command, shell=True, stdout=subprocess.PIPE)
	# print("[Debug] startbitcoind - Initilizing bitcoind with command: ", command)
	# print("[DEBUG] startbitcoind - http://"+conf["rpcuser"]+":"+conf["rpcpassword"]+"@127.0.0.1:"+conf["rpcport"])

	return AuthServiceProxy("http://"+conf["rpcuser"]+":"+conf["rpcpassword"]+"@127.0.0.1:"+conf["rpcport"])

def sendBtcTx(server, address, amount):	
	server.sendtoaddress(address, amount)


# if __name__ == '__main__':