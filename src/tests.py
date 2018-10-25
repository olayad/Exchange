#!/usr/bin/env python3
from exchange import * 
from test_framework.authproxy import AuthServiceProxy, JSONRPCException

import os
import random
import sys
import time
import subprocess
import shutil
import json

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
	# print("[DEBUG] startbitcoind - http://"+conf["rpcuser"]+":
	#	"+conf["rpcpassword"]+"@127.0.0.1:"+conf["rpcport"])
	return AuthServiceProxy("http://"+conf["rpcuser"]+":"
				+conf["rpcpassword"]+"@127.0.0.1:"
				+conf["rpcport"])

def initEnvironment():
	print("[Info] Initializing environment...")
	try:
		# Kill all bitcoind and liquidd that are currently running
		subprocess.call("./src/killdaemon.sh")
	except:
		subprocess.call("./killdaemon.sh")

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
	os.makedirs(b_datadir_ali)
	os.makedirs(b_datadir_bob)

	# Configure the nodes by copying the configuration files from /src/
	shutil.copyfile("./src/bitcoin-miner.conf", b_datadir_min+"/bitcoin.conf")
	shutil.copyfile("./src/bitcoin-exchange.conf", b_datadir_exc+"/bitcoin.conf")
	shutil.copyfile("./src/bitcoin-alice.conf", b_datadir_ali+"/bitcoin.conf")
	shutil.copyfile("./src/bitcoin-bob.conf", b_datadir_bob+"/bitcoin.conf")

	time.sleep(.5)
	bminconf = loadConfig(b_datadir_min+"/bitcoin.conf")
	bexcconf = loadConfig(b_datadir_exc+"/bitcoin.conf")
	baliconf = loadConfig(b_datadir_ali+"/bitcoin.conf")
	bbobconf = loadConfig(b_datadir_bob+"/bitcoin.conf")

	# Initialize bitcoind servers
	bmin = startbitcoind(b_datadir_min, bminconf)
	bexc = startbitcoind(b_datadir_exc, bexcconf)
	bali = startbitcoind(b_datadir_ali, baliconf)
	bbob = startbitcoind(b_datadir_bob, bbobconf)

	time.sleep(1.5)
	print("[Info] bitcoind servers initialized...")
	return (bmin, bexc, bbob, bali)


if __name__ == '__main__':

	bmin, bexc, bbob, bali = initEnvironment()

	print("[Info] Initializing exchange and user instances...")
	excX = Exchange("X")
	excY = Exchange("Y")
	alice = User("Alice", excX)
	tom = User("Tom", excX)
	bob = User("Bob", excY)
	
	# Start daemon searching for new txs and updating confirmations
	newtxdaemon_btc = NewTxDaemon("newTxDaemon_btc", excX, bexc, "BTC")
	checkconfsdaemon_btc = updateConfsDaemon("updateConfsDaemon_btc", excX, bexc, "BTC")
	newtxdaemon_btc.daemon = True
	checkconfsdaemon_btc.daemon = True
	newtxdaemon_btc.start()
	checkconfsdaemon_btc.start()
	time.sleep(2)

	# Generating some coins to spend
	bmin.generate(101) 
	time.sleep(1)	# Verified, enough time to propagate
	txid1 = bmin.sendtoaddress(bali.getnewaddress(), 10) # Sending 10 BTC to Alice
	time.sleep(2)
	bmin.generate(1)
	time.sleep(1) 
	# print("Min getrawmempool - Alice init funds:"+ str(bmin.getrawmempool()))
	# print("Exc getrawmempool - Alice init funds:"+ str(bexc.getrawmempool()))
	# print("Ali getrawmempool - Alice init funds:"+ str(bali.getrawmempool()))
	# print("Bob getrawmempool - Alice init funds:"+ str(bbob.getrawmempool()))
	# print()

	# print("Min getblockchaininfo():"+ str(bmin.getblockchaininfo()))
	# print("Exc getblockchaininfo():"+ str(bexc.getblockchaininfo()))
	# print("Ali getblockchaininfo():"+ str(bali.getblockchaininfo()))
	# print("Bob getblockchaininfo():"+ str(bbob.getblockchaininfo()))


	# Alice goes to exchange and wants to deposit BTC,
	# generates a deposit address in exchange
	# and sends some coins
	alice_deposit_addr = excX.generateBtcAddr(alice, bexc)
	alice.printBtcAddresses()
	bali.sendtoaddress(alice_deposit_addr, 1)
	bali.sendtoaddress(alice_deposit_addr, 2)
	bali.sendtoaddress(alice_deposit_addr, 3)
	# Tom deposits coins on the exchange
	tom_deposit_addr = excX.generateBtcAddr(tom, bexc)
	tom.printBtcAddresses()
	bali.sendtoaddress(tom_deposit_addr, 1)
	time.sleep(3)

	# print("Min getrawmempool - aftert exc deposit:"+ str(bmin.getrawmempool()))
	# print("Exc getrawmempool - aftert exc deposit:"+ str(bexc.getrawmempool()))
	# print("Ali getrawmempool - aftert exc deposit:"+ str(bali.getrawmempool()))
	# print("Bob getrawmempool - aftert exc deposit:"+ str(bbob.getrawmempool()))
	# print()
	# print("Exc listtransactions:"+ str(bexc.listtransactions()))
	bmin.generate(3)
	time.sleep(1)



	time.sleep(3)

	sys.exit(1)


	print()
	# print("bmin.listtransactions():"+ str(bmin.listtransactions()))

	print("Min getbalance():"+ str(bmin.getbalance()))
	print("Exc getbalance():"+ str(bexc.getbalance("*", 0)))
	print("Ali getbalance():"+ str(bali.getbalance()))
	print("Bob getbalance():"+ str(bbob.getbalance()))

	print("Exc listreceivedbyaddress:"+ str(bexc.listreceivedbyaddress(0 , False, True)))


	print()
	print("Exc listtransactions:"+ str(bexc.listtransactions()))
	# print("Min peers:"+str(bmin.getpeerinfo())+"\n")
	# print("Exc peers:"+str(bexc.getpeerinfo())+"\n")
	# print("Alice peers:"+str(bali.getpeerinfo())+"\n")
	# print("Bob peers:"+str(bbob.getpeerinfo())+"\n")

	bmin.stop()
	bexc.stop()
	bali.stop()
