#!/bin/bash

# Killing bitcoind processes
let -a arr;
num=( $(ps aux | grep bitcoind | awk '$11 ~ /^bitcoin/' | awk '{print$2}' | awk '{print NR}' | wc -l));
arr=( $(ps aux | grep bitcoind | awk '$11 ~ /^bitcoin/' | awk '{print$2}'));

echo "[Info - killdaemon.sh] Number of bitcoind processes to terminate [${num}]";
counter=0;
while [ ${counter} -lt ${num} ]
do
	kill -9 ${arr[$counter]}
	echo "[Info - killdaemon.sh] Terminating process ${arr[$counter]} ..."
	((counter++))
done
echo "[Info - killdaemon.sh] All bitcoind processes terminated"


# Killing liquidd processes
let -a arr;
num=( $(ps aux | grep liquidd | awk '$11 ~ /^liquidd/' | awk '{print$2}' | awk '{print NR}' | wc -l));
arr=( $(ps aux | grep liquidd | awk '$11 ~ /^liquidd/' | awk '{print$2}'));

echo "[Info - killdaemon.sh] Number of liquidd processes to terminate [${num}]";
counter=0;
while [ ${counter} -lt ${num} ]
do
	kill -9 ${arr[$counter]}
	echo "[Info - killdaemon.sh] Terminating process ${arr[$counter]} ..."
	((counter++))
done
echo "[Info - killdaemon.sh] All liquidd processes terminated"