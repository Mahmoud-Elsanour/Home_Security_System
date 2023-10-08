#############################################--{Import packages}--###################################################
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



#########################################--{Hardware Init}--#########################################

# 1-LCD
lcd = CharLCD(i2c_expander='PCF8574', address=0x27, port=1, cols=16, rows=2, dotsize=8)
lcd.clear()

button = Button(17)

# 2- Keypad
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

GPIO.setup(C1, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
GPIO.setup(C2, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
GPIO.setup(C3, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)



#3- 7-Segment
_a = LED(25)
_b = LED(24)
_c = LED(22)
_d = LED(27)
_e = LED(4)
_f = LED(26)
_g = LED(13)

def segment(num):
    global _a
    global _b
    global _c
    global _d
    global _e
    global _f
    global _g

    if num == 0:
        _a.on()
        _b.on()
        _c.on()
        _d.on()
        _e.on()
        _f.on()
        _g.off()
    elif num == 1:
        _a.off()
        _b.off()
        _c.off()
        _d.off()
        _e.on()
        _f.on()
        _g.off()
    elif num == 2:
        _a.on()
        _b.on()
        _c.off()
        _d.on()
        _e.on()
        _f.off()
        _g.on()
    elif num == 3:
        _a.on()
        _b.on()
        _c.on()
        _d.on()
        _e.off()
        _f.off()
        _g.on()
    elif num == 4:
        _a.off()
        _b.on()
        _c.on()
        _d.off()
        _e.off()
        _f.on()
        _g.on()
    elif num == 5:
        _a.on()
        _b.off()
        _c.on()
        _d.on()
        _e.off()
        _f.on()
        _g.on()
    elif num == 6:
        _a.on()
        _b.off()
        _c.on()
        _d.on()
        _e.on()
        _f.on()
        _g.on()
    elif num == 7:
        _a.on()
        _b.on()
        _c.on()
        _d.off()
        _e.off()
        _f.off()
        _g.off()
    elif num == 8:
        _a.on()
        _b.on()
        _c.on()
        _d.on()
        _e.on()
        _f.on()
        _g.on()
    elif num == 9:
        _a.on()
        _b.on()
        _c.on()
        _d.on()
        _e.off()
        _f.on()
        _g.on()
    else:
        _a.off()
        _b.off()
        _c.off()
        _d.off()
        _e.off()
        _f.off()
        _g.off()

# 4-Outputs(Servo, Ultra Sonic, Leds)
servo = Servo(16)
us = DistanceSensor(echo=20, trigger=21)
l1 = LED(26)
l2 = LED(19)
l3 = LED(6)


def readLine(line, characters):
    global entered_password

    GPIO.output(line, GPIO.HIGH)
    if(GPIO.input(C1) == 1):
        lcd.write_string(characters[0])
        entered_password += characters[0]
        #print(characters[0])
    if(GPIO.input(C2) == 1):
        lcd.write_string(characters[1])
        entered_password += characters[1]
        #print(characters[1])
    if(GPIO.input(C3) == 1):
        lcd.write_string(characters[2])
        entered_password += characters[2]
        #print(characters[2])
    #if(GPIO.input(C4) == 1):
     #   print(characters[3])
    GPIO.output(line, GPIO.LOW)

#####################################################################################################


#####################################--{Software Init}--#############################################

# 1- Arguments for files

## Get arguments from command
ap = argparse.ArgumentParser()
ap.add_argument("-c", "--cascade", required=True,
    help = "path to where the face cascade resides")
ap.add_argument("-e", "--encodings", required=True,
    help="path to serialized db of facial encodings")
args = vars(ap.parse_args())


## Load faces
print("[INFO] loading encodings + face detector...")
data = pickle.loads(open(args["encodings"], "rb").read())

detector = cv2.CascadeClassifier(args["cascade"])

# 2- Needed Variables 
Home = []
Guests = []
guest_id = 0
g_matches = []
g_data = {'encodings':[], 'names': []}
entered_password = ""
password = "4567"

#####################################################################################################


######################################--{Main Program}--#############################################
servo.max()# :3

vs = VideoStream(usePiCamera = True).start()#
time.sleep(2.0)# :3

waiting = np.zeros(250, np.uint8)
cv2.imshow("Frame", waiting)
while True:
    
    print(us.distance *100)
    
    # Flags
    found_resident = False
    found_someone = False
    found_guest = False
    allow = False
    
    # Delete old data
    entered_password = ''
    Random_person = "Unknown"
    Pic = {}
    l1.off()
    l2.off()

    if us.distance * 100 < 30:
        # Start counting
        attempts = 1
        
        while attempts < 4:
            # Delete attempt data
            g_known_encodings = []
            g_known_names = []
            Pic['Imgs'] = []

            # Start counting time
            start_time = time.time()
            # initialize the video stream
            print("[INFO] starting video stream...")
            # print try number
            print(f"Attempt Number {attempts}...")
            # start the FPS counter
            fps = FPS().start()

            # loop over frames from the video file stream
            while True:
                # Delete frame data
                names = []
                matches = []
                encodings = []
                
                # Grab the frame and resize it
                frame = vs.read()
                frame = imutils.resize(frame, width=500)
                Pic['Img'] = Pic.get('Img', [frame])

                # Convert the input frame
                gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

                # Detect faces in the grayscale frame
                rects = detector.detectMultiScale(gray, scaleFactor=1.1, 
                    minNeighbors=5, minSize=(30, 30))
                # Reorder points
                boxes = [(y, x + w, y + h, x) for (x, y, w, h) in rects]

                # Compute the facial embeddings for each face bounding box
                encodings = face_recognition.face_encodings(rgb, boxes)
                

                # loop over the facial embeddings searching for matches
                for encoding in encodings:

                    # Search for matched resident or guest
                    found_someone = True
                    matches = face_recognition.compare_faces(data["encodings"],
                            encoding)
                    if len(Guests) > 0:
                        g_matches = face_recognition.compare_faces(g_data["encodings"],
                            encoding)
                    else:
                        g_matches = [False for i in range(len(matches))]
                    name = "Unknown"

                    # Check to see if we have found a match
                    if True in matches or True in g_matches:

                        # Find the indexes
                        matchedIdxs = [[i,(b, c)] for (i, (b, c)) in enumerate(zip(matches, g_matches)) if b or c]
                        counts = {}

                        # loop over the matched indexes 
                        for element in matchedIdxs:
                            if element[1][0]:
                                name = data["names"][element[0]]
                                Random_person = name
                                found_resident = True
                            else:
                                name = g_data["names"][element[0]]
                                found_guest = True
                        
                        # Get the most matched name
                        counts[name] = counts.get(name, 0) + 1
                        name = max(counts, key=counts.get)
                        
                    # Update the list of names
                    names.append(name)

                # Clear the previous images if found more people
                Pic["Names"] = Pic.get("Names", names)
                if len(Pic["Names"]) <= len(names):
                    Pic['Imgs'] = []


                # Loop over the recognized faces
                for ((top, right, bottom, left), name) in zip(boxes, names):

                    # draw the predicted face name on the image
                    cv2.rectangle(frame, (left, top), (right, bottom),
                    (0, 255, 0), 2)
                    y = top - 15 if top - 15 > 15 else top + 15
                    cv2.putText(frame, name, (left, y), cv2.FONT_HERSHEY_SIMPLEX,
                    0.75, (0, 255, 0), 2)

                    # Save the images of each face temporary
                    if len(Pic["Names"]) <= len(names):
                        Pic['Imgs'].append(frame[(left, top), (right, bottom)])
                
                # Update current saved frame
                if len(Pic["Names"]) <= len(names):
                    Pic["Names"] = names
                    Pic['Img'] = frame

                # Display the image to our screen
                cv2.imshow("Frame", frame)
                
                # Update the FPS counter
                fps.update()

                # Check attempt time
                if (time.time() - start_time) > 5 :
                    attempts += 1
                    break


############# Check the previous attempt

            # Check whether the resident is ...
            if found_resident:

                # Comming
                if Random_person not in Home:

                    # Open the door
                    servo.min()

                    # Append residents and their guests
                    for n, name in enumerate(Pic['Names']):
                        if name != "Unknown":
                            Home.append(name)
                        else:
                            Guests.append(name + str(guest_id))

                        # Encode guests images
                        if len(Guests) > 0:
                            rgb = cv2.cvtColor(Pic['Imgs'][n], cv2.COLOR_BGR2RGB)
                            boxes = face_recognition.face_locations(rgb,
                                model="hog")
                            g_encodings = face_recognition.face_encodings(rgb, boxes)
                            for encoding in encodings:
                                g_known_names.append(name + str(guest_id))
                                g_known_encodings.append(encoding)
                            g_data["encodings"].extend(g_known_encodings)
                            g_data['names'].extend(g_known_names)
                            guest_id += 1

                    # Welcome the resident                            
                    print(f"Welcome {Random_person}!!")
                    lcd.write_string(f"Welcome {Random_person}!!")
                    time.sleep(1)
                    lcd.clear()

                    # End the attempts
                    attempts = 4

                # Leaving
                else:
                    # Remove the leaving names
                    for name in Pic['Names']:
                        if name[:7] != "Unknown":
                            Home.remove(name)
                        else:
                            Guests.remove(name)
                            n = g_data["names"].index(name)
                            del g_data["encodings"][n]
                            del g_data["names"][n]

                    # Say goodbye
                    print(f"Goodbye {Random_person}")
                    lcd.write_string(f"Goodbye {Random_person}")
                    time.sleep(1)
                    lcd.clear()
                    
                    # End the attempts
                    attempts = 4

                break# :3

            # Let the gest leave
            elif found_guest:
                # Remove the name
                for name in Pic['Names']:
                    Guests.remove(name)
                    n = g_data["names"].index(name)
                    del g_data["encodings"][n]
                    del g_data["names"][n]

                    # Say goodbye
                    print(f"Goodbye {name}")
                    lcd.write_string(f"Goodbye {name}")
                    time.sleep(1)
                    lcd.clear()

                    # End the attempts
                    attempts = 4

                break# :3

######## Check after the three attempts:

        # Check whether unknown came and the home is ....
        if found_someone and not found_resident and not found_guest:

            # Empty
            if len(Home) == 0:

                # Ask for password
                lcd.write_string("Password :")
                while True:
                    
                    # Count 10 seconds
                    key_start_time = time.time()

                    # Compare the passwords
                    if button.is_pressed:
                        lcd.clear()
                        if password == entered_password:
                            allow = True
                        else:
                            allow = False
                        break
                    
                    # Wait for keys
                    else:
                       # call the readLine function for each row of the keypad
                       readLine(L1, ["1","2","3"])
                       readLine(L2, ["4","5","6"])
                       readLine(L3, ["7","8","9"])
                       readLine(L4, ["*","0","#"])
                       time.sleep(0.1)

                    segment(int(key_start_time - time.time()))

                    # Quit if no key is pressed for 10 seconds
                    if (key_start_time - time.time()) > 10 and entered_password == '':
                        break
                
                segment(11)
                # Check password results
                if allow:
                    # Open the door
                    servo.min()
                else:
                    # WAAWEEWAAWEE
                    print("WHO ARE YOU!?!")
                    system("python3 import_requests.py")
                    l1.on()
                    lcd.write_string("WHO ARE YOU!?!")
                    time.sleep(1)
                    lcd.clear()

            # Not empty
            else:
                # Ring the bell
                print("Someone has came!")
                l2.blink(n=3, background = False)
                lcd.write_string("Someone has came!")
                time.sleep(1)
                lcd.clear()

        # Check whether the home is empty or not to turn off everything
        if len(Home) != 0 or len(Guests) != 0:
            l3.on()
        else:
            l3.off()

        # Stop the timer and display FPS information
        fps.stop()
        print("[INFO] elasped time: {:.2f}".format(fps.elapsed()))
        print("[INFO] approx. FPS: {:.2f}".format(fps.fps()))
        # Do a bit of cleanup
        #vs.release()

    #cv2.destroyAllWindows()

    # Add data from the bucket
    # Should we write a specific thing at the start?
    # Should we write anything or remove the window
    # FIX THE CAMERAAAA
