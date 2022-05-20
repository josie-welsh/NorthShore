import argparse
import os
from typing import OrderedDict
import pandas as pd
import geopandas as gpd
import numpy as np
from matplotlib import pyplot as plt
import sys
from scipy.optimize import curve_fit

######################################
# CREATE DFs WITH FOR SEGS AND NODES #
######################################

input_segments = "/home/josie/Desktop/Northshore_Data/CityofDuluth/CityofDuluth_Basin5.gpkg"
input_nodes = "/home/josie/Desktop/Northshore_Data/CityofDuluth/CityofDuluth_Basin5_nodes.gpkg"

input_segment_id = 9
outbase='plot_tmp'
outfmt = 'png'
_plot_ksn = True
_plot_show = True

# READ INPUT 

dfsegs = gpd.read_file(input_segments)
dfnodes = gpd.read_file(input_nodes)

    #Find out if the input segment is in the segments dataframe.
input_segment_id_found = False
for seg_id in dfsegs['id']:
    if seg_id == input_segment_id:
        input_segment_id_found = True
        print("Segment ID found.")

    if not input_segment_id_found:
        print("Error: No segment with the given ID")


#Begin to generate path.
#convert input to int
input_segment_id= int(input_segment_id)

#Look up user input seg id, create column is_input w/true and false
dfsegs['is_input'] = np.where(dfsegs['id']== input_segment_id, True, False)

#Create new df called dfpath that is populated by all the true values.
dfpath = dfsegs[dfsegs['is_input'] == True]


#Create the path
#Set input_toseg to the input_segment_id
#Does this generate a duplicate of the first segment?
input_toseg = input_segment_id
while input_toseg != -1:
    #find relevant toseg
    input_toseg=dfpath.loc[dfpath['id']== input_segment_id, 'toseg']
    #convert to int
    input_toseg=int(input_toseg)
    #query dfsegs to find the segment with the same id as toseg
    dfsegs['is_input'] = np.where(dfsegs['id']== input_toseg, True, False)
    #take this line ad append it to dfpath
    dfpath = dfpath.append(dfsegs[dfsegs['is_input'] == True])
    input_segment_id = input_toseg
    #print(dfpath)

#Begin pulling required nodes from segments
#Create list of relevant segments
queried_segments = []
queried_segments_idx = []
for seg_id in dfpath['id']:
    queried_segments.append(seg_id)
    queried_segments_idx.append(dfsegs.index[dfsegs['id'] == seg_id][0])

#Create list of df entries for relevant nodes in queried_segments
"""
# Approach querying the network
path_nodes=[]
for _id in queried_segments:
    _seg = dfsegs.geometry[dfsegs['id'] == _id]
    _xyz = np.array(_seg[_seg.index[0]].coords[:])
    _
"""
    
# Approach with nodes already printed
path_nodes=[]
for _id in queried_segments:
    path_nodes.append(dfnodes[dfnodes['segment_id'] == _id] )

#Create a df with relevant nodes in path
dfpath_nodes = pd.concat(path_nodes, ignore_index=True)


#Add slope for each point along path
slopes = []
for i in range(len(dfpath_nodes)):
    for j in range(len(dfsegs)):
        if dfsegs['id'].iloc[j] == dfpath_nodes['segment_id'].iloc[i]:
            slopes.append(dfsegs['slope'].iloc[j])

slopes_s = pd.Series(slopes)

dfpath_nodes = dfpath_nodes.assign(slope = slopes_s)

##################
# CREATE A MODEL #
##################

#Step 1: Find values for ks and theta
#power law:
def power_law(drainage_area, ks, theta):
    slope = ks*(drainage_area**(-theta))
    return slope

#create a list of drainage areas for slope-area analysis
drainage_area_as = []
for i in range(len(dfpath_nodes)):
    if dfpath_nodes['drainage_area'][i] <= 7 * 10**6:
        da = float(dfpath_nodes['drainage_area'][i])
        drainage_area_as.append(da)

#create a list of slopes
slope = []
for i in range(len(dfpath_nodes)):
    if dfpath_nodes['drainage_area'][i] <= 7 * 10**6:
        sl = float(dfpath_nodes['slope'][i])
        slope.append(sl)

#find trendline in log-log space
# Fit the dummy power-law data
pars, cov = curve_fit(f=power_law, xdata=drainage_area_as, ydata=slope, p0=[0, 0], bounds=(-np.inf, np.inf))

ks = pars[0]
theta = pars[1]

#Step 2: Create a model of elevation along the path
'''
This is going to involve a few steps. 
1. model slope at each point using power law function
2. use modeled slope at each point to find the elevation
3. add these values to a new column in the dataframe
'''

#2.a. modeling slope at each point using a power law function
#create a power law function
def power_law(drainage_area, ks, theta):
    slope = ks*(drainage_area**(-theta))
    return slope

#create a list of drainage areas for modeling purposes
drainage_area = []
for i in range(len(dfpath_nodes)):
    da = float(dfpath_nodes['drainage_area'][i])
    drainage_area.append(da)

#model slopes 
slope_model = []
for i in range(len(dfpath_nodes)):
    sm = power_law(drainage_area[i], ks, theta)
    slope_model.append(sm)

#2.b. use modeled slopes to model elevation at each point
#use the function y = mx + b to calculate the elevation using slope, distance and initial point.

#find initial elevation:
initial_elevation = dfpath_nodes['elevation'][0]

#create a list of distances between each point
distance = []
for i in range(len(dfpath_nodes)):
    if i + 1 == len(dfpath_nodes):
        print('Done finding distances between nodes')
    else:
        di = dfpath_nodes['flow_distance'][i] - dfpath_nodes['flow_distance'][i+1]
        distance.append(di)

#create a list of elevation changes for each point
elevation_change = []
for i in range(len(distance)):
    ec = distance[i] * slope_model[i]
    elevation_change.append(ec)

#model elevation at each point
elevation = []
for i in range(len(elevation_change)):
    if i == 0:
        el = initial_elevation
    else:
        el = elevation[i-1] - elevation_change[i]
    
    elevation.append(el)
elevation.append(el)

#some quick plotting
fig, ax = plt.subplots()
plt.scatter(dfpath_nodes['flow_distance']/1000, dfpath_nodes['elevation'], label = 'River Long Profile')
plt.scatter(dfpath_nodes["flow_distance"]/1000, elevation, label = 'Modeled Long Profile Pre-Disturbance')
ax.set_xlabel("Distance Upstream (km)")
ax.set_ylabel("Elevation Above Mouth (m)")
leg = ax.legend()
fig.show()