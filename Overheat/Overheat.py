import os, os.path
import math.random

voteDir = 'D:\Program Files\Streamlabs Chatbot\Services\Twitch\Votes'

for file in os.listdir(voteDir)
    with open(file, 'r') as file:
        filedata = file.read()
    