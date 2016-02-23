import redis
import time
import json
import tweepy

def load_creds(credloc):
    #load keys from key file
    with open(credloc) as data_file:
        data = json.load(data_file)
    return data

def post_twitter(keys,creds,r,status):
    #set tweepy auth with credentials from file
    auth = tweepy.OAuthHandler(creds['twitter_key'], creds['twitter_secret'])
    auth.set_access_token(creds['twitter_access_token'], creds['twitter_token_secret'])
    api = tweepy.API(auth)

    try:
        #post to twitter
        api.update_status(status)
    except tweepy.TweepError as e:
        #display errors, setup to block "Duplicate Tweet" errors
        print e.message[0]


def main():
    creds=load_creds('./cred/keys.txt')
    r=redis.Redis()
    #use_data(r)
    above_thresh=0
    #distance from city to be included (in KM), would like to do 100 but had to set at 1000 to get enough data for short duration
    dist_thresh=1000
    mention_thresh=1
    city_states={}

    while 1:
        counts={}
        #tracks whether city is sunny_alert_on
        #this is used to not send alert repeatedly, only when initially crossing

        keys=r.keys()
        for key in keys:
            #print r.get(key)
            dists=json.loads(r.get(key))
            #print dists
            for city in dists:
                if city in counts.keys():
                    if dists[city]<dist_thresh:
                        counts[city]+=1
                else:
                    if dists[city]<dist_thresh:
                        counts[city]=1
        #trigger alerts
        for city in counts:
            #establish base cases
            if city not in city_states.keys():
                print city_states.keys()
                city_states[city]=0
                print "set"
            if city not in counts.keys():
                counts[city]=0
            #Primary alert, post to twitter
            if counts[city]>mention_thresh and city_states[city]==0:
                status= "It's sunny in "+ city + ", " + str(counts[city])+ " people just said so on Twitter."
                print city_states[city],city
                city_states[city]=1
                print status
                post_twitter(keys,creds,r,status)
            else:
                #turn off state if set as on and no longer passing
                if counts[city]<mention_thresh:
                    city_states[city]=0

        print counts
        time.sleep(2)






if '__name__'!='main':
    main()