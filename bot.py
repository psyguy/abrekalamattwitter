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
                if user_name == robot_name:
                    user_name = tweet.in_reply_to_screen_name
                else:
                    if tweet.text.find(robot_name) == -1 or (
                            tweet.in_reply_to_screen_name is not None and tweet.in_reply_to_screen_name != robot_name and tweet.in_reply_to_screen_name != tweet.user.screen_name and tweet.text.count(
                        robot_name) <= 1):
                        continue
                    s = api.show_friendship(source_screen_name=robot_name, target_screen_name=user_name)[1].following

                    new_since_id = max(tweet.id, new_since_id)
                    ProcessStat.create_since_id(since_id=new_since_id)
                    last_time = ProcessedUserNames.give_last_time(user_name)
                    ProcessedUserNames.create_last_time(user_name)
                    if last_time != -1 and (get_time_in_iran_timezone() - make_aware(last_time)).total_seconds() < 60*60*10:
                        continue

                save_word_cloud(user_name, api)
                media_id = api.media_upload(word_cloud_address).media_id
                text = 'ابر کلمات‌ شما خدمت شما' + '@' + str(
                    user_name) + ' عزیز! چطوره عکسو با هشتگ #ابرکلمات توییت کنی و ربات رو منشن کنی تا بقیه هم ببینند! راستی خواهشا یه پیام بهم بده که مطمین بشم توییتر اسپم تشخیص نداده و به دستت رسیده. اگر پیام ندی ممکنه کم کم توییتر ربات رو اسپم تشخیص بده و ببندتش.' + str(
                    user_name)
                try:
                    api.send_direct_message(tweet.user.id, text, attachment_type='media', attachment_media_id=media_id)
                except:
                    api.update_status(status=text, in_reply_to_status_id=tweet.id, auto_populate_reply_metadata=True,
                                      media_ids=[media_id])
            except:
                traceback.print_exc()
                pass
            time.sleep(180)
        time.sleep(60)
