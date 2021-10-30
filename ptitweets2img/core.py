from . import tweepy, tw
from datetime import datetime
from PIL import Image, ImageFont, ImageDraw
from pilmoji import Pilmoji
import os
import validators
from langdetect import detect
import pytz

class PtiTweets2Img:
    def __init__(self,  
            consumer_key,
            consumer_secret,
            access_key,
            access_secret):
        self.status = None
        self.time = None
        self.tweet_text = None

        self.auth = tweepy.OAuthHandler(consumer_key, consumer_secret)

        self.auth.set_access_token(access_key, access_secret)
        
        self.api = tweepy.API(self.auth)

        self.lang = None


    def getTweet(self, status):
        IST = pytz.timezone('Asia/Kolkata')
        self.status = status
        tweet = self.api.get_status(self.status, tweet_mode='extended')

        self.time = datetime.strftime(datetime.strptime(tweet._json['created_at'], "%a %b %d %H:%M:%S %z %Y").astimezone(IST), "%I:%M %p %b %d, %Y")

        self.tweet_text = tweet._json['full_text']

        self.lang = tweet._json['lang']

    def generateTextImage(self, font, header, bgImg):
        if detect(self.tweet_text) == 'en' or self.lang == 'en':
            temp = Image.open(bgImg)
            drawRectangle = ImageDraw.Draw(temp)
            fnt = ImageFont.truetype(font, 42)
            timeFnt = ImageFont.truetype(font, 34)
            tw.width = 40
            d_text = PtiTweets2Img.text(PtiTweets2Img.remove_urls(self.tweet_text))
            d = Pilmoji(temp)
            h = d.getsize(text=d_text,spacing=14, font=fnt)[1] + 116 + 158
            banImg = Image.open(header)    
            newImg = Image.new(mode = "RGB", size = (866,h), color = (255,255,255))
            newImg.paste(banImg)
            draw = Pilmoji(newImg)
            cursor = (0,158)
            for i in d_text.split('\n'):
                line = draw.getsize(i, font=fnt)
                prefix = []
                if i == '':
                    cursor = (0, cursor[1]+line[1]+14)
                    continue
                else:
                    for j in i.split(' '):
                        if j[0] == '#' or j[0] == '@':
                            if prefix != []:
                                prefix = []
                                j = " " + j
                            if j[-1].isalnum():
                                draw.text((cursor), str(j+' '), align="left", font=fnt, fill=(29,161,242))
                                word = draw.getsize(str(j+' '), font=fnt)
                            else:
                                while True:
                                    if j[-1].isalnum():
                                        draw.text((cursor), str(j), align="left", font=fnt, fill=(29,161,242))
                                        word = draw.getsize(str(j), font=fnt)
                                        break
                                    else:
                                        prefix.append(j[-1])
                                        j = j[0:-1]
                        elif prefix != []:
                            pre = ""
                            for k in reversed(prefix):
                                pre = pre + k
                            j = pre + ' ' + j
                            prefix = []
                            draw.text((cursor), str(j+' '), align="left", font=fnt, fill=(0,0,0))
                            word = draw.getsize(str(j+' '), font=fnt)
                        else:
                            draw.text((cursor), str(j+' '), align="left", font=fnt, fill=(0,0,0))
                            word = draw.getsize(str(j+' '), font=fnt)
                        cursor = (cursor[0]+word[0], cursor[1])
                    cursor = (0, cursor[1]+line[1]+14)
            draw.text((0,h-45), self.time , align="left", spacing=14, font=timeFnt, fill=(116,116,116))
            location = ((1080-newImg.size[0])//2,(1080-newImg.size[1])//2)
            drawRectangle.rounded_rectangle((location[0]-55, location[1]-54, location[0]+866+55, location[1]+h+54), fill="white", radius=54)
            temp.paste(newImg, location)
            temp = temp.convert('RGB')
            filename = './temp/'+ str(self.status) +'.jpg'
            try:
                temp.save(filename, quality=100)
            except:
                path = os.getcwd()
                folder = './temp'
                os.mkdir(os.path.join(path, folder))
                temp.save(filename, quality=100)
            return filename
        else:
            raise RuntimeError('Tweets should be in English!')

            
    def text(string):
        if string.find('\n') == -1:
            string = "\n".join(tw.wrap(string))
            return string
        else:
            line = ""
            string = string.split('\n')
            for i in string:
                tw.width = 34
                line += "\n".join(tw.wrap(i))
                line += '\n'
            return line[0:-1]

    def remove_urls(string):
        string = string.split()
        for i in string:
            if validators.url(i):
                string.remove(i)
            else:
                continue
        return " ".join(string)