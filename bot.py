import time
import traceback

import tweepy

from db import ProcessStat
from make_word_cloud import save_word_cloud, word_cloud_address
from tokens import *

# Authenticate to Twitter
auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
auth.set_access_token(access_token, access_token_secret)

# Create API object
api = tweepy.API(auth)

if __name__ == '__main__':
    sleep_time = 60
    while True:
        new_since_id = ProcessStat.give_since_id()
        try:
            tweets = api.mentions_timeline(since_id=new_since_id)
        except:
            traceback.print_exc()
            time.sleep(sleep_time)
            sleep_time *= 2
            sleep_time = min(sleep_time, 60*60*2)
            continue

        for tweet in tweets:
            try:
                tweet.favorite()
            except:
                pass
            try:
                new_since_id = max(tweet.id, new_since_id)
                ProcessStat.create_since_id(since_id=new_since_id)
                user_name = tweet.user.screen_name
                save_word_cloud(user_name, api)
                api.update_with_media(word_cloud_address,
                                      status='#ابرکلمات‌ شما خدمت شما' + '@' + str(user_name) + ' عزیز!',
                                      in_reply_to_status_id=tweet.id)
            except:
                traceback.print_exc()
                pass
            time.sleep(60)
        time.sleep(60)
