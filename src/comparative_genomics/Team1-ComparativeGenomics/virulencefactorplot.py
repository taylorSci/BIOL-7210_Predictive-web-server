# -*- coding: utf-8 -*-
"""
Created on Sun Apr 25 17:27:14 2021

@author: gargi
"""

import optparse
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import re

#options----------------------------------------------
parser = optparse.OptionParser()
parser.add_option('-i', '--input_file', action="store", type="string", help = 'input directory', dest = 'i')
parser.add_option('-o', '--output_file', action="store", type="string", help = 'output directory', dest = 'o')
(options, args) = parser.parse_args()


#read in csv to data frame----------------------------
df = pd.read_csv(options.i, sep='\t')
isolates = []
for row in df.index:
     x = re.search("/([^/]*)$", row)
     isolates.append(x.group())
np.asarray(isolates)
print(isolates)
values = df.loc[ : , df.columns != ' ']
values = values.isnull()
val = (np.asarray(values))


#convert to binary values---------------------------
binary=[]
for i in val:
    row=[]
    for j in i:
        if j == True:
            row.append(0)
        if j == False:
            row.append(1)
    binary.append(row)      
binarray = np.asarray(binary)


#generate heatmap----------------------------------
from matplotlib import colors
cmap = colors.ListedColormap(['red', 'green'])
fig, ax = plt.subplots()
im = ax.imshow(binarray, cmap=cmap)

ax.set_xticks(np.arange(len(df.columns)))
ax.set_yticks(np.arange(len(isolates)))

ax.set_xticklabels(df.columns)
ax.set_yticklabels(isolates)


#adjust font size according to number of isolates--
plt.xticks(fontsize=4)
if len(isolates) <= 15:
    plt.yticks(fontsize=8)
if len(isolates) > 15:
    plt.yticks(fontsize=4)

plt.setp(ax.get_xticklabels(), rotation=90, ha="right",
         rotation_mode="anchor")


#adjust plot size---------------------------------
fig.set_size_inches(15, 4, forward=True)
plt.savefig(options.o + '.png', bbox_inches = 'tight')
