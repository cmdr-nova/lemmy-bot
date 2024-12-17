import os
import random
import json
import requests
from PIL import Image
from mastodon import Mastodon
import tempfile
from bs4 import BeautifulSoup

# Configuration
LEMMY_INSTANCE_URL = 'https://lemmy.zip'
SUBREDDITS = [
              'anime@hexbear.net',
              'animewallpapers@ani.social'
              ]
LOG_FILE = 'posted_images.json'
IMAGE_LIMIT = 50
MASTODON_INSTANCE_URL = 'https://your.mastodon.instance'
MASTODON_CLIENT_ID = 'your-client-id'
MASTODON_CLIENT_SECRET = 'your-client-secret'
MASTODON_ACCESS_TOKEN = 'your-access-token'
CUSTOM_TEXT = "You can edit this and have a custom status posted along with the image pulled from Lemmy."

# Load posted images
def load_posted_images():
    if os.path.exists(LOG_FILE):
        with open(LOG_FILE, 'r') as f:
            return json.load(f)
    return []

# Save posted image
def save_posted_image(image_url):
    posted_images = load_posted_images()
    posted_images.append(image_url)
    with open(LOG_FILE, 'w') as f:
        json.dump(posted_images, f)

# Get random subreddit i.e. community
def get_random_subreddit():
    return random.choice(SUBREDDITS)

# Get high resolution image URL from Lemmy post content
def get_high_res_image_url_from_content(post_url):
    response = requests.get(post_url)
    response.encoding = 'utf-8'
    soup = BeautifulSoup(response.content, 'html.parser')
    picture = soup.find('picture')
    if picture:
        img = picture.find('img')
        if img and 'src' in img.attrs:
            return img['src']
    return None

# Get a random photo from Lemmy community
def get_random_photo_from_lemmy(community_name, retries=5):
    community, instance = community_name.split('@')
    for attempt in range(retries):
        print(f"Attempt {attempt + 1} to fetch posts from {community}@{instance}")
        response = requests.get(f"https://{instance}/api/v3/post/list?community_name={community}&sort=Hot")
        if response.status_code != 200:
            print(f"Failed to fetch posts: {response.status_code}")
            continue

        posts = response.json().get('posts', [])
        print(f"Fetched {len(posts)} posts")

        image_posts = []
        for post_wrapper in posts:
            post = post_wrapper['post']
            creator = post_wrapper['creator']
            image_url = None
            if 'thumbnail_url' in post and post['thumbnail_url'].endswith(('jpg', 'jpeg', 'png')):
                image_url = post['thumbnail_url']
            elif 'url' in post and post['url'].endswith(('jpg', 'jpeg', 'png')):
                image_url = post['url']
            elif 'url' in post:
                image_url = get_high_res_image_url_from_content(post['url'])

            if image_url:
                image_posts.append((post, creator, image_url))

        print(f"Found {len(image_posts)} image posts")

        if image_posts:
            posted_images = load_posted_images()
            random_post, creator, image_url = random.choice(image_posts)

            while image_url in posted_images:
                random_post, creator, image_url = random.choice(image_posts)

            save_posted_image(image_url)
            post_url = f"https://{instance}/post/{random_post['id']}"
            return random_post, creator, image_url, post_url
    raise Exception("No image posts found after multiple retries")

# Download and optimize the image
def download_and_optimize_image(image_url):
    response = requests.get(image_url)
    temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.jpg')
    temp_file.write(response.content)
    temp_file.close()

    image = Image.open(temp_file.name)
    image = image.convert('RGB')
    image.save(temp_file.name, optimize=True, quality=85)
    return temp_file.name

# Post that motherfreaker to Mastodon
def post_to_mastodon(mastodon_client, image_path, status_text):
    media = mastodon_client.media_post(image_path)
    mastodon_client.status_post(status_text, media_ids=[media], sensitive=True)

# Main function
def main():
    mastodon_client = Mastodon(
        access_token=MASTODON_ACCESS_TOKEN,
        api_base_url=MASTODON_INSTANCE_URL
    )

    community_name = get_random_subreddit()
    post, creator, image_url, post_url = get_random_photo_from_lemmy(community_name)
    image_path = download_and_optimize_image(image_url)
    # You can edit the below status_text to say whatever you like, although I recommend keeping names, titles and sources, so that authors get credit
    mastodon_status_text = f"{CUSTOM_TEXT}\n\n Posted by: u/{creator['name']}\n Community: c/{community_name}\n Title: [{post['name']}]({post_url})"

    post_to_mastodon(mastodon_client, image_path, mastodon_status_text)

    os.remove(image_path)

if __name__ == "__main__":
    main()
