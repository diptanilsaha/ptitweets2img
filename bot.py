import time
import atexit
from ptitweets2img import PtiTweets2Img
import logging
import os
from keep_alive import keep_alive
from instagrapi import Client

try:
    logging.basicConfig(filename='./logs/tweet.log',
                                filemode='a',
                                format='%(asctime)s,%(msecs)d %(name)s %(levelname)s %(message)s',
                                datefmt="%Y-%m-%d %H:%M:%S",
                                level=logging.INFO)
except:
    path = os.getcwd()
    folder = './logs'
    os.mkdir(os.path.join(path, folder))
    logging.basicConfig(filename='./logs/tweet.log',
                                filemode='a',
                                format='%(asctime)s,%(msecs)d %(name)s %(levelname)s %(message)s',
                                datefmt="%Y-%m-%d %H:%M:%S",
                                level=logging.INFO)

console = logging.StreamHandler()
console.setLevel(logging.INFO)
# set a format which is simpler for console use
formatter = logging.Formatter('%(asctime)s -> %(levelname)-8s: %(message)s', "%Y-%m-%d %H:%M:%S")
# tell the handler to use this format
console.setFormatter(formatter)
# add the handler to the root logger
logging.getLogger('').addHandler(console)

font = "./media/fonts/Roboto-Regular.ttf"
header = './media/pti-header.png'
bgImg = "./media/ptitweet-bg.png"

# Fill the X's with the credentials obtained by
# following the above mentioned procedure.
consumer_key = ""
consumer_secret = ""
access_key = ""
access_secret = ""

username = ""
password = ""

t2iObj = PtiTweets2Img(consumer_key, consumer_secret, access_key, access_secret)

cl = Client()

cl.login(username=username, password=password)

# Function to extract tweets
def get_tweets(id):
    tweets = t2iObj.api.user_timeline(screen_name=id, 
                           include_rts = False,
                           exclude_replies = True,
                           # Necessary to keep full_text 
                           # otherwise only the first 140 words are extracted
                           tweet_mode = 'extended'
                           )
    statusList = []
    for i in tweets:
        statusList.append(i._json['id_str'])
    return statusList

@atexit.register
def at_exit():
    logging.info("Shutting Down Bot! Saved data at 'logs/tweet.log'")
    

# Driver code
def app():
    try:
        userID = "PTI_News"
        logging.info('Starting '+ userID +' Tweet Bot')
        # Here goes the twitter handle for the user
        # whose tweets are to be extracted.
        tweetData = get_tweets(userID)
        
        #intitializeing tweetData and storing all new Tweets available
        logging.info("Initialized with the existing Tweets")
        while True:
            try:
                newTweets = get_tweets(userID)

                stack = []

                for i in newTweets:
                    if i in tweetData:
                        continue
                    else:
                        logging.info(str('New tweets: '+ str(i)))
                        stack.append(i)

                if stack != None:
                    for i in stack:
                        tweetData.append(i)
                        logging.info("Adding new tweet")
                        t2iObj.getTweet(i)
                        file =  t2iObj.generateTextImage(font, header, bgImg)
                        logging.info(str("Image saved at "+ file))
                        cl.photo_upload(file, caption=t2iObj.tweet_text + "\n.\n.\nFor more information regarding this account, link in the bio.\n.\n.\n.\n.\n.\n.\n.(Ignore the hashtags)\n#india #news #politics #indianpolitics #bjp #congress #sports #modi #rahulgandhi #entertainment #presstrustofindia #pti #ndtv #republic #timesnow #tmc")
                        os.remove(file)
                else:
                    continue

                time.sleep(10)

            except Exception as e:
                #raise e
                logging.warning("Error!")
                logging.info('An unknown Error encountered!')

    except Exception as e:
        #raise e
        logging.warning("Error!")
        logging.info('Error encountered while initializing!')

    except KeyboardInterrupt as e:
        logging.warning("Shutting Down!")

keep_alive()
app()