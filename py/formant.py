import sys
import os
import glob as glob
import numpy as np
import pandas as pd
import parselmouth
from parselmouth.praat import call
import statistics
import matplotlib.pyplot as plt
import seaborn as sns
from reportlab.pdfgen import canvas
from reportlab.platypus import SimpleDocTemplate
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors

image_fullpath = sys.argv[1]
image_path = sys.argv[2]

def measureFormants(sound, f0min,f0max):
    sound = parselmouth.Sound(sound) # read the sound
    duration = call(sound, "Get total duration") # duration
    pitch = call(sound, "To Pitch (cc)", 0, f0min, 15, 'no', 0.03, 0.45, 0.01, 0.35, 0.14, f0max)
    pointProcess = call(sound, "To PointProcess (periodic, cc)", f0min, f0max)
    
    formants = call(sound, "To Formant (burg)", 0.0025, 5, 5000, 0.025, 50)
    numPoints = call(pointProcess, "Get number of points")

    f1_list = []
    f2_list = []
    f3_list = []
    f4_list = []
    
    # Measure formants only at glottal pulses
    for point in range(0, numPoints):
        point += 1
        t = call(pointProcess, "Get time from index", point)
        f1 = call(formants, "Get value at time", 1, t, 'Hertz', 'Linear')
        f2 = call(formants, "Get value at time", 2, t, 'Hertz', 'Linear')
        f3 = call(formants, "Get value at time", 3, t, 'Hertz', 'Linear')
        f4 = call(formants, "Get value at time", 4, t, 'Hertz', 'Linear')
        f1_list.append(f1)
        f2_list.append(f2)
        f3_list.append(f3)
        f4_list.append(f4)
    
    f1_list = [f1 for f1 in f1_list if str(f1) != 'nan']
    f2_list = [f2 for f2 in f2_list if str(f2) != 'nan']
    f3_list = [f3 for f3 in f3_list if str(f3) != 'nan']
    f4_list = [f4 for f4 in f4_list if str(f4) != 'nan']
    
    # calculate mean formants across pulses
    f1_mean = statistics.mean(f1_list)
    f2_mean = statistics.mean(f2_list)
    f3_mean = statistics.mean(f3_list)
    f4_mean = statistics.mean(f4_list)
    
    # calculate median formants across pulses, this is what is used in all subsequent calcualtions
    # you can use mean if you want, just edit the code in the boxes below to replace median with mean
    f1_median = statistics.median(f1_list)
    f2_median = statistics.median(f2_list)
    f3_median = statistics.median(f3_list)
    f4_median = statistics.median(f4_list)
    
    return f1_mean, f2_mean, f3_mean, f4_mean, f1_median, f2_median, f3_median, f4_median, f1_list, f2_list, duration    

duration_list = []
file_list = []
f1_mean_list = []
f2_mean_list = []
f3_mean_list = []
f4_mean_list = []
f1_median_list = []
f2_median_list = []
f3_median_list = []
f4_median_list = []

# Go through all the wave files in the folder and measure all the acoustics
sound = parselmouth.Sound(str(image_fullpath))
(f1_mean, f2_mean, f3_mean, f4_mean, f1_median, f2_median, f3_median, f4_median, f1_list, f2_list, duration) = measureFormants(
    sound, 75, 300)
file_list.append(str(image_fullpath)) # make an ID list
duration_list.append(duration) # make duration list
    
# add the formant data
f1_mean_list.append(f1_mean)
f2_mean_list.append(f2_mean)
f3_mean_list.append(f3_mean)
f4_mean_list.append(f4_mean)
f1_median_list.append(f1_median)
f2_median_list.append(f2_median)
f3_median_list.append(f3_median)
f4_median_list.append(f4_median)

df1 = pd.DataFrame(np.column_stack([duration_list, f1_mean_list, 
                                   f2_mean_list, f3_mean_list, f4_mean_list, 
                                   f1_median_list, f2_median_list, f3_median_list, 
                                   f4_median_list]),
                                   columns=['duration', 'f1_mean', 'f2_mean', 
                                            'f3_mean', 'f4_mean', 'f1_median', 
                                            'f2_median', 'f3_median', 'f4_median'])


df1.to_csv("processed_results.csv", index=False)
df1 = pd.read_csv('processed_results.csv', header=0)

sns.set() # Use seaborn's default style to make attractive graphs
plt.rcParams['figure.dpi'] = 70 # Show nicely large images in this notebook

#plt.scatter(x_data, y_data, c='r', label='data')
fig1 = plt.figure()
plt.plot(f1_list)
plt.plot(f2_list)
plt.savefig('media/formant.jpg')

fileSave = 'media/report1.pdf'
documentTitle = 'Report'
subTitle= 'Audio File:'
img1= 'media/formant.jpg'

pdf = canvas.Canvas(fileSave)
pdf.setTitle(documentTitle)
pdf.drawString(270, 770, 'Report')

def drawMyRuler(pdf):
    pdf.drawString(100,810, 'x100')
    pdf.drawString(200,810, 'x200')
    pdf.drawString(300,810, 'x300')
    pdf.drawString(400,810, 'x400')
    pdf.drawString(500,810, 'x500')

    pdf.drawString(10,100, 'y100')
    pdf.drawString(10,200, 'y200')
    pdf.drawString(10,300, 'y300')
    pdf.drawString(10,400, 'y400')
    pdf.drawString(10,500, 'y500')
    pdf.drawString(10,600, 'y600')
    pdf.drawString(10,700, 'y700')
    pdf.drawString(10,800, 'y800')    

#drawMyRuler(pdf)
pdf.setFillColorRGB(0,0, 255)
pdf.drawString(120, 720, subTitle )
pdf.drawString(180, 720, image_path )

pdf.line(30,710,550,710)

text = pdf.beginText(120, 690)
text.setFillColor(colors.red)
text.textLine("{}".format('Formant Analysis'))
pdf.drawText(text)

pdf.setFillColorRGB(0,0, 255)
pdf.drawString(120, 670, 'FORMANT PLOT : ' )

pdf.drawInlineImage(img1, 90, 330)

pdf.save()