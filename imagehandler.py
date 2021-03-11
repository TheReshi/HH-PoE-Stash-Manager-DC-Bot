import os
from imgurpython import ImgurClient

client_id = os.getenv('IMGUR_CLIENT_ID')
client_secret = os.getenv('IMGUR_CLIENT_SECRET')
#auth_pin = os.getenv('IMGUR_AUTH_PIN')
access_token = os.getenv('IMGUR_ACCESS_TOKEN')
refresh_token = os.getenv('IMGUR_REFRESH_TOKEN')

client = ImgurClient(client_id, client_secret, access_token, refresh_token)

def upload_to_imgur(url):
    imgur_link = client.upload_from_url(url, config=None, anon=True)
    return(imgur_link['link'])