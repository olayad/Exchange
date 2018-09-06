#!/usr/bin/env python3
from exchange import NewTxDaemon, CheckConfsDaemon, Exchange, User, BtcTx, LiqTx, loadConfig, startbitcoind
import os
import random
import sys
import time
import subprocess
import shutil
import json

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

	# Start daemon searching for new txs and updating confirmations
	newtxdaemon_btc = NewTxDaemon("newtxdaemon_btc", excA, bexc, "BTC")
	checkconfsdaemon_btc = CheckConfsDaemon("checkconfsdaemon_btc", excA, bexc, "BTC")
	NewTxDaemon.daemon = True
	CheckConfsDaemon.daemon = True
	newtxdaemon_btc.start()
	checkconfsdaemon_btc.start()

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



	#Alice goes to exchange and wants to deposit BTC, generates a deposit address in exchange
	alice_deposit_addr = excA.generateBtcAddr("Alice", bexc)
	# alice.printBtcAddresses()
	#Alice sends btc to exchange
	bali.sendtoaddress(alice_deposit_addr, 1)
	bali.sendtoaddress(alice_deposit_addr, 2)
	bali.sendtoaddress(alice_deposit_addr, 3)

	time.sleep(3)
	# print("Min getrawmempool - aftert exc deposit:"+ str(bmin.getrawmempool()))
	# print("Exc getrawmempool - aftert exc deposit:"+ str(bexc.getrawmempool()))
	# print("Ali getrawmempool - aftert exc deposit:"+ str(bali.getrawmempool()))
	# print("Bob getrawmempool - aftert exc deposit:"+ str(bbob.getrawmempool()))
	# print()
	# print("Exc listtransactions:"+ str(bexc.listtransactions()))
	bmin.generate(3)
	time.sleep(1)



	time.sleep(4)
	sys.exit(1)






	bmin.generate(1)
	time.sleep(3)

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
	bbob.stop()



	# excA.printUsers()
	# excB.printUsers()