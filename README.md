#Description

##Overview
I created a system that will track Tweets mentioning a specific keyword or set of keywords and then keep a rate for number of tweets within a geographic range from different points of interest.  The system then posts to a twitter account alerts if a specified threshold is reached. For testing I set the keywords to track mentions of "sun" and "sunny" and a list of 5 cities.  Because very few tweets have Tweet level Geolocation and I wanted a threshold result quickly, the threshold is set very low (<5).

## Comments on Requirements

###1. Measure the Rate  
The system measures a rate of (Tweets in proximity of interest points/N) where N is the number of seconds in the Redis expiry.  The system must be running for at least N seconds to be accurate.

###2. Set an Alert
The system both sends out an alert when a threshold for each city is reached as well as maintains a state of whether that alert has already been triggered.  In a more sophisticad system, it would be good to add a buffer to reset the state of each city require a time based cooling period or a percentage below threshold to be hit.

###3.  Output to a public channel 
The system posts back to a twitter channel.  That channel is viewable here: <src>https://twitter.com/SuperHappyBot</src>





Known Limitations and potential for refactoring:
- Processing could be more efficient by breaking down output of connector to more granular {city:1} denoting that a tweet matching within proximity of the city has just been posted.  This would allow for easier sums in the aggregation phase.
- No buffer is given in maintaining state so signals oscillating near the threshold could generate a lot of alerts.


## Running The Bot
## 1.  Start Redis

Run redis-server from command line in root directory

## 2.  Run Collector -  Connects to Twitter Stream and creates entries in Redis 

Run python collector.py

## 3.  Run Poller - Poll Redis for Threshold events

Run python stat_poller.py
