import json
import tweepy
import config
import sys
import time
import re
import nltk
from sklearn.externals import joblib
from tweepy import Stream
from tweepy import OAuthHandler
from tweepy.streaming import StreamListener
 
class MentalTruth:
	def __init__(self,twitter_handle):
		self.auth = OAuthHandler(config.consumer_key, config.consumer_secret)
		self.auth.set_access_token(config.access_token, config.access_secret)
		self.twitter_api = tweepy.API(self.auth)
		self.nlp = spacy.load('en')
		self.twitterHandle = twitter_handle
		self.tweet_text = []

	def preprocessTweets(self, tweet):
		#Convert www.* or https?://* to URL
		tweet = re.sub('((www\.[^\s]+)|(https?://[^\s]+))','URL',tweet)
		#Convert @username to __HANDLE
		tweet = re.sub('@[^\s]+','__HANDLE',tweet)  
		#Replace #word with word
		tweet = re.sub(r'#([^\s]+)', r'\1', tweet)
		#trim
		tweet = tweet.strip('\'"')
		# Repeating words like happyyyyyyyy
		rpt_regex = re.compile(r"(.)\1{1,}", re.IGNORECASE)
		tweet = rpt_regex.sub(r"\1\1", tweet)
		#Emoticons
		emoticons = \
		[
		 ('__positive__',[ ':-)', ':)', '(:', '(-:', \
		                   ':-D', ':D', 'X-D', 'XD', 'xD', \
		                   '<3', ':\*', ';-)', ';)', ';-D', ';D', '(;', '(-;', ] ),\
		 ('__negative__', [':-(', ':(', '(:', '(-:', ':,(',\
		                   ':\'(', ':"(', ':((', ] ),\
		]
		def replace_parenth(arr):
		   return [text.replace(')', '[)}\]]').replace('(', '[({\[]') for text in arr]
		def regex_join(arr):
		    return '(' + '|'.join( arr ) + ')'
		emoticons_regex = [ (repl, re.compile(regex_join(replace_parenth(regx))) ) \
		        for (repl, regx) in emoticons ]
		for (repl, regx) in emoticons_regex :
		    tweet = re.sub(regx, ' '+repl+' ', tweet)
		 #Convert to lower case
		tweet = tweet.lower()
		return tweet

	def iterate_twitter(self):
		for tweet in tweepy.Cursor(self.twitter_api.user_timeline, screen_name=self.twitterHandle).items(10):
			self.preprocessTweets(tweet['text']) #self.preprocessTweets(tweet._json)
		

		print("++++++++++++ SpaCy Purpose ++++++++++++")
		spa_test = self.nlp(u"Sometimes I do not want to be life,The darkness is not over , these recurring days comed and i can't change any thing, yes!  I'm #depressed.")
		print (spa_test)			
		
		print("++++++++++++ Debugging Purpose ++++++++++++")
		print('# of tweets: ' + str(len(self.tweet_text)))
		print(self.tweet_text)

MT = MentalTruth('@pilthelee') #realDonaldTrump, #
MT.iterate_twitter()