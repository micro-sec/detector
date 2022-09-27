#!/bin/bash
# stats.sh is a script to collect cpu and memory every 10seconds and for 30 minutes

cat /dev/null > ./results.csv

for i in {1..180}; do
  start=$(date +%s)
  
  # cpu macOS
  cpu_usage=$(top -l 1 | grep -E "^CPU" | grep -Eo "[^[:space:]]+%" | head -1)
  
  # memory macOS
  memory_usage=$(memory_pressure | tail -n 1 | grep -o "...$")

  echo "$i,$cpu_usage,$memory_usage"
  echo "$i,$cpu_usage,$memory_usage" >> ./results.csv
  end=$( bc <<< "scale=3;( 10 - (($(date +%s) - $start)/1000000000))" )
  sleep $end
  ((i=i+1))
done