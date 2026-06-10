import os
import numpy as np
import math
import cv2
import tkinter as tk
from tkinter import filedialog

root = tk.Tk()
root.withdraw()
file_path = filedialog.askopenfilename()
citra = file_path

#Color Filter
def color_filter(image):
    image = cv2.GaussianBlur(image,(5,5),0)   
	#Convert to HLS, set the color threshold
    hls = cv2.cvtColor(image, cv2.COLOR_RGB2HLS) #===> RGB to BGR
    lower = np.array([0,0,35])     # [0,0,35]     [39,30,30]      0,190,0     #0,130,0     #56,99,0    #56,140,0      56,120,0 125
    upper = np.array([60,120,255])   # [60,120,255] [45,255,255]     255,255,255 #255,255,255 #255,161,51 #255,255,255
    
    #yellower = np.array([0,0,37]) #[10,0,90]    [63,55,75]    #[91,91,46]  #[91,91,90] #91,91,155
    #yelupper = np.array([86,112,255]) #[50,255,255] [255,255,255] #[255,255,255]
    
    #yellowmask = cv2.inRange(hls, yellower, yelupper)    
    colormask = cv2.inRange(hls, lower, upper)
    
    #mask = cv2.bitwise_or(yellowmask, whitemask)  
    #masked = cv2.bitwise_and(image, image, mask = mask)    
    masked = cv2.bitwise_and(image, image, mask = colormask)
    return masked

#Region of Interest
def roi(img):
    x = int(img.shape[1])
    y = int(img.shape[0])
    ax = 0.0 #0
    ay = 0.95
    bx = 1 #1
    by = ay
    cx = 1 #0.7
    cy = 0.65 #0.8 0.6 0.4
    dx = 0 #0.3
    dy = cy
    shape = np.array([[int(ax*x), int(ay*y)], [int(bx*x), int(by*y)], [int(cx*x), int(cy*y)], [int(dx*x), int(dy*y)]]) #0.5
		
    #define a numpy array with the dimensions of img, but comprised of zeros
    mask = np.zeros_like(img)

    #Uses 3 channels or 1 channel for color depending on input image
    if len(img.shape) > 2:
        channel_count = img.shape[2]
        ignore_mask_color = (255,) * channel_count
    else:
        ignore_mask_color = 255

    #creates a polygon with the mask color
    cv2.fillPoly(mask, np.int32([shape]), ignore_mask_color)

    #returns the image only where the mask pixels are not zero
    masked_image = cv2.bitwise_and(img, mask)
    return masked_image

#Edge Detection
def grayscale(img):
    return cv2.cvtColor(img, cv2.COLOR_RGB2GRAY)

#Finding Lines
rightSlope, leftSlope, rightIntercept, leftIntercept = [],[],[],[]
def draw_lines(img, lines, thickness=5):
    global rightSlope, leftSlope, rightIntercept, leftIntercept
    rightColor=[0,255,100]
    leftColor=[255,0,0]
    centerColor=[0,255,0]
    y = int(img.shape[0])
    x = int(img.shape[1])
    cy = 0.65 #0.8
    ay = 0.95 
    #this is used to filter out the outlying lines that can affect the average
    #We then use the slope we determined to find the y-intercept of the filtered lines by solving for b in y=mx+b
    for line in lines:
        for x1,y1,x2,y2 in line:
		    #if (x1-x2) <> 0:
                try: 
                    slope = (y1-y2)/(x1-x2) #HATI1 pembagian dg NOL, jika x1 dan x2 sama2 tdk diketahui
                    #print ('slope=',slope)
                    if slope > 0.3:
                        if x1 > (int(x/2)):#903 : #500 (640-64) 320
                            yintercept = y2 - (slope*x2)                    
                            rightSlope.append(slope)
                            rightIntercept.append(yintercept)
                        else: None                
                    elif slope < -0.3:
                        if x1 < (int(x/2)) : #1018: #600 640 320
                            yintercept = y2 - (slope*x2)                    
                            leftSlope.append(slope)
                            leftIntercept.append(yintercept)    
                        else: None
                except ZeroDivisionError:
                    #print ('Error Pembagian Dengan NOL')
                    pass
		    #else: None		
                    
    leftavgSlope = np.mean(leftSlope[-30:])
    leftavgIntercept = np.mean(leftIntercept[-30:])
    
    rightavgSlope = np.mean(rightSlope[-30:])
    rightavgIntercept = np.mean(rightIntercept[-30:])
    
    
    #Here we plot the lines and the shape of the lane using the average slope and intercepts
    try:
        left_line_x1 = int((cy*img.shape[0] - leftavgIntercept)/leftavgSlope) #0.58 0.735
        #print ('leftX1=', left_line_x1)
        left_line_x2 = int((ay*img.shape[0] - leftavgIntercept)/leftavgSlope)
        #print ('leftX2=', left_line_x2)
    
        right_line_x1 = int((cy*img.shape[0] - rightavgIntercept)/rightavgSlope) #0.735
        #print ('rightX1=', right_line_x1)
        right_line_x2 = int((ay*img.shape[0] - rightavgIntercept)/rightavgSlope)
        #print ('rightX2=', right_line_x2)

        pts = np.array([[left_line_x1, int(cy*img.shape[0])],[left_line_x2, int(ay*img.shape[0])],[right_line_x2, int(ay*img.shape[0])],[right_line_x1, int(cy*img.shape[0])]], np.int32)
        pts = pts.reshape((-1,1,2))
        cv2.fillPoly(img,[pts],(0,0,255))      
        
        
        cv2.line(img, (left_line_x1, int(cy*img.shape[0])), (left_line_x2, int(ay*img.shape[0])), leftColor, 3) #10 0.735
        cv2.line(img, (right_line_x1, int(cy*img.shape[0])), (right_line_x2, int(ay*img.shape[0])), rightColor, 3) #10  0.735
        CL=int((right_line_x1 - left_line_x1)/2)+left_line_x1
        cv2.line(img, (CL,y), (CL,int(0.85*y)), centerColor, 5)
        selisih=int(CL-(x/2))
        #cv2.putText(img, "%s"% derajat(selisih), (60,60),cv2.FONT_HERSHEY_SIMPLEX, 1,(0,255,0),2) # ",%s"% untuk merubah numeric ke string
        #print ("sudut=",derajat(selisih)," deg")
        
    except ValueError as err:
            #I keep getting errors for some reason, so I put this here. Idk if the error still persists.
        #print('error nilai=',err)
        pass
        
def derajat(selisih):
    piksel = 0.2 #1 piksel berapa meter???
    jarak = 3 #jarak dari kamera ke titik acuan berapa meter?
    sudut = math.atan(selisih*piksel/jarak)*57.2958
    #sudut=re.sub(r'^(\d+\.\d{,2})\d*$',r'\1',str(sudut)) #merubah ke format 2 digit dibelakang point
    sudut = f"{sudut:.2f}"
    return sudut
                
def hough_lines(img, rho, theta, threshold, min_line_len, max_line_gap):
    """
    `img` should be the output of a Canny transform.
    """
    lines = cv2.HoughLinesP(img, rho, theta, threshold, np.array([]), minLineLength=min_line_len, maxLineGap=max_line_gap)
    if lines is not None:
        line_img = np.zeros((img.shape[0], img.shape[1], 3), dtype=np.uint8)
        draw_lines(line_img, lines)
        #print ('Ada hasil HL')
    else: 
        #print ('TIDAK ADA HASIL HL')
        line_img = np.zeros((img.shape[0], img.shape[1], 3), dtype=np.uint8)
        pass
    
    return line_img

#Overlaying the Image and the Lines
def weighted_img(img, initial_img, α=0.8, β=1., λ=0.):
    """
    initial_img * α + img * β + λ
    NOTE: initial_img and img must be the same shape!
    """
    return cv2.addWeighted(initial_img, α, img, β, λ)

#Applying it to Video
def processImage(image): 
	interest = roi(image)
	filtering = color_filter(interest)
	canny = cv2.Canny(grayscale(filtering), 50, 120) #interest
	myline = hough_lines(canny, 1, np.pi/180, 10, 37, 6) #10, 20, 5 #10,20,6
	weighted_img = cv2.addWeighted(myline, 1, image, 0.8, 0)
    
	return weighted_img #filtering #weighted_img canny

while True: #cap
    cap = cv2.imread(citra)
    frame = cap
    frame = cv2.resize(frame, (1280,720), interpolation = cv2.INTER_AREA)
    cv2.imshow('INPUT', frame)
    try:
        frame = processImage(frame)
        #frame = cv2.resize(frame,(640,480))
    except ValueError:
        pass
	
    x = int(frame.shape[1])
    y = int(frame.shape[0])
    ax = 0
    ay = 0.95
    bx = 1
    by = ay
    cx = 1
    cy = 0.65
    dx = 0
    dy = cy
    shape = np.array([[int(ax*x), int(ay*y)], [int(bx*x), int(by*y)], [int(cx*x), int(cy*y)], [int(dx*x), int(dy*y)]]) #0.51*x 0.4*x
    frame = cv2.polylines(frame,[shape],True,(0,0,255),1)
    frame = cv2.line(frame, (int(x/2),0), (int(x/2),y),[0,255,255], 1)
    frame = cv2.line(frame, (0,int(y/2)), (x,int(y/2)),[0,255,255], 1)
    cv2.imshow('OUTPUT',frame)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()	
