import sys
import numpy
import cv2
import urllib.request
import urllib.parse
import urllib.error
import mysql.connector
import os
import env_file
from time import sleep

class MysqlHelper:

    """Initialize connection to Mysql
    """
    def __init__(self):
        # Query Connection
        MySQLConfig = {
            'host':os.environ.get('REVIEW_DB_HOST'),
            'user':os.environ.get('REVIEW_DB_USER'),
            'password':os.environ.get('REVIEW_DB_PASS'),
            'database':os.environ.get('REVIEW_DB_NAME')
        }
        self.queryCnx = mysql.connector.connect(**MySQLConfig)
        self.queryCursor = self.queryCnx.cursor(buffered=True)

        # Command Connection
        self.commandCnx = mysql.connector.connect(**MySQLConfig)
        self.commandCursor = self.commandCnx.cursor()

    """Get list of review
    """
    def get_reviews(self, offset = 0, limit = 100):
        try:
            self.queryCursor.execute("SELECT re.id as review_id, im.file_path "
                            "FROM review as re JOIN image as im "
                            "ON im.review_id = re.id LIMIT " + str(offset) + "," + str(limit))
        except:
            print("An exception occurred: get_reviews", sys.exc_info()[0])

    """Tracking fake image review
    """
    def track_review_fake_image(self, review_id, file_path, method):
        try:
            self.commandCursor.execute("INSERT INTO fake_review_images "
                "(review_id, file_path, method) "
                "VALUES (%s, %s, %s)", (review_id, file_path, method))
            fake_tracking_id = self.commandCursor.lastrowid
            print("Fake tracking id is inserted: {}".format(fake_tracking_id))

            return fake_tracking_id
        except:
            print("An exception occurred: track_review_fake_image", sys.exc_info()[0])


class ReviewDetector:

    CDN_URL_REVIEW = 'https://vcdn.tikicdn.com/ts/review/'

    """Detect review which has anomaly uploaded image like selfie
    """
    def detect_anomaly_review(self, img_path):
        try:
            urllib.request.urlretrieve(self.CDN_URL_REVIEW + img_path, 'temporary.jpg')
            img = cv2.imread('temporary.jpg')
            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

            method = 0
            face_cascade = cv2.CascadeClassifier('/viet-test/opencv/data/haarcascades/haarcascade_profileface.xml')
            faces = face_cascade.detectMultiScale(
                gray,
                scaleFactor=2,
                minNeighbors=6,
                minSize=(10,10),
                flags = cv2.CASCADE_FIND_BIGGEST_OBJECT
            )

            if len(faces) == 0 :
                face_cascade = cv2.CascadeClassifier('/viet-test/opencv/data/haarcascades/haarcascade_frontalface_default.xml')
                faces = face_cascade.detectMultiScale(
                    gray,
                    scaleFactor=1.5,
                    minNeighbors=5,
                    minSize=(30,30),
                    flags = cv2.CASCADE_SCALE_IMAGE
                )
                method = 1

            if len(faces) == 0 :
                face_cascade = cv2.CascadeClassifier('/viet-test/opencv/data/haarcascades/haarcascade_frontalface_default.xml')
                faces = face_cascade.detectMultiScale(
                    gray,
                    scaleFactor=2,
                    minNeighbors=2,
                    minSize=(150,150),
                    flags = cv2.CASCADE_SCALE_IMAGE
                )
                method = 2

            if len(faces) == 0 :
                face_cascade = cv2.CascadeClassifier('/viet-test/lbpcascade_animeface.xml')
                faces = face_cascade.detectMultiScale(
                    gray,
                    scaleFactor=1.3,
                    minNeighbors=5,
                    minSize=(10,10),
                    flags = cv2.CASCADE_SCALE_IMAGE
                )
                method = 3

            for (x,y,w,h) in faces:
                img = cv2.rectangle(img,(x,y),(x+w,y+h),(255,0,0),2)
            
            status = cv2.imwrite('detected.jpg', img)

            return { 
                "num_of_detected": len(faces),
                "method": method
            }
        except KeyboardInterrupt:
            sys.exit()
        except:
            print("An exception occurred: detect_anomaly_review", sys.exc_info()[0])
            return { 
                "num_of_detected": -1,
                "method": -1
            }

        


env_file.load()
print(os.environ.get('DETECT_VERSION'))
mysql_helper = MysqlHelper()
reviewHandler = ReviewDetector()
offset = 0
limit = 100

while True:
    mysql_helper.get_reviews(offset, limit)
    count = mysql_helper.queryCursor.rowcount
    if count <= 0 :
        break
    offset += limit
    for (review_id, file_path) in mysql_helper.queryCursor:
        print("=====================================================================")
        faces_count = reviewHandler.detect_anomaly_review(file_path)
        if faces_count["num_of_detected"] > 0 :
            print("Found {} Faces!".format(faces_count["num_of_detected"]))
            tracking_id = mysql_helper.track_review_fake_image(review_id, file_path, faces_count["method"])
            remainder = tracking_id % 5
            if remainder == 0 : # batch insert data
                mysql_helper.commandCnx.commit()
        
        sleep(0.05)

    mysql_helper.commandCnx.commit()

#close db connection
mysql_helper.queryCursor.close()
mysql_helper.commandCursor.close()
mysql_helper.queryCnx.close()
mysql_helper.commandCnx.close()

