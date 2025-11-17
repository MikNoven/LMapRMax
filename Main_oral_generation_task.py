#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Aug 12 14:11:54 2025
Generation task for oral generation in LMapRMax project. 
@author: gdf724
"""

#%% Import necessary packages.
import os
from psychopy import gui
from psychopy.visual import Window, TextStim, SimpleImageStim
from psychopy import event, core, monitors, prefs
from psychopy.sound import Sound
prefs.general['audioLib'] = ['PTB']
import numpy as np
import Grammar_stimuli as gstim
from datetime import date
import pandas as pd

#%% Get subject dialog box
def subject_dialog(title_text):
    subj=''
    exp_info = {'Generation task\nsubject': ''}  
    loopDiag=True
    while loopDiag:
        dlg = gui.DlgFromDict(exp_info,title=title_text)
        
        if not dlg.OK:
            controlled_e()
        else:
            subj=exp_info['Generation task\nsubject']
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
    savefolder = os.path.join(save_path,subj,subj+'_'+date.today().isoformat()+'_oralgeneration')
    if os.path.exists(savefolder):
        savefolder = "error"
    else:
        os.makedirs(savefolder)
    return savefolder


#%% Define the hardware
cedrus_RB840 = True #Whether to use Cedrus or keyboard. (affects which buttons to use.)
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


#%% Define the paradigm.  
grammar_type = '5050' #'8020', '5050', or 'random'
grammar_version = 'a' 
nbrOfStartKeys = 2 #Can be 2 or 1 and alternates between [L3] and [L3,R1].
#Generation task
lengthOfSequences = 8 #Number of presses per sequence.
pregeneratedGenerationTask = 3 #How many of the elements should be pre-generated in the generation task. 0 for completely free generation.
grammaticalPregenerated_randomGenTask = True #False if starting sequence should be random
nbrOfGeneratedSequences = 8
sound_interval_time = 0.4 #Time between sounds.


#%% Define paths
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
    else:
        loop_subjDial = False
    
#%% Save settings
with open(os.path.join(savefolder,'settings.txt'),'w') as f:
    f.write('subject:'+str(subj)+'\n')
    f.write('cedrus_RB840:'+str(cedrus_RB840)+'\n')
    f.write('lengthOfSequences:'+str(lengthOfSequences)+'\n')
    f.write('grammar_type:'+str(grammar_type)+'\n')
    f.write('grammar_version:'+str(grammar_version)+'\n')
    f.write('nbrOfStartKeys:'+str(nbrOfStartKeys)+'\n')
    f.write('pregeneratedGenerationTask:'+str(pregeneratedGenerationTask)+'\n')
    f.write('nbrOfGeneratedSequences:'+str(nbrOfGeneratedSequences)+'\n')
    f.write('grammaticalPregenerated_randomGenTask:'+str(grammaticalPregenerated_randomGenTask)+'\n')
   
#%%Generation task intialization.
win = Window(size=winsize, monitor=mon, fullscr=False, screen=0, units="norm", pos=[0,0], color=[-.69,-.69,-.69], colorSpace = 'rgb')
gentest_start_text = "In the previous part of the experiment,\nthe cues were presented in sequences\nthat came from a system.\nPress "+continue_key_name+" to continue."
gentest_start_stim = TextStim(win, gentest_start_text, color=(1, 1, 1), colorSpace='rgb')
gentest_start_stim.draw()
win.flip()
gentest_start_text = "In the previous part of the experiment,\nthe cues were presented in sequences\nthat came from a system.\nPress "+continue_key_name+" to continue."
gentest_start_stim = TextStim(win, gentest_start_text, color=(1, 1, 1), colorSpace='rgb')
gentest_start_stim.draw()
win.flip()
response = event.waitKeys(keyList=continue_keys+['escape'], clearEvents = True)
if response[-1] in continue_keys:
    print('First gentest text done.')
elif response[-1]=='escape':
    controlled_e()

tmp_sound = Sound(os.path.join(audstim_path,'silence.wav'))
tmp_sound.play()

clock = core.Clock()
#%%Generation task grammatical.
if pregeneratedGenerationTask == 0 or grammar_type == 'random':
    gentest_grammar_text = "We now ask you to freely speak "+str(nbrOfGeneratedSequences)+" sequences\nfrom that system.\nPress "+continue_key_name+" to continue."
else:
    gentest_grammar_text = "We now ask you to freely speak "+str(nbrOfGeneratedSequences)+" sequences\nfrom that system.\nYou will get "+str(pregeneratedGenerationTask)+" sounds to start you off\nPress "+continue_key_name+" to continue."
   
gentest_grammar_stim = TextStim(win, gentest_grammar_text, color=(1, 1, 1), colorSpace='rgb')
gentest_grammar_stim.draw()
win.flip()
response = event.waitKeys(keyList=continue_keys+['escape'], clearEvents = True)
if response[-1] in continue_keys:
    print('Generation task grammar.')
elif response[-1]=='escape':
    controlled_e()

for gen_itr in range(nbrOfGeneratedSequences):
    gen_seq_text="Sequence "+str(gen_itr+1)+" of "+str(nbrOfGeneratedSequences)
    gen_seq_text_stim = TextStim(win, gen_seq_text, color=(1, 1, 1), colorSpace='rgb')
    gen_seq_text_stim.draw()
    win.flip()
    gen_seq_text="Sequence "+str(gen_itr+1)+" of "+str(nbrOfGeneratedSequences)
    gen_seq_text_stim = TextStim(win, gen_seq_text, color=(1, 1, 1), colorSpace='rgb')
    gen_seq_text_stim.draw()
    win.flip()
    core.wait(0.5)
    pregen_seq = gstim.getPreGeneratedSequences(pregeneratedGenerationTask,'5050',cedrus_RB840,nbrOfStartKeys,grammar_version)
    for pregen_itr in range(pregeneratedGenerationTask):
        tmp_sound = Sound(os.path.join(audstim_path,sound_paths[pregen_seq[pregen_itr]]))
        tmp_sound.play()
        t_init = clock.getTime()
        core.wait(sound_interval_time)


    gentest_pause_text = "Press "+continue_key_name+" to continue."
    gentest_pause_stim = TextStim(win, gentest_pause_text, color=(1, 1, 1), colorSpace='rgb')
    gentest_pause_stim.draw()
    win.flip()
    gentest_pause_text = "Press "+continue_key_name+" to continue."
    gentest_pause_stim = TextStim(win, gentest_pause_text, color=(1, 1, 1), colorSpace='rgb')
    gentest_pause_stim.draw()
    win.flip()
    response = event.waitKeys(keyList=continue_keys+['escape'], clearEvents = True)
    if response[-1] in continue_keys:
        print('First gentest text done.')
    elif response[-1]=='escape':
        controlled_e()
                

#%%Generation task random.
if pregeneratedGenerationTask == 0 or grammar_type == 'random':
    gentest_grammar_text = "We now ask you to freely speak "+str(nbrOfGeneratedSequences)+" sequences\nthat you are sure is not\nfrom that system.\nYou are not allowed to press the same key twice in a row.\nPress "+continue_key_name+" to continue."
else:
    gentest_grammar_text = "We now ask you to freely speak "+str(nbrOfGeneratedSequences)+" sequences\nthat you are sure is not\nfrom that system.\nYou are not allowed to press the same key twice in a row.\nYou will get "+str(pregeneratedGenerationTask)+" keys to press to start you off\nPress "+continue_key_name+" to continue."
   
gentest_random_text = "We now ask you to freely speak "+str(nbrOfGeneratedSequences)+" sequences\nthat you are sure is not\nfrom that sequence.\nYou are not allowed to say the same sound two times in a row.\nPress "+continue_key_name+" to continue."
gentest_random_stim = TextStim(win, gentest_random_text, color=(1, 1, 1), colorSpace='rgb')
gentest_random_stim.draw()
win.flip()
gentest_random_text = "We now ask you to freely speak "+str(nbrOfGeneratedSequences)+" sequences\nthat you are sure is not\nfrom that sequence.\nYou are not allowed to say the same sound two times in a row.\nPress "+continue_key_name+" to continue."
gentest_random_stim = TextStim(win, gentest_random_text, color=(1, 1, 1), colorSpace='rgb')
gentest_random_stim.draw()
win.flip()
response = event.waitKeys(keyList=continue_keys+['escape'], clearEvents = True)
if response[-1] in continue_keys:
    print('Generation task random.')
elif response[-1]=='escape':
    controlled_e()

for gen_itr in range(nbrOfGeneratedSequences):
    gen_seq_text="Sequence "+str(gen_itr+1)+" of "+str(nbrOfGeneratedSequences)
    gen_seq_text_stim = TextStim(win, gen_seq_text, color=(1, 1, 1), colorSpace='rgb')
    gen_seq_text_stim.draw()
    win.flip()
    gen_seq_text="Sequence "+str(gen_itr+1)+" of "+str(nbrOfGeneratedSequences)
    gen_seq_text_stim = TextStim(win, gen_seq_text, color=(1, 1, 1), colorSpace='rgb')
    gen_seq_text_stim.draw()
    win.flip()
    core.wait(0.5)
    pregen_seq = gstim.getPreGeneratedSequences(pregeneratedGenerationTask,'5050',cedrus_RB840,nbrOfStartKeys,grammar_version)
    for pregen_itr in range(pregeneratedGenerationTask):
        tmp_sound = Sound(os.path.join(audstim_path,sound_paths[pregen_seq[pregen_itr]]))
        tmp_sound.play()
        t_init = clock.getTime()
        core.wait(sound_interval_time)


    gentest_pause_text = "Press "+continue_key_name+" to continue."
    gentest_pause_stim = TextStim(win, gentest_pause_text, color=(1, 1, 1), colorSpace='rgb')
    gentest_pause_stim.draw()
    win.flip()
    gentest_pause_text = "Press "+continue_key_name+" to continue."
    gentest_pause_stim = TextStim(win, gentest_pause_text, color=(1, 1, 1), colorSpace='rgb')
    gentest_pause_stim.draw()
    win.flip()
    response = event.waitKeys(keyList=continue_keys+['escape'], clearEvents = True)
    if response[-1] in continue_keys:
        print('Second gentest text done.')
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
core.wait(3)
controlled_e()