import requests
import os
from django.db import models
from django.utils.text import slugify
from django.dispatch import receiver
from django.shortcuts import render
import subprocess
import sys
from subprocess import run,PIPE
from django.core.files.storage import FileSystemStorage
from django.http import HttpResponse
import pickle
model = pickle.load(open('model.pkl', 'rb'))
#Measure pitch of all wav files in directory
import glob
import numpy as np
import pandas as pd
import parselmouth
from parselmouth.praat import call
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
sns.set() # Use seaborn's default style to make attractive graphs
import statistics 
from django import forms
import glob
import decimal



def deleteMedia(request):
    # Get a list of all the file paths that ends with .txt from in specified directory
    fileList = glob.glob('media/*.mp3')
    
    # Iterate over the list of filepaths & remove each file.
    for filePath in fileList:
        try:
            os.remove(filePath)
        except:
            print("Error while deleting file : ", filePath)
    return render(request,'upload1.html')


def button(request):
    return render(request,'upload1.html')
def vow(request):
    return render(request, 'vowel.html')
def el(request):
    aud=request.FILES['audio']
    aud1=request.FILES['audio1']
    aud2=request.FILES['audio2']
    fs=FileSystemStorage()
    filename=fs.save(aud.name,aud)
    filename1=fs.save(aud1.name,aud1)
    filename2=fs.save(aud2.name,aud2)
    fileurl=fs.open(filename)
    fileurl1=fs.open(filename1)
    fileurl2=fs.open(filename2)
    templateurl=fs.url(filename)
    print("dodo")
    aud = subprocess.Popen([sys.executable,'py/vowel.py',str(fileurl),str(fileurl1),str(fileurl2),str(filename),str(filename1),str(filename2)],shell=False,stdout=PIPE)
    aud.communicate()
    print("dodo")
    return render(request, 'vowel.html',{'raw_url':templateurl,'edit_url':aud.stdout})
def gen(request):
    return render(request,'audio.html')
def ttll(request):
    audi=request.FILES['files']
    print("audio is ",audi)
    fs=FileSystemStorage()
    filename=fs.save(audi.name,audi)
    fileurl=fs.open(filename)
    templateurl=fs.url(filename)
    print("file raw url",filename)
    print("file full url", fileurl)
    print("template url",templateurl)
    print("dodo")
    print("dodo")
    # This is the function to measure voice pitch
    def measurePitch(voiceID, f0min, f0max, unit):
        sound = parselmouth.Sound(voiceID) # read the sound
        pitch = call(sound, "To Pitch", 0.0, f0min, f0max) #create a praat pitch object
        meanfreq = call(pitch, "Get mean", 0, 0, unit) # get mean pitch
        sd = call(pitch, "Get standard deviation", 0 ,0, unit) # get standard deviation
        return meanfreq, sd

    # Go through all the wave files in the folder and measure pitch
    sound = parselmouth.Sound(str(fileurl))
    (meanfreq, sd) = measurePitch(sound, 75, 600, "Hertz")
    
    meanfreq = meanfreq/1000
    sd = sd/1000
    
    pitch = sound.to_pitch()
    pitch_values = pitch.selected_array['frequency']
    
    minfun = (np.argmin(pitch_values))/1000
    maxfun = (np.argmax(pitch_values))/1000
    meanfun = (statistics.mean(pitch_values))/1000 

    df = pd.DataFrame(np.column_stack([meanfreq, sd, meanfun, minfun, maxfun]),
                                columns=["meanfreq", "sd", "meanfun", "minfun", "maxfun"])  #add these lists to pandas in the right order
    
    df.set_index("meanfreq", inplace=True)
    # Write out the updated dataframe
    df.to_csv('media/test.csv')
    input_model = pd.read_csv('media/test.csv')
    prediction = model.predict(input_model)
    print(prediction)
    return render(request,'audio.html', {'prediction' : 'PREDICTED GENDER IS {}'.format(prediction)})


def upload(request):
    return render(request,'upload.html', {'start_page': 'yes'})

def SaveAudio(request):
    aud=request.FILES['audio']
    print("audio is ",aud)
    fs=FileSystemStorage()
    filename=fs.save(aud.name,aud)
    fileurl=fs.open(filename)
    templateurl=fs.url(filename)
    print("file raw url",filename)
    print("file full url", fileurl)
    print("template url",templateurl)
    print("dodo")

    #to get the info of the subject
    subjectInfoSave = 'media/subjectInfo.csv'
    sub_info = pd.read_csv(subjectInfoSave)
    # add the audio path infomation of the subject
    sub_info['audio_path']=[fileurl]
    #sub_info.to_csv('media/subjectInfo.csv',index=False)



    #Plots and waveinfo
    sound = parselmouth.Sound(str(fileurl))
    StartTime=sound.xmin
    StartTime = round(StartTime,3)
    EndTime=sound.xmax
    EndTime = round(EndTime,3)

    sub_info['audio_ST']=[str(StartTime)]
    sub_info['audio_ET']=[str(EndTime)]
    sub_info.to_csv('media/subjectInfo.csv',index=False)    

    plt.figure()
    plt.plot(sound.xs(), sound.values.T[:,0])
    plt.xlim([sound.xmin, sound.xmax])
    plt.xlabel("time [s]")
    plt.ylabel("amplitude")
    plt.savefig('media/sound.png')#, or plt.savefig("sound.pdf")

    def draw_spectrogram(spectrogram, dynamic_range=70):
        X, Y = spectrogram.x_grid(), spectrogram.y_grid()
        sg_db = 10 * np.log10(spectrogram.values)
        plt.pcolormesh(X, Y, sg_db, vmin=sg_db.max() - dynamic_range, cmap='afmhot')
        plt.ylim([spectrogram.ymin, spectrogram.ymax])
        plt.xlabel("time [s]")
        plt.ylabel("frequency [Hz]")

    #pre_emphasized_sound = sound.copy()
    #pre_emphasized_sound.pre_emphasize()
    #spectrogram = pre_emphasized_sound.to_spectrogram(window_length=0.03, maximum_frequency=5000)
    
    spectrogram = sound.to_spectrogram(window_length=0.02)
    plt.figure()
    draw_spectrogram(spectrogram)
    plt.xlim([sound.xmin, sound.xmax])
    plt.savefig('media/spectrogram.png')

    return render(request,'upload.html', {'wave_trim':'yes','max_dur':sound.xmax})    

def wavForm(request):

    #to get the info of the subject
    subjectInfoSave = 'media/subjectInfo.csv'
    sub_info = pd.read_csv(subjectInfoSave)
    fileurl = str(sub_info.audio_path[0])

    sound = parselmouth.Sound(str(fileurl))
    
    StartTime = request.GET.get('StartTime', sound.xmin)
    StartTime = float(StartTime)
    StartTime = round(StartTime,3)
    EndTime = request.GET.get('EndTime', sound.xmax)
    EndTime = float(EndTime)
    EndTime = round(EndTime,3)
    
    if StartTime<sound.xmin:
        StartTime=round(sound.xmin,3)

    if EndTime>sound.xmax:
        EndTime=round(sound.xmax,3)
    #if EndTime<StartTime:
     #   return render(request, 'upload.html', {'wave_trim':'yes','error_msg':'yes'})

    # add the audio start and end time infomation of the subject
    sub_info['audio_ST']=[str(StartTime)]
    sub_info['audio_ET']=[str(EndTime)]
    sub_info.to_csv('media/subjectInfo.csv',index=False)    

    sound = sound.extract_part(from_time=StartTime, to_time=EndTime, preserve_times=True)

    plt.figure()
    plt.plot(sound.xs(), sound.values.T[:,0])
    plt.xlim([sound.xmin, sound.xmax])
    plt.xlabel("time [s]")
    plt.ylabel("amplitude")
    plt.savefig('media/sound.png')#, or plt.savefig("sound.pdf")


    def draw_spectrogram(spectrogram, dynamic_range=70):
        X, Y = spectrogram.x_grid(), spectrogram.y_grid()
        sg_db = 10 * np.log10(spectrogram.values)
        plt.pcolormesh(X, Y, sg_db, vmin=sg_db.max() - dynamic_range, cmap='afmhot')
        plt.ylim([spectrogram.ymin, spectrogram.ymax])
        plt.xlabel("time [s]")
        plt.ylabel("frequency [Hz]")

    #pre_emphasized_sound = sound.copy()
    #pre_emphasized_sound.pre_emphasize()
    #spectrogram = pre_emphasized_sound.to_spectrogram(window_length=0.03, maximum_frequency=5000)
    
    spectrogram = sound.to_spectrogram(window_length=0.03)
    plt.figure()
    draw_spectrogram(spectrogram)
    plt.xlim([sound.xmin, sound.xmax])
    plt.savefig('media/spectrogram.png')

    return render(request,'upload.html', {'wave_trim':'yes','max_dur':sound.xmax})

#computing pitch analysis
def external(request):
    
    #to get the info of the subject
    subjectInfoSave = 'media/subjectInfo.csv'
    sub_info = pd.read_csv(subjectInfoSave)
    fileurl = str(sub_info.audio_path[0])

    def measurePitch(voiceID, f0min, f0max, unit):
        sound = parselmouth.Sound(voiceID) # read the sound
        pitch = call(sound, "To Pitch", 0.0, f0min, f0max) #create a praat pitch object
        meanfreq = call(pitch, "Get mean", 0, 0, unit) # get mean pitch
        sd = call(pitch, "Get standard deviation", 0 ,0, unit) # get standard deviation
        return meanfreq, sd

    # Go through all the wave files in the folder and measure pitch
    sound = parselmouth.Sound(str(fileurl))
    (meanfreq, sd) = measurePitch(sound, 75, 600, "Hertz")
    
    meanfreq = meanfreq/1000
    sd = sd/1000
    
    pitch = sound.to_pitch()
    pitch_values = pitch.selected_array['frequency']
    
    minfun = (np.argmin(pitch_values))/1000
    maxfun = (np.argmax(pitch_values))/1000
    meanfun = (statistics.mean(pitch_values))/1000 

    df = pd.DataFrame(np.column_stack([meanfreq, sd, meanfun, minfun, maxfun]),
                                columns=["meanfreq", "sd", "meanfun", "minfun", "maxfun"])  #add these lists to pandas in the right order
    
    df.set_index("meanfreq", inplace=True)
    # Write out the updated dataframe
    df.to_csv('media/test.csv')
    input_model = pd.read_csv('media/test.csv')
    prediction = model.predict(input_model)
    aud = subprocess.Popen([sys.executable,'py/doit.py',str(fileurl),str('Temp_data'),str(prediction)],shell=False,stdout=PIPE)
    aud.communicate()
    print("dodo_doit")
    print(aud.stdout)
    return render(request,'upload.html',{'raw_url':'temp_data','edit_url':aud.stdout})

def getData(request):
    inp_name = request.GET.get('Name', 'XXXX')
    inp_age = request.GET.get('Age', 'XXXX')
    inp_gender = request.GET.get('Gender', 'XXXX')
    inp_uhid = request.GET.get('UHID', 'XXXX')

    df = pd.DataFrame({'Name':inp_name, 'Age':inp_age, 'Gender':inp_gender, 'UHID':inp_uhid}, index=[1])
    df.index.names=['Sl_no']
    df.to_csv('media/subjectInfo.csv')

    return render(request,'thanksPage.html')
