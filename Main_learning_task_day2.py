#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Jun 03 08:35:37 2025
Main file of the LMapRMax learning experiment.
2025-10-08: 
    X Made checks to ensure a distribution of 75-85% 0.8 transitions for each block. 
    X Included reading grammar version from a configuration file for each subject. 
@author: gdf724
"""

#%% Import necessary packages.
import os
from psychopy import gui
from psychopy.visual import Window, TextStim, ImageStim, SimpleImageStim
from psychopy import event, core, monitors, prefs
prefs.general['audioLib'] = ['PTB']
from psychopy.sound import Sound

import numpy as np
import Grammar_stimuli as gstim
from datetime import date
import pandas as pd
import random

#%% Get subject dialog box
def subject_dialog(title_text):
    subj=''
    exp_info = {'Learning task\nsubject': ''}  
    loopDiag=True
    while loopDiag:
        dlg = gui.DlgFromDict(exp_info,title=title_text)
        
        if not dlg.OK:
            controlled_e()
        else:
            subj=exp_info['Learning task\nsubject']
            if subj!='':
                loopDiag=False  
    return subj

#%% Remove problematic variables and quit 
def controlled_e():
    if 'kb' in globals():
        global kb
        del(kb)
    if 'keys' in globals():
        global keys
        del(keys)
    if 'win' in globals():
        global win
        win.close()
        del(win)
    if 'loopDiag' in globals():
        global loopDiag
        del(loopDiag)
    if 'clock' in globals():
        global clock
        del(clock)
    core.quit()

#%% Make a save folder with date stamp
def make_savefolder(save_path, subj):
    savefolder = os.path.join(save_path,subj,subj+'_'+date.today().isoformat()+'_learning')
    if os.path.exists(savefolder):
        savefolder = "error"
    else:
        os.makedirs(savefolder)
    return savefolder

#%% Get relative 0.8 transitions form 8020 grammar
def get_rel_08(block_stimuli,grammar):
    trialcounter=0
    count_08=0
    for itr in range(1,len(block_stimuli)):
        if block_stimuli[itr] != 'pause':
            trialcounter = trialcounter+1
            if block_stimuli[itr-1] != 'pause':
                if grammar[block_stimuli[itr]][block_stimuli[itr-1]]==0.8:
                    count_08=count_08+1
            
    
    return count_08/trialcounter

#%% Define the hardware
cedrus_RB840 = False #Whether to use Cedrus or keyboard. (affects which buttons to use.)
mon = monitors.Monitor('SonyG55')
mon.setSizePix((2560,1600))
winsize=(1080,720)

sound_files = ["fi.wav", "pu.wav", "le.wav", "ka.wav", "ty.wav", "jo.wav"]

#Define the sound-key mappings here. 
if cedrus_RB840:
    allowed_keys = ['a', 'b', 'c', 'f', 'g', 'h']
    continue_keys = ['d', 'e']
    continue_key_name = "one of the bottom keys"
    sound_paths = {
        "a": sound_files[0],
        "b": sound_files[1],
        "c": sound_files[2],
        "f": sound_files[3],
        "g": sound_files[4],
        "h": sound_files[5]
        }
else:
    allowed_keys = ['s', 'd', 'f', 'j', 'k', 'l']
    continue_keys = ['space']
    continue_key_name = "space bar"
    sound_paths = {
        "s": sound_files[0],
        "d": sound_files[1],
        "f": sound_files[2],
        "j": sound_files[3],
        "k": sound_files[4],
        "l": sound_files[5]
        }

#%% Define paths
settings_path = '/Users/gdf724/Data/LMapRMax/Settingsfiles'
save_path = '/Users/gdf724/Data/LMapRMax/Piloting' 
audstim_path = '/Users/gdf724/Code/LMapRMax_paradigm/AudioStimuli/250ms'


#%% Gather subject information and make sure that the subject name is set and make a save folder.
loop_subjDial=True
title_text = "Write subject ID"
while loop_subjDial:
    subj = subject_dialog(title_text)
    savefolder = make_savefolder(save_path, subj)
    if savefolder == "" or savefolder == "error":
        title_text = "Subject ID already tested today!"
    elif not os.path.exists(os.path.join(settings_path,subj+'.csv')):
        title_text= "No settings file specified for Subject ID."
    else:
        loop_subjDial = False
    
#%% Define the paradigm. 
#SRTT
nbrOfFamiliarizations = 28 #Number of stimuli in the familiarization step
nbrOfGuidedTrials = 5 #Number of trials the guide stays on at the start of the trial.
trials_in_accuracy_average = 10 #Number of trials that go into the running average accuracy. 
guide_accuracy_threshold = 0.7 #Average accuracy 
nbrOfGuidePeek = 2 #Number of trials that the guide stays on. 

#Also include 2 erroneous elements per sequence in blocks 9-13
blockstart_err = 8
nbrOfErrorblocks = 4
trial_pause = 0.05 #Pause between trials to make the mapping more clear.
nbrOfBlocks = 15 
lengthOfSequences = 8 #Number of presses per sequence.
sequencesPerBlock = 5
pause_block_length = 3 #Pause between blocks length in seconds. 
pause_trial_length = 0.5 #Pause length for pause trials in seconds.
nbrOfLongBreaks = 1 #Number of longer breaks that are gone through by button press. 
grammar_type = '8020' #'8020', '5050', or 'random'
settings_file = pd.read_csv(os.path.join(settings_path,subj+'.csv'))
grammar_version = settings_file["grammar_version"][0]
nbrOfStartKeys = 2 #Can be 2 or 1 and alternates between [L3] and [L3,R1].
grammar=gstim.getGrammar(grammar_type, cedrus_RB840, grammar_version)

#%% Save settings
with open(os.path.join(savefolder,'settings.txt'),'w') as f:
    f.write('subject:'+str(subj)+'\n')
    f.write('cedrus_RB840:'+str(cedrus_RB840)+'\n')
    f.write('trial_pause'+str(trial_pause)+'\n')
    f.write('nbrOfBlocks:'+str(nbrOfBlocks)+'\n')
    f.write('lengthOfSequences:'+str(lengthOfSequences)+'\n')
    f.write('sequencesPerBlock:'+str(sequencesPerBlock)+'\n')
    f.write('pause_block_length:'+str(pause_block_length)+'\n')
    f.write('pause_trial_length:'+str(pause_trial_length)+'\n')
    f.write('nbrOfLongBreaks:'+str(nbrOfLongBreaks)+'\n')
    f.write('grammar_type:'+str(grammar_type)+'\n')
    f.write('grammar_version:'+str(grammar_version)+'\n')
    f.write('nbrOfStartKeys:'+str(nbrOfStartKeys)+'\n')
    f.write('nbrOfFamiliarizations:'+str(nbrOfFamiliarizations)+'\n')
    f.write('nbrOfGuidedTrials:'+str(nbrOfGuidedTrials)+'\n')
    f.write('trials_in_accuracy_average:'+str(trials_in_accuracy_average)+'\n')    
    f.write('guide_accuracy_threshold:'+str(guide_accuracy_threshold)+'\n')
    f.write('nbrOfGuidePeek:'+str(nbrOfGuidePeek)+'\n')


#%% Initialize Window and make welcome screen.
welcome_string = "Welcome to the experiment!\nPut your fingers on the target keys on the keyboard.\nPlease press the indicated keys as quickly as possible.\nAre you ready to start?\nPress "+continue_key_name+" to continue"
win = Window(size=winsize, monitor=mon, fullscr=False, screen=0, units="norm", pos=[0,0], color=[-.69,-.69,-.69], colorSpace = 'rgb')
welcome_text = TextStim(win, welcome_string, pos=(0.0, 0.8), color=(1, 1, 1), units = "norm", height = 0.05, wrapWidth=0.8)
instr_image_stim = ImageStim(win, image='Instructions_figure.jpeg')
instr_image_stim.draw()
welcome_text.draw()
win.flip()
welcome_text = TextStim(win, welcome_string, pos=(0.0, 0.8), color=(1, 1, 1), units = "norm", height = 0.05, wrapWidth=0.8)
instr_image_stim = ImageStim(win, image='Instructions_figure.jpeg')
instr_image_stim.draw()
welcome_text.draw()
win.flip()
#Wait until subject has pressed enter or escape
#kb = Keyboard()
response = event.waitKeys(keyList=continue_keys+['escape'], clearEvents=True)
if response[-1] in continue_keys: 
    pause_text = TextStim(win, "Wait", color=(1, 1, 1), colorSpace='rgb')
    pause_text.draw()
    win.flip()
    pause_text = TextStim(win, "Wait", color=(1, 1, 1), colorSpace='rgb')
    pause_text.draw()
    win.flip()
if 'escape' in response:
    controlled_e()

tmp_sound = Sound(os.path.join(audstim_path,'silence.wav'))
tmp_sound.play()

clock = core.Clock()


#%%Warm up
#Start with some interactive instructions. E.g. Generate s-d-f-j-k-l. Inform 
#that participants need to be as quick and accurate as possible. 
warmup_timings = []
warmup_responses = []
instr_image_stim = ImageStim(win, image='Instructions_figure.jpeg')
instr_image_stim.draw()
win.flip()
instr_image_stim = ImageStim(win, image='Instructions_figure.jpeg')
instr_image_stim.draw()
win.flip()
for key in allowed_keys:
    #Present correct instruction.
    t_wu_start = clock.getTime()
    tmp_sound_name = sound_paths[key]
    tmp_sound = Sound(os.path.join(audstim_path,tmp_sound_name))
    tmp_sound.play()
    #Collect keypress. Right now only allows presses on the correct 
    response = event.waitKeys(keyList=allowed_keys+['escape'], clearEvents = True)
    if response[-1] in allowed_keys:
        warmup_timings.append(clock.getTime()-t_wu_start)
        warmup_responses.append(response[-1])
        if sound_paths[response[-1]]==tmp_sound_name: 
            feedback_text = TextStim(win, "Correct!", color=(1, 1, 1), pos=(0,0.5), colorSpace='rgb')
            instr_image_stim.draw()
            feedback_text.draw()
            win.flip()
            feedback_text = TextStim(win, "Correct!", color=(1, 1, 1), pos=(0,0.5), colorSpace='rgb')
            instr_image_stim.draw()
            feedback_text.draw()
            win.flip()
        else:
            feedback_text = TextStim(win, "Not correct!", color=(1, 1, 1), pos=(0,0.5), colorSpace='rgb')
            instr_image_stim.draw()
            feedback_text.draw()
            win.flip()
            feedback_text = TextStim(win, "Not correct!", color=(1, 1, 1), pos=(0,0.5), colorSpace='rgb')
            instr_image_stim.draw()
            feedback_text.draw()
            win.flip()
        core.wait(trial_pause)
        continue
    elif response[-1]=='escape':
        controlled_e()

#%%Familiarization step. Random sequences (but no repeats) with feedback
fam_string = "Great job!\nSecond warm up!\nPress the indicated key as quickly as possible.\nPress "+continue_key_name+" to continue"
fam_text = TextStim(win, fam_string, color=(1, 1, 1), colorSpace='rgb')
fam_text.draw()
win.flip()
fam_string = "Great job!\nSecond warm up!\nPress the indicated key as quickly as possible.\nPress "+continue_key_name+" to continue"
fam_text = TextStim(win, fam_string, color=(1, 1, 1), colorSpace='rgb')
fam_text.draw()
win.flip()
#Wait until subject has pressed enter or escape
#kb = Keyboard()
fam_timings = []
fam_responses = []
response = event.waitKeys(keyList=continue_keys+['escape'], clearEvents=True)
if response[-1] in continue_keys: 
    fix_text = TextStim(win, "+", color=(1, 1, 1), colorSpace='rgb')
    fix_text.draw()
    win.flip()
    fix_text = TextStim(win, "+", color=(1, 1, 1), colorSpace='rgb')
    fix_text.draw()
    win.flip()
if 'escape' in response:
    controlled_e()
    
last_stim=''
fix_text = TextStim(win, "+", color=(1, 1, 1), colorSpace='rgb')
mappings_image_stim = ImageStim(win, image='Mappings.jpeg')
mappings_image_stim.draw()
fix_text.draw()
win.flip()
fix_text = TextStim(win, "+", color=(1, 1, 1), colorSpace='rgb')
mappings_image_stim = ImageStim(win, image='Mappings.jpeg')
mappings_image_stim.draw()
fix_text.draw()
win.flip()
for fam_itr in range(nbrOfFamiliarizations):
    tmp_sound_files = [x for x in sound_files if x!=last_stim]
    tmp_sound_name=random.choices(tmp_sound_files)[0]
    last_stim=tmp_sound_name
    tmp_sound = Sound(os.path.join(audstim_path,tmp_sound_name))
    tmp_sound.play()
    response = event.waitKeys(keyList=allowed_keys+['escape'], clearEvents=True)
    if response[-1] in allowed_keys:
        fam_timings.append(clock.getTime()-t_wu_start)
        fam_responses.append(response[-1])
        #Feedback
        if sound_paths[response[-1]]==tmp_sound_name: 
            feedback_text = TextStim(win, "Correct!", color=(1, 1, 1), colorSpace='rgb', pos=(0,-0.3), height=0.2)
            mappings_image_stim.draw()
            feedback_text.draw()
            win.flip()
            feedback_text = TextStim(win, "Correct!", color=(1, 1, 1), colorSpace='rgb', pos=(0,-0.3), height=0.2)
            mappings_image_stim.draw()
            feedback_text.draw()
            win.flip()
        else:
            feedback_text = TextStim(win, "Not correct!", color=(1, 1, 1), colorSpace='rgb', pos=(0,-0.3), height=0.2)
            mappings_image_stim.draw()
            feedback_text.draw()
            win.flip()
            feedback_text = TextStim(win, "Not correct!", color=(1, 1, 1), colorSpace='rgb', pos=(0,-0.3), height=0.2)
            mappings_image_stim.draw()
            feedback_text.draw()
            win.flip()
        core.wait(trial_pause)
        continue
    elif response[-1]=='escape':
        controlled_e()
    

#%%Familiarization step with feedback but no guide.
fam_string = "Great job!\nThird warm up!\nPress the correct key as quickly as possible.\nYou can look at the cheat sheet below the screen but it won't be there when the experiment starts.\nPress "+continue_key_name+" to continue"
fam_text = TextStim(win, fam_string, color=(1, 1, 1), colorSpace='rgb')
fam_text.draw()
win.flip()
fam_string = "Great job!\nThird warm up!\nPress the correct key as quickly as possible.\nYou can look at the cheat sheet below the screen but it won't be there when the experiment starts.\nPress "+continue_key_name+" to continue"
fam_text = TextStim(win, fam_string, color=(1, 1, 1), colorSpace='rgb')
fam_text.draw()
win.flip()
#Wait until subject has pressed enter or escape
#kb = Keyboard()
fam_timings = []
fam_responses = []
response = event.waitKeys(keyList=continue_keys+['escape'], clearEvents=True)
if response[-1] in continue_keys: 
    fix_text = TextStim(win, "+", color=(1, 1, 1), colorSpace='rgb')
    fix_text.draw()
    win.flip()
    fix_text = TextStim(win, "+", color=(1, 1, 1), colorSpace='rgb')
    fix_text.draw()
    win.flip()
if 'escape' in response:
    controlled_e()
    
last_stim=''
fix_text = TextStim(win, "+", color=(1, 1, 1), colorSpace='rgb')
fix_text.draw()
win.flip()
fix_text = TextStim(win, "+", color=(1, 1, 1), colorSpace='rgb')
fix_text.draw()
win.flip()
for fam_itr in range(nbrOfFamiliarizations):
    tmp_sound_files = [x for x in sound_files if x!=last_stim]
    tmp_sound_name=random.choices(tmp_sound_files)[0]
    last_stim=tmp_sound_name
    tmp_sound = Sound(os.path.join(audstim_path,tmp_sound_name))
    tmp_sound.play()
    response = event.waitKeys(keyList=allowed_keys+['escape'], clearEvents=True)
    if response[-1] in allowed_keys:
        fam_timings.append(clock.getTime()-t_wu_start)
        fam_responses.append(response[-1])
        #Feedback
        if sound_paths[response[-1]]==tmp_sound_name: 
            feedback_text = TextStim(win, "Correct!", color=(1, 1, 1), colorSpace='rgb', pos=(0,-0.3), height=0.2)
            feedback_text.draw()
            win.flip()
            feedback_text = TextStim(win, "Correct!", color=(1, 1, 1), colorSpace='rgb', pos=(0,-0.3), height=0.2)
            feedback_text.draw()
            win.flip()
        else:
            feedback_text = TextStim(win, "Not correct!", color=(1, 1, 1), colorSpace='rgb', pos=(0,-0.3), height=0.2)
            feedback_text.draw()
            win.flip()
            feedback_text = TextStim(win, "Not correct!", color=(1, 1, 1), colorSpace='rgb', pos=(0,-0.3), height=0.2)
            feedback_text.draw()
            win.flip()
        core.wait(trial_pause)
        continue
    elif response[-1]=='escape':
        controlled_e()
    
#%%Ready to start screen. Remind that there will be no feedback.
ready_string = "Great job!\nWe will remove the text once you get going.\nAre you ready to start the experiment?\nPress "+continue_key_name+" to continue"
ready_text = TextStim(win, ready_string, color=(1, 1, 1), colorSpace='rgb')
ready_text.draw()
win.flip()
ready_string = "Great job!\nWe will remove the text once you get going.\nAre you ready to start the experiment?\nPress "+continue_key_name+" to continue"
ready_text = TextStim(win, ready_string, color=(1, 1, 1), colorSpace='rgb')
ready_text.draw()
win.flip()
#Wait until subject has pressed enter or escape
#kb = Keyboard()
response = event.waitKeys(keyList=continue_keys+['escape'], clearEvents=True)
if response[-1] in continue_keys: 
    pause_text = TextStim(win, "Wait", color=(1, 1, 1), colorSpace='rgb')
    pause_text.draw()
    win.flip()
    pause_text = TextStim(win, "Wait", color=(1, 1, 1), colorSpace='rgb')
    pause_text.draw()
    win.flip()
if 'escape' in response:
    controlled_e()

#%%Calculate number of blocks before longer break
pause_indices = np.linspace(0,nbrOfBlocks,nbrOfLongBreaks+2)
pause_indices = [round(x) for x in pause_indices[1:-1]]

quarantine_presses_key = []
quarantine_presses_RT = []
quarantine_presses_correct = []
quarantine_presses_block = []
quarantine_presses_trial = []

running_average_accuracy = 0 #Running average accuracy to see if the guide is needed. Needs to be here because otherwise it's reset to 0 and messes with the data.

for block_itr in range(nbrOfBlocks):
#%% Initialize the experiment.
    #Get sequences for the block. (Separate class.)
    if grammar_type == 'random':
        block_trials = gstim.getRandomSequences(lengthOfSequences,sequencesPerBlock,cedrus_RB840)
    elif block_itr >= blockstart_err and block_itr < (blockstart_err+nbrOfErrorblocks):
        print("In error")
        block_trials = gstim.getErrorSequences(lengthOfSequences,sequencesPerBlock,\
                                              grammar_type,savefolder,block_itr+1,subj,cedrus_RB840,nbrOfStartKeys,grammar_version)
    else:
        print("In not pregen")
        gen_block=True
        while gen_block:
            block_trials = gstim.getGrammarSequences(lengthOfSequences,sequencesPerBlock,\
                                                  grammar_type,savefolder,block_itr+1,subj,cedrus_RB840,nbrOfStartKeys,grammar_version)
            rel_08 = get_rel_08(block_trials,grammar)
            if rel_08<0.85 and rel_08>0.75:
                gen_block=False
    
    # Initialize data save structures.
    block_RT = np.zeros(len(block_trials))
    block_response = []
    block_feedbackGiven = [] #Saves 1 if the subject was too slow or inaccurate.
    block_accuracy = np.zeros(len(block_trials)) #To keep track of accuracy in the experiment.
    block_guide_visible = np.zeros(len(block_trials))
    nbrOfPeeks = 0#nbrOfGuidePeek+1 #To not enable peeks from the start.
    
    if block_itr==0:
        mappings_image_stim.draw()
        win.flip()
        mappings_image_stim.draw()
        win.flip()
        show_guide=True

#%%Run experiment block.
    acc_check_skips = 0
    for trial_itr in range(len(block_trials)):
        
        if block_itr==0 and trial_itr > nbrOfGuidePeek:
            pause_text = TextStim(win, "+", color=(1, 1, 1), colorSpace='rgb')
            pause_text.draw()
            win.flip()
            pause_text = TextStim(win, "+", color=(1, 1, 1), colorSpace='rgb')
            pause_text.draw()
            win.flip()
            show_guide=False
            
        
        if nbrOfPeeks > nbrOfGuidePeek:
            pause_text = TextStim(win, "+", color=(1, 1, 1), colorSpace='rgb')
            pause_text.draw()
            win.flip()
            pause_text = TextStim(win, "+", color=(1, 1, 1), colorSpace='rgb')
            pause_text.draw()
            win.flip()
            show_guide=False
        
        if show_guide:
            mappings_image_stim.draw()
            win.flip()
            mappings_image_stim.draw()
            win.flip()
            nbrOfPeeks=nbrOfPeeks+1
            
        trial = block_trials[trial_itr]
        #Present correct stimulus + measure t_trial_init
        if trial == 'pause':
            block_RT[trial_itr] = np.nan
            block_response.append(np.nan)
            block_accuracy[trial_itr] = np.nan
            core.wait(pause_trial_length)
            #Could be rewritten to apply a help image.
            if trial_itr >= 29:
                msg_text = ""
                acc_check = block_accuracy[trial_itr-20:trial_itr]
                acc_check = acc_check[~np.isnan(acc_check)]
                #if np.nanmean(block_RT[trial_itr-10:trial_itr]) >= 0.8:
                #    msg_text = msg_text+"Too slow, please speed up.\n"
                if sum(acc_check)/len(acc_check) < 0.7 and acc_check_skips==0:
                    msg_text = msg_text+"Too many inaccuracies. Please pay attention.\n"
                    acc_check_skips=20
                if not msg_text=="":
                    feedback_text = TextStim(win, msg_text, color=(1, 1, 1), colorSpace='rgb')
                    block_feedbackGiven.append(1)
                    feedback_text.draw()
                    win.flip()
                    feedback_text = TextStim(win, msg_text, color=(1, 1, 1), colorSpace='rgb')
                    block_feedbackGiven.append(1)
                    feedback_text.draw()
                    win.flip()
                    core.wait(1.5)
                    instr_image_stim.draw()
                    win.flip()
                    instr_image_stim.draw()
                    win.flip()
        else:
            t_init = clock.getTime()
            #Trial is the name of a keyboard key.
            tmp_sound = Sound(os.path.join(audstim_path,sound_paths[trial]))
            tmp_sound.play()
            #Collect response from the keyboard.
            stop = False
            while not stop:
                response = event.getKeys(keyList=allowed_keys+['escape'])
                if len(response)>0 and clock.getTime()-t_init <= 0.1:
                    quarantine_presses_key.append(response[-1])
                    quarantine_presses_RT.append(clock.getTime()-t_init)
                    quarantine_presses_correct.append(trial)
                    quarantine_presses_block.append(block_itr+1)
                    quarantine_presses_trial.append(trial_itr+1)
                elif len(response)>0 and response[-1] in allowed_keys:
                    block_RT[trial_itr] = clock.getTime()-t_init
                    block_response.append(response[-1])
                    block_accuracy[trial_itr] = int(trial==response[-1])
                    block_guide_visible[trial_itr] = int(show_guide)
                    running_average_accuracy = running_average_accuracy*(1-1/trials_in_accuracy_average)+int(trial==response[-1])/trials_in_accuracy_average
                    stop=True
                elif len(response)>0 and response[-1]=='escape':
                    controlled_e()
                core.wait(trial_pause)
    
            
            if acc_check_skips > 0:
                acc_check_skips = acc_check_skips - 1
                
            if running_average_accuracy < guide_accuracy_threshold and trial_itr>trials_in_accuracy_average:
                nbrOfPeeks = 0
                show_guide = True
                
    #Save block data and save to csv-file.
    block_save = pd.DataFrame({'trial':block_trials,
                                'reaction_time':block_RT,
                                'response':block_response,
                                'accuracy':block_accuracy,
                                'guide_shown':block_guide_visible}
        )
    block_save.to_csv(os.path.join(savefolder,subj+'_block_'+str(block_itr+1)+'.csv')) #Maybe save as pickle instead.
    #Take a break
    if block_itr < nbrOfBlocks-1:
        if block_itr in pause_indices:
            ready_string = "Great job!\nHave a short break.\nPress "+continue_key_name+" to continue"
            ready_text = TextStim(win, ready_string, color=(1, 1, 1), colorSpace='rgb')
            ready_text.draw()
            win.flip()
            ready_string = "Great job!\nHave a short break.\nPress "+continue_key_name+" to continue"
            ready_text = TextStim(win, ready_string, color=(1, 1, 1), colorSpace='rgb')
            ready_text.draw()
            win.flip()

            response = event.waitKeys(keyList=continue_keys+['escape'], clearEvents=True)
            if response[-1] in continue_keys: 
                pause_text = TextStim(win, "+", color=(1, 1, 1), colorSpace='rgb')
                pause_text.draw()
                win.flip()
                pause_text = TextStim(win, "+", color=(1, 1, 1), colorSpace='rgb')
                pause_text.draw()
                win.flip()
            if 'escape' in response:
                controlled_e()
        else:
            start = clock.getTime()
            for pause_itr in range(pause_block_length):
                pause_text=TextStim(win, "Great job! Take a "+str(pause_block_length)+" second break.\n", color=(1, 1, 1), colorSpace='rgb')
                pause_text.draw()
                win.flip()
                pause_text=TextStim(win, "Great job! Take a "+str(pause_block_length)+" second break.\n", color=(1, 1, 1), colorSpace='rgb')
                pause_text.draw()
                win.flip()
                core.wait(1)
            pause_text = TextStim(win, "+", color=(1, 1, 1), colorSpace='rgb')
            pause_text.draw()
            win.flip()
            pause_text = TextStim(win, "+", color=(1, 1, 1), colorSpace='rgb')
            pause_text.draw()
            win.flip()
            print(clock.getTime()-start)

#%% Save the quarantine presses
quarantine_presses = pd.DataFrame({'response':quarantine_presses_key,
                                    'reaction_time':quarantine_presses_RT,
                                    'trial':quarantine_presses_correct,
                                    'block':quarantine_presses_block,
                                    'trialNbr':quarantine_presses_trial}
                                  )
quarantine_presses.to_csv(os.path.join(savefolder,subj+'_quarantine_presses.csv'))

#%% End of SRTT message.
end_text = "Great job! You are now done with this part of the experiment!\nPress "+continue_key_name+" to continue."
end_stim = TextStim(win, end_text, color=(1, 1, 1), colorSpace='rgb')
end_stim.draw()
win.flip()
end_text = "Great job! You are now done with this part of the experiment!\nPress "+continue_key_name+" to continue."
end_stim = TextStim(win, end_text, color=(1, 1, 1), colorSpace='rgb')
end_stim.draw()
win.flip()
response = event.waitKeys(keyList=continue_keys+['escape'], clearEvents = True)
if response[-1] in continue_keys:
    print('SRTT done.')
elif response[-1]=='escape':
    controlled_e()


#%% Thank the participant and quit the program
end_of_experiment_text = "Thank you for participating in our experiment!"
end_of_experiment_stim = TextStim(win, end_of_experiment_text, color=(1, 1, 1), colorSpace='rgb')
end_of_experiment_stim.draw()
win.flip()
end_of_experiment_text = "Thank you for participating in our experiment!"
end_of_experiment_stim = TextStim(win, end_of_experiment_text, color=(1, 1, 1), colorSpace='rgb')
end_of_experiment_stim.draw()
win.flip()
core.wait(3)
controlled_e()