import sys
import os
import glob as glob
import numpy as np
import pandas as pd
import parselmouth
from parselmouth.praat import call
import statistics
import math
import matplotlib.pyplot as plt
import seaborn as sns
from reportlab.pdfgen import canvas
from reportlab.platypus import SimpleDocTemplate
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors

image_fullpath = sys.argv[1]
print(image_fullpath)
au2 = sys.argv[2]
au3 = sys.argv[3]
name1 = sys.argv[4]
name2 = sys.argv[5]
name3 = sys.argv[6]


def measureFormants(sound, f0min,f0max):
    sound = parselmouth.Sound(sound) # read the sound
    duration = call(sound, "Get total duration") # duration
    pitch = call(sound, "To Pitch (cc)", 0, f0min, 15, 'no', 0.03, 0.45, 0.01, 0.35, 0.14, f0max)
    pointProcess = call(sound, "To PointProcess (periodic, cc)", f0min, f0max)
    
    formants = call(sound, "To Formant (burg)", 0.0025, 5, 5000, 0.025, 50)
    numPoints = call(pointProcess, "Get number of points")

    f1_list = []
    f2_list = []
    
    # Measure formants only at glottal pulses
    for point in range(0, numPoints):
        point += 1
        t = call(pointProcess, "Get time from index", point)
        f1 = call(formants, "Get value at time", 1, t, 'Hertz', 'Linear')
        f2 = call(formants, "Get value at time", 2, t, 'Hertz', 'Linear')
        f1_list.append(f1)
        f2_list.append(f2)
    
    f1_list = [f1 for f1 in f1_list if str(f1) != 'nan']
    f2_list = [f2 for f2 in f2_list if str(f2) != 'nan']
    
    # calculate mean formants across pulses
    f1_mean = statistics.mean(f1_list)
    f2_mean = statistics.mean(f2_list)
    
    return f1_mean, f2_mean, f1_list, f2_list    


# Go through all the wave files in the folder and measure all the acoustics
sound = parselmouth.Sound(str(image_fullpath))
(f1_mean,f2_mean, f1_list,f2_list) = measureFormants(
    sound, 75, 300)

sound = parselmouth.Sound(str(au2))
(f21_mean, f22_mean,f21_list,f22_list) = measureFormants(
    sound, 75, 300)

sound = parselmouth.Sound(str(au3))
(f31_mean, f32_mean,f31_list,f32_list) = measureFormants(
    sound, 75, 300)



sns.set() # Use seaborn's default style to make attractive graphs
plt.rcParams['figure.dpi'] = 80 # Show nicely large images in this notebook

#plt.scatter(x_data, y_data, c='r', label='data')
fig1 = plt.figure()
x = [f1_mean, f21_mean, f31_mean]
y = [f2_mean, f22_mean, f32_mean]
plt.plot(y, x, color='red', marker='o', linestyle='solid',linewidth=8, markersize=12)
s = [f1_mean,f31_mean]
t = [f2_mean,f32_mean]
plt.plot(t, s, color='red', marker='o', linestyle='solid',linewidth=8, markersize=12)
color = np.random.rand(len(f1_list))
plt.scatter(f2_list,f1_list, c=color, alpha=0.5)
color = np.random.rand(len(f21_list))
plt.scatter(f22_list,f21_list, c=color, alpha=0.5)
color = np.random.rand(len(f31_list))
plt.scatter(f32_list,f31_list, c=color, alpha=0.5)
plt.xlabel('f2')
plt.ylabel('f1')
plt.savefig('media/vowel_triangle.jpg')

x1= f2_mean
x2= f22_mean
x3= f32_mean
y1= f1_mean
y2= f21_mean
y3= f31_mean
p1 = [x1,y1]
p2 = [x2,y2]
p3 =[x3,y3]
a = math.sqrt(((p1[0]-p2[0])**2)+((p1[1]-p2[1])**2))
b = math.sqrt(((p3[0]-p2[0])**2)+((p3[1]-p2[1])**2))
c = math.sqrt(((p1[0]-p3[0])**2)+((p1[1]-p3[1])**2))
s = (a + b + c) / 2
area = (s*(s-a)*(s-b)*(s-c)) ** 0.5

fileSave = 'media/report1.pdf'
documentTitle = 'Report'
subTitle= 'Audio Files:'
img1= 'vowel_triangle.jpg'

#to get the info of the subject
subjectInfoSave = 'media/subjectInfo.csv'
sub_info = pd.read_csv(subjectInfoSave)




#image_filename = os.path.join(os.path.dirname(__file__), 'formant.jpg')

#Creating report pdf
from pylatex import Document, Section, Command ,VerticalSpace, Subsection,\
 MiniPage, TextColor, LineBreak, MediumText, Tabular, Math, TikZ, Axis,\
 StandAloneGraphic, MultiColumn, Plot, Figure, Matrix, Alignat ,LargeText,\
 NewLine, PageStyle, Head, Foot ,Tabularx, simple_page_number
from pylatex.utils import italic, bold, NoEscape
from datetime import date
today = date.today()
d2 = today.strftime("%B %d, %Y")


# Maergin and size
geometry_options = {
    "head": "40pt",
    "margin": "0.5in",
    "bottom": "0.6in",
    "includeheadfoot": True
}
doc = Document(geometry_options=geometry_options)

#title and subject info     
with doc.create(MiniPage(align='l')):

    #doc.append(NoEscape(r"\noindent\rule{\textwidth}{1pt}"))
    #doc.append(NewLine())
    doc.append('Name : '+str(sub_info.Name[0]))
    doc.append('\nAge: '+str(sub_info.Age[0]))
    doc.append('\nGender: '+str(sub_info.Gender[0]))
    doc.append('\nUH Id: '+str(sub_info.UHID[0]))
    doc.append('\nDate: '+d2)
    doc.append(LineBreak())
    doc.append(NoEscape(r"\noindent\rule{\textwidth}{1pt}"))
    doc.append(NewLine())
    doc.append(LineBreak())

    with doc.create(MiniPage(align='c')):
        doc.append(LargeText(bold('Vowel Triangle Analysis Report')))
    
# Analysis result and image

with doc.create(Section('Vowel Triangle Analysis')):
    with doc.create(Figure(position='h!')) as img_plot:
        img_plot.add_image(img1, width='300px')
        img_plot.add_caption('Vowel Triangle PLot')
    with doc.create(Subsection('Vowel Triangle')):
        doc.append('Area : '+str(area))
    doc.append(NoEscape(r"\pagebreak[4]"))

# saving the pdf and tex

doc.generate_pdf(filepath='media/VT.report1', clean_tex=False)


