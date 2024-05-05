from plexapi.server import PlexServer
import datetime
from dotenv import load_dotenv
import os

# Load environment variables from .env file
load_dotenv()

# Access variables
PLEX_URL = os.getenv('PLEX_URL')
PLEX_TOKEN = os.getenv('PLEX_TOKEN')
USER1 = os.getenv('USER1')
USER2 = os.getenv('USER2')

# Configuration
WATCHED_TIME_LIMIT = datetime.timedelta(days=7)

# Connect to Plex server
plex = PlexServer(PLEX_URL, PLEX_TOKEN)

try:
    # Connect to Plex server
    plex = PlexServer(PLEX_URL, PLEX_TOKEN)
    print("Successfully connected to Plex server:", PLEX_URL)
except Exception as e:
    print("Failed to connect to Plex server:", e)
    exit(1)  # Stop the script if connection is not successful

# Informative start message
print("Starting to process TV shows...")

# Iterate through all TV shows
for show in plex.library.section('TV Shows').all():
    # Check if the show has the 'bro_watch' label
    has_bro_watch = 'bro_watch' in [label.tag for label in show.labels]

    # Process each episode based on the label presence at the show level
    for episode in show.episodes():
        try:
            # Fetch user1's watch status for the episode
            user1_views = [v for v in episode.views if v.user.title == USER1]
            if user1_views:
                user1_latest_watch = max(v.viewedAt for v in user1_views)
                if datetime.datetime.now() - user1_latest_watch > WATCHED_TIME_LIMIT:
                    # If the show does not have the 'bro_watch' label, delete the episode
                    if not has_bro_watch:
                        episode.delete()
                        print(f"Deleted {episode.title} from show {show.title} as it's watched by {USER1} and the show has no 'bro_watch' label.")
                    else:
                        # If the show has the 'bro_watch' label, check user2's watch status
                        user2_views = [v for v in episode.views if v.user.title == USER2]
                        if user2_views:
                            user2_latest_watch = max(v.viewedAt for v in user2_views)
                            if datetime.datetime.now() - user2_latest_watch > WATCHED_TIME_LIMIT:
                                episode.delete()
                                print(f"Deleted {episode.title} from show {show.title} as both {USER1} and {USER2} watched it over a week ago.")
                        else:
                            print(f"Kept {episode.title} from show {show.title} as {USER2} has not watched it yet.")
        except Exception as e:
            print(f"Error processing {episode.title} from show {show.title}: {str(e)}")

# Informative end message
print("Finished processing all TV shows.")
