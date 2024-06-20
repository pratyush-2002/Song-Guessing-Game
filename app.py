from flask import Flask , render_template,request,session,redirect,url_for,flash
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

@app.route("/", methods=["GET","POST"])
def index():
    if request.method=="POST":
        name=request.form.get('name',None)
        entry=Entry(name=name) 
        db.session.add(entry)
        db.session.commit()
    return render_template("index.html")

class Song:
    def __init__(self, client_id, client_secret):
        self.client_id = client_id
        self.client_secret = client_secret
    #we are sending our client id and client secret  which should be in base64 encoded to the url which is specified and we do it using post
    #we post the url then the headers then data
    def get_token(self):
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
    def get_authorized_header(self,token):
        return {"Authorization":"Bearer "+token}

    def top_songs(self,token):
        pick=['37i9dQZEVXbK4NvPi6Sxit','37i9dQZEVXbLZ52XmnySJg','37i9dQZF1DWZNJXX2UeBij','37i9dQZF1DWVq1SXCH6uFn','37i9dQZF1DWYztMONFqfvX']
        random_pick=random.choice(pick)
        url=f"https://api.spotify.com/v1/playlists/{random_pick}/tracks"
        header=self.get_authorized_header(token)
        query="?&limit=10&market=IN&include_external=audio"
        query_url=url+query
        result=get(query_url,headers=header)
        json_result=json.loads(result.content)
        return json_result


    def extract_songs(self,songs):
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


    def sep_title_url(self, lis):
        dic = {}
        title_lis = []
        counter=0
        for element in lis:
            title, artist, url, is_playable = element
            print(title,url)
            if url and len(title_lis) < 4: # Only add if a valid URL is present
                dic[title] = url
                title_lis.append(title)
   
            
        print(dic)
        chosen_title = random.choice(title_lis)
        return dic, chosen_title



@app.route("/game", methods=["POST", "GET"])
def game():
    session['name'] = request.form.get('name', '')
    song_dic={}
    url=''
    session['score']=0
    if request.method == 'POST':
        song_n = Song(client_id, client_secret)
        token=song_n.get_token()
        if token:
            songs = song_n.top_songs(token)
            song_data = song_n.extract_songs(songs) if songs else []
            song_dic, selected = song_n.sep_title_url(song_data)
            session['selected_song'] = selected   # Store selected in session
            url = song_dic.get(selected, "") 
        else:
            flash("Authorization failed. Please check your credentials.")
        selected_song = session.get('selected_song', '')
        choosen_song = request.form.get('chosen_song', "")
        if choosen_song==selected_song:
            session['score']=session['score']+10
        else:
            session['score']=session['score']
        

    return render_template("game.html", name=session['name'], song_dic=song_dic, url=url,score=session['score'])



if __name__=="__main__":
    with app.app_context():
        db.create_all()
    app.run(debug=True)
