import os
import numpy as np
import math
import cv2
#import serial

#Masking Unnecessary Colors
def color_filter(image):
    image = cv2.GaussianBlur(image,(5,5),0)   
	#convert to HLS to mask based on HLS
    hls = cv2.cvtColor(image, cv2.COLOR_RGB2HLS) #===> RGB to BGR
    lower = np.array([60,35,30])     #[60,35,30] red color of rubber-tape 
    upper = np.array([255,255,255])  #[255,255,255]   
    redtapemask = cv2.inRange(hls, lower, upper)    
    masked = cv2.bitwise_and(image, image, mask = redtapemask)
    return masked

#Region of Interest
def roi(img):    #MENENTUKAN TITIK ABCD SEBAGAI TRAPESIUM ROI
    x = int(img.shape[1])
    y = int(img.shape[0])
    ax = 0.05 #0
    ay = 0.95
    bx = 0.95 #1
    by = ay
    cx = 0.75 #0.7
    cy = 0.65 #0.8 0.6 0.4
    dx = 0.25 #0.3
    dy = cy
    shape = np.array([[int(ax*x), int(ay*y)], [int(bx*x), int(by*y)], [int(cx*x), int(cy*y)], [int(dx*x), int(dy*y)]]) #0.5
		
    #define a numpy array with the dimensions of img, but comprised of zeros
    mask = np.zeros_like(img)

    #Uses 3 channels or 1 channel for color, depending on the input image
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
                    if slope > 0.5: #>0.3
                        if x1 > (int(x/2)):#903 : #500 (640-64) 320 #> x/2
                            yintercept = y2 - (slope*x2)                    
                            rightSlope.append(slope)
                            rightIntercept.append(yintercept)
                        else: None                
                    elif slope < -0.5: #< -0.3
                        if x1 < (int(x/2)) : #1018: #600 640 320 #< x/2
                            yintercept = y2 - (slope*x2)                    
                            leftSlope.append(slope)
                            leftIntercept.append(yintercept)    
                        else: None
                except ZeroDivisionError:
                    #print ('Error Pembagian Dengan NOL')
                    pass
		    #else: None		
                    
    #We use slicing operators and np.mean() to find the averages of the 30 previous frames
    #This makes the lines more stable and less likely to shift rapidly
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
        #cv2.fillPoly(img,[pts],(0,0,255))      
        
        
        cv2.line(img, (left_line_x1, int(cy*img.shape[0])), (left_line_x2, int(ay*img.shape[0])), leftColor, 10) #10 0.735
        cv2.line(img, (right_line_x1, int(cy*img.shape[0])), (right_line_x2, int(ay*img.shape[0])), rightColor, 10) #10  0.735
        CL=int((right_line_x1 - left_line_x1)/2)+left_line_x1
        cv2.line(img, (int(x/2),y), (CL,int(0.65*y)), centerColor, 5)
        selisih=int(CL-(x/2))
        cv2.putText(img,"%s"%derajat(selisih),(int(CL),int(0.8*y)), cv2.FONT_HERSHEY_SIMPLEX, 1,(0,0,255),5)
        cv2.putText(img,"%s"%right_line_x1,(int(right_line_x1),int(0.6*y)), cv2.FONT_HERSHEY_SIMPLEX, 1,(0,0,255),5)
        cv2.putText(img,"%s"%left_line_x1,(int(left_line_x1),int(0.6*y)), cv2.FONT_HERSHEY_SIMPLEX, 1,(0,0,255),5)
        cv2.putText(img,"%s"%CL,(CL,int(0.6*y)), cv2.FONT_HERSHEY_SIMPLEX, 1,(0,0,255),5)
        #cv2.putText(img,kirimdata, (200,60),cv2.FONT_HERSHEY_SIMPLEX, 1,(0,255,0),3)
    except ValueError as err:
            #I keep getting errors for some reason, so I put this here. Idk if the error still persists.
        #print('error nilai=',err)
        pass

def derajat(selisih):
    piksel = 4.6 #1 piksel berapa milimeter??? 0.2 4.65
    jarak = 4000 #jarak dari kamera ke titik acuan berapa milimeter? #3000
    sudut = (math.atan(selisih*piksel/jarak))*57.32 #57,32 #57.2958
    kemudi=sudut#*50/15 #+200
    kemudi=f"{kemudi:.0f}"
    return kemudi #sudut                

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

def linedetect(img):
    return hough_lines(img, 1, np.pi/180, 10, 20, 100) #10, 20, 100

#hough_img = list(map(linedetect, canny_img))
#display_images(hough_img)  #cek point

#Overlaying the Image and the Lines
def weighted_img(img, initial_img, α=0.8, β=1., λ=0.):
    """
    initial_img * α + img * β + λ
    NOTE: initial_img and img must be the same shape!
    """
    return cv2.addWeighted(initial_img, α, img, β, λ)

def weightSum(input_set):
    img = list(input_set)
    return cv2.addWeighted(img[0], 1, img[1], 0.8, 0)

#result_img = list(map(weightSum, zip(hough_img, imageList)))
#display_images(result_img)  #cek point

def sharpen(img):
	filter = np.array([[-1, -1, -1], [-1, 9, -1], [-1, -1, -1]])
	#filter = np.array([[0,0,-1,0,0],[0,-1,-2,-1,0],[-1,-2,16,-2,-1],[0,-1,-2,-1,0],[0,0,-1,0,0]])	#Mexican hat filter
	filter = np.array([[3, -2, -3], [-4, 8, -6], [5, -1, -0]]) #your own
	return cv2.filter2D(img,-1,filter)

#Applying it to Video
def processImage(image):
    interest = roi(image)
    myline = hough_lines(interest, 1, np.pi/180, 10, 37, 6)
    weighted_img = cv2.addWeighted(myline, 1, frame, 0.8, 0)
    return weighted_img #filtering #weighted_img #canny

path0 = "c:\\Users\\HP\\Documents\\2025\\ELCVIA_draft\\Code\\" #location of video_data
namafile = "vid_mevi_1a" #WIN_4 kameraroof  CIPALI  PALIKANCI  PEJAGAN PML3 jpro7
videoFile = namafile+".mp4" #size 1280x720 setengahnya 640x360 
cap = cv2.VideoCapture(path0+videoFile)
video_output = "VIDEO OUTPUT" #+namaJendela
cv2.namedWindow(video_output,0) #0 size full, 1 size original
#cv2.namedWindow('out video '+namafile,1) #0 size full, 1 size original
cv2.resizeWindow(video_output,640,480) #Jendela viewnya saja yg di resize
video_input = "VIDEO INPUT "
cv2.namedWindow(video_input,0)
cv2.resizeWindow(video_input,640,480) #Jendela viewnya saja yg di resize
#cap = cv2.VideoCapture(0)c

#def classify(img, ratio):
#    M = img.shape[0]
#    N = img.shape[1]
#    img = cv2.resize(img, (int(ratio*N),int(ratio*M)),interpolation = cv2.INTER_AREA)
#    return img
os.system("cls")

saveVideo = True  #False
frameIdx = 0
ratio = 1 #0.5

cap = cv2.VideoCapture(path0+videoFile)
totalFrames = cap.get(cv2.CAP_PROP_FRAME_COUNT)

ret, frame = cap.read()
#M = frame.shape[0]
#N = frame.shape[1]

#M = int(ratio*M)
#N = int(ratio*N)

videoPathToSave = "c:\\Users\\HP\\Documents\\2025\\ELCVIA_draft\\Code\\" #location of the output video stored
#if saveVideo == True:
#    out = cv2.VideoWriter(videoPathToSave+"mevi1.avi",cv2.VideoWriter_fourcc('M','J','P','G'), 30, (N,M))
	
frameIdxMax = 3000 #2900
#ser=serial.Serial("COM3",115200)
#ser.reset_input_buffer()

while cap.isOpened(): #cap
    ret, frame = cap.read()
    #frame = cv2.resize(frame,(640,480))
    cv2.imshow(video_input, frame)
    filtering = color_filter(frame)
    edge = cv2.Canny(grayscale(filtering), 50, 120)
    try:
        frame = processImage(edge)   
        #interest = roi(edge)
        #myline = hough_lines(interest, 1, np.pi/180, 10, 37, 6)
        #frame = cv2.addWeighted(myline, 1, frame, 0.8, 0) #weighted_img
        #frame = cv2.resize(frame,(640,480))
    except ValueError:
        pass
    #frame = filtering
    x = int(frame.shape[1])
    y = int(frame.shape[0])
    #print(x,y)
    ax = 0.05
    ay = 0.95
    bx = 0.95
    by = ay
    cx = 0.75
    cy = 0.65
    dx = 0.25
    dy = cy
    #shape = np.array([[int(ax*x), int(ay*y)], [int(bx*x), int(by*y)], [int(cx*x), int(cy*y)], [int(dx*x), int(dy*y)]]) #0.51*x 0.4*x
    #frame = cv2.polylines(frame,[shape],True,(0,0,255),2)
    #frame = cv2.line(frame, ((640+20),0), ((640+20),720),[0,255,255], 1) #x tengah = 640 (640-64)
    #frame = cv2.line(frame, (0,360), (1280,360),[0,255,255], 1)
    #cv2.resizeWindow(video_output,1280,720) #1920,1080 1280,720
    frame = cv2.line(frame, (int(x/2),0), (int(x/2),y),[0,255,255], 2)
    frame = cv2.line(frame, (0,int(y/2)), (x,int(y/2)),[0,255,255], 2)
    cv2.imshow(video_output,frame) #frame
    #print("Frame index: %d  of %d [%3.2f %%]" %(frameIdx, frameIdxMax,(float(frameIdx/frameIdxMax*100))))
    #if saveVideo == True:
        #out.write(frame)
    #    print("ok")
    #frameIdx = frameIdx + 1
    #ser.write(kirimdata+'\n')	#send steering angle to serial port
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()	
