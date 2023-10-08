# import the necessary packages
from imutils.video import VideoStream
from imutils.video import FPS
import face_recognition
import argparse
import imutils
import pickle
import time
import cv2
import time
from os import system
import numpy as np
import datetime
#from gpiozero import DistanceSensor, Servo, LED

# Initialize hardware
#servo = Servo(17)
#us = DistanceSensor(23, 24)
#l1 = LED(10)
#l2 = LED(11)

# construct the argument parser and parse the arguments
ap = argparse.ArgumentParser()
ap.add_argument("-c", "--cascade", required=True,
    help = "path to where the face cascade resides")
ap.add_argument("-e", "--encodings", required=True,
    help="path to serialized db of facial encodings")
args = vars(ap.parse_args())

# load the known faces and embeddings along with OpenCV's Haar
# cascade for face detection
print("[INFO] loading encodings + face detector...")
data = pickle.loads(open(args["encodings"], "rb").read())
print(data)
detector = cv2.CascadeClassifier(args["cascade"])
#g_data = pickle.loads(open("guests.pickle", "rb").read())
g_data = {'encodings':[], 'names': []}
# Test place:
#print(set(data["names"]))
#print(data)

#vs = VideoStream(src=0).start()
# vs = VideoStream(usePiCamera=True).start()
Home = []
Guests = []
guest_id = 0
unknown_id = 0
g_matches = []


# --------------->>>>>>>>>>>>># START CONDITION (WILL BE ULTRAAAA) #<<<<<<<<-----------------
waiting = np.zeros(500, np.uint8)
cv2.imshow("Frame", waiting)
while True:
    # Flags?
    found_resident = False
    found_someone = False
    found_guest = False

    Random_person = "Unknown"
    Pic = {}

    key = cv2.waitKey(1)
    if key == ord("s"):
    #if us.distance * 100 < 30:   ####################################################
        vs = VideoStream(src=0).start() #VideoStream(usePiCamera=True).start()
        time.sleep(2.0)
        #time.sleep(2)
        #servo.max()
        #l1.off()
        #l2.off()
        attempts = 1
        
        while attempts < 4:
            g_known_encodings = []
            g_known_names = []
            Pic['Imgs'] = []
            # start counting time
            start_time = time.time()
            # initialize the video stream and allow the camera sensor to warm up
            print("[INFO] starting video stream...")
            # print try number
            print(f"Attempt Number {attempts}...")
            # start the FPS counter
            fps = FPS().start()

            # loop over frames from the video file stream
            while True:
                #?
                names = []
                matches = []
                encodings = []
                
                # grab the frame from the threaded video stream and resize it
                # to 500px (to speedup processing)
                frame = vs.read()
                frame = imutils.resize(frame, width=500)
                Pic['Img'] = Pic.get('Img', [frame])
                #Pic['Imgs'] = []
                # convert the input frame from (1) BGR to grayscale (for face
                # detection) and (2) from BGR to RGB (for face recognition)
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
                # attempt to match each face in the input image to our known
                # encodings
                    found_someone = True
                    matches = face_recognition.compare_faces(data["encodings"],
                            encoding)
                    if len(Guests) > 0:
                        g_matches = face_recognition.compare_faces(g_data["encodings"],
                            encoding)
                    else:
                        g_matches = [False for i in range(len(matches))]
                    name = "Unknown"
                    #print("Matches and group:", matches,'\n' , g_matches)
                    
                    # check to see if we have found a match
                    if True in matches or True in g_matches:
                        # find the indexes of all matched faces then initialize a
                        # dictionary to count the total number of times each face
                        # was matched
                        matchedIdxs = [[i,(b, c)] for (i, (b, c)) in enumerate(zip(matches, g_matches)) if b or c]
                        counts = {}
                        print("Matched Indexs:", matchedIdxs)
                        # loop over the matched indexes and maintain a count for
                        # each recognized face face
                        for element in matchedIdxs:
                            print(f"Element is: {element}")
                            if element[1][0]:
                                print(f"{element[0]} is a res")
                                name = data["names"][element[0]]
                                Random_person = name
                                found_resident = True
                            else:
                                print(f"{element[0]} is a guest")
                                name = g_data["names"][element[0]]
                                found_guest = True
                        #for i in matchedIdxs:
                        #    name = data["names"][i]
                        counts[name] = counts.get(name, 0) + 1
                        #print(counts)
                        # determine the recognized face with the largest number
                        # of votes (note: in the event of an unlikely tie Python
                        # will select first entry in the dictionary)
                        name = max(counts, key=counts.get)
                        
                        
                    # update the list of names
                    names.append(name)

                # Get the frame with most people
                Pic["Names"] = Pic.get("Names", names)
                #print(Pic["Names"])
                if len(Pic["Names"]) <= len(names):
                    Pic['Imgs'] = []

                # loop over the recognized faces
                for ((top, right, bottom, left), name) in zip(boxes, names):
                    # draw the predicted face name on the image
                    cv2.rectangle(frame, (left, top), (right, bottom),
                    (0, 255, 0), 2)
                    y = top - 15 if top - 15 > 15 else top + 15
                    cv2.putText(frame, name, (left, y), cv2.FONT_HERSHEY_SIMPLEX,
                    0.75, (0, 255, 0), 2)
                    if len(Pic["Names"]) <= len(names):
                        Pic['Imgs'].append(frame[(left, top), (right, bottom)])
                        #cv2.imwrite()
                    #guest_id += 1
                
                if len(Pic["Names"]) <= len(names):
                    #print("Image changed")
                    Pic["Names"] = names
                    Pic['Img'] = frame

                # display the image to our screen
                cv2.imshow("Frame", frame)
                key = cv2.waitKey(1) & 0xFF
                # if the `q` key was pressed, break from the loop
                if key == ord("q"):
                    break
                # update the FPS counter
                fps.update()
                if (time.time() - start_time) > 5 :
                    attempts += 1
                    break
            if found_resident: # Scope: Found attempt
                if Random_person not in Home:
                    #--------------->>>>>(SERVO IS HERE)<<<<--------------#
                    #servo.min()
                    for n, name in enumerate(Pic['Names']):
                        if name != "Unknown":
                            Home.append(name)
                        else:
                            print(name + str(guest_id))
                            Guests.append(name + str(guest_id))
                        if len(Guests) > 0:
                            #g_Name = name + guest_id
                            # load the input image and convert it from BGR (OpenCV ordering)
                            # to dlib ordering (RGB)
                            print('Len of images', len(Pic["Imgs"]))
                            rgb = cv2.cvtColor(Pic['Imgs'][n], cv2.COLOR_BGR2RGB)
                            # detect the (x, y)-coordinates of the bounding boxes
                            # corresponding to each face in the input image
                            boxes = face_recognition.face_locations(rgb,
                                model="hog")
                            # compute the facial embedding for the face
                            g_encodings = face_recognition.face_encodings(rgb, boxes)
                            # loop over the encodings
                            # dump the facial encodings + names to disk
                            for encoding in encodings:
                                # add each encoding + name to our set of known names and
                                # encodings
                                g_known_names.append(name + str(guest_id))
                                g_known_encodings.append(encoding)
                            print("[INFO] serializing encodings...")
                            g_data["encodings"].extend(g_known_encodings)
                            g_data['names'].extend(g_known_names)
                            #print(g_data['names'])
                            #f = open("guests.pickle", "ab")
                            #f.write(pickle.dumps(g_data))
                            #f.close()
                            guest_id += 1
                            
                    print(f"Welcome home {Random_person}!!")
                    cv2.imwrite(f"logs/{Random_person}.png", Pic['Img'])
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
                    attempts = 4
                break

        #------------->>>(ALARM!!!!!!!!!!!!!!!)<<<<-----------------#
        if found_someone and not found_resident and not found_guest:
            if len(Home) == 0:  # Scope Last attempt or last frame? nope frame, we want attempt
                print("WHO ARE YOU!?!")
                cv2.putText(Pic["Img"], str(datetime.datetime.now()), (10, 20), cv2.FONT_HERSHEY_SIMPLEX,
                    0.5, (0, 255, 0), 2)
                cv2.imwrite(f'./log/thief{unknown_id}.jpg', Pic["Img"])
                unknown_id += 1
                system("python3 import_requests.py")
                #l1.on()
                #cv2.imwrite(f"logs/{Random_person}.png", Pic['Img'])
            else:
                print("Someone has came!")
                #l2.on

        # stop the timer and display FPS information
        fps.stop()
        print("[INFO] elasped time: {:.2f}".format(fps.elapsed()))
        print("[INFO] approx. FPS: {:.2f}".format(fps.fps()))
        # do a bit of cleanup
        vs.stream.release()
        #break # WILL BE REMOVED !!!!!!!!!!!!!!!!!!!!

    #cv2.destroyAllWindows()
        