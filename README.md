# lemmy-bot
A recreation of my "reddit-bot" script that pulls images from indicated Lemmy communities, and posts them to Mastodon!

Using this script is very simple, and you should definitely use it in a secure environment where others cannot access it (due to the credentials it's storing). Firstly, install the requirements.
```
pip install -r requirements.txt
```
If this isn't working, it's because you need to setup an environment first, by doing the following:
```
python3 -m venv your-environment-name
```
And then
```
source your-environment-name/bin/activate
```
And now you can run the requirements installation.

Next (assuming you've already put the script into the folder where you intend to keep, and run it, do this:
```
python3 lemmy-bot.py
```
And, if you've provided all of the correct credentials, and input your own communities for the script to pull from (not YOUR own communities, but communities you want to showcase image content from), it will post an image to the Mastodon account you've provided credentials for, including the user's name, a link to the original post, your custom text, and the title of the post!

Enjoy.
