import cv2

video = cv2.VideoCapture(0)
ip = "https://191.20.188.61:8080/video"
video.open(ip)

while True:
    check, img = video.read()
    cv2.imshow('img', img)
    cv2.waitKey(1)
