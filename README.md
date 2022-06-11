# About the Project
I've seen a lot of people making bots that can create Reddit videos for TikTok, so I decided to expand on that idea
to make a program that can make TikTok meme videos and automatically post them. Memes are collected from either Reddit,
Instagram, or YouTube, and then they are put on top of a randomly sliced video from the footage folder, and given a sound
randomly picked from the sounds folder. After that, the video is saved as "output.mp4" and the video will be uploaded to TikTok.

# How to Use
Ensure the following before running the program:

- A .env file exists with the values from .env.template filled out.

- There is at least one mp4 video in the footage folder that is longer than any of the audios, and the resolution is 1080x1920.

- There is at least one mp3 audio in the sounds folder which is of reasonable length (usually between 5-60 seconds).

Once that is all complete, you can run the project by running the tiktok_bot.py file.

When running the program for the first time, make sure you sign into TikTok. Afterward, your Google Chrome data will be stored in the selenium_data
folder, so you won't have to log back in again. Note that this is done because TIkTok has bot protection and will not let you automatically
log into your account.

# Issues with the Project
One of the main issues I found with this is that TikTok does not let you upload videos from PC that use others' audio. This means that each
TikTok that is uploaded has to use original sound, which hurts its growth in the algorithm. Another major issue is that it is very possible that it will
upload a video with the same meme. Even though it keeps track of posts it's already seen, it is very common on platforms like Instagram for one meme to be
reposted on many different accounts, and there isn't an easy solution to check whether the same image contents are being uplaoded or not.

# Modularity
If you wish to use separate parts of this project rather than just running the main TikTok bot, here are ways to do so:
- MemeMachine can be imported into any project and can be used for many different purposes, such as personal meme viewing/collecting.

- VideoGenerator can be used on its own to generate videos which can then be manually uploaded to TikTok. This can be a good work-around for the aforementioned
problem of uploading TikToks on PC, as you can use this to generate the videos and then upload them on a mobile device, allowing you to use a different audio.

- The TikTok bot itself can be used to post other content aside from generate memes. All you need to do is give a different input to the upload_meme
method, and different content can be uploaded. For instance, you could use a bot to generate Reddit videos, then pass in the directory of the Reddit videos
to the upload_meme method to upload the videos automatically.
