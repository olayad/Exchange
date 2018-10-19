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

CONFS = 3	# Number of confirmations required to have a confirmed tx

# Thread that is updating confirmations in the conf/unconf user tx list
class updateConfsDaemon(threading.Thread):
	def __init__(self, tid, exc, bexc, chain):
		assert((chain is not None) and (chain == "BTC" or chain == "LIQ"))
		assert ((exc is not None) and (bexc is not None))
		threading.Thread.__init__(self)
		self.exc = exc
		self.tid = tid
		self.bexc = bexc
		self.chain = chain 

	def run(self):
		print("[Info] Initializing "+str(self.tid)+
			" thread, updating confirmations in user txs list...")
		while(True):
			time.sleep(1)
			# Updating unconfirmed txs
			for u in self.exc.users:
				if u.total_unconf >= 1:
					self.updateConfs(u)
				else:
					continue
			#TODO: I have the transaction, check if it has confirmations

	def updateConfs(self, user):
		print("[Debug] updateConfsDaemon - Updating confs for user:"+user.name
			+"")
		# Updates BTC txs first
		for t in user.unconf_btc_txs:
			print("***\t[Debug] updateConfs \tuser:"+user.name+
				"\ttx:"+t)
			tx = self.bexc.getrawtransaction(user.unconf_btc_txs[t].txid, 1)
			try:
				if tx["confirmations"] >= CONFS:
					print("[Debug] updateConfs - Monitored", \
					"tx is now CONF",tx["confirmations"])
				print(user.unconf_btc_txs[t])
				user.unconf_btc_txs[t].status = 1
				# Remove from unconf list and add to confirmed
				print("BTC unconf list (before pop) len:%d"% len(user.unconf_btc_txs))
				print("BTC confirmed list (before insertion) len:%d"% len(user.conf_btc_txs))	
				popped = user.unconf_btc_txs.pop(t)
				user.conf_btc_txs[t] = popped
				print("BTC unconf list (after pop) len:%d"% len(user.unconf_btc_txs))
				print("BTC confirmed list (after insertion) len:%d"% len(user.conf_btc_txs))	
				#LEFT HERE: Fix error dictionary changed size during iteration
				#TODO: change name of function to updateStatus	
			except KeyError:
				print("[Debug] updateConfs - Monitored tx still", \
					"UNCONFIRMED:", tx["txid"])



		#TODO: Do not forget to decrease total_unconf at the end

# Thread that monitors listtransactions() to check if a new transaction has been recieved. 
# If a new transaction has been received, it appends to the exchange
# list of conf/unconf transaction. 
class NewTxDaemon(threading.Thread):
	def __init__(self, tid, exc, bexc, chain):
		assert((chain is not None) and (chain == "BTC" or chain == "LIQ"))
		assert((exc is not None) and bexc is not None)
		threading.Thread.__init__(self)
		self.exc = exc 
		self.tid = tid
		self.bexc = bexc
		self.chain = chain

	def process_new_tx(self, tx):
		# Find user from the recepient adddress
		user = self.exc.address_user[tx["address"]]

		# New UNCONF tx found
		if (self.chain == "BTC" 
			and tx["txid"] not in self.exc.btc_tx_set 
			and tx["confirmations"] < CONFS):

			print("[Debug] "+self.chain+
				" tx is UNCONFIRMED and not in btc_tx_set - txid: "+tx["txid"])
			new_tx = BtcTx(tx["account"], tx["address"], tx["category"],
					tx["amount"], tx["label"], tx["vout"], 
					tx["txid"], tx["time"], 0)
			print("[Debug] NewTxDaemon - User of the deposit address is:"
				+ user.name+" ,  address:"+tx["address"])
			# Add the transaction to user
			if user is not None:
				user.unconf_btc_txs[tx["txid"]] = new_tx
				user.total_unconf+=1
				print("[Debug] NewTxDaemon - "+user.name+
					" total_unconfs: "+str(user.total_unconf))
			# Adds to the set monitored by NewTxDaemon
			self.exc.btc_tx_set.add(tx["txid"])	
			self.exc.print_monitored_tx()

		# New CONF tx found
		elif (self.chain == "BTC"
			and tx["txid"] not in self.exc.btc_tx_set
			and tx["confirmations"] >= CONFS):

			print("[Debug] "+self.chain+
				" tx is CONF and not in btc_tx_set - txid: "+tx["txid"])
			new_tx = BtcTx(tx["account"], tx["address"], tx["category"],
					tx["amount"], tx["label"], tx["vout"], 
					tx["confirmations"], tx["txid"], tx["time"], 0)
			print("[Debug] NewTxDaemon - User of the deposit address is:"
				+ user.name+" ,  address:"+tx["address"])
			# Add the transaction to user
			if user is not None:
				user.conf_btc_txs[tx["txid"]] = new_tx
				user.total_unconf+=1
				print("[Debug] NewTxDaemon - "+user.name+
					" total_unconfs: "+str(user.total_unconf))
			# Adds to the set monitored by NewTxDaemon
			self.exc.btc_tx_set.add(tx["txid"])			

		# TODO: Liq business logic
		else:
			pass

	def run(self):
		# TODO: What happens if I get a transaction without user?

		print("[Info] Initializing "+str(self.tid)+" thread, monitoring address list...")
		# Checks if the recieved tx is alred included in the exchange 
		# btc_tx_set, if not, it creates a new tx instance and adds 
		# it to exchange list of conf and unconf txs
		while (+
			True):
			time.sleep(1)
			try:
				if (self.chain == "BTC"):
					data = self.bexc.listtransactions()
				else:
					# TODO
					print("This is for Liquid transactions")
			except:
				continue
		 	# Case for when there are no new transactions	
			if (len(data) == 0):
				continue
			else:
				for tx in data:
					self.process_new_tx(tx)

	def printTxSet(self):
			print("-=-=-= Printing "+self.exc+self.chain+"_tx_set =-=-=-")
			if (self.chain == "BTC"):
				print(self.exc.btc_tx_set)
			else:
				# TODO
				print("TODO, LIQ tx set")
			print("-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-")
		

		
class Exchange:
	def __init__(self, name):
		self.name = name
		self.user_ctr = 0
		self.users = []

		self.address_user = {}	# Retuns a user for a given deposit address
		self.btc_tx_set = set()

	# def getUser(self, name):
	# 	for u in self.users:
	# 		if u.name == name:
	# 			 print("[Debug] getUser() - name:"+name+
	#				"\t return:"+str(u.uid)+" "+u.name)
	# 			return u
	# 	# print("[Debug] getUser() - name:"+name+"\t return:-1")
	# 	return -1
	
	# def getUserID(self, name):
	# 	for u in self.users:
	# 		if u.name == name:
	# 			# print("[DEBUG] getUserID() - Returning user_name:
	#				"+name+"\tuid:"+str(u.uid))
	# 			return u.uid
	# 	# print("[DEBUG] getUserID() - Returning -1 for user_name:"+name)
	# 	return -1 

	def print_monitored_tx(self):
		print("[Debug] \t-=-=-= Printing list of monitored NewTxDaemon =-=-=-Exc:"+self.name)
		for tx in self.btc_tx_set:
				print("\t"+tx)
		print("\t-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-")

	def generateBtcAddr(self, user, bexc):
		assert(isinstance(user, User) or (user == None))
		address = bexc.getnewaddress()	
		if user is None:
			print("[Debug] generateBtcAddr() - No user given, pubkey:"+address+"\t")
			return bexc.getnewaddress()
	
		# Add new address to user's used btc address list and monitored address list for exchange
		else:	
			# Adds new adddress to the user set of address 
			user.btc_addr.add(address)
			# Adds new address to the exchange dict Address:User 
			self.address_user[address] = user 
			print("[Debug] generateBtcAddr() pubkey:"+address+" \t | User:"+user.name)
			return address

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
		self.total_unconf = 0
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
	def __init__ (self, account, address, category, amount,
			 label, vout, txid, time, status):
		self.account = account
		self.address = address
		self.category = category
		self.amount = amount
		self.label = label
		self.vout = vout
		self.txid = txid
		self.time = time
		self.status = status # 0: unconfirmed, 1: confirmed

	def __repr__(self):
		return str("\nBTCTX:\t: "+self.txid+"\t addr: "+self.address+
				"\tstatus:"+str(self.status)+
				"\tamount:"+str(self.amount))

class LiqTx(BtcTx):
	def __init__ (self, txid, vout, address, amount, status, blinder, assetblinder):
		super().__init__(txid, vout, address, amount, status)
		self.blinder = blinder
		self.assetblinder = assetblinder

# if __name__ == '__main__':
