from flask import Flask, render_template, url_for, request, redirect, g
from album_downloader import Playlist, Downloader


app = Flask(__name__)

MUSIC_DIRECTORY = "/home/deadboy/Desktop/Music"


@app.route('/', methods=['POST', 'GET'])
def index():
    if request.method == 'POST':
        artist = request.form['artist']
        album = request.form['album']

        downloader = Downloader(MUSIC_DIRECTORY, artist, album)
        downloader.load_playlists()

        playlists = downloader.playlists

        return render_template('results.html', artist=artist, album=album, playlists=playlists)
    else:
        return render_template('index.html')


@app.route('/download/<artist>/<album>/<int:index>', methods=['POST', 'GET'])
def download(artist, album, index):
    downloader = Downloader(MUSIC_DIRECTORY,
                            artist, album)
    downloader.do_the_work(index)
    return redirect('/')


if __name__ == "__main__":
    app.run(debug=True)
