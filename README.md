# Running The Bot
# 1.  Start Redis

Run redis-server from command line in root directory

# 2.  Run Collector -  Connects to Twitter Stream and creates entries in Redis 

Run python collector.py

# 3.  Run Poller - Poll Redis for Threshold events

Run python stat_poller.py