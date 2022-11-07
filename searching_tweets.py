import tweepy
import pandas as pd
import os
import time

consumer_key = os.environ['CONSUMER_KEY']
consumer_secret = os.environ['CONSUMER_SECRET']
Bearer_Token = os.environ['BEARER_TOKEN']
Token = os.environ['Token']
Token_Secret = os.environ['Token_Secret']


OPENAI_API_KEY = os.environ['OPENAI_API_KEY']
access_key =  os.environ['ACCESS_KEY']
secret_access_key = os.environ['SECRET_ACCESS_KEY']
Credentials_Access_Key_ID = os.environ['CREDENTIALS_ACCESS_KEY_ID']
Credentials_Secret_Access_Key = os.environ['CREDENTIALS_SECRET_ACCESS_KEY']


auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
auth.set_access_token(Token, Token_Secret)
api = tweepy.API(auth)

getClient = tweepy.Client(bearer_token=Bearer_Token,
                          consumer_key=consumer_key,
                          consumer_secret=consumer_secret,
                          access_token=Token,
                          access_token_secret=Token_Secret)
client = getClient

search_df = pd.read_csv('/Users/scottlai/Desktop/cording_project/Twitter/Twitter_whole_Final/Twitter/search_df_1.csv')
search_df = search_df.drop(columns=['Unnamed: 0'])
search_df['created_at'] = pd.to_datetime(search_df['created_at'], format='%Y-%m-%d %H:%M:%S')
# search_df

# search_df.to_csv("s3://projecttwitterbot/Searching/ai_search_df.csv",
#                  storage_options={'key': access_key, 'secret': secret_access_key})


def searchTweets(query, max_results):
    tweets = client.search_recent_tweets(query=query,
                                         tweet_fields=[
                                             'id','text', 'context_annotations', 'created_at', 'lang'],
                                         expansions=['referenced_tweets.id', 'attachments.media_keys',
                                                     'author_id', 'entities.mentions.username', 'geo.place_id'],
                                         user_fields=[
                                             'id', 'username', 'description', 'entities', 'protected', 'public_metrics', 'verified'],
                                         place_fields=['place_type', 'geo'],
                                         media_fields=['duration_ms', 'height', 'media_key', 'preview_image_url', 'type', 'width','url', 'public_metrics'],
                                         max_results=max_results)

    user = {u['id']: u for u in tweets.includes['users']}
    results = []
    if not tweets.data is None and len(tweets.data) > 0:
        for tweet in tweets.data:
            twt = client.get_tweets(tweet['id'], expansions=['author_id'], user_fields=['username'])
            obj = {}
            obj['id'] = tweet['id']
            obj['created_at'] = tweet['created_at']
            obj['author_id'] = tweet.id
            obj['text'] = tweet.text
            obj['lang'] = tweet.lang
            # obj['entities'] = tweet.entities
            obj['username'] = twt.includes['users'][0].username
            if user[tweet.author_id]:
                user1 = user[tweet.author_id]
                # obj['public_metrics'] = user1.public_metrics
                obj['verified'] = user1.verified
                
            obj['url'] = 'https://twitter.com/{}/status/{}'.format(
                twt.includes['users'][0].username, tweet['id'])
            obj['followers_count'] = user1.public_metrics['followers_count']
            obj['following_count'] = user1.public_metrics['following_count']
            obj['tweet_count'] = user1.public_metrics['tweet_count']

            results.append(obj)
    else:
        return "No tweets found"

    search_df_new = pd.DataFrame(results)

    # merge the search_df_new with the search_df base on the id
    new_df = pd.merge(search_df, search_df_new, on = ['id','created_at','author_id','text','lang','username', 'verified','url','followers_count','following_count','tweet_count'], how='outer')

    # save the dataframe to s3
    search_df.to_csv("s3://projecttwitterbot/Searching/search_df.csv",
                     storage_options={'key': keys.access_key, 'secret': keys.secret_access_key})
#     new_df.to_csv("/Users/scottlai/Desktop/cording_project/Twitter/Twitter_whole_Final/Twitter/search_df_1.csv")
    return search_df

if __name__ == '__main__':
#       coins = ['BTC','ETH','DOGE','ADA','BNB','XRP','SOL','MATIC','DOT','STETH','SHIB','TRX','DAI','UNI','WBTC','LTC','LEO','OKB','ATOM','LINK','FTT','XLM','CRO','XMR','ALGO','NEAR','TON']
    coins = ['DAI','UNI','WBTC','LTC','LEO'] 
    for i in coins:
        searchTweets(i, int(200/len(coins)))
        time.sleep(60*15)
