#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Mar  3 14:51:58 2020

@author: kausthubha
"""

import parselmouth

import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

sns.set() # Use seaborn's default style to make attractive graphs
snd = parselmouth.Sound("/media/kausthubha/New Volume/Pavan_Kumar_backup/takeit/media/mediafile_SLfNM1G.mp3")

plt.figure()
plt.plot(snd.xs(), snd.values.T[:,1])
plt.xlim([snd.xmin, snd.xmax])
plt.xlabel("time [s]")
plt.ylabel("amplitude")
plt.show() # or plt.savefig("sound.png"), or plt.savefig("sound.pdf")



