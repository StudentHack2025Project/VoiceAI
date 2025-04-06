# -*- coding: utf-8 -*-
"""
Created on Sat Apr  5 14:45:46 2025

@author: shaha
"""

import os
import time
import schedule
from pyneuphonic import Neuphonic, TTSConfig
from pyneuphonic.player import AudioPlayer

current_job = None

def server_initiation():
    client = Neuphonic(api_key=os.environ.get('NEUPHONIC_API_KEY'))
    sse = client.tts.SSEClient()
    tts_config = TTSConfig(
        speed=1.05,
        lang_code='en',
        voice_id='e564ba7e-aa8d-46a2-96a8-8dffedade48f'
    )
    return tts_config, sse

tts_config, sse = server_initiation()

def text_to_speech(text): 
    with AudioPlayer() as player:
        response = sse.send(text, tts_config=tts_config)
        player.play(response)

def break_timer():
    schedule.every(45).minutes.do(start_timer)

def start_timer():
    global current_job
    text = "It is time for a 15 minutes break"
    text_to_speech(text)
    if current_job:
        schedule.cancel_job(current_job)
    current_job = schedule.every(15).minutes.do(end_break) 

def end_break():
    text = "Break is over! Time to get back to work!"
    text_to_speech(text)
    schedule.cancel_job(current_job)
    break_timer()  

break_timer()

while True:
    schedule.run_pending()
    time.sleep(1)
