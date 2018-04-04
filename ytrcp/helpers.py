import os
import urllib.request
from urllib.parse import urlparse, parse_qs
import json
import requests

from flask import redirect, render_template, request, session
from functools import wraps


def getkey():
    key = os.environ.get("api_key")
    return key

def login_required(f):
    """
    Decorate routes to require login.

    http://flask.pocoo.org/docs/0.12/patterns/viewdecorators/
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get("user_id") is None:
            return redirect("/login")
        return f(*args, **kwargs)
    return decorated_function


#get video id
def get_videoID(link):
    ytlink = urlparse(link)
    res = parse_qs(ytlink.query)['v']
    videoID = res[0]
    return videoID


#get stats from video
def get_video_stats(videoID, key):
    urlStats = "https://www.googleapis.com/youtube/v3/videos?id={}&key={}&part=statistics".format(videoID, key)
    rS = requests.get(urlStats)
    dataStats = json.loads(rS.content)
    result = {}
    #variable for total counts
    for item in dataStats["items"]:
	    result['viewCount'] = item["statistics"]["viewCount"]
	    result['likeCount'] = item["statistics"]["likeCount"]
	    result['dislikeCount'] = item["statistics"]["dislikeCount"]

    return result


#get json
def get_comments_list(videoID, key):


    url = 'https://www.googleapis.com/youtube/v3/commentThreads?part=snippet&maxResults=100&textFormat=plainText&videoId={}&fields=items%2CnextPageToken%2CpageInfo&key={}'.format(videoID ,key)

    r = requests.get(url)
    #JSON v data
    r = r.content
    data = json.loads(r.decode('utf-8'))

    #список постов в айдишниках
    listID = []

    nextKey = None
    #если комментов меньше чем сто
    try:
        nextKey = data["nextPageToken"]
    except KeyError:
        pass



    #get first page
    for item in data["items"]:
        id = item["id"]
        listID.append(id)

    #get others
    while nextKey is not None:
        url = 'https://www.googleapis.com/youtube/v3/commentThreads?part=snippet&maxResults=100&pageToken={}&textFormat=plainText&videoId={}&fields=etag%2CeventId%2Citems%2Ckind%2CnextPageToken%2CpageInfo%2CtokenPagination%2CvisitorId&key={}'.format(nextKey, videoID, key)

        r = requests.get(url)
        r = r.content

        data = json.loads(r.decode('utf-8'))

        for item in data["items"]:
            id = item["id"]
            listID.append(id)
        if "nextPageToken" in data:
            nextKey = data["nextPageToken"]
        else:
            nextKey = None

    return listID


#get comment content
def get_comment_content(commentID, key):
    urlComment = 'https://www.googleapis.com/youtube/v3/comments?part=snippet&id={}&textFormat=plainText&fields=items&key={}'.format(commentID, key)
    rC = requests.get(urlComment)
    rC = rC.content
    dataC = json.loads(rC.decode('utf-8'))

    result = {}

    for item in dataC["items"]:
    	result['author'] = item["snippet"]["authorDisplayName"]
    	result['comment'] = item["snippet"]["textDisplay"]
    	result['authorImage'] = item["snippet"]["authorProfileImageUrl"]
    	result['authorChannelUrl'] = item["snippet"]["authorChannelUrl"]
    	result['likeCount'] = item["snippet"]["likeCount"]

    return result











