# !/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  Syntax: python storage.py <path to folder images> <diameter of scalemarker> <blunder size=4000>
#  
#  This program is free software; you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation; either version 2 of the License, or
#  (at your option) any later version.
#  
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#  
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software
#  Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston,
#  MA 02110-1301, USA.
#  
#

'''
External library imports
'''
import matplotlib.patches as mpatches
import matplotlib.pyplot as plt
import numpy as np
from skimage import io
from skimage.color import label2rgb
from skimage.filters import threshold_otsu
from skimage.measure import label
from skimage.measure import regionprops
from skimage.morphology import medial_axis, opening, closing
from skimage.morphology import square
from skimage.segmentation import clear_border
from skimage.transform import resize

'''
Python library imports
'''
import csv
import os
import sys

'''
Funtions
'''


def extractTraits(labelImg, rootIdx, d, mm):
    medialAxisImg = np.zeros_like(labelImg, dtype=float)
    medialAxisImg[np.where(labelImg == rootIdx)] = labelImg[np.where(labelImg == rootIdx)]
    s = medialAxisImg.shape
    medialAxisImgSmall = resize(medialAxisImg.copy(), (100, int(float(s[1]) / float(s[0]) * 100)))

    # Compute the medial axis (skeleton) and the distance transform for the root object
    medialAxisImg = opening(medialAxisImg)
    medialAxisImg = closing(medialAxisImg)
    medialAxisImgSmall = opening(medialAxisImgSmall)
    medialAxisImgSmall = closing(medialAxisImgSmall)
    skel, distance = medial_axis(medialAxisImg, return_distance=True)
    skelSmall, distanceSmall = medial_axis(medialAxisImgSmall, return_distance=True)
    dist_on_skel = distance * skel
    dist_on_skelSmall = resize(distanceSmall * skelSmall, s)
    skelList = np.where(dist_on_skelSmall == 0)
    dist_on_skel[skelList] = 0
    dist_on_skel = pruneMA(dist_on_skel)
    diameterPos = np.where(dist_on_skel > 0)
    try:
        testArr = dist_on_skel[diameterPos]
        radius = np.median(dist_on_skel[diameterPos])
        radius = (radius / d) * mm
    except:
        radius = 0.
        length = 0.
    try:
        length = len(dist_on_skel[diameterPos]) + dist_on_skel[diameterPos][0] + dist_on_skel[diameterPos][
            len(dist_on_skel[diameterPos]) - 1]
        length = (length / d) * mm
    except:
        length = 0.
        radius = 0.
    volume = 0.
    if length > 0:
        height = 1  # relace with scaled pixel value
        for i in dist_on_skel[diameterPos]:
            try:
                volume += np.pi * ((float(i) / d) * mm) * ((float(height) / d) * mm)
            except:
                volume = 0
                print('VOLUME ERROR')

    if volume > 0:
        volumeArr.append(volume)
        lengthArr.append(length)
        diameterArr.append(radius)
    else:
        print(length, radius)


def pruneMA(MAimg):
    # positions of the MA
    pos = np.where(MAimg > 0)
    oneConnectedEnds = []
    for i in zip(pos[0], pos[1]):
        if MAimg[i[0], i[1]] < np.max(MAimg) / 1.5:
            MAimg[i[0], i[1]] = 0
    # Loop through MA
    for i in zip(pos[0], pos[1]):
        count = 0
        for j in (-1, 0, 1):
            for k in (-1, 0, 1):
                try:
                    if MAimg[i[0] + j, i[1] + k] > 0:
                        if j != 0 or k != 0:
                            count += 1
                except:
                    pass
        if count == 1:
            oneConnectedEnds.append(i)
    collect = []
    for idx, i in enumerate(oneConnectedEnds):
        MAimg[i[0], i[1]] = 0
        for j in (-1, 0, 1):
            for k in (-1, 0, 1):
                try:
                    if MAimg[i[0] + j, i[1] + k] > 0:
                        if j != 0 or k != 0:
                            collect.append((i[0] + j, i[1] + k))
                except:
                    pass
        if len(collect) == 1:
            oneConnectedEnds.append(collect[0])
        collect = []

    return MAimg


'''
Execution of the program
'''
print('------------------------------------------------------------------------')
print('DIRT/storage')
print('------------------------------------------------------------------------')
print('Syntax: python storage.py <path > <diameter> <blunder>')
print('------------------------------------------------------------------------')
print('path: path to storage root images')
print('diameter: diameter of the scale marker')
print('blunder: min. number of pixels in connected components (standard = 4000)')
print('------------------------------------------------------------------------')
print('Publication to cite: https://doi.org/10.1002/ppp3.10130')
print('------------------------------------------------------------------------')
f = sys.argv[1]
path = os.path.dirname(os.path.abspath(f))
print('---------')
print(f)
print(path)
print(os.path.dirname(f))
print('---------')
mm = float(sys.argv[2])
skipIt = 4000
try:
    skipIt = int(sys.argv[3])
except:
    pass

# fileList=glob.glob(path+'/*tubers*')
diameter = 0
volumeArr = []
lengthArr = []
diameterArr = []
tuberID = []
imgName = []

image = io.imread(f, as_gray=True, plugin="matplotlib")
# apply threshold
thresh = threshold_otsu(image)
bw = closing(image > thresh, square(3))

# remove artifacts connected to image border
cleared = bw.copy()
clear_border(cleared)

# label image regions
label_image = label(cleared)
image_label_overlay = label2rgb(label_image, image=image)
regions = regionprops(label_image)
for i in regions:
    if i.area < skipIt:
        continue
    elif i.eccentricity < 0.5:  # Circle
        diameter = i.equivalent_diameter
        print('Diameter of Circle:' + str(diameter))

for i in regions:
    if i.area < skipIt:
        continue
    elif i.eccentricity < 0.8:  # Circle
        continue
    elif np.linalg.norm(i.orientation) < 0.7:  # Tag
        continue
    else:
        extractTraits(label_image, i.label, diameter, mm)
        tuberID.append(str(i.label))
        imgName.append(f)
plt.figure(1)
plt.clf()
fig, ax = plt.subplots(ncols=1, nrows=1, figsize=(6, 6))
ax.imshow(image_label_overlay)
for region in regions:
    # skip small images
    if region.area < skipIt:
        continue
    elif region.eccentricity < 0.8:  # Circle
        continue
    elif np.linalg.norm(region.orientation) < 0.7:  # Tag
        continue
    # draw rectangle around segmented coins
    minr, minc, maxr, maxc = region.bbox
    rect = mpatches.Rectangle((minc, minr), maxc - minc, maxr - minr,
                              fill=False, edgecolor='red', linewidth=2)
    ax.add_patch(rect)
print("save segmentation")
plt.savefig(os.path.join(os.path.dirname(path), os.path.splitext(os.path.basename(f))[0] + '_segmentation.jpg'))
plt.close()

allValues = [['Length (mean)', 'Length (std)', 'Volume (mean)', 'Volume (std)', 'Diameter (mean)', 'Diameter (std)'],
             [np.average(lengthArr), np.std(lengthArr), np.average(volumeArr), np.std(volumeArr, ddof=1),
              np.average(diameterArr), np.std(diameterArr, ddof=1)]]
with open(os.path.join(os.path.dirname(path), 'all.csv'), 'w') as csvFile:
    writer = csv.writer(csvFile, delimiter=',')
    writer.writerows(allValues)

header = ['Image', 'Tuber ID', 'Length', 'Volume', 'Diameter']
with open(os.path.join(os.path.dirname(path), 'allSingle.csv'), 'w') as csvFile:
    writer = csv.writer(csvFile, delimiter=',')
    writer.writerow(header)
    for idx in range(len(lengthArr)):
        writer.writerow([imgName[idx], tuberID[idx], lengthArr[idx], volumeArr[idx], diameterArr[idx]])
