import json
import tweepy
import redis
import math

class StdOutListener(tweepy.StreamListener):
    #pass redis connection to connector
    def __init__(self,conn):
        self.conn=conn

    def city_distance(self,tweet):
        distances={}
        #hard coded list of common city latlong
        #positive numbers are North and east
        cities={'New York':(40.7127, -74.0059),\
                'Chicago':(41.8369, -87.6847),\
                "San Francisco":(37.7833, -122.4167),\
                "LA":(34.0500, 118.2500),\
                "Sydney":(-33.8650, 151.2094)}
        for city in cities.keys():
            #take the "middle" of the polygon for calculating distance
            lat_lon_est=mid_polygon(tweet['place']['bounding_box']['coordinates'])
            #calculate distance from Tweet to each city
            distances[city]= haversine(cities[city][0],cities[city][1],lat_lon_est[0],lat_lon_est[1])

        return distances


    def on_data(self, data):
        # Twitter returns data in JSON format - we need to decode it first
        tweet = json.loads(data)
        #give some feedback that its running
        print "Event"

        try:
            #only process Tweets with a location, would be better to filter stream with server side parmeter for Has:Geo
            #but I didn't see as an option
            if tweet['place'] is not None:
                if 'bounding_box' in tweet['place']:
                    distances=self.city_distance(tweet)
                    self.conn.setex(tweet['id'], json.dumps(distances), 600)
        except KeyError:
            #pass for non-tweet messages, Twitter sends rate limit and other messages with much different structure
            try:
                l=tweet['limit']
                print "Rate Limit Hit"
            except:
                print "Unknown Error - Type"
                #print "Bad Key"
                #print tweet

        return True

    def on_error(self, status):
        print status

def avg(l):
    return sum(l) / float(len(l))


def mid_polygon(poly):
    #flip lat and long and average sides of bounding box
    poly_lat=[poly[0][0][1],poly[0][1][1],poly[0][2][1],poly[0][3][1]]
    poly_lon=[poly[0][0][0],poly[0][1][0],poly[0][2][0],poly[0][3][0]]

    return (avg(poly_lat),avg(poly_lon))

from math import radians, cos, sin, asin, sqrt
def haversine(lon1, lat1, lon2, lat2):
    #borrowed code from http://stackoverflow.com/questions/15736995/how-can-i-quickly-estimate-the-distance-between-two-latitude-longitude-points
    #to caclulate approx distance with only math package
    """
    Calculate the great circle distance between two points
    on the earth (specified in decimal degrees)
    """
    # convert decimal degrees to radians
    lon1, lat1, lon2, lat2 = map(radians, [lon1, lat1, lon2, lat2])
    # haversine formula
    dlon = lon2 - lon1
    dlat = lat2 - lat1
    a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
    c = 2 * asin(sqrt(a))
    km = 6367 * c
    return km

def open_twitter(args,creds,conn):
    #open a stream to twitter based on keyword arguments
    l = StdOutListener(conn)
    auth = tweepy.OAuthHandler(creds['twitter_key'], creds['twitter_secret'])
    auth.set_access_token(creds['twitter_access_token'], creds['twitter_token_secret'])
    stream = tweepy.Stream(auth, l)
    #subscribe to terms on stream
    stream.filter(track=args['terms'])

    return l
    #return a connection


def load_creds(credloc):
    #load keys from key file
    with open(credloc) as data_file:
        data = json.load(data_file)
    return data

def conn_redis():
    r = redis.Redis(host='localhost', port=6379, db=0)
    return r


def main():
    #load credentials
    creds=load_creds('./cred/keys.txt')
    #start redis via bash script
    rdb_conn=conn_redis()
    #set search terms for stream
    args={"terms":["sun","sunny"]}
    #open connection
    conn=open_twitter(args,creds,rdb_conn)


if '__name__'!='main':
    main()