#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Aug 14 09:53:35 2025
Script for collecting data from pilot LMapRMax.
Will later be adopted for collecting data for real project.
@author: gdf724
"""

#%% Import necessary libraries
import os 
import pandas as pd
from glob import glob
import Grammar_stimuli as gramstim
import numpy as np

#%% Help functions
def sortDynamic(listed):
    sortedList = [None]*len(listed)
    for itr in range(len(listed)):
        tmp = listed[itr]
        if tmp[-1]=='v':
            if tmp[-6].isnumeric():
                indx = int(tmp[-6:-4]) #Works for now but could be more versatile. 
            else:
                indx = int(tmp[-5:-4])
        else:
            indx = int(os.path.basename(tmp)[2:])
        sortedList[indx-1] = tmp
    
    return sortedList

def gethandshifts(trials):
    left = ['a', 'b', 'c'] 
    right = ['f', 'g', 'h']
    handshift = []
    skip = False
    for itr in range(len(trials)):
        if (skip) or (itr==0):
            handshift.append(-1)
            skip=False
        else:
            if trials[itr]=='pause':
                skip = True
            elif (left.count(trials[itr]) > 0) and (right.count(trials[itr-1]) > 0):
                handshift.append(1)
            elif (right.count(trials[itr]) > 0) and (left.count(trials[itr-1]) > 0):
                handshift.append(1)
            else:
                handshift.append(0)
                
    return handshift

def getGrammarScores(responses,seq,grammar,gr):
    grammarscores = []
    grammarscores.append(np.nan)
    for itr in range(1,len(responses)):
        if seq[itr-1]!=seq[itr]:
            grammarscores.append(np.nan)
        else:
            grammarscores.append(grammar[responses[itr]][responses[itr-1]])
    
    return grammarscores

def getTransProb(group,cuelist,grammar_version):
    grammar = gramstim.getGrammar(group, True, grammar_version)
    transprob = []
    transprob.append(np.nan)
    for itr in range(1,len(cuelist)):
        if cuelist[itr-1]=='pause':
            transprob.append(np.nan)
        elif cuelist[itr]!='pause':
            transprob.append(grammar[cuelist[itr]][cuelist[itr-1]])
            
    return transprob

#%% Define variables
datapath = '/Users/gdf724/Data/LMapRMax/Piloting'
output_path = '/Users/gdf724/Data/LMapRMax/Piloting/Postproc'

subjlist = glob(os.path.join(datapath,'*'))
subjlist.remove(output_path)
grammar_version_col = []
subjcol_gv = []

nbrOfDays = 2
nbrOfBlocks = 15
nbrOfSequences = 5 
nbrOfItems = 8

#%% SRTT
# Output: csv-file with subject, day, block, sequence_nbr, element_nbr, cue, RT, response, accuracy, handshift and potentially background measures.
# Named "learning"

seq_nbr_template = []
element_nbr_template = []
indx_template = []
indx_itr = 1

for seqitr in range(nbrOfSequences):
    for ittr in range(nbrOfItems):
        seq_nbr_template.append(seqitr+1)
        element_nbr_template.append(ittr+1)
        indx_template.append(indx_itr)
        indx_itr = indx_itr+1

subjcol = []
groupcol = []
gramtypecol = []
daycol = []
blockcol = []
sequence_nbr_col = []
element_nbr_col = []
indx_col = []
cue_col = []
prob_col = []
prob_hilo_cue_col = []
RTcol = []
responsecol = []
accuracycol = []
handshiftcol = []
guideshowncol = []

for subject in subjlist:
    subj = os.path.basename(subject)
    subj = subj.replace(" ","")
    learning_list = sorted(glob(os.path.join(subject,subj+'*_learning')))    
    for day_itr in range(len(learning_list)):
        block_list = sortDynamic(glob(os.path.join(learning_list[day_itr],'*_block_*.csv')))
        tmp = pd.read_table(os.path.join(learning_list[day_itr],'settings.txt'),sep=':')
        group = tmp.iloc[8,1]
        grammar_version = tmp.iloc[9,1]
        if day_itr==0:
            grammar_version_col.append(grammar_version)
            subjcol_gv.append(subj)

        for block_itr in range(len(block_list)):
            block_data = pd.read_csv(os.path.join(block_list[block_itr]))
            handshiftcol.extend(gethandshifts(block_data['trial'].tolist()))
            prob_col.extend(getTransProb(group,block_data['trial'].tolist(),grammar_version))
            prob_hilo_cue_col.extend(getTransProb('8020',block_data['trial'].tolist(),grammar_version))
            block_data=block_data.drop(block_data[block_data['trial']=='pause'].index)
            subjcol.extend([subj]*len(seq_nbr_template))
            groupcol.extend([group]*len(seq_nbr_template))
            gramtypecol.extend([grammar_version]*len(seq_nbr_template))
            daycol.extend([day_itr+1]*len(seq_nbr_template))
            blockcol.extend([block_itr+1]*len(seq_nbr_template))
            sequence_nbr_col.extend(seq_nbr_template)
            element_nbr_col.extend(element_nbr_template)
            indx_col.extend(indx_template)
            cue_col.extend(block_data['trial'].tolist())
            RTcol.extend(block_data['reaction_time'].tolist())
            responsecol.extend(block_data['response'].tolist())
            accuracycol.extend(block_data['accuracy'].tolist())
            guideshowncol.extend(block_data['guide_shown'].tolist())

savedf = pd.DataFrame({'subject': subjcol,
                       'group': groupcol,
                       'day': daycol,
                       'block': blockcol,
                       'sequence': sequence_nbr_col,
                       'element': element_nbr_col,
                       'indx': indx_col,
                       'cue': cue_col,
                       'transprob': prob_col,
                       'hilo_transprob': prob_hilo_cue_col,
                       'RT': RTcol,
                       'response': responsecol,
                       'accuracy': accuracycol,
                       'handshift': handshiftcol,
                       'guide_shown': guideshowncol})
savedf.to_csv(os.path.join(output_path,'LearningSRTT_data.csv'), index=False)
        
#%% Sequence production
element_nbr_template = []

for seqitr in range(8):
    for ittr in range(nbrOfItems):
        element_nbr_template.append(ittr+1)

subjcol = []
groupcol = []
conditioncol = []
sequence_nbr_col = []
element_nbr_col = []
gentimecol = []
responsecol = []
fixed = []
grammatical = []
hilo_grammatical = []
eq_grammatical = []
bin_grammatical = []

for subject in subjlist:
    subj = os.path.basename(subject)
    subj = subj.replace(" ","")
    
    grammar_version = grammar_version_col[subjcol_gv.index(subj)]
    production_list = sorted(glob(os.path.join(subject,subj+'*_generation','*generation*')))
    if len(production_list) > 1:
        tmp = pd.read_table(os.path.join(os.path.dirname(production_list[0]),'settings.txt'),sep=':')
        group = tmp.iloc[2,1]
        grver_tmp = pd.read_table(os.path.join(sorted(glob(os.path.join(subject,subj+'*_learning')))[0],'settings.txt'),sep=':')
        grammar = gramstim.getGrammar('8020', True, grammar_version)
        for prod_itr in range(len(production_list)):
            if production_list[prod_itr][-5] == 'l':
                gr = 'grammatical'
            elif production_list[prod_itr][-5] == 'm':
                gr = 'random'
            
            tmp_data = pd.read_csv(production_list[prod_itr])
            subjcol.extend([subj]*len(tmp_data))
            groupcol.extend([group]*len(tmp_data))
            conditioncol.extend([gr]*len(tmp_data))
            sequence_nbr_col.extend(tmp_data['sequence'].tolist())
            element_nbr_col.extend(element_nbr_template)
            gentimecol.extend(tmp_data['generation_time'].tolist())
            responsecol.extend(tmp_data['response'].tolist())
            fixed.extend(tmp_data['pregenerated'].tolist())
            grammatical.extend(getGrammarScores(tmp_data['response'].tolist(),tmp_data['sequence'].tolist(),grammar,gr))
            bin_grammatical.extend([1 if x>0 and not np.isnan(x) else 0 for x in getGrammarScores(tmp_data['response'].tolist(),tmp_data['sequence'].tolist(),grammar,gr)])
savedf = pd.DataFrame({'subject': subjcol,
                       'group': groupcol,
                       'condition': conditioncol,
                       'sequence': sequence_nbr_col,
                       'element': element_nbr_col,
                       'generation_time': gentimecol,
                       'response': responsecol,
                       'pregenerated': fixed,
                       'grammaticality': grammatical,
                       'bin_grammaticality': bin_grammatical})
savedf.to_csv(os.path.join(output_path,'SequenceProduction_data.csv'), index=False)

#%% Post SRTT
element_nbr_template = []
seq_nbr_template = []
for seqitr in range(5):
    for ittr in range(nbrOfItems):
        seq_nbr_template.append(seqitr+1)
        element_nbr_template.append(ittr+1)

subjcol = []
groupcol = []
probcond = []
sequence_nbr_col = []
element_nbr_col = []
cue_col = []
prob_col = []
RTcol = []
responsecol = []
accuracycol = []
handshiftcol = []
hilo_col =[]
#testorder=['grammatical']*4 + ['random']*4


for subject in subjlist:
    subj = os.path.basename(subject)
    subj = subj.replace(" ","")
    grammar_version = grammar_version_col[subjcol_gv.index(subj)]
    block_list = sorted(glob(os.path.join(subject,subj+'*_post','*block*')))  
    if len(block_list) > 0:
        for block_itr in range(len(block_list)):
            block_data = pd.read_csv(block_list[block_itr])
            if len(block_data)>45: #Quick fix. Check why this is
                block_data = block_data[1:]
                block_data = block_data.reset_index()
                
            handshiftcol.extend(gethandshifts(block_data['trial'].tolist()))
            prob_col.extend(getTransProb(group,block_data['trial'].tolist(),grammar_version))
            transprobs = getTransProb(group,block_data['trial'].tolist(),grammar_version)
            if transprobs.count(0)>0:
                block_cond = 'random'
            else:
                block_cond = 'grammatical'
            block_data=block_data.drop(block_data[block_data['trial']=='pause'].index,  )
            subjcol.extend([subj]*len(block_data))
            groupcol.extend([group]*len(block_data))
            probcond.extend([block_cond]*len(block_data))
            sequence_nbr_col.extend(seq_nbr_template)
            element_nbr_col.extend(element_nbr_template)
            cue_col.extend(block_data['trial'].tolist())
            RTcol.extend(block_data['reaction_time'].tolist())
            responsecol.extend(block_data['response'].tolist())
            accuracycol.extend(block_data['accuracy'].tolist())
            block_cond = 'grammatical'
        
        #Check if there were random trials in (non-NA) trials, if so the block was random
        # otherwise grammatical
        
            
savedf = pd.DataFrame({'subject': subjcol,
                       'group': groupcol,
                       'condition': probcond,
                       'sequence': sequence_nbr_col,
                       'element': element_nbr_col,
                       'cue': cue_col,
                       'transprob': prob_col,
                       'RT': RTcol,
                       'response': responsecol,
                       'accuracy': accuracycol,
                       'handshift': handshiftcol})
savedf.to_csv(os.path.join(output_path,'PostSRTT_data_updated.csv'), index=False)
        

#%% Oral production

