

from cs50 import SQL
from flask import Flask, render_template, request, redirect, abort, session
from flask_session import Session
from tempfile import mkdtemp
from urllib.parse import urlparse, parse_qs
from helpers import getkey, login_required, get_videoID, get_video_stats, get_comments_list, get_comment_content
import requests
import json
import os
import random
from werkzeug.security import check_password_hash, generate_password_hash
from datetime import datetime, date, time



app = Flask(__name__)

# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_FILE_DIR"] = mkdtemp()
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

#database
db = SQL("sqlite:///sc.db")

#api key
key = getkey()



@app.route("/")
@login_required
def index():
    return render_template("index.html")


@app.route("/login", methods=["GET", "POST"])
def login():

    session.clear()

    if request.method == "POST":
        if not request.form.get("email"):
            return  "must provide email"
        elif not request.form.get("password"):
            return  "must provide password"

        rows = db.execute("SELECT * FROM users WHERE email = :email", \
                            email = request.form.get("email"))

        #check if password is correct
        if len(rows) != 1 or not check_password_hash(rows[0]["password"], request.form.get("password")):
            return "invalid password or username"

        #remember who logged in
        session["user_id"] = rows[0]["id"]
        return render_template("index.html")
    else:
        return render_template("login.html")



@app.route("/register", methods = ["GET", "POST"])
def register():
    if request.method == "POST":
        if not request.form.get("username"):
            return  "must provide name"
        if not request.form.get("email"):
            return  "must provide email"
        if not request.form.get("phone"):
            return "must provide phone number"
        if not request.form.get("password"):
            return "must provide password"
        if not request.form.get("confirmation"):
            return "must provide confirmation"
        if request.form.get("password") != request.form.get("confirmation"):
            return "password confirmation is not correct"

        hashPass =  generate_password_hash(request.form.get("password"))

        res = db.execute("INSERT INTO users (name, password, phone, email) VALUES(:name, :password, :phone, :email)", \
                            name = request.form.get("username"), password = hashPass, phone = request.form.get("phone"), \
                            email = request.form.get("email"))

        if not res:
            return "username is already exist"

        session["user_id"] = res
        return redirect("/")
    else:
        return render_template("register.html")


@app.route("/logout")
def logout():
    """Log user out"""

    # Forget any user_id
    session.clear()

    # Redirect user to login form
    return redirect("/")


@login_required
@app.route("/get", methods = ["GET" ,"POST"])
def getComments():

    if request.method == "GET":
        return render_template("index.html")

    else:
        if not request.form.get("contestName"):
            return "must provide contest name"


        if not request.form.get("ytlink"):
            return "must provide youtube video link"

        #азделяем ссылку на части, и вытаскиваем айди в ЛИСТЕ
        global videoID
        videoID = get_videoID(request.form.get("ytlink"))

        #get stats from video
        global stats
        stats = get_video_stats(videoID, key)


        #get list of comments
        global listID
        listID = list(get_comments_list(videoID, key))


        #get len of comments
        global lenListID
        lenListID = len(listID)


        #получаем время
        nowF = datetime.strftime(datetime.now(), "%Y.%m.%d %H:%M:%S")

        #add info in table
        rows = db.execute("INSERT INTO contests (user_id, title, link, date) VALUES(:id, :title, :link, :date)", \
                            id = session["user_id"], title = request.form.get("contestName"), link = request.form.get("ytlink"),\
                                        date = nowF)
        session["id"] = rows


        return render_template("/result.html", videoID = videoID, views = stats['viewCount'], likes = stats['likeCount'],\
                                                                dislikes = stats['dislikeCount'], total = lenListID)




@login_required
@app.route("/getw")
def getWinner():
    #get comment id
    commentID =  random.choice(listID)

    #get comment content
    commentData = get_comment_content(commentID, key)

    #json
    winnerData = {}
    winnerData['name'] = commentData['author']
    winnerData['comment'] = commentData['comment']
    winnerData['id'] = commentID
    winnerData['data'] = commentData
    winnerDataJSON = json.dumps(winnerData)

    #info about winner
    author = commentData['author']
    comment = commentData['comment']
    imgUrl = commentData['authorImage']
    chUrl = commentData['authorChannelUrl']



    db.execute("UPDATE contests SET post_id = :postID, winner = :data WHERE id = :contestID",\
                    postID = commentID, data = winnerDataJSON, contestID = session["id"])





    return render_template("getw.html", videoID = videoID, views = stats['viewCount'], likes = stats['likeCount'],\
                             dislikes = stats['dislikeCount'], total = lenListID,\
                                author = author, comment = comment, imgUrl = imgUrl, chUrl = chUrl)





@login_required
@app.route("/history")
def history():

    rows = db.execute("SELECT * FROM contests WHERE user_id = :id", id = session["user_id"])














