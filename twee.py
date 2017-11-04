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
		print('Loading the SVM Classifier, please wait...')
		self.classifier = joblib.load('src/svm_Classifier.pkl')
		print('Model ready for use.')
		self.twitterHandle = twitter_handle
		self.tweet_count = 0
		self.sentiment_score = 0

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

	def stem(self, tweet):
		stemmer = nltk.stem.PorterStemmer()
		tweet_stem = ''
		words = [word if(word[0:2]=='__') else word.lower() \
					for word in tweet.split() \
					if len(word) >= 3]
		words = [stemmer.stem(w) for w in words] 
		tweet_stem = ' '.join(words)
		return tweet_stem

	def iterate_twitter(self):
		for tweet in tweepy.Cursor(self.twitter_api.user_timeline, screen_name=self.twitterHandle).items():
			sentiment = None
			self.tweet_count += 1
			tweet_text = json.dumps(tweet._json)
			tweet_processed = self.stem(self.preprocessTweets(tweet_text))

			if ( ('__positive__') in (tweet_processed)):
				sentiment  = 1
				print(sentiment)
			elif ( ('__negative__') in (tweet_processed)):
				sentiment  = 0
				print(sentiment)
			else:
				X =  [tweet_processed]
				sentiment = self.classifier.predict(X)
				print(sentiment[0])
			self.sentiment_score += sentiment
			print(self.sentiment_score[0])
			print(self.tweet_count)
		self.sentiment_score = self.sentiment_score / self.tweet_count
		return (self.sentiment_score)

MT = MentalTruth('@xferreiraxo‏') #pilThelee, Time4Depression, Yunii_que, SaiMoorthy14, iDepressing, SelfHarmer13, montesinomay ‏
# print('The sentiment score is: ' + str(MT.iterate_twitter())
print(MT.iterate_twitter()[0])