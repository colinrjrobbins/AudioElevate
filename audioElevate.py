#---------------------------------------------------------------------------------
#   Project Name: audioElevate.py
#   Project Start Date: June 3rd, 2019
#   Creator Name: Colin Robbins
#   Company: YRDSB
#
#   Project Purpose: To create a program that will handle incoming information
#                    from a Adafruit Mic and adjust the volume level of the
#                    Adafruit 20W Audio amplifier.
#
#   General Use: To be used in music rooms for announcements.
#
#   Requirements: Microphone takes in sound data, waits 5 seconds and then
#                 adjusts volume to the amplifier accordingly.
#
#   V1.0: In a way, it works correctly but something happened during the
#         V1 code that caused backfire and fried the PI.
#
#   V2.0: Current set of code, should be bulletproof and not blow the speakers/
#         amp/Raspberry Pi. Still under test.
#
#   PINOUTS
#   Microphone              Amplifier
#   SEL - GND Pin           SDA - Pin 3
#   LRCL - Pin 35           SCL - Pin 5
#   DOUT - Pin 38           Vi2c - Pin 1 (3.3V)
#   BCLK - Pin 12           GND - GND Pin
#   GND - GND Pin
#   3V - Pin 1
#
#                   !!! ----- WARNINGS FOR PINOUT ----- !!!
#       I believe the mistake for V1.0 was the initial connection of the 3.3V
#       to the VDD pin on the amplifier which caused the voltage into the amp
#       12V to cause the trace to blow off.
#------------------------------------------------------------------------------

#IMPORTS
# General Raspberry Pi Import
import RPi.GPIO as GPIO

# Imports for PyAudio and Microphone
import audioop
import pyaudio
import time
import wave

# Imports for the Amplifier Board
import board
import busio
import adafruit_max9744

# General System imports
import sys
import os

# Imports for Added Log function
import datetime as datetime

#FUNCTION - calculations
#Purpose: Used to take incoming .wav file data and convert it
#         into a valid readable value to identify max/min
def calculations(gatheredData):
    # take in the gathered data and convert it to an RMS value
    dataAverage = audioop.rms(gatheredData, 1)
    return dataAverage

#FUNCTION - ampVolume
#Purpose: To adjust the volume and increase at a progressive rate
#         so as to not shock the people in the room, and after 30
#         seconds to lower it back down to half volume.
def ampVolume(amp, defaultVol, levelHigh, maxVol, minVol, timeHold):
    # preset the amp volume to default volume
    amp.volume = defaultVol
    
    # wait 5 seconds before increasing the volume.
    time.sleep(5)

    # increase the volume progressively to avoid damage to the speakers.
    for x in range(minVol, maxVol):
        time.sleep(0.5)
        amp.volume_up()
        
    # used to identify that the function was indeed accessed
    print("Volume turned up, holding for "+str(timeHold)+" seconds.")
    for x in range(0,timeHold):
        time.sleep(1)
        print("-",end="")
        
    # hold the volume level for the announcements to be made
    # begin lowering volume range back to the standard 31
    for x in range(minVol,maxVol):
        time.sleep(0.5)
        amp.volume_down()

    # confirm the set is actually at the default volume
    amp.volume = defaultVol
    
def createModLog(rmsLevel):
    #FUNCTION VARIABLES
    now = datetime.datetime.now()
    count = 0

    # check to see if a log file exists already
    if os.path.isfile('/home/pi/Desktop/log.txt'):
        file = open('/home/pi/Desktop/log.txt','a')
    # if it does not exist, create it
    else:
        file = open('/home/pi/Desktop/log.txt','w+')

    # count the lines to avoid overload
    for line in open('/home/pi/Desktop/log.txt','r'): 
        count+=1

    # empty the log file if it has been triggered 300 times.
    if count > 1000:
        open('/home/pi/Desktop/log.txt', 'w').close()
        
    file.write("LOG DATE "+str(now.day)+"/"+str(now.month)+"/"+str(now.year)+"\n")
    file.write("System triggered at "+str(rmsLevel)+" RMS at time: "+ str(now.hour)+":"+str(now.minute)+":"+str(now.second)+".\n")
    

#MAIN CALL SECTION
# basic variables used in counting etc.
count = 0
safetyCount = 0

# variable to loop given functions
RECORDLOOP = 0

# Initialize all variables for the amplifier
try:
    print("Attempting I2C Connection")
    i2c = busio.I2C(board.SCL, board.SDA)
    for x in range(0,30):
        print("-",end="")
    print("Success.")
except:
    print("Failed.")
    exit()

try:
    print("Attempting Connection to the Amplifier")
    amp = adafruit_max9744.MAX9744(i2c)
    # test to see if changes can be made to the amp prior to the system
    # booting up and reading data.
    
    for x in range(0,30):
        print("-",end="")
    amp.volume = 31
    print("Success.")
except:
    print("Failed.")
    exit()

# Gather config.txt input data.
settingHold = []
holdConfig = []

# opening and reading config.txt
file = open('/config.txt','r')

# read all data from the file
for lines in file:
    holdConfig.append(lines)

print("\n-----------------------\n    CONFIG.TXT INFO\n-----------------------\n")

# gathering default volume level
try:
    settingHold = holdConfig[1].split()
    defaultVol = int(settingHold[2])
    print("Default Volume = " + str(defaultVol))
    if defaultVol < 0 or defaultVol > 62:
        raise ValueError
except ValueError:
    print ("Not a valid default value option, edit the config.txt to the parameters.")
    exit()

# gathering minimum volume level
try:
    settingHold = holdConfig[2].split()
    minVol = int(settingHold[2])
    print("Min Volume = " + str(minVol))
    if minVol < defaultVol or minVol > 62:
        raise ValueError
except ValueError:
    print ("Not a valid minimum value option, edit the config.txt to the parameters.")
    exit()
    
# gathering maximum volume level
try:
    settingHold = holdConfig[3].split()
    maxVol = int(settingHold[2])
    print("Max Volume = "+ str(maxVol))
    if maxVol < defaultVol or maxVol > 62:
        raise ValueError
except ValueError:
    print ("Not a valid maximum value option, edit the config.txt to the parameters.")
    exit()

# gathering bellSafety timer
try:
    settingHold = holdConfig[6].split()
    bellSafety = int(settingHold[2])
    print("Bell Safety = " + str(bellSafety))
    if bellSafety < 10:
        raise ValueError
except ValueError:
    print ("Not a valid bell safety value option, edit the config.txt to the parameters.")
    exit()

# gathering sensativity level
try:
    settingHold = holdConfig[9].split()
    sensativity = int(settingHold[4])
    print("Sensativity Range = " + str(sensativity))
    if sensativity < 1 or sensativity > 10:
        raise ValueError
except ValueError:
    print ("Not a valid sensativity range, edit the config.txt file to the parameters.")
    exit()

triggerRange = 0

if sensativity == 1:
    triggerRange = 75
elif sensativity == 2:
    triggerRange = 73
elif sensativity == 3:
    triggerRange = 71
elif sensativity == 4:
    triggerRange = 69
elif sensativity == 5:
    triggerRange = 67
elif sensativity == 6:
    triggerRange = 65
elif sensativity == 7:
    triggerRange = 63
elif sensativity == 8:
    triggerRange = 61
elif sensativity == 9:
    triggerRange = 59
elif sensativity == 10:
    triggerRange = 50
else:
    print("Not a valid sensativity option.")
    exit()

print("Trigger Range (RMS Value) = " + str(triggerRange))

try:
    settingHold = holdConfig[12].split()
    timeHold = int(settingHold[2])
    print("Time for Max Volume = " + str(timeHold))
    if timeHold < 10:
        raise ValueError
except ValueError:
    print ("Time is too short for an average announcement, 10 seconds minimum. Edit config.txt file appropriately.")
    exit()

print("IF ANY OF THESE DONT WORK OR NEED TO BE EDITED PRESS CTRL+C NOW")
print("Pausing for 30 seconds.")
os.system('sleep 30')

# Initialize all stream formats for PyAudio
CHUNKSIZE = 1024*4
CHANNELS = 1
RATE = 44100
FORMAT = pyaudio.paFloat32

# initiate PyAudio
pyA = pyaudio.PyAudio()
pyA.get_default_input_device_info()
#pyA.get_default_output_device_info()

# create a stream to monitor continuous data
stream = pyA.open(format = FORMAT,
                  channels = CHANNELS,
                  rate = RATE,
                  input = True,
                  output = False,
                  input_device_index = 1,
                  frames_per_buffer = CHUNKSIZE)

# keep the program looping so it is in a constant read state
while RECORDLOOP == 0:
    # to avoid integer overload and causing the program to
    # crash, a 1000 limit is set on the cap.
    if count == 1000:
        count = 0
    # increase count by 1 each time for validation
    count += 1

    # begin the stream to allow for data gathering
    stream.start_stream()

    # read the microphone data and store it in the variable dataHold
    dataHold = stream.read(CHUNKSIZE, exception_on_overflow = False)
    # gather 10 milli-seconds of data before stopping stream
    time.sleep(0.1)

    stream.stop_stream()
    # send dataHold to the calculations function to turn it into a
    # valid RMS value.
    checkLevel = calculations(dataHold)

    # this is the safety count, making sure that it wont increase volume
    # unnessisarily
    if checkLevel < triggerRange:
        if count > 4:
            safetyCount+= 1
    
    #COMMENT TO HIDE RMS AND UNCOMMENT FOLLING SECTION TO DISPLAY GRAPH
    os.system('clear')
    print("")
    print("RMS Value: " + str(checkLevel),end = "")

    # runs a check to make sure before increase that it follows all
    # requested parameters
    if checkLevel < triggerRange and count > 4 and safetyCount > bellSafety:
        print(" <== ",end="")
        ampVolume(amp, defaultVol, checkLevel, maxVol, minVol, timeHold)
        createModLog(checkLevel)
        # reset safety count
        safetyCount = 0

    #----------------------------------------------------------------------        
    #UNCOMMENT TO DISPLAY VERTICAL GRAPH

    #print("\n")
    #for x in range(0, int(checkLevel / 2)):
        #print("|",end="")
        #print(str(checkLevel))
    #----------------------------------------------------------------------

# close the stream and terminate the PyAudio application
stream.close()
pyA.terminate()

