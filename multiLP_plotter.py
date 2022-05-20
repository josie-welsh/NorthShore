import argparse
import os
from typing import OrderedDict
import pandas as pd
import geopandas as gpd
import numpy as np
from matplotlib import pyplot as plt
import sys

filelist = os.listdir(path='/home/josie/Desktop/Plotting_Code/TEST/test_data')

filelist.sort()

#create a dictionary to put all of the information about each basin and channel of interest
basins = {}

#A ditionary that we are going to fill in with path info
selected_channels = OrderedDict()


#print(filelist)

for file in filelist:
    if "nodes" not in file:
        #print(file)
        #fill the basins dictionary with information from the directory of basins
        
        #Name of the basin
        basins[file[:7]] = {}
        #path to segments file and nodes file, the value of the segment id that our selected basin begins at
        basins[file[:7]]['segments'] = '/home/josie/Desktop/Plotting_Code/TEST/test_data/' + file
        basins[file[:7]]['nodes'] = '/home/josie/Desktop/Plotting_Code/TEST/test_data/' + file[:7] + '_nodes.gpkg'
        basins[file[:7]]['seg_id'] = 0

#print(basins)

for i in basins: 
    input_segments = basins[i]['segments']
    input_nodes = basins[i]['nodes']
    input_segment_id = basins[i]['seg_id']
    river_name = basins[i]

    #print(input_segments)
    #print(input_nodes)

    outbase='plot_tmp'
    outfmt = 'png'
    _plot_ksn = True
    _plot_show = True


##############
# READ INPUT #
##############

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

    #Now have a df that has all the relevant segments, in order moving down path.

    #Begin pulling required nodes from segments
    #Create list of relevant segments
    queried_segments = []
    queried_segments_idx = []
    for seg_id in dfpath['id']:
        queried_segments.append(seg_id)
        queried_segments_idx.append(dfsegs.index[dfsegs['id'] == seg_id][0])
        
    # Approach with nodes already printed
    path_nodes=[]
    for _id in queried_segments:
        path_nodes.append(dfnodes[dfnodes['segment_id'] == _id] )

    #Create a df with relevant nodes in path
    dfpath_nodes = pd.concat(path_nodes, ignore_index=True)

    #print(dfpath_nodes)
    #print(river_name)
    #print(i)

    ##############################################################################################
    # Put these path nodes into a dictionary that can be called from later for plotting purposes #
    ##############################################################################################

    selected_channels[i] = dfpath_nodes

#print(selected_channels)



############
# Plotting #
############

colors =[]

plt.figure(figsize=(9,5))

k=0

for i in selected_channels:
    
    df = selected_channels[i]
    print(i)
    #print(df)

    # Only one (selected) long profile
    if _plot_ksn:
        plt.plot((df['flow_distance']/1000), df['elevation'], '.5', linewidth=4)
        #sc = plt.scatter((df['flow_distance']/1000), df['elevation'], c=np.log10(df['m_chi']), cmap='magma', vmin= 0, vmax = 4, s=16, zorder=999999)
        sc = plt.scatter((df['flow_distance']/1000), df['elevation'], c=colors[k], vmin= 0, vmax = 4, s=16, zorder=999999)

    else:
        plt.plot((df['flow_distance']/1000), df['elevation'], 'k-', linewidth=4)

    k+=1

    #plt.gca().invert_xaxis()
    plt.xlabel("'Upchannel Distance [km]'", fontsize=16)
    plt.ylabel('Elevation Above Mouth [m]', fontsize=16)
    plt.tight_layout()

    if outbase is not None:
        plt.savefig(outbase+'_LongProfile.'+outfmt, dpi=300,
                facecolor='w', edgecolor='w',
                orientation='portrait', transparent=False)

if _plot_ksn == True:
    cbar = plt.colorbar(sc)
    cbar.set_label(label='log$_{10} (k_{sn})$', fontsize=16)


if _plot_show:
    plt.show()
