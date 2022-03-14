# -*- coding: utf-8 -*-
""" DESCRIPTION:
The following is the structure of the EEG experiment:
    - Welcome Text
    - Instructions
    - Approximately 10 minutes worth of trials
    - Debriefing and goodbye text

Each trial is structured in the following way:
    - Fixation cross
    - Colour prime, spatial prime or no prime (0.005 seconds)
    - Fixation cross
    - Coloured frame task

In the coloured frame task participants have to press 'a' if the colour of the frame is corresponding to the colour of the circle on the left, 
or 'l' if the colour corresponds to the colour of the circle on the right.

The script lasts approximately 10 minutes and has 120 number of trials.

/Laura Paaby, Niels Krogsgaard, Olivia Elst, Sara Krejberg & Sigurd Sørensen, 2022  (with some of the code adapted from Jonas LindeLoev:
    https://github.com/lindeloev/psychopy-course/blob/master/ppc_template.py)

Structure:
    SET VARIABLES
    GET PARTICIPANT INFO USING GUI
    SPECIFY TIMING AND MONITOR
    STIMULI
    OUTPUT
    FUNCTIONS FOR EXPERIMENTAL LOOP
    DISPLAY INTRO TEXT AND AWAIT SCANNER TRIGGER
    CALL FUNCTION RUNNING THE EXPERIMENTAL LOOP

"""

# Import the modules that we need in this script
from __future__ import division
from psychopy import core, visual, event, gui, monitors, event
from random import sample
import pandas as pd
#Import local scripts
import ppc
#from triggers import setParallelData
import random


"""
SET VARIABLES
"""
# Monitor parameters
MON_DISTANCE = 60  # Distance between subject's eyes and monitor
MON_WIDTH = 20  # Width of your monitor in cm
MON_SIZE = [1200, 1000]  # Pixel-dimensions of your monitor
FRAME_RATE = 60 # Hz  [120]
SAVE_FOLDER = 'tobe_data'  # Log is saved to this folder. The folder is created if it does not exist.
#RUNS = 3 # Number of sessions to loop over (useful for EEG experiment)


"""
GET PARTICIPANT INFO USING GUI
"""
# Intro-dialogue. Get subject-id and other variables.
# Save input variables in "V" dictionary (V for "variables")
V= {'ID':'','gender':['male','female'],'age':''}
if not gui.DlgFromDict(V, order=['ID', 'age','gender']).OK: # dialog box; order is a list of keys
    core.quit()

"""
SPECIFY TIMING AND MONITOR
"""

# Clock and timer
clock = core.Clock()  # A clock wich will be used throughout the experiment to time events on a trial-per-trial basis (stimuli and reaction times).

# Create psychopy window
my_monitor = monitors.Monitor('testMonitor', width=MON_WIDTH, distance=MON_DISTANCE)  # Create monitor object from the variables above. This is needed to control size of stimuli in degrees.
my_monitor.setSizePix(MON_SIZE)
win = visual.Window(monitor=my_monitor, units='deg', fullscr=True, allowGUI=False, color='Gray')  # Initiate psychopy Window as the object "win", using the myMon object from last line. Use degree as units!

#Prepare Fixation cross
stim_fix = visual.TextStim(win, '+')#, height=FIX_HEIGHT)  # Fixation cross is just the character "+". Units are inherited from Window when not explicitly specified.
myGrat1 = visual.GratingStim(win, pos=(-7.5,4), units = 'deg', tex='sin', mask='circle', size = 2, sf = 3)
myGrat2 = visual.GratingStim(win, pos=(7.5,4), units = 'deg', tex='sin', mask='circle', size = 2, sf = 3)

"""
STIMULI
"""
#EXPERIMANTAL DETAILS

####---------ALL PRIMING FUNCTION---------------####
#A function to be used for all priming objects, including the "No prime object" which will just be a fixation cross of the same length as the primes
def prime_func(string, window):
    if string == 'blue':
        #prime = visual.Rect(window, units = "deg", size = 10, lineWidth=1.5, fillColor='Navy', lineColor = None)
        prime = visual.TextStim(window, '+', color='Navy', bold = True)
        prime.win = window
    elif string == 'red':
        #prime = visual.Rect(window, units = "deg", size = 10, lineWidth=1.5, fillColor = 'DarkRed', lineColor = None)
        prime = visual.TextStim(window, '+', color='DarkRed', bold = True)
        prime.win = window
    elif string == 'left':
        prime = visual.Circle(window, radius=0.06, units = 'deg', edges=50, lineWidth=1.5, fillColor = 'DimGray', pos=(-7.5,4), fillColorSpace=None,  size=20, lineColor = None)
        prime.win = window 
    elif string == 'right':
        prime = visual.Circle(window, radius=0.06, units = 'deg', edges=50, lineWidth=1.5, fillColor = 'DimGray', pos=(7.5,4), fillColorSpace=None,  size=20, lineColor = None)
        prime.win = window
    else:
        prime = visual.TextStim(window, '+')
    return prime

#Variables used for controlling the time of the different elements in a trial
#dealys is used to vary the time of the fixation cross between prime and task. The number is used for number of frames, so 90 frames / 60 Hz = 1.5 seconds
#delays=(90,168)# different time intervals between stimuli mean 4.1 sec x 60 hz refresh rate =246, in order to make less predictable and increase power.
delays=(40,118)

#dur_prime is the number of frames that the prime will be shown, which will be 3 frames corresponding to 0.050 seconds
dur_prime=int(0.134*FRAME_RATE) # duration in seconds multiplied by 60 Hz and made into integer
#dur_prime=int(0.15*FRAME_RATE) # this duration is used for testing the experimental setup, but it should be commented out for the actual experiment

#dur_task is the number of frames that the task will be shown, which will be 18 frames corresponding to 0.3 seconds
dur_task=int(1.5*FRAME_RATE) # duration in seconds multiplied by 60 Hz and made into integer


# Visual dot for check of stimulus in EEG (commented out due to fear of an additional priming effect)
#stimDot = visual.GratingStim(win, size=.5, tex=None, pos=(7, -6),
#                             color=1, mask='circle', autoLog=False)

####---------MAKING TRIAL LIST FUNCTION---------------####
def make_trial_list():
    random.seed(1)
    
    #Making the shuffled list of trials (120 trials in total)
    left_list = 2*["left"]
    right_list = 2*["right"]
    blue_list = 2*["blue"]
    red_list = 2*["red"]
    none_list = 4*["none"]
    trial_list_1 = left_list + right_list + blue_list + red_list + none_list
    random.shuffle(trial_list_1)

    #Creating a list of tasks to use, when there is no prime. This is done to make sure that there will be an equal number of each task
    none_task_list = 2*[1] + 2*[2]
    random.shuffle(none_task_list)
    
# Factorial design
    trial_list_2 = []
    counter = 0
    for i, trial in enumerate(trial_list_1): # images
        # define triggers and image stimulus based on word
        if trial == 'blue':
            prime = 'blue' #priming thing
            task = 1
            TRIG_P=11 #trigger code prime
            TRIG_T=21 #trigger code task
            TRIG_BEFORE=31
        elif trial == 'red':
            prime = 'red' #priming thing
            task = 2
            TRIG_P=12
            TRIG_T=22
            TRIG_BEFORE=32
        elif trial == 'left':
            prime = 'left' #priming thing
            task = 1
            TRIG_P=13
            TRIG_T=23
            TRIG_BEFORE=33
        elif trial == 'right':
            prime = 'right' #priming thing
            task = 2
            TRIG_P=14
            TRIG_T=24
            TRIG_BEFORE=34
        else:
            prime = 'no_prime' #no priming thing
            TRIG_P=15
            task = none_task_list[counter]
            if task==1:
                TRIG_T=41
                TRIG_BEFORE=51
                counter += 1
            else:
                TRIG_T=42
                TRIG_BEFORE=52
                counter += 1
        delaysR= sample(delays,2)
        # Add a dictionary for every trial
        trial_list_2 += [{
            'ID': V['ID'],
            'age': V['age'],
            'gender': V['gender'],
            'trial_type':trial,
            'task_type':task,
            'prime_trigger':TRIG_P,
            'pause_trigger':TRIG_BEFORE,
            'pause_trigger_t':'',
            'prime':prime,
            'task_trigger':TRIG_T,
            'onset_prime':'' ,# a place to note onsets
            'offset_prime': '',
            'duration_measured_prime':'',
            'onset_task':'' ,# a place to note onsets
            'offset_task': '',
            'duration_measured_task':'',
            'duration_frames_prime': dur_prime,
            'duration_frames_task': dur_task,
            'delay_frames_before': delaysR[0],
            'delay_frames_after': delaysR[1],
            'response': '',
            'key_t':'',
            'rt': '',
            'correct_resp': ''
        }]
        
    # Add trial numbers and return
    for i, trial in enumerate(trial_list_2):
        trial['trial_number'] = i + 1  # start at 1 instead of 0
    
    return trial_list_2

####---------TASK_FUNCTION--------------####
def circle_frame(spot, window): 
    if spot == 1:
        col_frame = visual.Rect(window, size = 10000, lineWidth=1.5, fillColor='Navy')
        black_frame = visual.Rect(window,width=22, height=13.9, units='deg', lineWidth=1.5, lineColor=None, lineColorSpace=None, fillColor='Gray', fillColorSpace=None, pos=(0, 0))
        left_circle = visual.Circle(window, radius=0.06, units = 'deg', edges=50, lineWidth=1.5, fillColor='Navy', pos=(-7.5,4), fillColorSpace=None,  size=20, lineColor = None)
        right_circle = visual.Circle(window, radius=0.06, units = 'deg', edges=50, lineWidth=1.5, fillColor='DarkRed', pos=(7.5,4), fillColorSpace=None,  size=20, lineColor = None)
        right_circle.win = window
        left_circle.win = window
    else:
        col_frame = visual.Rect(window, size = 10000, lineWidth=1.5, fillColor='DarkRed')
        black_frame = visual.Rect(window,width=22, height=13.9, units='deg', lineWidth=1.5, lineColor=None, lineColorSpace=None, fillColor='Gray', fillColorSpace=None, pos=(0, 0))
        left_circle = visual.Circle(window, radius=0.06, units = 'deg', edges=50, lineWidth=1.5, fillColor='Navy', pos=(-7.5,4), fillColorSpace=None,  size=20, lineColor = None)
        right_circle = visual.Circle(window, radius=0.06, units = 'deg', edges=50, lineWidth=1.5, fillColor='DarkRed', pos=(7.5,4), fillColorSpace=None,  size=20, lineColor = None)
        right_circle.win = window
        left_circle.win = window
    return (col_frame, black_frame, right_circle, left_circle)

""" OUTPUT """

#KEYS
KEYS_QUIT = ['escape','q']  # Keys that quits the experiment
KEYS_trigger=['t'] # The MR scanner sends a "t" to notify that it is starting. Do we still need this?
KEYS_target = dict(left=['a'],
                  right=['l'])

""" FUNCTIONS FOR EXPERIMENTAL LOOP"""

####---------EXPERIMENTAL LOOP FUNCTION--------------####
def run_condition(exp_start):
    """
    Runs a block of trials. This is the presentation of stimuli,
    collection of responses and saving the trial
    """
    #Set EEG trigger in off state
    pullTriggerDown = False
    # Loop over trials
    for trial in make_trial_list():
        #event.clearEvents(eventType='keyboard')# clear keyboard input to make sure that no responses are logged that do not belong to stimulus
        
        #prepare prime
        stim_prime = prime_func(trial['prime'], win)
        time_flip_prime=core.monotonicClock.getTime() #onset of prime
        for frame in range(trial['duration_frames_prime']):
            stim_prime.draw()
            #stimDot.draw()
            if frame==1:
                #win.callOnFlip(setParallelData, trial['prime_trigger'])  # pull trigger up
                pullTriggerDown = True
            win.flip()
            if pullTriggerDown:
                #win.callOnFlip(setParallelData, 0)
                pullTriggerDown = False
        
        # Display fixation cross
        offset_prime = core.monotonicClock.getTime()  # offset of stimulus
        for frame in range(trial['delay_frames_before']):
            stim_fix.draw()
            myGrat1.draw()
            myGrat2.draw()

            # Send pause trigger 1 sec (500 ms?) after offset
            #if frame  == 60:
            if frame  == 30:
                #win.callOnFlip(setParallelData, trial['pause_trigger'])  # pull trigger up
                pullTriggerDown = True
                pause_trigger_t = core.monotonicClock.getTime()  # offset of stimulus
            win.flip()

            if pullTriggerDown:
                #win.callOnFlip(setParallelData, 0)
                pullTriggerDown = False

        # Prepare task
        stim_task = circle_frame(trial['task_type'], win)
        no_key_yet = 0

        # Display image and monitor time
        time_flip_task=core.monotonicClock.getTime() #onset of stimulus
        event.clearEvents(eventType='keyboard')# clear keyboard input to make sure that no responses are logged that do not belong to stimulus
        for frame in range(trial['duration_frames_task']):
            #stimDot.draw()
            stim_task[0].draw()
            stim_task[1].draw()
            stim_task[2].draw()
            stim_task[3].draw()
            
            if frame==1:
                #win.callOnFlip(setParallelData, trial['task_trigger'])  # pull trigger up
                pullTriggerDown = True
            if frame>1 and no_key_yet == 0:
                try:
                    key, time_key = event.getKeys(keyList=('a', 'l', 'escape'), timeStamped=True)[0]  # timestamped according to core.monotonicClock.getTime() at keypress
                except IndexError:  #if no responses were given, the getKeys function produces an IndexError
                    key = 'z'
                if key in KEYS_target['left']:
                    no_key_yet = 1
                    trial['response']=key
                    trial['key_t']=time_key-exp_start
                    trial['rt'] = time_key-time_flip_task
                    if (trial['prime_trigger']==11 or trial['prime_trigger']==13):
#                        if trial['task']==1:
                        trial['correct_resp'] = 1
                        #win.callOnFlip(setParallelData, 111)  # pull trigger up; 100 = correct; X1X = left prime; XX1 left-response
                        pullTriggerDown = True
#                        elif trial['task']==2:
#                            trial['correct_resp'] = 0
#                            win.callOnFlip(setParallelData, 211)  # pull trigger up; 200 = incorrect; X1X =  XX1 left-response
#                            pullTriggerDown = True
                    else: # no prime or right/red prime before
                        if trial['task_type']==1:
                            trial['correct_resp'] = 1
                            #win.callOnFlip(setParallelData, 131)  # pull trigger up; 100 = correct; X3X = no prime; XX1 left-response
                            pullTriggerDown = True
                        elif (trial['task_type']==2 and trial['prime_trigger'] != 15):
                            trial['correct_resp'] = 0
                            #win.callOnFlip(setParallelData, 221)  # pull trigger up; 200 = incorrect; X2X = right prime; XX1 left-response
                            pullTriggerDown = True
                        elif (trial['task_type']==2 and trial['prime_trigger'] == 15):
                            trial['correct_resp'] = 0
                            #win.callOnFlip(setParallelData, 231)  # pull trigger up; 200 = incorrect; X3X = no prime; XX1 left-response
                            pullTriggerDown = True
                elif key in KEYS_target['right']:
                    no_key_yet = 1
                    trial['response']=key
                    trial['key_t']=time_key-exp_start
                    trial['rt'] = time_key-time_flip_task
                    if (trial['prime_trigger']==12 or trial['prime_trigger']==14):
#                        if trial['task']==2:
                        trial['correct_resp'] = 1
                        #win.callOnFlip(setParallelData, 122)  # pull trigger up; 100 = correct; X2X = right prime; XX2 right-response
                        pullTriggerDown = True
#                        elif trial['task']==1:
#                            trial['correct_resp'] = 0
#                            win.callOnFlip(setParallelData, 211)  # pull trigger up; 200 = incorrect; XX1 pos-response
#                            pullTriggerDown = True
                    else: # no prime or left/blue prime before
                        if trial['task_type']==2:
                            trial['correct_resp'] = 1
                            #win.callOnFlip(setParallelData, 132)  # pull trigger up; 100 = correct; X3X = no prime XX2 right-response
                            pullTriggerDown = True
                        elif (trial['task_type']==1 and trial['prime_trigger'] != 15):
                            trial['correct_resp'] = 0
                            #win.callOnFlip(setParallelData, 212)  # pull trigger up; 200 = incorrect; X1X = left prime; XX2 right-response
                            pullTriggerDown = True
                        elif (trial['task_type']==1 and trial['prime_trigger'] == 15):
                            trial['correct_resp'] = 0
                            #win.callOnFlip(setParallelData, 232)  # pull trigger up; 200 = incorrect; X3X = no prime; XX2 right-response
                            pullTriggerDown = True
                if key in KEYS_QUIT:  # Look at first reponse [0]. Quit everything if quit-key was pressed
    #                writer.flush()
    #                print('just flushed!')
                    win.close()
                    core.quit()
            win.flip()
            if pullTriggerDown:
                #win.callOnFlip(setParallelData, 0)
                pullTriggerDown = False

        # Display fixation cross
        offset_task = core.monotonicClock.getTime()  # offset of stimulus
        for frame in range(trial['delay_frames_after']):
            stim_fix.draw()
            myGrat1.draw()
            myGrat2.draw()
            if no_key_yet == 0:
                try:
                    key, time_key = event.getKeys(keyList=('a', 'l', 'escape'), timeStamped=True)[0]  # timestamped according to core.monotonicClock.getTime() at keypress
                except IndexError:  #if no responses were given, the getKeys function produces an IndexError
                    key = 'z'
                    if frame == trial['delay_frames_after']:
                        # NB! We only log "no response" if no keys were pressed in this section - not the previous section
                        trial['response']=''
                        trial['key_t']=''
                        trial['rt']=''
                if key in KEYS_target['left']:
                    no_key_yet = 1
                    trial['response']=key
                    trial['key_t']=time_key-exp_start
                    trial['rt'] = time_key-time_flip_task
                    if (trial['prime_trigger']==11 or trial['prime_trigger']==13):
#                        if trial['task']==1:
                        trial['correct_resp'] = 1
                        #win.callOnFlip(setParallelData, 111)  # pull trigger up; 100 = correct; X1X = left prime; XX1 left-response
                        pullTriggerDown = True
#                        elif trial['task']==2:
#                            trial['correct_resp'] = 0
#                            win.callOnFlip(setParallelData, 211)  # pull trigger up; 200 = incorrect; X1X =  XX1 left-response
#                            pullTriggerDown = True
                    else: # no prime or right/red prime before
                        if trial['task_type']==1:
                            trial['correct_resp'] = 1
                            #win.callOnFlip(setParallelData, 131)  # pull trigger up; 100 = correct; X3X = no prime; XX1 left-response
                            pullTriggerDown = True
                        elif (trial['task_type']==2 and trial['prime_trigger'] != 15):
                            trial['correct_resp'] = 0
                            #win.callOnFlip(setParallelData, 221)  # pull trigger up; 200 = incorrect; X2X = right prime; XX1 left-response
                            pullTriggerDown = True
                        elif (trial['task_type']==2 and trial['prime_trigger'] == 15):
                            trial['correct_resp'] = 0
                            #win.callOnFlip(setParallelData, 231)  # pull trigger up; 200 = incorrect; X3X = no prime; XX1 left-response
                            pullTriggerDown = True
                elif key in KEYS_target['right']:
                    no_key_yet = 1
                    trial['response']=key
                    trial['key_t']=time_key-exp_start
                    trial['rt'] = time_key-time_flip_task
                    if (trial['prime_trigger']==12 or trial['prime_trigger']==14):
#                        if trial['task']==2:
                        trial['correct_resp'] = 1
                        #win.callOnFlip(setParallelData, 122)  # pull trigger up; 100 = correct; X2X = right prime; XX2 right-response
                        pullTriggerDown = True
#                        elif trial['task']==1:
#                            trial['correct_resp'] = 0
#                            win.callOnFlip(setParallelData, 211)  # pull trigger up; 200 = incorrect; XX1 pos-response
#                            pullTriggerDown = True
                    else: # no prime or left/blue prime before
                        if trial['task_type']==2:
                            trial['correct_resp'] = 1
                            #win.callOnFlip(setParallelData, 132)  # pull trigger up; 100 = correct; X3X = no prime XX2 right-response
                            pullTriggerDown = True
                        elif (trial['task_type']==1 and trial['prime_trigger'] != 15):
                            trial['correct_resp'] = 0
                            #win.callOnFlip(setParallelData, 212)  # pull trigger up; 200 = incorrect; X1X = left prime; XX2 right-response
                            pullTriggerDown = True
                        elif (trial['task_type']==1 and trial['prime_trigger'] == 15):
                            trial['correct_resp'] = 0
                            #win.callOnFlip(setParallelData, 232)  # pull trigger up; 200 = incorrect; X3X = no prime; XX2 right-response
                            pullTriggerDown = True
                if key in KEYS_QUIT:  # Look at first reponse [0]. Quit everything if quit-key was pressed
        #                writer.flush()
        #                print('just flushed!')
                    win.close()
                    core.quit()
            win.flip()
            if pullTriggerDown:
                #win.callOnFlip(setParallelData, 0)
                pullTriggerDown = False
            # Get actual duration at offset

        #Log values
        trial['onset_prime']=time_flip_prime-exp_start
        trial['offset_prime'] = offset_prime-exp_start
        trial['duration_measured_prime']=offset_prime-time_flip_prime
                #Log values
        trial['onset_task']=time_flip_task-exp_start
        trial['offset_task'] = offset_task-exp_start
        trial['duration_measured_task']=offset_task-time_flip_task
        trial['pause_trigger_t']=pause_trigger_t-exp_start

        # Save trials to csv file
        writer.write(trial)

"""
DISPLAY INTRO TEXT AND AWAIT SCANNER TRIGGER
"""
textPos= [0, 0]                            # Position of question message
textHeight=0.6 # height in degrees
introText1=[u'In this experiment you will solve a simple task of matching the colour of the frame with the correct circle', # some blanks here to create line shifts

            u'Primes can be used to predict colours',

            u'Press "a" key with INDEX finger on left hand if blue',

            u'Press "l" key with INDEX finger on right hand if red',

            u'',

            u'Press "t" to start the experiment']

# Loop over lines in Intro Text1
ypos=4
xpos=0
for intro in introText1:
    ypos=ypos-1
    introText1 = visual.TextStim(win=win, text=intro, pos=[xpos,ypos], height=textHeight, alignHoriz='center')
    introText1.draw()
win.flip()          # Show the stimuli on next monitor update and ...

#Wait for scanner trigger "t" to continue
event.waitKeys(keyList=KEYS_trigger)
exp_start=core.monotonicClock.getTime()

#1 sec of fixation cross before we start
for frame in range(1*FRAME_RATE):
     stim_fix.draw()
     myGrat1.draw()
     myGrat2.draw()
     win.flip()

#""" CALL FUNCTION RUNNING THE EXPERIMENTAL LOOP"""
   # Prepare a csv log-file using the ppc3 script
#ID_sess=  str(V['ID']) + '_sess_' + str(V['session'])
ID_sess=  str(V['ID'])
writer = ppc.csv_writer(ID_sess, folder=SAVE_FOLDER)  # writer.write(trial) will write individual trials with low latency

   # Run the actual session
run_condition(exp_start)

#Use flush function to make sure that the log file has been updated
#writer.flush()
#Close the experimental window
win.close()
core.quit()
