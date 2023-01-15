#!/bin/bash

###
# Schoco-cookies script
# (based on Codeboard-Mantra, see below)
#-----------------------------
#
# Codeboard - Mantra script
#
# Executes "compile" or "run" actions
# Times out when either a CPU usage limit is reached
# or the process (session) has been alive for a certain time
#
# IMPORTANT: this script assumes that you have 'bc' installed (apt-get install bc)
# Note: we run this in a bash because bash has the "time" command
#
# Copyright: H.-Christian Estler
# 
###

CMD_ARG=$1
TIMEOUT_CPU=$2
TIMEOUT_SESSION=$3

( sleep $TIMEOUT_SESSION && echo -e "\n\nSchoco terminated your program because it exceeded the session time limit.\n" && kill $$ ) &

forkedPID=$!
disown

ulimit -t $TIMEOUT_CPU
exec 3>&1 4>&2;
CPU_TIME_STRING=$(TIMEFORMAT="%U;%S"; { time sh -c "$CMD_ARG" 1>&3 2>&4; } 2>&1);
CPU_TIME_USER=$(echo $CPU_TIME_STRING | cut -d ';' -f 1)
CPU_TIME_SYSTEM=$(echo $CPU_TIME_STRING | cut -d ';' -f 2)
exec 3>&- 4>&-;

if [ $(echo "$CPU_TIME_USER + $CPU_TIME_SYSTEM + 0.1 >= $TIMEOUT_CPU" | bc) -eq 1 ]; then
   echo -e "\n\nSchoco terminated your program because it exceeded the CPU usage limit.\n"
fi;

kill $forkedPID
