# -*- coding: utf-8 -*-
"""
Created on Sat Apr  5 14:45:46 2025

@author: shaha
"""

import os
import random
import time
import schedule
import datetime

from pyneuphonic import Neuphonic, TTSConfig
from pyneuphonic.player import AudioPlayer
def server_initiation():
    client = Neuphonic(api_key=os.environ.get('NEUPHONIC_API_KEY'))
    sse = client.tts.SSEClient() #Creating a connection between me and the server
    tts_config = TTSConfig(
    speed=1.05, #speech speed
    lang_code='en', # replace the lang_code with the desired language code.
    voice_id='e564ba7e-aa8d-46a2-96a8-8dffedade48f'  # use client.voices.list() to view all available voices
    ) #Voice_id is just to choose which voice we want
    voices = client.voices.list()
    #print(voices) to print out the list of voices so we gotta choose between them later
    return tts_config, sse

tts_config, sse = server_initiation()   
def text_to_speech(text): 
    with AudioPlayer() as player:
        print("This works")
        response = sse.send(text, tts_config=tts_config)
        player.play(response)
        player.save_audio('output.wav')  # save the audio to a .wav file
        
def motivational_prompts():
    motivational_prompts_status = True#Need to adjust it and add a drop down menu from the main thing
    motivational_prompts = [
    "You're doing great, keep it up!",
    "You're making awesome progress!",
    "Keep going! You're almost there!",
    "Great job! Now, let's focus on the next task.",
    "Amazing effort! Keep pushing!",
    "You’re on fire today, keep it up!",
    "You’re staying focused! Let’s keep it going!"
]
    if motivational_prompts_status:
        schedule.every(25).minutes.do(motivational_prompts_function,motivational_prompts)
        
def motivational_prompts_function(original_motivational_prompts):
    sample_text = random.choice(original_motivational_prompts)
    text_to_speech(sample_text)
        

def reminders(time, reminder):
    now = datetime.datetime.now()
    print(now.time())
     # returns a string like '14:35:22'
    time_obj = datetime.datetime.strptime(time, "%H:%M:%S").time()
    if time_obj < now.time():
        text_to_speech("This is your reminder to " + reminder)


motivational_prompts()
reminders("1:26:00", "Cook")

while True:
    schedule.run_pending()
    time.sleep(1)
    









