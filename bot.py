import time
import traceback

import tweepy

from db import ProcessStat, ProcessedUserNames
from make_word_cloud import save_word_cloud, word_cloud_address
from tokens import *
# Authenticate to Twitter
from utils import get_time_in_iran_timezone, make_aware

auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
auth.set_access_token(access_token, access_token_secret)

# Create API object
api = tweepy.API(auth, wait_on_rate_limit=True,
                 wait_on_rate_limit_notify=True)

if __name__ == '__main__':
    sleep_time = 60
    while True:
        new_since_id = ProcessStat.give_since_id()
        try:
            tweets = api.mentions_timeline(since_id=new_since_id)
        except:
            traceback.print_exc()
            time.sleep(sleep_time)
            print('going to sleep for ', sleep_time)
            continue
        print('yey, another one', len(tweets))
        for tweet in tweets:
            try:
                tweet.favorite()
            except:
                pass
            robot_name = 'abrekalamatfa'
            try:
                user_name = tweet.user.screen_name
                if tweet.text.find(robot_name) == -1 or (
                        tweet.in_reply_to_screen_name is not None and tweet.in_reply_to_screen_name != robot_name and tweet.in_reply_to_screen_name != tweet.user.screen_name and tweet.text.count(
                    robot_name) <= 1):
                    continue

                new_since_id = max(tweet.id, new_since_id)
                ProcessStat.create_since_id(since_id=new_since_id)
                last_time = ProcessedUserNames.give_last_time(user_name)
                ProcessedUserNames.create_last_time(user_name)
                if last_time != -1 and (get_time_in_iran_timezone() - make_aware(last_time)).total_seconds() < 60:
                    continue

                save_word_cloud(user_name, api)
                media_id = api.media_upload(word_cloud_address).media_id
                api.update_status(status='ابر کلمات‌ شما خدمت شما' + '@' + str(user_name) + ' عزیز! چطوره این پیامو ریتوییت کنی تا بقیه هم ببینند! هر کس به همین پیام هم ریپلای بده براش ابر کلمات ترسیم میشه!'+str(user_name),
                                in_reply_to_status_id=tweet.id, auto_populate_reply_metadata=True, media_ids=[media_id])
            except:
                traceback.print_exc()
                pass
            time.sleep(60)
        time.sleep(60)
