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
print("dodo")

image_fullpath = sys.argv[1]
image_path = sys.argv[2]
prediction= sys.argv[3]

# add the audio start and end time infomation of the subject
subjectInfoSave = 'media/subjectInfo.csv'
sub_info = pd.read_csv(subjectInfoSave)



def measurePitch(voiceID, f0min, f0max, unit):
    sound = parselmouth.Sound(voiceID) # read the sound
    duration = call(sound, "Get total duration") # duration
    pitch = call(sound, "To Pitch", 0.0, f0min, f0max) #create a praat pitch object
    meanF0 = call(pitch, "Get mean", 0, 0, unit) # get mean pitch
    stdevF0 = call(pitch, "Get standard deviation", 0 ,0, unit) # get standard deviation
    harmonicity = call(sound, "To Harmonicity (cc)", 0.01, 75, 0.1, 1.0)
    hnr = call(harmonicity, "Get mean", 0, 0)
    return meanF0, stdevF0, hnr, duration
file_list = []
mean_F0_list = []
sd_F0_list = []
hnr_list = []

# Go through all the wave files in the folder and measure pitch
sound = parselmouth.Sound(str(image_fullpath))
sound = sound.extract_part(from_time=sub_info.audio_ST, to_time=sub_info.audio_ET, preserve_times=True)


(meanF0, stdevF0, hnr, duration) = measurePitch(sound, 75, 600, "Hertz")
file_list.append(str(image_path)) # make an ID list
mean_F0_list.append(meanF0) # make a mean F0 list
sd_F0_list.append(stdevF0) # make a sd F0 list
hnr_list.append(hnr)

df = pd.DataFrame(np.column_stack([file_list, mean_F0_list, sd_F0_list, hnr_list]), 
                               columns=['voiceID', 'meanF0Hz', 'stdevF0Hz', 'HNR'])  #add these lists to pandas in the right order


# Write out the updated dataframe
#df.to_html("media/test1.html")
print(df)

sns.set() # Use seaborn's default style to make attractive graphs
plt.rcParams['figure.dpi'] = 70 # Show nicely large images in this notebook

snd = parselmouth.Sound(str(image_fullpath))
snd = snd.extract_part(from_time=sub_info.audio_ST, to_time=sub_info.audio_ET, preserve_times=True)


def draw_pitch(pitch):
    # Extract selected pitch contour, and
    # replace unvoiced samples by NaN to not plot
    pitch_values = pitch.selected_array['frequency']
    pitch_values[pitch_values==0] = np.nan
    plt.plot(pitch.xs(), pitch_values, 'o', markersize=5, color='w')
    plt.plot(pitch.xs(), pitch_values, 'o', markersize=2)
    plt.grid(False)
    plt.ylim(0, pitch.ceiling)
    plt.ylabel("pitch values [Hz]")
    
pitch = snd.to_pitch()

# If desired, pre-emphasize the sound fragment before calculating the spectrogram
pre_emphasized_snd = snd.copy()
pre_emphasized_snd.pre_emphasize()
spectrogram = pre_emphasized_snd.to_spectrogram(window_length=0.03, maximum_frequency=8000)

fig = plt.figure()
draw_pitch(pitch)
plt.xlim([snd.xmin, snd.xmax])
plt.savefig('media/pitch.jpg')

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
sound = sound.extract_part(from_time=sub_info.audio_ST, to_time=sub_info.audio_ET, preserve_times=True)

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


sns.set() # Use seaborn's default style to make attractive graphs
plt.rcParams['figure.dpi'] = 70 # Show nicely large images in this notebook

#plt.scatter(x_data, y_data, c='r', label='data')
fig1 = plt.figure()
plt.plot(f1_list)
plt.plot(f2_list)
plt.savefig('media/formant.jpg')
 
fileSave = 'media/report.pdf'
documentTitle = 'Report'
subTitle= 'Audio File:'
img = 'pitch.jpg'
img1= 'formant.jpg'



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
        doc.append(LargeText(bold('Pitch and Formant Analysis Report')))
    
# Analysis result and image

with doc.create(Section('Audio wave-form and spectrogram')):
    with doc.create(Subsection('Wave-form of selected part of the audio signal')):
        doc.append(NoEscape(r"\begin{figure}[h!]%"))
        doc.append(NoEscape(r"\centering%"))
        doc.append(NoEscape(r"\includegraphics[width=400px, height=150px]{sound.png}%"))
        doc.append(NoEscape(r"\caption{Wave-Form Plot}%"))
        doc.append(NoEscape(r"\end{figure}"))

    with doc.create(Subsection('Spectrogram of selected part of the audio signal')):
        doc.append(NoEscape(r"\begin{figure}[h!]%"))
        doc.append(NoEscape(r"\centering%"))
        doc.append(NoEscape(r"\includegraphics[width=400px, height=150px]{spectrogram.png}%"))
        doc.append(NoEscape(r"\caption{Spectrogram Plot}%"))
        doc.append(NoEscape(r"\end{figure}"))        
    doc.append(NoEscape(r"\pagebreak[4]"))

with doc.create(Section('Pitch Analysis on the selected part')):
    with doc.create(Figure(position='h!')) as img_plot:
        img_plot.add_image(img, width='300px')
        img_plot.add_caption('Pitch Plot')
    with doc.create(Subsection('Pitch')):
        doc.append('Mean value : '+str(mean_F0_list[0]))
        doc.append('\nMedian value : '+str(sd_F0_list[0]))
    with doc.create(Subsection('Subject Gender prediction based on pitch analysis')):
        doc.append('Predicted Gender of the Subject is '+str(prediction))
    doc.append(NoEscape(r"\pagebreak[4]"))

with doc.create(Section('Formant Analysis on the selected part')):
    with doc.create(Figure(position='h!')) as img_plot:
        img_plot.add_image(img1, width='300px')
        img_plot.add_caption('Formant Plot')
    with doc.create(Subsection('First Formant')):
        doc.append('Mean value : '+str(f1_mean))
        doc.append('\nMedian value : '+str(f1_median))
    with doc.create(Subsection('Second Formant')):
        doc.append('Mean value : '+str(f2_mean))
        doc.append('\nMedian value : '+str(f2_median))


# saving the pdf and tex

doc.generate_pdf(filepath='media/PF.report1', clean_tex=True )

