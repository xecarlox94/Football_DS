# -*- coding: utf-8 -*-
"""
Created on Wed Jun 24 15:36:13 2020

@author: jf94u
"""

import matplotlib.pyplot as plt
from matplotlib.patches import Arc


def createPitch( width=130, height=90, spotSize = 0.3, lineColor = "black"):
    halfWidth = width/2
    halfHeight = height/2
    penDistance = 11
    penArcSz = 18.3
    centerCircleSz = 9
    
    boxSize = (40, 16.5)
    smBoxSize = (18, 5.5)
    goalSize = (10,1.5)
    
    
    goalPosts = (halfHeight - (goalSize[0]/2), halfHeight + (goalSize[0]/2))
    boxSideEdges = (halfHeight - (boxSize[0]/2), halfHeight + (boxSize[0]/2))
    smBoxSideEdges = (halfHeight - (smBoxSize[0]/2), halfHeight + (smBoxSize[0]/2))

    fig = plt.figure()
    ax = fig.add_subplot(1,1,1)
    
    #main box
    plt.plot([-halfWidth, -halfWidth],[-halfHeight, halfHeight], color=lineColor)
    plt.plot([-halfWidth, halfWidth], [halfHeight, halfHeight], color=lineColor)
    plt.plot([halfWidth, halfWidth], [halfHeight, -halfHeight], color=lineColor)
    plt.plot([halfWidth, -halfWidth], [-halfHeight,-halfHeight], color=lineColor)
    plt.plot([0, 0], [-halfHeight,height-halfHeight], color=lineColor)
    
    
    #left box
    plt.plot([boxSize[1] -halfWidth, boxSize[1] -halfWidth], [boxSideEdges[1]-halfHeight, boxSideEdges[0]-halfHeight], color=lineColor)
    plt.plot([-halfWidth, boxSize[1] -halfWidth], [boxSideEdges[1]-halfHeight, boxSideEdges[1]-halfHeight], color=lineColor)
    plt.plot([boxSize[1]-halfWidth, -halfWidth], [boxSideEdges[0]-halfHeight, boxSideEdges[0]-halfHeight], color=lineColor)
    leftArc = Arc((penDistance - halfWidth, 0), height=penArcSz, width=penArcSz, angle=0, theta1=310, theta2=50,color=lineColor)
    
    
    #right box
    plt.plot([halfWidth, halfWidth - boxSize[1]], [boxSideEdges[1] -halfHeight, boxSideEdges[1] -halfHeight], color=lineColor)
    plt.plot([halfWidth - boxSize[1], halfWidth - boxSize[1]], [boxSideEdges[1] -halfHeight, boxSideEdges[0] -halfHeight], color=lineColor)
    plt.plot([halfWidth - boxSize[1], halfWidth], [boxSideEdges[0] -halfHeight, boxSideEdges[0] -halfHeight], color=lineColor)
    rightArc = Arc((halfWidth - penDistance, 0), height=penArcSz, width=penArcSz, angle=0, theta1=130, theta2=230, color=lineColor)
    
    
    #left small box
    plt.plot([-halfWidth, smBoxSize[1] -halfWidth], [smBoxSideEdges[1] -halfHeight,smBoxSideEdges[1] -halfHeight], color=lineColor)
    plt.plot([smBoxSize[1] -halfWidth, smBoxSize[1] -halfWidth], [smBoxSideEdges[1] -halfHeight, smBoxSideEdges[0] -halfHeight], color=lineColor)
    plt.plot([smBoxSize[1] -halfWidth, -halfWidth], [smBoxSideEdges[0] -halfHeight, smBoxSideEdges[0] -halfHeight], color=lineColor)
    
    
    #right small box
    plt.plot([halfWidth, halfWidth - smBoxSize[1]], [smBoxSideEdges[1] -halfHeight,smBoxSideEdges[1] -halfHeight], color=lineColor)
    plt.plot([halfWidth - smBoxSize[1], halfWidth - smBoxSize[1]], [smBoxSideEdges[1] -halfHeight, smBoxSideEdges[0] -halfHeight], color=lineColor)
    plt.plot([halfWidth - smBoxSize[1], halfWidth], [smBoxSideEdges[0] -halfHeight, smBoxSideEdges[0] -halfHeight], color=lineColor)
    
    #left goal
    plt.plot([-halfWidth, -goalSize[1] -halfWidth], [goalPosts[1] -halfHeight,goalPosts[1] -halfHeight], color=lineColor)
    plt.plot([-goalSize[1] -halfWidth, -goalSize[1] -halfWidth], [goalPosts[1] -halfHeight, goalPosts[0] -halfHeight], color=lineColor)
    plt.plot([-goalSize[1] -halfWidth, -halfWidth], [goalPosts[0] -halfHeight, goalPosts[0] -halfHeight], color=lineColor)
    
    #right goal
    plt.plot([halfWidth + goalSize[1], halfWidth], [goalPosts[1] -halfHeight, goalPosts[1] -halfHeight], color=lineColor)
    plt.plot([halfWidth + goalSize[1], halfWidth + goalSize[1]], [goalPosts[1] -halfHeight, goalPosts[0] -halfHeight], color=lineColor)
    plt.plot([halfWidth, halfWidth + goalSize[1]], [goalPosts[0] -halfHeight, goalPosts[0] -halfHeight], color=lineColor)
    
    
    #center circle
    centerCircle = plt.Circle((0, 0), centerCircleSz, color=lineColor, fill=False)
    
    #spots
    centerSpot = plt.Circle((0, 0), spotSize, color=lineColor)
    leftPenSpot = plt.Circle((penDistance -halfWidth, 0), spotSize, color=lineColor)
    rightPenSpot = plt.Circle((halfWidth - penDistance, 0), spotSize, color=lineColor)
    
    #adding patches
    ax.add_patch(centerCircle)
    ax.add_patch(centerSpot)
    ax.add_patch(leftArc)
    ax.add_patch(rightArc)
    ax.add_patch(leftPenSpot)
    ax.add_patch(rightPenSpot)
    
    plt.axis('off')
    
    pitchDimen = (width,height)
    figaxplt = (fig, ax, plt)
    
    return figaxplt, pitchDimen

createPitch()