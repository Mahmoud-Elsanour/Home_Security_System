# import the necessary packages
from imutils.video import VideoStream
from imutils.video.pivideostream import PiVideoStream
from imutils.video import FPS
import face_recognition
import argparse
import imutils
import pickle
import time
import cv2
import time
import numpy as np
from os import system
from gpiozero import DistanceSensor, Servo, LED
import RPi.GPIO as GPIO
import gpiozero
import time
from RPLCD.i2c import CharLCD
from gpiozero import Button



#######################--{Hardware Initialization}--####################

# LCD
lcd = CharLCD(i2c_expander='PCF8574', address=0x27, port=1, cols=16, rows=2, dotsize=8)
lcd.clear()

#Bush Button
button = Button(17)

#Keypad
L1 = 14
L2 = 15
L3 = 18
L4 = 23

C1 = 24
C2 = 25
C3 = 12

# Initialize the GPIO pins

GPIO.setwarnings(False)
GPIO.setmode(GPIO.BCM)

GPIO.setup(L1, GPIO.OUT)
GPIO.setup(L2, GPIO.OUT)
GPIO.setup(L3, GPIO.OUT)
GPIO.setup(L4, GPIO.OUT)

# Make sure to configure the input pins to use the internal pull-down resistors

GPIO.setup(C1, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
GPIO.setup(C2, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
GPIO.setup(C3, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)



entered_password = ""

def readLine(line, characters):
    global entered_password

    GPIO.output(line, GPIO.HIGH)
    if(GPIO.input(C1) == 1):
        lcd.write_string(characters[0])
        entered_password += characters[0]
    if(GPIO.input(C2) == 1):
        lcd.write_string(characters[1])
        entered_password += characters[1]
    if(GPIO.input(C3) == 1):
        lcd.write_string(characters[2])
        entered_password += characters[2]
    
    GPIO.output(line, GPIO.LOW)

password = "45"

#Servo 
servo = Servo(16)

#Ultrasonic
us = DistanceSensor(echo=20, trigger=21)

#Alert LED
l1 = LED(26)

#Ring LED
l2 = LED(19)

#Home Lights 
l3 = LED(6)

#7-Segment
a= LED(7)
b= LED(8)
c= LED(9)
d= LED(10)
e= LED(11)
f= LED(22)
g= LED(27)


leds ={1:[b,c],
       2:[a,b,g,e,d],
       3:[a,b,g,c,d],
       4:[f,g,b,c],
       5:[a,f,g,c,d],
       6:[a,f,g,c,d,e],
       7:[a,b,c],
       8:[a,b,c,d,e,f,g],
       9:[f,a,b,g,c],
       0:[a,b,c,d,e,f]
        }
        
def segmentOff():
    for i in leds.values() :
        for j in i :   
            j.on()
            
def segmenton(num):
    for i in leds[num]:
            i.off()
            
segmentOff()          

############################# Read Dataset #############################

# construct the argument parser and parse the arguments
ap = argparse.ArgumentParser()
ap.add_argument("-c", "--cascade", required=True,
    help = "path to where the face cascade resides")
ap.add_argument("-e", "--encodings", required=True,
    help="path to serialized db of facial encodings")
args = vars(ap.parse_args())

# load the known faces and embeddings along with OpenCV's Haar cascade for face detection
print("[INFO] loading encodings + face detector...")
data = pickle.loads(open(args["encodings"], "rb").read())
detector = cv2.CascadeClassifier(args["cascade"])
g_data = {'encodings':[], 'names': []}


Home = []
Guests = []
guest_id = 0
g_matches = []

servo.max()
vs = VideoStream(usePiCamera = True).start() 



# ------------->>>>>>>>>>>>># START Programe #<<<<<<<<-----------------#

waiting = np.zeros(250, np.uint8)
cv2.imshow("Frame", waiting)

while True:
    
    print(us.distance *100)
    found_resident = False
    found_someone = False
    found_guest = False
    allow = False
    entered_password = ''

    Random_person = "Unknown"
    Pic = {}

    l1.off()
    l2.off()

    # Start Detection
    if us.distance * 100 < 30:   
        time.sleep(2.0)        
        attempts = 1
        
        
        #Start Attempt
        while attempts < 3:
            g_known_encodings = []
            g_known_names = []
            Pic['Imgs'] = []
            # start counting time
            start_time = time.time()
            # initialize the video stream and allow the camera sensor to warm up
            print("[INFO] starting video stream...")
            print(f"Attempt Number {attempts}...")
            
            # start the FPS counter (frame per second)
            fps = FPS().start()

            # loop over frames from the video file stream
            while True:
                names = []
                matches = []
                encodings = []
 
                frame = vs.read()
                frame = imutils.resize(frame, width=500)
                Pic['Img'] = Pic.get('Img', [frame])

                gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                
                # detect faces in the grayscale frame
                rects = detector.detectMultiScale(gray, scaleFactor=1.1, 
                    minNeighbors=5, minSize=(30, 30))
                # OpenCV returns bounding box coordinates in (x, y, w, h) order
                # but we need them in (top, right, bottom, left) order, so we
                # need to do a bit of reordering
                boxes = [(y, x + w, y + h, x) for (x, y, w, h) in rects]
                
                
                # compute the facial embeddings for each face bounding box
                encodings = face_recognition.face_encodings(rgb, boxes)
                

                # loop over the facial embeddings
                for encoding in encodings:
                # attempt to match each face in the input image to our known encodings
                    found_someone = True
                    matches = face_recognition.compare_faces(data["encodings"],
                            encoding)
                            
                    # Guests Recognition        
                    if len(Guests) > 0:
                        g_matches = face_recognition.compare_faces(g_data["encodings"],
                            encoding)
                    else:
                        g_matches = [False for i in range(len(matches))]
                    name = "Unknown"
                    
                    # check to see if we have found a match
                    if True in matches or True in g_matches:
                        # find the indexes of all matched faces then initialize a
                        # dictionary to count the total number of times each face
                        # was matched
                        matchedIdxs = [[i,(b, c)] for (i, (b, c)) in enumerate(zip(matches, g_matches)) if b or c]
                        counts = {}

                        # loop over the matched indexes and maintain a count for
                        # each recognized face face
                        for element in matchedIdxs:
                            if element[1][0]:
                                name = data["names"][element[0]]
                                Random_person = name
                                found_resident = True
                            else:
                                name = g_data["names"][element[0]]
                                found_guest = True
                   
                        counts[name] = counts.get(name, 0) + 1
                      
                        # determine the recognized face with the largest number
                        # of votes (note: in the event of an unlikely tie Python
                        # will select first entry in the dictionary)
                        name = max(counts, key=counts.get)
                        
                        
                    # update the list of names
                    names.append(name)

                # Get the frame with most people
                Pic["Names"] = Pic.get("Names", names)

                if len(Pic["Names"]) <= len(names):
                    Pic['Imgs'] = []

                # loop over the recognized faces and draw boxes
                for ((top, right, bottom, left), name) in zip(boxes, names):

                    cv2.rectangle(frame, (left, top), (right, bottom),
                    (0, 255, 0), 2)
                    y = top - 15 if top - 15 > 15 else top + 15
                    cv2.putText(frame, name, (left, y), cv2.FONT_HERSHEY_SIMPLEX,
                    0.75, (0, 255, 0), 2)
                    if len(Pic["Names"]) <= len(names):
                        Pic['Imgs'].append(frame[(left, top), (right, bottom)])

                
                if len(Pic["Names"]) <= len(names):

                    Pic["Names"] = names
                    Pic['Img'] = frame

                # display the image to our screen
                cv2.imshow("Frame", frame)
                key = cv2.waitKey(1) & 0xFF
                # if the q key was pressed, break from the loop
                if key == ord("q"):
                    break
                # update the FPS counter
                fps.update()
                if (time.time() - start_time) > 5 :
                    attempts += 1
                    break
                    
                    
            if found_resident: # Scope: Found attempt
                if Random_person not in Home:
                    #open the door
                    servo.min()
                    for n, name in enumerate(Pic['Names']):
                        if name != "Unknown":
                            Home.append(name)
                        else:
                            Guests.append(name + str(guest_id))
                        if len(Guests) > 0:
                            rgb = cv2.cvtColor(Pic['Imgs'][n], cv2.COLOR_BGR2RGB)
                            boxes = face_recognition.face_locations(rgb,model="hog")
                            g_encodings = face_recognition.face_encodings(rgb, boxes)
                         
                            for encoding in encodings:
                                g_known_names.append(name + str(guest_id))
                                g_known_encodings.append(encoding)
                            print("[INFO] serializing encodings...")
                            g_data["encodings"].extend(g_known_encodings)
                            g_data['names'].extend(g_known_names)
                          
                          
                            guest_id += 1
                            
                    print(f"Welcome {Random_person}!")
                    lcd.write_string(f"Welcome {Random_person}!")
                    time.sleep(2)
                    lcd.clear()

                    attempts = 4
                else:
                    for name in Pic['Names']:
                        print("Name is :", name)
                        if name[:7] != "Unknown":
                            Home.remove(name)
                        else:
                            print(Guests)
                            Guests.remove(name)
                            n = g_data["names"].index(name)
                            del g_data["encodings"][n]
                            del g_data["names"][n]

                    print(f"Goodbye {Random_person}")
                    lcd.write_string(f"Goodbye {Random_person}")
                    time.sleep(2)
                    lcd.clear()
                    attempts = 4
                break
            elif found_guest:
                for name in Pic['Names']:
                    print(Pic['Names'])
                    Guests.remove(name)
                    n = g_data["names"].index(name)
                    del g_data["encodings"][n]
                    del g_data["names"][n]

                    print(f"Goodbye {name}")
                    lcd.write_string(f"Goodbye {name}")
                    time.sleep(2)
                    lcd.clear()
                    attempts = 4
                break

        #------------->>>(ALARM!!!!!!!!!!!!!!!)<<<<-----------------#
        if found_someone and not found_resident and not found_guest:
            if len(Home) == 0:  
                lcd.write_string("Password :")
                key_start_time = time.time()
                while True:
                    print(time.time() - key_start_time)
                    
                    if(entered_password == ''):
                        segmenton(int(time.time() - key_start_time))
                        time.sleep(0.2)
                        segmentOff()

                    if button.is_pressed:
                        print("Button is pressed")
                        # Compare password
                        lcd.clear()
                        if password == entered_password:
                            allow = True
                        else:
                            allow = False
                        break
                        
                    else:
                       # call the readLine function for each row of the keypad
                       readLine(L1, ["1","2","3"])
                       readLine(L2, ["4","5","6"])
                       readLine(L3, ["7","8","9"])
                       readLine(L4, ["*","0","#"])
                       time.sleep(0.2)
                    if (time.time() - key_start_time) > 10 and entered_password == '':
                        break
                
                if allow:
                    servo.min()
                else:
                    print("WHO ARE YOU!?!")
                    l1.on()
                    lcd.clear()
                    lcd.write_string("WHO ARE YOU!?!")
                    system("python3 notification.py")
                    time.sleep(3)
                    lcd.clear()

            else:
                print("Someone has came!")
                l2.blink(on_time=0.3, off_time=0.3,n=5, background = False)
                lcd.write_string("Someone has came!")
                time.sleep(2)
                lcd.clear()

        if len(Home) != 0 or len(Guests) != 0:
            l3.on()
        else:
            l3.off()

        # stop the timer and display FPS information
        fps.stop()
        print("[INFO] elasped time: {:.2f}".format(fps.elapsed()))
        print("[INFO] approx. FPS: {:.2f}".format(fps.fps()))
