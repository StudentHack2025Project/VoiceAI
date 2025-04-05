# -*- coding: utf-8 -*-
"""
Created on Sat Apr  5 14:45:46 2025

@author: shaha
"""

import os
from pyneuphonic import Neuphonic, TTSConfig
from pyneuphonic.player import AudioPlayer
def text_to_speech():
    client = Neuphonic(api_key=os.environ.get('NEUPHONIC_API_KEY'))
    sse = client.tts.SSEClient() #Creating a connection between me and the server
    tts_config = TTSConfig(
    speed=1.05, #speech speed
    lang_code='en', # replace the lang_code with the desired language code.
    voice_id='e564ba7e-aa8d-46a2-96a8-8dffedade48f'  # use client.voices.list() to view all available voices
    ) #Voice_id is just to choose which voice we want
    voices = client.voices.list()
    #print(voices) to print out the list of voices so we gotta choose between them later
    with AudioPlayer() as player:
        response = sse.send('Hello Shahad I am here!', tts_config=tts_config)
        player.play(response)
    
        player.save_audio('output.wav')  # save the audio to a .wav file
    
    
text_to_speech()
    