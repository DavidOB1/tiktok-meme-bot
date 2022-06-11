from math import floor
from moviepy.video.io.ffmpeg_tools import ffmpeg_extract_subclip
import moviepy.editor as mp
import random, os
from meme_collecting import MemeMachine   


# Generates meme vidoes to be uploaded on TikTok
class VideoGenerator:
    # Constructor
    def __init__(self, output_name, meme_machine):
        # Ensures there is at least one sound in the list
        sounds = []
        for file in os.listdir("sounds"):
            if file[-3:] == "mp3":
                sounds.append("sounds/" + file)
        if len(sounds) == 0:
            raise Exception("Please make sure there is at least one mp3 file in the sounds folder.")
        self.sounds = sounds

        # Ensures there is at least one video clip in the list
        footage = []
        for file in os.listdir("footage"):
            if file[-3:] == "mp4":
                footage.append("footage/" + file)
        if len(footage) == 0:
            raise Exception("Please make sure there is at least one mp4 file in the footage folder.")
        self.footage = footage

        # Sets the other fields
        self.output_name = output_name
        self.machine = meme_machine

    # Gets a random audio clip based on the saved sounds
    def get_audio_clip(self):
        sound = random.choice(self.sounds)
        clip = mp.AudioFileClip(sound)
        return clip.set_duration(floor(clip.duration))

    # Gets a video clip of the specified length, with the name "clip.mp4"
    def get_clip(self, clip_length):
        clip_name = "clip.mp4"
        video_footage = random.choice(self.footage)
        rand = random.randint(0, 813 - clip_length)
        ffmpeg_extract_subclip(video_footage, rand, rand + clip_length, targetname=clip_name)
        return clip_name    

    # Generates a meme video with a unique background clip and meme
    def gen_meme_video(self):
        # Gets the audio, meme image, and video clip
        audio = self.get_audio_clip()
        duration = audio.duration
        meme_name = self.machine.new_meme()
        clip_name = self.get_clip(duration)
        clip = mp.VideoFileClip(clip_name).set_audio(audio)

        # Reshapes the meme to fit in the video well (goes off of 1080x1920 video resolution)
        meme = mp.ImageClip(meme_name).set_position(lambda x: ('center', x + 220)).set_duration(duration)
        meme = meme.resize(min(900 / meme.w, 1050 / meme.h))
        
        # Creates the final meme video and returns the file name
        final = mp.CompositeVideoClip([clip, meme])
        final.write_videofile(self.output_name)
        return self.output_name
