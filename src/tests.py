#!/usr/bin/env python3
from exchange import Exchange, User, BtcTx, LiqTx, loadConfig, startbitcoind
import os
import random
import sys
import time
import subprocess
import shutil

def initEnvironment():
	print("[Info] Initializing environment...")
	subprocess.call("./src/killdaemon.sh")	# Kill all bitcoind and liquidd that are currently running

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
	excA = Exchange("A")
	excB = Exchange("B")
	alice = User("Alice", excA)
	tom = User("Tom", excA)
	bob = User("Bob", excB)


	# excA.printUsers()
	# excB.printUsers()
	bmin.generate(101) # Generating some coins to spend
	time.sleep(.5)
	print("\nSending initial coins to spend to Alice...")
	print("bmin.getbalance():"+ str(bmin.getbalance()))

	txid1 = (bmin.sendtoaddress(excA.generateBtcAddr(None, bexc), 10)) # Sending 10 BTC to Alice
	print("Txid1:"+txid1)
	txid2 = bmin.sendtoaddress(bbob.getnewaddress(), 10)
	time.sleep(1)
	print("Min getrawmempool 1:"+ str(bmin.getrawmempool()))
	print("Exc getrawmempool 1:"+ str(bexc.getrawmempool()))
	print("Ali getrawmempool 1:"+ str(bali.getrawmempool()))
	print("Bob getrawmempool 1:"+ str(bbob.getrawmempool()))
	print()
	time.sleep(5)

	print("Min getrawmempool 2:"+ str(bmin.getrawmempool()))
	print("Exc getrawmempool 2:"+ str(bexc.getrawmempool()))
	print("Ali getrawmempool 2:"+ str(bali.getrawmempool()))
	print("Bob getrawmempool 2:"+ str(bbob.getrawmempool()))
	bmin.generate(1)


	# excA.generateBtcAddr("Alice", bexc)
	# excB.generateBtcAddr("Bob", bexc)
	# excA.generateBtcAddr("Tom", bexc)
	# alice.printBtcAddresses()
	# bob.printBtcAddresses()
	# tom.printBtcAddresses()
	print()
	# print("bmin.listtransactions():"+ str(bmin.listtransactions()))
	print()
	print("Min getrawmempool 3:"+ str(bmin.getrawmempool()))
	print("Exc getrawmempool 3:"+ str(bexc.getrawmempool()))
	print("Ali getrawmempool 3:"+ str(bali.getrawmempool()))
	print("Bob getrawmempool 3:"+ str(bbob.getrawmempool()))
	print()
	print("Min getbalance():"+ str(bmin.getbalance()))
	print("Exc getbalance():"+ str(bexc.getbalance()))
	print("Ali getbalance():"+ str(bali.getbalance()))
	print("Bob getbalance():"+ str(bbob.getbalance()))

	print()
	print("Exc listtransactions:"+ str(bexc.listtransactions()))
	# print("Min peers:"+str(bmin.getpeerinfo())+"\n")
	# print("Exc peers:"+str(bexc.getpeerinfo())+"\n")
	# print("Alice peers:"+str(bali.getpeerinfo())+"\n")
	# print("Bob peers:"+str(bbob.getpeerinfo())+"\n")

	bmin.stop()
	bexc.stop()
	bali.stop()
	bbob.stop()


