#!/Library/Frameworks/Python.framework/Versions/3.6/bin/python3
import praw
import re
from imgurpython import ImgurClient
import requests
import time
import os
import urllib.request

import config

#TODO fix for reddit images redd.it/###.jpg

# max number of submissions to check
LIMIT = 50

# subreddit being checked
#TODO allow for multireddits
SUBREDDIT = config.subreddit

img = (".png", ".jpg", ".jpeg", ".gif", ".webm", ".bmp")

file_name_queue = []
download_queue = []
reddit_id_cache = []

# the directory this file is in
#CURRENT_PATH = (os.path.dirname(os.path.realpath(__file__)))
CURRENT_PATH = os.getcwd()

# create the reddit instance in read-only mode
reddit = praw.Reddit(
	client_id = config.reddit_id,
	client_secret = config.reddit_secret,
	user_agent = config.user_agent)

# create the imgur instance or something
imgur = ImgurClient(
	client_id = config.imgur_id,
	client_secret = config.imgur_secret)

# get the extension of the file
def get_file_name(url, file_name):
	# get the extension from the url and append it to the file name
	f = file_name + '.' + url.split('.')[-1]
	return f # string

# add the url to download_queue and file name to file_name_queue
def add_to_queue(url, name):
	download_queue.append(url)
	file_name_queue.append(name)

# download files from the queue then clear the queue
def download_files():
	q = 0
	while q < len(download_queue):
		# download the file
		print(str(len(download_queue) - q) + " downloads left in queue")
		urllib.request.urlretrieve(download_queue[q], file_name_queue[q])
		print("downloading " + download_queue[q])
		q += 1
		time.sleep(1)
	print(str(len(download_queue)) + " images have been downloaded")
		# clear download_queue and file_name_queue
	download_queue[:] = []
	file_name_queue[:] = []

def check_if_album(url, file_name):
	# check if the url is an imgur album or gallery
	if "imgur.com/a/" in url or "imgur.com/gallery/" in url:
		# checks if the url is actually an album? idk i copied it from the internet
		match = re.match("(https?)\:\/\/(www\.)?(?:m\.)?imgur\.com/(a|gallery)/([a-zA-Z0-9]+)(#[0-9]+)?", url)
		imgur_album_id = match.group(4) # id of the imgur album
		print( "submission is an album containing " + str(len(imgur.get_album_images(imgur_album_id))) + " images")
		i = 0 # counter for file names
		n = 0 # counter for new files
		if len(imgur.get_album_images(imgur_album_id)) == 1:
			add_to_queue(image.link, file_name)
		else:
			full_path = CURRENT_PATH + "/pictures/" + file_name + "/"
			if not os.path.isdir(full_path):
				os.mkdir(full_path)
				print("creating /" + file_name + "/ in " + CURRENT_PATH + "/pictures/")
			for image in imgur.get_album_images(imgur_album_id):
				i += 1
				# append a number if the image is part of an album
				f = file_name + "_" + str(i)
				f = get_file_name(image.link, f)
				if not os.path.isfile(full_path + f):
					n += 1
					add_to_queue(image.link, full_path + f)
			print("album contained " + str(n) + " new images")
		return True
	else:
		return False

# checks if the url is an image or is an imgur album
def check_submission(url, file_name):
	if url.endswith(img):
		f = CURRENT_PATH + "/pictures/" + get_file_name(url, file_name)
		if not os.path.isfile(f):
			add_to_queue(url, f)
			print(url + " added to the download_queue")
	else:
		check_if_album(url, file_name)

# get reddit submissions
def get_submissions():
	c = 0
	# check SUBREDDIT for LIMIT number of submissions
	print("checking " + SUBREDDIT + " for " + str(LIMIT) + " submissions")
	# can change to either hot/new/top etc.
	for submission in reddit.subreddit(SUBREDDIT).hot(limit = LIMIT):
		url = submission.url
		id = submission.id
		if id not in reddit_id_cache: #TODO change this to url so the same url on different subs doesnt get dled
			reddit_id_cache.append(id)
			print(str(c) + ": " + id + " added to reddit_id_cache")
			check_submission(url, id)
			c += 1
		else:
			print(id + " has already been checked")
		print("sleeping for 1 seconds...")
		time.sleep(1)

	print(str(c) + " new submissions found")

if not os.path.isdir(CURRENT_PATH + "/pictures/"):
	os.mkdir(CURRENT_PATH + "/pictures/")
	print("creating /pictures/ in " + CURRENT_PATH)

get_submissions()
download_files()
