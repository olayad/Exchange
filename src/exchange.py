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
		
	def getUser(self, name):
		for u in self.users:
			if u.name == name:
				print("[Debug] getUser() - name:"+name+"\t return:"+str(u.uid)+" "+u.name)
				return u
		print("[Debug] getUser() - name:"+name+"\t return:-1")
		return -1

	def getUserID(self, name):
		for u in self.users:
			if u.name == name:
				# print("[DEBUG] getUserID() - Returning user_name:"+name+"\tuid:"+str(u.uid))
				return u.uid
		# print("[DEBUG] getUserID() - Returning -1 for user_name:"+name)
		return -1 

	def generateBtcAddr(self, user_name):
		address = bexc.getnewaddress()	
		user = self.getUser(user_name)
		print("[Debug] getUser() return:",user)
		if (user is not -1):
			user.addBtcAddress(address)
		else:
			sys.exit('getUser() returned -1, Is the user "%s" is registered in the exchange "%s"?'%(user_name, self.name))
		print("[Info] - generateBtcAddr() pubkey:"+address+" \t | User:"+user_name)

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
tom = User("Tom", excA)
bob = User("Bob", excB)


excA.printUsers()
excB.printUsers()

# Generating some coins to spend
bmin.generate(101)
time.sleep(.5)
print()

excA.generateBtcAddr("Alice")
excA.generateBtcAddr("Alice")
excA.generateBtcAddr("Alice")
excA.generateBtcAddr("Alice")
excA.generateBtcAddr("Alice")
excB.generateBtcAddr("Bob")
excB.generateBtcAddr("Tom")

alice.printBtcAddresses()
bob.printBtcAddresses()
tom.printBtcAddresses()

excA.getUser("Tom")


bmin.stop()
bexc.stop()


