# -*- coding: utf-8 -*-
"""
Created on Wed Jun 24 15:36:13 2020

@author: jf94u
"""

import matplotlib.pyplot as plt
from matplotlib.patches import Arc

def createPitch( width=130, height=90, spotSize = 0.7, lineColor = "black"):
    halfWidth = width/2
    halfHeight = height/2
    penDistance = 11
    penArcSz = 18.3
    centerCircleSz = 15
    
    boxSize = (40, 16.5)
    smBoxSize = (18, 5.5)
    goalSize = (10,1.5)
    
    
    goalPosts = (halfHeight - (goalSize[0]/2), halfHeight + (goalSize[0]/2))
    boxSideEdges = (halfHeight - (boxSize[0]/2), halfHeight + (boxSize[0]/2))
    smBoxSideEdges = (halfHeight - (smBoxSize[0]/2), halfHeight + (smBoxSize[0]/2))

    fig = plt.figure()
    ax = fig.add_subplot(1,1,1)
    
    #main box
    plt.plot([0, 0],[0, height], color=lineColor)
    plt.plot([0, width], [height, height], color=lineColor)
    plt.plot([width, width], [height, 0], color=lineColor)
    plt.plot([width, 0], [0,0], color=lineColor)
    plt.plot([halfWidth, halfWidth], [0,height], color=lineColor)
    
    
    #left box
    plt.plot([boxSize[1], boxSize[1]], [boxSideEdges[1], boxSideEdges[0]], color=lineColor)
    plt.plot([0, boxSize[1]], [boxSideEdges[1], boxSideEdges[1]], color=lineColor)
    plt.plot([boxSize[1], 0], [boxSideEdges[0], boxSideEdges[0]], color=lineColor)
    leftArc = Arc((penDistance, halfHeight), height=penArcSz, width=penArcSz, angle=0, theta1=310, theta2=50,color=lineColor)
    
    
    #right box
    plt.plot([width, width - boxSize[1]], [boxSideEdges[1], boxSideEdges[1]], color=lineColor)
    plt.plot([width - boxSize[1], width - boxSize[1]], [boxSideEdges[1], boxSideEdges[0]], color=lineColor)
    plt.plot([width - boxSize[1], width], [boxSideEdges[0], boxSideEdges[0]], color=lineColor)
    rightArc = Arc((width - penDistance, halfHeight), height=penArcSz, width=penArcSz, angle=0, theta1=130, theta2=230, color=lineColor)
    
    
    #left small box
    plt.plot([0, smBoxSize[1]], [smBoxSideEdges[1],smBoxSideEdges[1]], color=lineColor)
    plt.plot([smBoxSize[1], smBoxSize[1]], [smBoxSideEdges[1], smBoxSideEdges[0]], color=lineColor)
    plt.plot([smBoxSize[1], 0], [smBoxSideEdges[0], smBoxSideEdges[0]], color=lineColor)
    
    
    #right small box
    plt.plot([width, width - smBoxSize[1]], [smBoxSideEdges[1],smBoxSideEdges[1]], color=lineColor)
    plt.plot([width - smBoxSize[1], width - smBoxSize[1]], [smBoxSideEdges[1], smBoxSideEdges[0]], color=lineColor)
    plt.plot([width - smBoxSize[1], width], [smBoxSideEdges[0], smBoxSideEdges[0]], color=lineColor)
    
    #left goal
    plt.plot([0, -goalSize[1]], [goalPosts[1],goalPosts[1]], color=lineColor)
    plt.plot([-goalSize[1], -goalSize[1]], [goalPosts[1], goalPosts[0]], color=lineColor)
    plt.plot([-goalSize[1], 0], [goalPosts[0], goalPosts[0]], color=lineColor)
    
    #right goal
    plt.plot([width + goalSize[1], width], [goalPosts[1], goalPosts[1]], color=lineColor)
    plt.plot([width + goalSize[1], width + goalSize[1]], [goalPosts[1], goalPosts[0]], color=lineColor)
    plt.plot([width, width + goalSize[1]], [goalPosts[0], goalPosts[0]], color=lineColor)
    
    
    #center circle
    centerCircle = plt.Circle((halfWidth, halfHeight), centerCircleSz, color=lineColor, fill=False)
    
    #spots
    centerSpot = plt.Circle((halfWidth, halfHeight), spotSize, color=lineColor)
    leftPenSpot = plt.Circle((penDistance, halfHeight), spotSize, color=lineColor)
    rightPenSpot = plt.Circle((width - penDistance, halfHeight), spotSize, color=lineColor)
    
    #adding patches
    ax.add_patch(centerCircle)
    ax.add_patch(centerSpot)
    ax.add_patch(leftArc)
    ax.add_patch(rightArc)
    ax.add_patch(leftPenSpot)
    ax.add_patch(rightPenSpot)
    
    plt.axis('off')
    
    #render plot
    plt.show()
    
    return (fig, ax)
    
createPitch()