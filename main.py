from flask import Flask, render_template, redirect, url_for, request
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired
from flask_bootstrap import Bootstrap
import requests
import os

MM_ENDPOINT = "https://api.musixmatch.com/ws/1.1"
API_KEY = os.environ.get("API_KEY")

app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get("SECRET_KEY")

Bootstrap(app)


class SearchForm(FlaskForm):
    search = StringField(label="Search a Song, Artist or Lyrics", validators=[DataRequired()])
    submit = SubmitField(label="Search")


@app.route('/', methods=["GET", "POST"])
def home():
    form = SearchForm()

    # This gets the top 10 artist in USA
    response = requests.get(f"{MM_ENDPOINT}/chart.artists.get?format=json&callback=callback&country=us&apikey={API_KEY}")
    data = response.json()["message"]["body"]["artist_list"]

    # This gets the top 10 songs in USA
    response_2 = requests.get(f"{MM_ENDPOINT}/chart.tracks.get?format=json&callback=callback&country=us&f_has_lyrics=<string>&apikey={API_KEY}")
    data_2 = response_2.json()["message"]["body"]["track_list"]

    if form.validate_on_submit():
        song_input = form.search.data
        return redirect(url_for('search', song_input=song_input))

    return render_template("index.html", form=form, artists=data, songs=data_2)


@app.route('/search/<song_input>', methods=["GET", "POST"])
def search(song_input):
    # This gets the search results in tracks
    track_response = requests.get(
        f"{MM_ENDPOINT}/track.search?format=json&callback=callback&q_track={song_input}&page_size=100&s_track_rating=desc&apikey={API_KEY}")
    track_data = track_response.json()["message"]["body"]["track_list"]

    # This gets the search results in artists
    artist_response = requests.get(
        f"{MM_ENDPOINT}/artist.search?format=json&callback=callback&q_artist={song_input}&page_size=100&apikey={API_KEY}")
    artist_data = artist_response.json()["message"]["body"]["artist_list"]

    # This gets the search results in lyrics
    lyrics_response = requests.get(
        f"{MM_ENDPOINT}/track.search?format=json&callback=callback&q_lyrics={song_input}&f_has_lyrics=<number>&s_track_rating=desc&page_size=100&apikey={API_KEY}")
    lyrics_data = lyrics_response.json()["message"]["body"]["track_list"]

    return render_template("search.html", tracks=track_data, artists=artist_data, lyrics=lyrics_data)


@app.route('/search', methods=["GET", "POST"])
def navbar_search():
    song_input = request.form['search']
    return redirect(url_for('search', song_input=song_input))


@app.route('/lyrics/<int:index>/<artist>/<track>', methods=["GET", "POST"])
def lyrics(index, artist, track):
    lyric_response = requests.get(f"{MM_ENDPOINT}/track.lyrics.get?format=json&callback=callback&track_id={index}&apikey={API_KEY}")
    lyric_data = lyric_response.json()["message"]["body"]["lyrics"]["lyrics_body"].split("\n")
    copyright_data = lyric_response.json()["message"]["body"]["lyrics"]
    return render_template("lyrics.html", results=lyric_data, artist=artist, track=track, cr=copyright_data)


@app.route('/album/<artist>/<int:index>', methods=["GET", "POST"])
def artist(index, artist):
    artist_response = requests.get(f"{MM_ENDPOINT}/artist.albums.get?format=json&callback=callback&artist_id={index}&page_size=100&apikey={API_KEY}")
    artist_data = artist_response.json()["message"]["body"]["album_list"]
    return render_template("artist-album.html", albums=artist_data)


@app.route('/album-songs/<int:index>', methods=["GET", "POST"])
def songs(index):
    songs_response = requests.get(f"{MM_ENDPOINT}/album.tracks.get?format=json&callback=callback&album_id={index}&f_has_lyrics=<string>&page_size=100&apikey={API_KEY}")
    songs_data = songs_response.json()["message"]["body"]["track_list"]
    return render_template("album-songs.html", songs=songs_data)


if __name__ == '__main__':
    app.run(debug=True)