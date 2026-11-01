import cv2, numpy as np

def analyze_image(path):
    img=cv2.imread(path)
    if img is None: raise ValueError('Uploaded file could not be decoded as an image')
    hsv=cv2.cvtColor(img,cv2.COLOR_BGR2HSV); h,s,v=cv2.split(hsv)
    green=((h>=25)&(h<=95)&(s>35)&(v>35)).mean()
    yellow=((h>=15)&(h<35)&(s>40)&(v>50)).mean()
    brown=((h<20)&(s>35)&(v<170)).mean()
    return {"visual_green_fraction":round(float(green),3),"yellow_brown_fraction":round(float(yellow+brown),3),"method":"RGB colour heuristic; not a diagnosis or NDVI"}
