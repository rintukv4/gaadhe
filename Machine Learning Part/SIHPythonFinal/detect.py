import cv2
import numpy as np
import imgdwnld,xyz
import mysql.connector

def updateSQL(lod):
    mydb = mysql.connector.connect(
    host="localhost",
    user="root",
    password="",
    database="sih",
    buffered=True
    )
    
    

#load yolo
net = cv2.dnn.readNet("yolov2-tiny_4000.weights", "yolov2-tiny.cfg")
classes = []
with open("coco.names","r") as f:
    classes = [line.strip() for line in f.readlines()]
layer_names = net.getLayerNames()
output_layers = [layer_names[i[0] - 1] for i in net.getUnconnectedOutLayers()]
p = 0
fcnt=0
while True:
    mydb = mysql.connector.connect(
    host="localhost",
    user="root",
    password="",
    database="sih"
    )

    mycursor = mydb.cursor()

    mycursor.execute("SELECT * FROM citizen_data order by id desc")

    myresult = mycursor.fetchall()
    # url1 = url1 + myresult[7]  


    no = len(myresult)
    if no > p:
        print("Length:")
        print(no)
        p = no
    
    #downloading imge
        file_image=imgdwnld.imageload(fcnt)
        fcnt += 1
        #print(file_image)

        #loading image
        img = cv2.imread(file_image) #the image name/path goes here
        # cv2.imshow("Image",img)  

        #img = cv2.resize(img,None, fx=0.3, fy=0.3)
        height, width, channels = img.shape

        #detecting objects
        blob = cv2.dnn.blobFromImage(img, 0.00392, (416, 416), (0, 0, 0), True, crop=False)

        net.setInput(blob)
        outs = net.forward(output_layers)

        #count= 0
        #showing info on the screen
        area = 0
        for out in outs:
            for detection in out:
                scores = detection[5:]
                class_id = np.argmax(scores)
                confidence = scores[class_id]
                if confidence > 0.2:
                    
                    #object detected
                    #count += 1
                    center_x = int(detection[0] * width)
                    center_y = int(detection[1] * height)
                    w = int(detection[2] * width)
                    h = int(detection[3] * height)

                    #cv2.circle(img, (center_x, center_y), 10, (0,255,0), 2)
                    #rectangle coordinates
                    x = int(center_x - w / 2)
                    y = int(center_y - h / 2)

                    cv2.rectangle(img, (x,y), (x+w, y+h), (0,255,0), 2)
                    area += (w*h)


        print("area=")
        print(area)
        if area == 0:
            lod = 'None'
        elif area > 0 and area < 20000 :
            lod = 'Minor'
        elif area > 20000 and area < 45000:
            lod = 'Modrate'
        else:
            lod = 'Major'


        idd = xyz.getvalue()
        sql = "UPDATE citizen_data SET lod = %s WHERE id = %s"
        val = (lod,idd)
        mycursor.execute(sql,val)
        mydb.commit()



    # print("No Of Pothole:")
	# print(count)
	# if count>2 and count<7 :
	# 	lod = 'Modrate'
	# elif count >= 7 :
	# 	lod = 'Major'
	# elif count>0 and count<3:
	# 	lod = 'Minor'
	# else:
	# 	lod = 'None'

	# idd = xyz.getvalue()
	# sql = "UPDATE collect SET lod = %s WHERE id = %s"
	# val = (lod,idd)
	# mycursor.execute(sql,val)
	# mydb.commit()


