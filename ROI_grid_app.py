# -*- coding: utf-8 -*-
"""
Created on Wed Jan 02 11:33:12 2019

@author: pmoran
"""

import os

try:
	# Python 3
	from Tkinter import * 					
except:
	# Python 2
	from tkinter import * 					

try:
	# Python 3
	import tkinter as tk 					
except:
	# Python 2
	import Tkinter as tk 					

try:
	# Python 3
    from tkinter import messagebox			
except:
    # Python 2
    import tkMessageBox as messagebox 		

from PIL import ImageTk 
from PIL import Image
import matplotlib.pyplot as plt
import argparse
import io

parser = argparse.ArgumentParser()

parser.add_argument("-img","--image_path",default=os.path.join(os.getcwd(),'RV.bmp'),help="Please specify full or relative paths to Image")    #made change
parser.add_argument("-s","--step_size",type=int,default=32,choices=[16,32,64],help="Size of the grid")                                         #made change
args = parser.parse_args()                                                                                                                     #made change

# Set the path to the image(s)
path_to_images = args.image_path                                                                                                               #made change

raw_image = plt.imread(path_to_images)							
poly_coords = []

if os.path.exists("ROI_Config.txt"):
  os.remove("ROI_Config.txt")
else:
  print("The file does not exist")
  
#Define grid height and width of the grid in pixels
height = raw_image.shape[0]
width =  raw_image.shape[1]
y_end, x_end = height, width
x_start, y_start = 0, 0
    
#Define step size of grid in pixels i.e. 32x32 tiles
step_size = args.step_size                                                                                                                     #made change
  
def num_round(x, base=5):
    return int(base * round(float(x)/base))

def DisplayImage(self):
    """This function loads the image and overlays the grid upon it
    """
    global cam_pic
    global line
    global poly
    
    #first add image to canvas
    img = Image.fromarray(raw_image)
    cam_pic = ImageTk.PhotoImage(img)
    cam_map = canvas.create_image(0, 0, image=cam_pic, anchor=NW)
    canvas.itemconfigure(cam_map, image=cam_pic)
    
    for x in range(0, width, step_size):
        line = canvas.create_line(x, y_start, x, y_end, fill="cyan", width=2)

    for y in range(0, height, step_size):
        line = canvas.create_line(x_start, y, x_end, y, fill="cyan", width=2)
        
def SaveImage(self):                                                    
   if messagebox.askokcancel("Quit", "Do you really wish to quit?"):        
        ps = canvas.postscript(colormode='color')                       
        img = Image.open(io.BytesIO(ps.encode('utf-8')))                
        img.save('Roi_display.png', 'png')                              
        root.destroy()                                                     
        

def DrawPoly(event):
    """This function interactively draws the polyline (ROI) onto the grid
    """
    global cam_pic
    global line
    global poly
         
    poly_coords.append((num_round(event.x,step_size), num_round(event.y,step_size)))
    DisplayImage(event)                                                       #Added this line to reload image and grid.
    poly = canvas.create_polygon(poly_coords, outline='red', fill='', width=3)
    print("clicked at:", num_round(event.x,step_size), num_round(event.y,step_size))

    #Append the x and y coordinates of the polyline to file
    with open("ROI_Config.txt", "a+") as text_file:
        text_file.write('<xp_{}>{:.02f}</xp_{}>\n'.format(len(poly_coords), num_round(event.x,step_size), len(poly_coords)))           #made change
        text_file.write('<yp_{}>{:.02f}</yp_{}>\n'.format(len(poly_coords), num_round(event.y,step_size), len(poly_coords)))            #made change
        text_file.write('<zp_{}>{:.02f}</zp_{}>\n'.format(len(poly_coords), 0.00, len(poly_coords)))                                 #made change               
        text_file.close()
        
"""
Create a frame and canvas (size in pixels) for each ROI
"""
root = Tk()
root.title('ROI App')
root.protocol("WM_DELETE_WINDOW", SaveImage)

frame = Frame(root)
frame.pack(expand=YES,fill=BOTH)
canvas = Canvas(frame,width=0, height=0, bg='navy')
canvas.pack(expand=YES,fill=BOTH, side = LEFT)

#Add help function to explain the use of the GUI
def helpCallBack():
   messagebox.showinfo( "HELP for ROI Configuration", "INSTRUCTION: \n Left-click: Draws/adds the next point of the polygon \n\n RULES: \n 1. Points must be placed at one of the corners of blue tiles \n 2. First point must be placed near the bottom left of grid \n 3. Continue drawing polygon until desired area is covered \n 4. Last point must be placed near the bottom right of grid \n 5. When finished hit the return key. Click 'OK' and the canvas will be saved as a .png") #made change
B = Button(root, text ="HELP", command = helpCallBack)
B.pack(side=TOP)

"""
DEFINE SIZE OF INPUT OVIEW IMAGE (WIDTH x HEIGHT)
"""
frame_shape = str(width)+'x'+str(height)
#frame_shape = '1200x650'                                                                                
root.wm_geometry(frame_shape)                                                                                               

"""
Overlay the grid onto the input image and draw the polyline ROI
"""
canvas.bind("<Button-3>", DisplayImage)
canvas.bind_all("<Return>", SaveImage)
canvas.bind("<Button-1>", DrawPoly)

# run it ...
root.mainloop()