#!/usr/bin/python
# -*- coding: utf-8 -*-

import codecs
import os
import io
import glob
import random

def feed(reduceby):
    #Parent.SendStreamMessage("Beginning Overheat")
    global timerActive
    voteDir = 'D:/Program Files/Streamlabs Chatbot/Services/Twitch/Votes/'
    campfireDir = 'D:/Program Files/Streamlabs Chatbot/Services/Twitch/flame.txt'
    retVal = ''
    threshold = 800
    interval = 100 # for every 100 past 1000, increase the multiplier by 1
    payoutBase = 2
    payoutInterval = 1000
    
    timerActive = False
    choices = os.listdir(voteDir)
    
    # add multiple copies of choices with higher values
    for file in os.listdir(voteDir):
        
        with io.open(voteDir + file, 'r', encoding = 'utf-8-sig') as f:
            campfire = int(f.read().decode('utf-8-sig'))
            
            if campfire >= (threshold+interval):
                multiplier = (campfire-1000)/100
                
                for i in range(multiplier):
                    choices.append(file)
    
    choice = random.choice(choices)
    name = choice # choose a random file from within the directory
    
    #for each in choices:
    #    Parent.SendStreamMessage(each)
    
    with open(voteDir + name, 'r') as file: # open the random file
        filedata = int(file.read().decode('utf-8-sig'))
    
    #Parent.SendStreamMessage('Opened name: ' + name)

    if reduceby > filedata: # make sure it has enough logs to reduce by that much
        retVal += 'The questing tendrils of salamander flame pass up ' + name.split('.')[0] + '; It is too small to sate it\'s appetite.'
        
        #Parent.SendStreamMessage('Too small')
    else: # feed
        filedata = filedata - reduceby
        retVal += 'The salamander flame gorges itself on '+ name.split('.')[0] + '\'s log pile, consuming ' + str(reduceby) + ' logs. It is sated for now.'
        
        #Parent.SendStreamMessage('The right size.')
        
        # Write the reduced log count to the file.
        with open(voteDir + name, 'w+') as file:
            file.write(str(filedata))
            
        print('The right size, but smaller')
        
        # read in the campfire
        with open(campfireDir, 'r') as file:
            campfire = int(file.read().decode('utf-8-sig'))
        print(str(campfire))
        campfire = campfire + reduceby
        
        #Parent.SendStreamMessage('Payout interval: ' + payoutInterval)
        #payout = int(payoutBase) + int(campfire / payoutInterval)
        #Parent.SendStreamMessage(payout)
        payout = 2
        print("The growing forest rewards users with " + str(payout))
        
        # write the new campfire value in
        with open(campfireDir, 'w+') as file:
            file.write(str(campfire))
        
        myDict = {}
        #for viewers in Parent.GetViewerList():
            # this controls how much chatters get payed
        #    myDict[viewers] = payout

        #Parent.AddPointsAll(myDict)
        #Parent.SendStreamMessage("The growing forest rewards users with " + payout)
        
        print(retVal)
        
feed(10)