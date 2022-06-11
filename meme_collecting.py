import os, random, scrapetube, praw, requests, urllib.request
from pytube import YouTube
from instaloader import Instaloader, Profile


# Reads the dejavu txt file and returns a list of the contents
def get_dejavu():
    with open("dejavu.txt", "r") as f:
        return f.read().splitlines()

# Adds a new value to the dejavu txt file
def add_to_dejavu(s):
    with open("dejavu.txt", "a") as f:
        f.write(s + "\n")

# Clears the dejavu txt file
def clear_dejavu():
    with open("dejavu.txt", "w") as f:
        f.write("")

# Overwrites the dejavu txt file with just it's last 100 lines
def dejavu_last_hundred():
    new_list = get_dejavu()
    if len(new_list) > 200:
        clear_dejavu()
        with open("dejavu.txt", "a") as f:
            for item in new_list[-100:]:
                f.write(item + "\n")

# Converts the given video to an image if it is less than 1 second
def vid_to_img(s):
    import cv2
    cap = cv2.VideoCapture(f"{s}.mp4")
    if (int(cap.get(cv2.CAP_PROP_FRAME_COUNT)) / cap.get(cv2.CAP_PROP_FPS)) <= 1:
        cv2.imwrite(f"{s}.jpeg", cap.read()[1])
        return True
    else:
        return False

# Holds information relevent to using the Reddit library
class RedditInfo:
    # Constructor
    def __init__(self, client_id, secret, reddit_username, reddit_password, user_agent):
        self.client_id = client_id
        self.secret = secret
        self.reddit_username = reddit_username
        self.reddit_password = reddit_password
        self.user_agent = user_agent

# Retrieves memes
class MemeMachine:
    # filenames = name it saves the memes as
    # reddit_ids = list of subreddits it searches
    # yt_ids = list of yt channels (links) it looks for memes from
    # insta_ids = list of instagram accounts it looks for memes from
    # perecentages = list of numbers indicating the percent chance of getting a certain type of meme
    #           example: [20, 40, 40] => 20% reddit memes, 40% youtube memes, 40% instagram memes
    # reddit_info = RedditInfo class containing info needed to use Praw
    # no_vidoes = Boolean stating whether or not videos should be procuded
    def __init__(self, filenames, reddit_ids, yt_ids, insta_ids, percents, reddit_info, no_videos=False):
        if len(reddit_ids) == 0 and percents[0] != 0:
            raise Exception("Please give at least one subreddit for the bot to pick from.")
        if len(yt_ids) == 0 and percents[1] != 0:
            raise Exception("Please give at least one YouTube channel for the bot to pick from.")
        if len(insta_ids) == 0 and percents[2] != 0:
            raise Exception("Please give at least one Instagram account for the bot to pick from.")
        if sum(percents) != 100:
            raise Exception("Please ensure the sum of percentages is equal to 100.")
        if no_videos and percents[1] > 0:
            raise Exception("If you wish to disable videos, please set the YouTube percent to 0.")
        self.filenames = filenames
        self.reddit_ids = reddit_ids
        self.yt_ids = yt_ids
        self.insta_ids = insta_ids
        self.perecents = percents
        self.reddit_info = reddit_info
        self.no_videos = no_videos
    
    # Retrieves a reddit meme
    def reddit_meme(self):
        # Initializes the reddit variable
        reddit = praw.Reddit(
            client_id=self.reddit_info.client_id,
            client_secret=self.reddit_info.secret,
            username=self.reddit_info.reddit_username,
            password=self.reddit_info.reddit_password,
            user_agent=self.reddit_info.user_agent
        )

        # Finds a reddit post
        reddit_url = ""
        meme_type = ""
        dejavu = get_dejavu()
        subreddit_pick = random.choice(self.reddit_ids)
        subreddit = reddit.subreddit(subreddit_pick).hot(limit=40)
        for submission in subreddit:
            if not (submission.is_self or submission.stickied or submission.url in dejavu):
                meme_type = submission.url.split(".")[-1]
                if meme_type == "png" or meme_type == "jpg":
                    reddit_url = submission.url
                    add_to_dejavu(reddit_url)
                    break
        
        # Downloads the reddit meme, or throws an exception if an image could not be found
        if reddit_url == "":
            raise Exception(f"Unable to find Reddit image for subreddit {subreddit_pick}")
        else:
            img_data = requests.get(reddit_url).content
            with open(f"{self.filenames}.{meme_type}", "wb") as handler:
                handler.write(img_data)
        
        # Returns the name of the saved file
        return f"{self.filenames}.{meme_type}"

    # Retrieves a Youtube meme
    def yt_meme(self):
        # Finds a video
        yt_channel = random.choice(self.yt_ids)
        videos = scrapetube.get_channel(channel_url=yt_channel)
        vid_url = ""
        dejavu = get_dejavu()
        for video in videos:
            vid_id = video["videoId"]
            if not vid_id in dejavu:
                add_to_dejavu(vid_id)
                vid_url = f"https://www.youtube.com/watch?v={vid_id}"
                break
        
        # Downloads the video, or throws an exception if no video was found
        if vid_url == "":
            raise Exception(f"Unable to find YouTube video for channel {yt_channel}")
        else:
            yt = YouTube(vid_url)
            ys = yt.streams.get_highest_resolution()
            ys.download(filename=f"{self.filenames}.mp4")
        
        # Returns the output filename
        return f"{self.filenames}.mp4"

    # Retrieves an Instagram meme
    def insta_meme(self):
        #Finds an instagram account
        prof_choice = random.choice(self.insta_ids)
        insta = Instaloader()
        profile = Profile.from_username(insta.context, prof_choice)

        # Finds a post
        posts = profile.get_posts()
        dejavu = get_dejavu()
        meme_type = ""
        meme_url = ""
        for post in posts:
            # Checks type
            if post.is_video:
                meme_type = "mp4"
                temp_url = post.video_url
            else:
                meme_type = "jpg"
                temp_url = post.url
            # Ensures the meme hasn't already been seen and that it is the correct type
            if (not (post.is_video and self.no_videos)) and (not temp_url in dejavu):
                meme_url = temp_url
                add_to_dejavu(meme_url)
                break
        
        # Downloads the meme, or throws an exception if one was not found
        if meme_url == "":
            raise Exception(f"Unable to find Instagram meme for account {prof_choice}")
        else:
            urllib.request.urlretrieve(meme_url, f"{self.filenames}.{meme_type}")
            # Converts the video to a photo if it's short enough
            if meme_type == "mp4" and vid_to_img(self.filenames):
                os.remove(f"{self.filenames}.mp4")
                meme_type = "jpeg"
        
        # Returns the name of the file
        return f"{self.filenames}.{meme_type}"

    # Retrieves a new meme (50% youtube, 50% reddit)
    def new_meme(self):
        rand = random.randint(1, 100)
        reddit_p = self.perecents[0]
        yt_p = self.perecents[1]
        if rand <= reddit_p:
            return self.reddit_meme()
        elif rand <= reddit_p + yt_p:
            return self.yt_meme()
        else:
            return self.insta_meme()
