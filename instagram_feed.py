from instaloader import *
from dotenv import load_dotenv
import os

# Load environment variables from .env file
load_dotenv()

# Get credentials from environment variables
USERNAME = os.getenv("USERNAME")
PASSWORD = os.getenv("PASSWORD")
CSRFTOKEN = os.getenv("CSRFTOKEN")
SESSIONID = os.getenv("SESSIONID")
DS_USER_ID = os.getenv("DS_USER_ID")
MID = os.getenv("MID")
IG_DID = os.getenv("IG_DID")

L = instaloader.Instaloader()
L.load_session(
    USERNAME,
    {
        "csrftoken": CSRFTOKEN,
        "sessionid": SESSIONID,
        "ds_user_id": DS_USER_ID,
        "mid": MID,
        "ig_did": IG_DID,
    },
)

profile = Profile.from_username(L.context, 'uwpokerclub')
for i, post in enumerate(profile.get_posts()):
    if i > 10:
        break
    print(i, post.caption)
    # L.download_post(post, target=profile.username)

# test = L.get_followers()
