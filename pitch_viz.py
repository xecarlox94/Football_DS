# -*- coding: utf-8 -*-
"""
Created on Wed Jun 24 15:36:13 2020

@author: jf94u
"""

import matplotlib.pyplot as plt
from matplotlib.patches import Arc

def createPitch():

    fig = plt.figure()
    ax = fig.add_subplot(1,1,1)
    
    #main box
    plt.plot([0, 0],[0, 90], color="black")
    plt.plot([0, 130], [90, 90], color="black")
    plt.plot([130, 130], [90, 0], color="black")
    plt.plot([130, 0], [0,0], color="black")
    plt.plot([65, 65], [0,90], color="black")
    
    
    #left box
    plt.plot([16.5, 16.5], [65, 25], color="black")
    plt.plot([0, 16.5], [65, 65], color="black")
    plt.plot([16.5, 0], [25, 25], color="black")
    leftArc = Arc((11, 45), height=18.3, width=18.3, angle=0, theta1=310, theta2=50,color="black" )
    
    
    #right box
    plt.plot([130, 113.5], [65, 65], color="black")
    plt.plot([113.5, 113.5], [65, 25], color="black")
    plt.plot([113.5, 130], [25, 25], color="black")
    rightArc = Arc((119,45), height=18.3, width=18.3, angle=0, theta1=130, theta2=230, color="black")
    
    
    
    #left 6 yard box
    plt.plot([0, 5.5], [54,54], color="black")
    plt.plot([5.5, 5.5], [54, 36], color="black")
    plt.plot([5.5, 0], [36, 36], color="black")
    
    #left goal
    plt.plot([0, -1.5], [50,50], color="black")
    plt.plot([-1.5, -1.5], [50, 40], color="black")
    plt.plot([-1.5, 0], [40, 40], color="black")
    
    
    #right 6 yard box
    plt.plot([130, 124.5], [54,54], color="black")
    plt.plot([124.5, 124.5], [54, 36], color="black")
    plt.plot([124.5, 130], [36, 36], color="black")
    
    
    #right goal
    plt.plot([131.5, 130], [50, 50], color="black")
    plt.plot([131.5, 131.5], [50, 40], color="black")
    plt.plot([130, 131.5], [40, 40], color="black")
    
    
    #center circle
    centerCircle = plt.Circle((65, 45), 13, color="black", fill=False)
    
    #spots
    centerSpot = plt.Circle((65, 45), 0.8, color="black")
    leftPenSpot = plt.Circle((11, 45), 0.8, color="black")
    rightPenSpot = plt.Circle((119, 45), 0.8, color="black")
    
    
    
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
    
createPitch()