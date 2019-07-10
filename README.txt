Welcome!

SIMPLE SETUP

1. Copy to desktop in a folder called "AudioProject"
    Files REQUIRED TO BE COPIED
        -audioElevate.py
        -config.txt
        -setup.sh

2. Open terminal.
    -Navigate to the AudioProject folder on the desktop.
        cd /home/pi/Desktop/AudioProject
    -Allow to make setup.sh executable.
        sudo chmod 755 setup.sh
    -Run setup.sh
        sudo ./setup.sh

3. Wait for the system to reboot and assuming everything is plugged in correctly
   the program will start on its own at boot time.

-----------------------------------------------------------------

CHANGING SETTINGS

If any settings need to be changed the code is pre-set to adjust based on the
'config.txt' file which will be located on the desktop. Change any settings
that need to be edited in there, note that if accessing VIA SSH connection the 
config.txt file is located in the root folder (/) and will have to be edited there. 
The desktop just contains a sudo link that will open a leafpad for anyone running 
Desktop mode (HDMI Link or VNC).

DEFAULT_VOLUME - this is the volume that will be returned to, almost the same
         as minimum volume but it is used as a reset method.
    Range  - (0-62) is based on the RMS values that will be read from the MIC
MIN_VOLUME     - this is the minimum volume used for any ranges that are used.
    Range  - (62-default) meaning that it cant be lower then the default range.
MAX_VOLUME     - this is the volume that will be escalated to if a high enough
         ambient volume level is achieved.
    Range  - (default-62) meaning that it cant be lower then the default range.
BELL_LENGTH_SAFETY - this is how many cycles the system will go through, to account
             for the ever changing bells in each school.
    Range       - (MINIMUM 10 = 5 seconds)
SENSITIVITY    - this is how sensitive the mic is to alerting the system to increase
         volume.
    Range  - (1-10) 1 being incredibly sensative and 10 being dull
MAX_VOL_HOLD   - this is the length of time the maximum volume will be held for.
    Range  - (VALUE>10) because usually announcements are min 10 seconds.
           - DEFAULT VALUE (30 seconds)

-----------------------------------------------------------------

RESTARTING THE PROGRAM WITHOUT REBOOT

FOR HDMI LINK / VNC LINK
Once the setup.sh file is run there should be a program created called "Start audioElevate"
on the desktop and that can be run to restart the program after configurations have been changed.

FOR SSH
If linked via SSH you will have to start the program in a virtual environment so that when you
close your SSH connection it will continue to run. Screen is automatically installed after the
setup.sh file is run.

Steps:
1. If required edit the config.txt document in the root folder (/)
    Navigate to it by running:
        cd /
    Then edit by:
        sudo nano config.txt
    Make your required changes then:
        CTRL+X, Y then Enter

2. If restarting the program from SSH navigate to the desktop.
    Navigate to desktop:
        cd ~/Desktop
    Run screen with Python and AudioElevate
        screen sudo python3 forceStart.py
Once in screen it will be running automatically, if an error occurs it means that a program is already running using the same port, that needs to be killed first, check step 3 in that case.
    Once in screen mode to exit without closing the running program:
        Press CTRL+A then D
    At this point you are okay to exit SSH and it will be running.

3. Killing a preexisting program running in screen or on desktop.
    SCREEN KILL
If screen is running from a past SSH connection, type "screen -list" to see if any processes are running. If there are you can open them by typing "screen -r (screen name in list)" then once in using CTRL+C to
stop the program, if your not automatically ejected from the screen view can press CTRL+D to close the screen.

    DESKTOP PRE RUNNING KILL
Run the command "ps aux | grep python3" and there should be 3+ running processes, on the far left there is an id number (usually #####). Find the one that is "python3 audioElevate.py" or "python3 forceStart.py" and run the command "kill #####". That will immediately terminate the program and it can then be restarted.

-----------------------------------------------------------------

TROUBLESHOOTING
If the program fails to open on boot:
    Open Terminal
        -Navigate to desktop:
            cd /home/pi/Desktop
        -Run the program via terminal to view error code:
            sudo python3 audioElevate.py
        MOST LIKELY ERRORS:
            -Amplifier not found: Check the power to the amplifier.
            -IOERROR: Input Default Device Not Found:
Highly unlikely to be an error but check /etc/asound.conf and make sure that this is in:
                                  
                    pcm.!default{
                        type hw card 0
                    }
                    ctl.!default{
                        type hw card 0
                    }
                           
If setup.sh fails:
    It has been tested quite a bit but could be a few issues.
        1. Check to make sure the system time did indeed update.
        2. Make sure internet connection is available.
        3. Make sure setup.sh has full executable access (chmod 755 setup.sh)
 4. If using VNC to run install try switching to SSH or vice versa,     should install fine in both but with SSH you can see the error codes.
           Then try running where it failed in portions. (HIGHLY UNLIKELY TO HAPPEN)
