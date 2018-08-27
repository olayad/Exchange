#!/bin/bash


num=( $(ps aux | grep bitcoind | awk '$11 ~ /^bitcoin/' | awk '{print$2}' | awk '{print NR}' | wc -l));

let -a arr;
arr=( $(ps aux | grep bitcoind | awk '$11 ~ /^bitcoin/' | awk '{print$2}'));

echo "[Info - killdaemon.sh] Number of daemons to kill [${num}]";
counter=0;
while [ ${counter} -lt ${num} ]
do
	kill -9 ${arr[$counter]}
	echo "[Info - killdaemon.sh] Killing process ${arr[$counter]} ..."
	((counter++))
done

echo "[Info - killdaemon.sh] All processes terminated"