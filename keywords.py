import rake
import string
import re
import json
import random
import itertools
from nltk.tokenize import TweetTokenizer

class TweetKeywords:
    """Uses the Rake keyword extractor to identify keywords in blocks of tweets.
    Attributes:
        tokenizer (nltk.tokenize) : tokenizer to be used when parsing tweets
        keywords (list) : list of tuples containing the keyword and it's Rake score 
    """
    def __init__(self, tokenizer='tweet'):
        """
        Args:
            tokenizer (str or nltk.tokenize) : specify an nltk tokenizer. Default is 'tweet', which is a TweetTokenizer
        """ 
        if tokenizer == 'tweet':
            # removes handles and reduces length of repeating characters (e.g. !!!!!)
            self.tokenizer = TweetTokenizer(strip_handles=True, reduce_len=True)
        else:
            self.tokenizer = tokenizer
        
    def json_tweets(self, json_file):
        """Returns a list of tweets from a json file.
        
        Args:
            json_file (str) : path to the json file containing tweets.
        Returns:
            list : list of tweets
        """
        tweet_data = []
        with open(json_file) as f:
            for line in f:
                temp = json.loads(line)
                tweet_data.append(temp['text'])
        random.shuffle(tweet_data)
        return tweet_data 
    
    def clean_text(self, tweet):
        """Returns the tweet without some of the major unicode annoyances, apostrophes, 'RT', links, and 'I'm's.
        
        Args:
            tweet (str) : a single tweet
        Returns:
            str : a singel cleaned tweet
        """
        printable = set(string.printable)
        tweet = filter(lambda x: x in printable, tweet)
        tweet = tweet.replace(u'\u2026', "...")
        tweet = tweet.replace("#","")
        tweet = tweet.replace(u'\ufffd',"")
        tweet = tweet.replace(u"'","")
        tweet = re.sub(r"^RT","", tweet)
        tweet = re.sub(r"http\S+", "", tweet)
        tweet = re.sub(r"\b[Ii]'*m\b","",tweet)
        tweet = tweet.encode('utf8')
        return tweet
    
    def tweet_tokenizer(self, tweet):
        """Cleans and tokenizes tweets.
        
        Args:
            tweet (str) : a single tweet
        Returns:
            tuple : a tuple of a single tokenized tweet
        """
        tweet = self.clean_text(tweet)
        tweet = self.tokenizer.tokenize(tweet)
        filtered_words = [word for word in tweet if len(word) >= 2]
        tweet_tuple = tuple(filtered_words)
        return tweet_tuple
    
    def clean_de_dup_tweets(self, tweet_list):
        """Cleans and sets a block of tweets.
        
        Args:
            tweet_list (list) : a block of tweets
        Returns:
            list : a list of unique tweets
        """
        temp_list = []
        for tweet in tweet_list:
            tweet_tup = self.tweet_tokenizer(tweet)
            temp_list.append(tweet_tup)
        temp_list = list(set(temp_list))
        temp_list = map(list, temp_list)
        return temp_list
    
    def __remove_shorter_repeats(self, keywords):
        """Removes shorter terms that appear in longer ones. i.e. "details hospitality" would be removed if 
        'details hospitality job' was there.
        
        Args:
            keywords (list) : keywords extracted from Rake
        
        Returns:
            list : a de-duped list of keywords
        """
        shorter_list = keywords[:]
        for term in keywords:
            for keyword in keywords:
                if (term[0] in keyword[0]) and term != keyword:
                    shorter_list.remove(term)
                    break
        return shorter_list
    
    def keywords_from_tweet_list(self, tweet_list, num_characters=3, max_phrase=3, remove_repeats=False):
        """Uses RAKE to output the keywords from a tweet list.
        
        Args:
            tweet_list (list) : a block of tweets
            num_characters (int) : minimum number of characters in a keyword. Default is 3
            max_phrase (int) : maximum amount of words in a keyword phrase. Default is 3.
        
        Returns:
            list : list of tuples containing the keyword and it's Rake score 
        """
        num_of_tweets = len(tweet_list)
        joined_tweets = ' '.join(itertools.chain(*tweet_list))
        rake_object = rake.Rake("SmartStoplist.txt", num_characters, max_phrase, num_of_tweets/1000) 
        self.keywords = rake_object.run(joined_tweets)
        
        if remove_repeats:
            self.keywords = self.__remove_shorter_repeats(self.keywords)
            
        return self.keywords