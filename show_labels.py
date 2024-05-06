from flask import Flask, render_template, request, redirect, url_for
import os
import requests
from dotenv import load_dotenv
from flask_httpauth import HTTPBasicAuth

load_dotenv()

app = Flask(__name__)
auth = HTTPBasicAuth()

PLEX_URL = os.getenv('PLEX_URL')
PLEX_TOKEN = os.getenv('PLEX_TOKEN')
FLASK_USER = os.getenv('FLASK_USER')
FLASK_PASSWORD = os.getenv('FLASK_PASSWORD')

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
        url = f"{PLEX_URL}library/metadata/{show_id}"
        headers = {'X-Plex-Token': PLEX_TOKEN, 'Accept': 'application/json'}
        
        try:
            if label_action == 'add':
                response = requests.put(url, headers=headers, params={'label': 'KEEP'})
            elif label_action == 'remove':
                response = requests.delete(url, headers=headers, params={'label': 'KEEP'})
            
            response.raise_for_status()  # This will raise an exception for HTTP errors
        except requests.exceptions.RequestException as e:
            print(f"Error processing request: {e}")
            return f"Error processing request: {e}", 500
        return redirect(url_for('index'))

    # Fetch shows (simplified example, adjust as needed)
    try:
        response = requests.get(f"{PLEX_URL}library/sections/2/all", headers={'X-Plex-Token': PLEX_TOKEN, 'Accept': 'application/json'})
        response.raise_for_status()
        shows = response.json()['MediaContainer']['Metadata']
    except requests.exceptions.RequestException as e:
        print(f"Error fetching shows: {e}")
        return f"Error fetching shows: {e}", 500

    shows_info = [{
        'title': show['title'],
        'thumb': f"{PLEX_URL.rstrip('/')}/{show.get('thumb', '').lstrip('/')}?X-Plex-Token={PLEX_TOKEN}" if 'thumb' in show else None,
        'ratingKey': show['ratingKey'],
        'has_keep': 'KEEP' in [label['tag'] for label in show.get('Genre', [])]
    } for show in shows]

    return render_template('index.html', shows=shows_info)

if __name__ == '__main__':
    app.run(debug=True)
