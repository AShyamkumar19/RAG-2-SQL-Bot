import tweepy

auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
auth.set_access_token(access_token, access_token_secret)
api = tweepy.API(auth)
tweets=api.user_timeline(screen_name="",count=100,tweet_mode="extended")
print(f"No of tweets exracted:{len(tweets)}")

# Codes still needs to be finsihed by getting the keys