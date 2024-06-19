from flask import Flask , render_template,request,session
from flask_sqlalchemy import SQLAlchemy
from dotenv import load_dotenv
import os
import base64
from requests import post,get
import json
import random

load_dotenv()


client_id=os.getenv("Client_id")
client_secret=os.getenv("client_secret")

app=Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI']="sqlite:///test.db"
app.secret_key = os.urandom(24)
app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'  # or 'Strict' or 'None'
app.config['SESSION_COOKIE_SECURE'] = True

db=SQLAlchemy(app)

class Entry(db.Model):
    id=db.Column(db.Integer,primary_key=True)
    name=db.Column(db.String(200),nullable=False)
    score=db.Column(db.Integer,default=0)

    def __repr__(self) -> str:
        return super().__repr__()

@app.route("/", methods=["get","post"])
def index():
    j=0
    if request.method=="POST":
        name=request.form.get('name',None)
        entry=Entry(name=name) 
        db.session.add(entry)
        db.session.commit()
        print("post")
        j=j+1
    return render_template("index.html")

#we are sending our client id and client secret  which should be in base64 encoded to the url which is specified and we do it using post
#we post the url then the headers then data
def get_token():
    auth_string=client_id+':'+client_secret
    encode_auth=auth_string.encode("utf-8")
    auth_base64=str(base64.b64encode(encode_auth),"utf-8")

    url="https://accounts.spotify.com/api/token"

    headers={
        "Authorization":   'Basic ' +auth_base64,
        "Content-Type":     "application/x-www-form-urlencoded"
    }
    data={'grant_type': 'client_credentials'}
    result= post(url, headers=headers,data=data)
    json_result = json.loads(result.content)
    token=json_result["access_token"]
    return token


#this function is creating a header which we can use further to get data
def get_authorized_header(token):
    return {"Authorization":"Bearer "+token}

def top_songs(token):
    url="https://api.spotify.com/v1/playlists/37i9dQZEVXbK4NvPi6Sxit/tracks"
    header=get_authorized_header(token)
    query="?&limit=4&market=IN&include_external=audio"
    query_url=url+query
    result=get(query_url,headers=header)
    json_result=json.loads(result.content)
    return json_result


def extract_songs(songs):
    title_artits=[]
    items=songs["items"]
    for item in items:
        track=item["track"]
        title_name=track["name"]
        is_playable=track["is_playable"]
        preview_url=track["preview_url"]
        artist_names = [art['name'] for art in track['artists']]
        title_artits.append((title_name,artist_names,preview_url,is_playable))
    return title_artits

def sep_title_url(lis):
    dic={}
    title_lis=[]
    for element in lis:
        title=element[0]
        artist=element[1]
        url=element[2]
        is_playable=element[3]
        dic[title]=url
        title_lis.append(title)

    for item in dic:
        choose=random.choice(title_lis)
        if  dic[choose]:
              break
        else:
              pass
    
    return dic,choose

@app.route("/game", methods=["POST", "GET"])
def game():
    if 'score' not in session:
        session['score'] = 0  # Initialize score in session

    if get_token():
        token = get_token()
        songs = top_songs(token)
        song_data = extract_songs(songs) if songs else []
        song_dic, selected = sep_title_url(song_data)
        session['selected'] = selected
        print(selected)  # Store selected in session
        url = song_dic[selected]

    else:
        print("No authorization is granted")
    name = request.form.get('name', '')
    # Retrieve chosen song from form data
    if request.method == "post":
        choosen_song = request.form.get('chosen_song', None)
        if choosen_song == session.get('selected', ''):
            session['score'] += 10  # Update score in session
        else:
            print("Nothing")
    else:
        print("nothjing found")
        

        

    return render_template("game.html", name=name, song_dic=song_dic, url=url, score=session['score'])

# @app.route("/game", methods=["post", "get"])
# def game():
#     if 'score' not in session:
#         session['score'] = 0  # Initialize score in session

#     if get_token():
#         token = get_token()
#         songs = top_songs(token)
#         song_data = extract_songs(songs) if songs else []
#         song_dic, selected = sep_title_url(song_data)
#         session['selected'] = selected  # Store selected in session
#         url = song_dic[selected]

#     else:
#         print("No authorization is granted")

#     choosen_song = request.form.get('value', "")
#     name = request.form.get('name', '')

#     if choosen_song == session.get('selected', ''):
#         session['score'] += 10  # Update score in session

#     return render_template("game.html", name=name, song_dic=song_dic, url=url, score=session['score'])



if __name__=="__main__":
    with app.app_context():
        db.create_all()
    app.run(debug=True)


# from flask import Flask, render_template, request, session
# from flask_sqlalchemy import SQLAlchemy
# from dotenv import load_dotenv
# import os
# import base64
# from requests import post, get
# import json
# import random

# load_dotenv()

# client_id = os.getenv("Client_id")
# client_secret = os.getenv("client_secret")

# app = Flask(__name__)
# app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///test.db"
# app.secret_key = os.urandom(24)
# app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'  # or 'Strict' or 'None'
# app.config['SESSION_COOKIE_SECURE'] = True

# db = SQLAlchemy(app)

# class Entry(db.Model):
#     id = db.Column(db.Integer, primary_key=True)
#     name = db.Column(db.String(200), nullable=False)
#     score = db.Column(db.Integer, default=0)

#     def __repr__(self) -> str:
#         return super().__repr__()

# @app.route("/", methods=["GET", "POST"])
# def index():
#     if request.method == "POST":
#         name = request.form.get('name', None)
#         entry = Entry(name=name)
#         db.session.add(entry)
#         db.session.commit()
#     return render_template("index.html")

# def get_token():
#     auth_string = client_id + ':' + client_secret
#     encode_auth = auth_string.encode("utf-8")
#     auth_base64 = str(base64.b64encode(encode_auth), "utf-8")

#     url = "https://accounts.spotify.com/api/token"
#     headers = {
#         "Authorization": 'Basic ' + auth_base64,
#         "Content-Type": "application/x-www-form-urlencoded"
#     }
#     data = {'grant_type': 'client_credentials'}
#     result = post(url, headers=headers, data=data)
#     json_result = json.loads(result.content)
#     token = json_result["access_token"]
#     return token

# def get_authorized_header(token):
#     return {"Authorization": "Bearer " + token}

# def top_songs(token):
#     url = "https://api.spotify.com/v1/playlists/37i9dQZEVXbK4NvPi6Sxit/tracks"
#     header = get_authorized_header(token)
#     query = "?&limit=4&market=IN&include_external=audio"
#     query_url = url + query
#     result = get(query_url, headers=header)
#     json_result = json.loads(result.content)
#     return json_result

# def extract_songs(songs):
#     title_artists = []
#     items = songs["items"]
#     for item in items:
#         track = item["track"]
#         title_name = track["name"]
#         is_playable = track["is_playable"]
#         preview_url = track["preview_url"]
#         artist_names = [art['name'] for art in track['artists']]
#         title_artists.append((title_name, artist_names, preview_url, is_playable))
#     return title_artists

# def sep_title_url(lis):
#     dic = {}
#     title_lis = []
#     for element in lis:
#         title = element[0]
#         artist = element[1]
#         url = element[2]
#         is_playable = element[3]
#         dic[title] = url
#         title_lis.append(title)

#     for item in dic:
#         choose = random.choice(title_lis)
#         if dic[choose]:
#             break

#     return dic, choose

# @app.route("/game", methods=["POST", "GET"])
# def game():
#     if 'score' not in session:
#         session['score'] = 0  # Initialize score in session

#     token = get_token()
#     songs = top_songs(token)
#     song_data = extract_songs(songs) if songs else []
#     song_dic, selected = sep_title_url(song_data)
#     session['selected'] = selected  # Store selected in session
#     url = song_dic[selected]

#     name = request.form.get('name', '')

#     if request.method == "POST":
#         chosen_song = request.form.get('chosen_song', None)
#         if chosen_song == session.get('selected', ''):
#             session['score'] += 10  # Update score in session

#     return render_template("game.html", name=name, song_dic=song_dic, url=url, score=session['score'])

# if __name__ == "__main__":
#     with app.app_context():
#         db.create_all()
#     app.run(debug=True)
