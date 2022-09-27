#!/bin/bash
# stats.sh is a script to collect cpu and memory every 10seconds and for 30 minutes

cat /dev/null > results.csv

for i in {1..180}; do
  start=$(date +%s%N)
  
  # cpu linux
  cpu_usage=$(top -bn2 | grep '%Cpu' | tail -1 | grep -P '(....|...) id,'|awk '{print  100-$8}' | sed 's/,/\./')
  
  # memory linux
  memory_usage=$(free | grep Mem | awk '{print $3/$2 * 100.0}' | sed 's/,/\./')

  echo "$i,$cpu_usage,$memory_usage"
  printf "$i,$cpu_usage,$memory_usage\n" >> results.csv
  end=$( bc <<< "scale=3;( 10 - (($(date +%s%N) - $start)/1000000000))" )
  sleep $end
  ((i=i+1))
done