import os, time, random
from selenium.webdriver import Chrome, ChromeOptions
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from clip_generator import VideoGenerator
from meme_collecting import MemeMachine, RedditInfo
from dotenv import load_dotenv


# Given an element and list of hashtags, shuffles the hashtags and types them into the given element
# (The given element should almost always be the caption text box)
def type_caption(elem, cap_list):
    random.shuffle(cap_list)
    for hashtag in cap_list:
        elem.send_keys("#")
        time.sleep(0.1)
        for letter in hashtag:
            elem.send_keys(letter)
        time.sleep(0.5)
        elem.send_keys(Keys.SPACE)
        time.sleep(0.1)


# Represents a bot that can upload TikTok videos
class TikTok(Chrome):
    # Constructor
    def __init__(self, hashtags, video_generator, first_login=False):
        # Ensures the caption is not too long
        if len(" ".join(["#" + s for s in hashtags])) >= 150:
            raise Exception("You have too many hashtags, please shorten the amount.")
        
        # Setting the options for the Chrome instance
        options = ChromeOptions()
        options.add_argument("--disable-blink-features=AutomationControlled")
        options.add_argument("window-size=1920,1000")
        options.add_argument("--profile-directory=Default")
        options.add_argument("--disable-notifications")

        # Sets the Chrome data to be the folder in the directory that's called selenium_data
        data_abs_path = os.path.abspath("selenium_data")
        options.add_argument("--user-data-dir=" + data_abs_path)

         # Let's the user log in to TikTok if they need to
        if first_login:
            self.log_into_tiktok(data_abs_path)

        # Initializes the driver
        super().__init__(options=options)

        # Sets the other fields
        self.wait = WebDriverWait(self, 15)
        self.hashtags = hashtags
        self.video_generator = video_generator
    
    # Uploads the meme based on the file name given/it's directory
    def upload_meme(self, meme_file):
        # Goes to the upload page and finds the select file button
        self.get("https://www.tiktok.com/upload?lang=en")
        self.wait.until(EC.presence_of_element_located((By.XPATH, '//*[@id="main"]/div[2]/div/iframe')))
        self.switch_to.frame(self.find_element(By.XPATH, '//*[@id="main"]/div[2]/div/iframe'))
        self.implicitly_wait(1)

        # Uploads the given meme
        select_file = self.find_element(By.XPATH, '//*[@id="root"]/div/div/div/div/div[2]/div[1]/div/input')
        meme_abs_path = os.path.abspath(meme_file)
        select_file.send_keys(meme_abs_path)

        # Types the caption
        cap_text = self.find_element(By.XPATH, '//*[@id="root"]/div/div/div/div/div[2]/div[2]/div[1]/div/div[1]/div[2]/div/div[1]/div/div/div/div/div/div')
        type_caption(cap_text, self.hashtags)

        # Posts the TikTok once it is ready
        self.wait.until(EC.element_to_be_clickable((By.XPATH, '//*[@id="root"]/div/div/div/div/div[2]/div[2]/div[7]/div[2]/button'))).click()
        time.sleep(15)

        # The upload was successful
        print("[TikTok] - Video upload is complete")
        self.get("https://www.google.com/")

    # Let's the user log into TikTok, given the absolute path to the data folder
    def log_into_tiktok(self, data_abs_path):
        # Intializes the alternative driver used to log into TikTok
        altoptions = ChromeOptions()
        altoptions.add_argument("--user-data-dir=" + data_abs_path)
        altdriver = Chrome(options=altoptions)

        # Let's the user log in
        print("Please log into your TikTok account.")
        altdriver.get("https://www.tiktok.com/login/")
        WebDriverWait(altdriver, 600).until(EC.presence_of_all_elements_located((By.XPATH, '//*[@id="app"]/div[1]/div/div[2]/div[1]/a/div/span')))
        print("Log in was successful.")
        altdriver.quit()
    
    # Runs the bot automatically ever n minutes
    def run(self):
        print("Starting the run loop ....")
        while True:
            self.upload_meme(self.video_generator.gen_meme_video())
            time.sleep(5400)


# Running the TikTok bot
if __name__ == "__main__":
    # Opens the .env file and reads the data to setup the needed classes
    load_dotenv()

    reddit_info = RedditInfo(
        os.getenv("CLINET_ID"),
        os.getenv("SECRET"),
        os.getenv("REDDIT_USERNAME"),
        os.getenv("REDDIT_PASSWORD"),
        os.getenv("USER_AGENT")
        )

    meme_generator = MemeMachine(
        "meme",
        [s for s in os.getenv("SUBREDDITS").split(", ") if s != ""],
        [],
        [s for s in os.getenv("IG_ACCOUNTS").split(", ") if s != ""],
        [int(os.getenv("REDDIT_PERCENT")), 0, int(os.getenv("IG_PERCENT"))],
        reddit_info,
        True
        )

    video_generator = VideoGenerator("output.mp4", meme_generator)

    tiktok = TikTok(
        [s for s in os.getenv("TIKTOK_HASHTAGS").split(", ") if s != ""],
        video_generator,
        os.getenv("TIKTOK_LOGIN").lower() == "yes"
        )
    
    # Running the loop
    tiktok.run()
