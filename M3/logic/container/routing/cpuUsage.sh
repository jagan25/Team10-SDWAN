#!/bin/bash

PREV_TOTAL=0
PREV_IDLE=0
PREV_STEAL=0
COUNT=0
TH="$1"
CPUNUMBER=$(nproc)
IP=$(/sbin/ip route|awk '/default/ { print $3 }')
LOOP=1

while [[ $LOOP -eq "1" ]] ; do
  # Get the total CPU statistics, discarding the 'cpu ' prefix.
  CPU=(`sed -n 's/^cpu\s//p' /proc/stat`)
  IDLE=${CPU[3]} # Just the idle CPU time.
  STEAL=${CPU[7]} # steal time
  # Calculate the total CPU time.
  TOTAL=0
  for VALUE in "${CPU[@]}"; do
    let "TOTAL=$TOTAL+$VALUE"
  done

  # Calculate the CPU usage since we last checked.
  let "DIFF_IDLE=$IDLE-$PREV_IDLE"
  let "DIFF_TOTAL=$TOTAL-$PREV_TOTAL"
  let "DIFF_STEAL=$STEAL-$PREV_STEAL"
  let "DIFF_USAGE=(1000*($DIFF_TOTAL-$DIFF_IDLE-$DIFF_STEAL)/$DIFF_TOTAL+5)/10"
  
  if [[ $DIFF_USAGE -lt $TH ]] ; then

     #arr=($CPUNUMBER $DIFF_USAGE "FALSE")
     
     arr['cpus'] = $CPUNUMBER
     arr['flag'] = "FALSE"
     arr['load'] = $DIFF_USAGE
     arr['ip'] = $IP
     result=$(curl -d $arr -H "Content-Type: application/json" -X POST http://172.17.0.5:5000/alive)
     LOOP=$((LOOP-1))
  fi
  if [[ $DIFF_USAGE -ge $TH ]] ; then
     COUNT=$((COUNT+1))
     sleep 2
  fi

  if [[ $COUNT -eq "3" ]] ; then
      #no of cpus,load
      #arr=($CPUNUMBER $DIFF_USAGE "TRUE")
      
      arr['cpus'] = $CPUNUMBER
      arr['flag'] = "TRUE"
      arr['load'] = $DIFF_USAGE
      arr['ip'] = $IP
      result=$(curl -d "'cpus'=$CPUNUMBER" -H "Content-Type: application/json" -X POST http://172.17.0.5:5000/alive)
      LOOP=$((LOOP-1))
  fi

  #echo "\rCPU: $DIFF_USAGE%  \b\b"

  # Remember the total and idle CPU times for the next check.
  PREV_TOTAL="$TOTAL"
  PREV_IDLE="$IDLE"
  PREV_STEAL="$STEAL"

# Wait before checking again.
#result=$(curl -X GET --header "Accept: */*" "http://localhost:9090/employees")
#result=$(curl -d '{"ip":"value1", "key2":"value2"}' -H "Content-Type: application/json" -X POST http://localhost:3000/stats)

done
