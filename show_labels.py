from flask import Flask, render_template, request, redirect, url_for
from plexapi.server import PlexServer
import os
from dotenv import load_dotenv
from flask_httpauth import HTTPBasicAuth

load_dotenv()

app = Flask(__name__)
auth = HTTPBasicAuth()

PLEX_URL = os.getenv('PLEX_URL')
PLEX_TOKEN = os.getenv('PLEX_TOKEN')
FLASK_USER = os.getenv('FLASK_USER')
FLASK_PASSWORD = os.getenv('FLASK_PASSWORD')
plex = PlexServer(PLEX_URL, PLEX_TOKEN)

users = {
    FLASK_USER: FLASK_PASSWORD  
}

@auth.verify_password
def verify_password(username, password):
    if username in users and users[username] == password:
        return username

@app.route('/', methods=['GET', 'POST'])
@auth.login_required
def index():
    if request.method == 'POST':
        show_id = request.form.get('show_id')
        label_action = request.form.get('label_action')
        show = plex.fetchItem(show_id)
        if label_action == 'add':
            show.addLabel('KEEP')
        elif label_action == 'remove':
            show.removeLabel('KEEP')
        return redirect(url_for('index'))

    shows = plex.library.section('TV Shows').all()
    shows_info = [{
        'title': show.title,
        'thumb': f"{PLEX_URL}{show.thumb}?X-Plex-Token={PLEX_TOKEN}",
        'ratingKey': show.ratingKey,
        'has_keep': 'KEEP' in [label.tag for label in show.labels]
    } for show in shows]
    return render_template('index.html', shows=shows_info)



if __name__ == '__main__':
    app.run(debug=True)
