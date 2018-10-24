#!/usr/bin/env python
import cv2
import dic


from SystemInfo import SystemInfo
from utils.PerfCounter import PerfCounter
from utils.DebugWindow import DebugWindow
from utils.TemperatureControl import TemperatureControl
from videoStream.FileVideoStream import FileVideoStream
from tracking.Detector import Detector
from tracking.CascadeDetector import CascadeDetector
from tracking.Tracker import Tracker
from tracking.OpenCVTracker import OpenCVTracker
import time
import tkinter as tk
from tkinter import filedialog

root = tk.Tk()
root.withdraw()

videoPath = filedialog.askopenfilename()
cascadePath = filedialog.askopenfilename()

systemInfo = SystemInfo()

#Captura de video
video = FileVideoStream(videoPath, resolution = (640, 368))
video.start()

detector = CascadeDetector(video.resolution, cascadePath)
tracker = OpenCVTracker(detector, 4000, "MEDIANFLOW")
window = DebugWindow(True, "debug", video.resolution, 1, False)

#Medida de performance
fps = PerfCounter(False)
temp = TemperatureControl(1)


lastUpdateTime = 0

def setup():
    video.setCameraFocalLenght(3.04) # Padrão do raspberry pi
    systemInfo.isRunning = True
    tracker.isRunning = True
    while not systemInfo.isRunning:
        continue
    
    fps.start()
    window.open()
    

def loop():
    global lastUpdateTime

    if not(video.more()):
        return True
    
    frame = video.read()
    frame = cv2.resize(frame, (640, 368)) 

    if frame is None:
        return
    
    if not tracker.isRunning:
        pass
    elif not systemInfo.isTracking:
        (systemInfo.isTracking, systemInfo.trackedRect, systemInfo.trackedDirection) = tracker.init(frame)
        window.putTextWarning(frame, "Tentando detectar...", (20, 20), cv2.FONT_HERSHEY_SIMPLEX, 0.75, 2)
    else:   
        (systemInfo.isTracking, systemInfo.trackedRect, systemInfo.trackedDirection) = tracker.update(frame)

        if systemInfo.trackedRect is None or systemInfo.trackedDirection == -1:
            window.putTextError(frame, "Falha detectada no rastreamento", (20, 80), cv2.FONT_HERSHEY_SIMPLEX, 0.75, 2)
        else:    
            systemInfo.trackedRect = [int(i) for i in systemInfo.trackedRect]
            p1, p2 = Detector.rectToPoints(systemInfo.trackedRect)
            window.rectangle(frame, p1, p2, (255, 255, 0), 2, 1)

            distance = video.calculateDistance(systemInfo.trackedRect[2], 0.5)
            window.putTextInfo(frame, tracker.methodName + ": " + str(distance), (20, 20), cv2.FONT_HERSHEY_SIMPLEX, 0.75, 2)

    window.putTextInfo(frame, "({:.0f}, {:.2f})".format(*fps.update()) + " - Temp: " + str(temp.update()) + " 'C", (20, 50), cv2.FONT_HERSHEY_SIMPLEX, 0.75, 2)

    if(lastUpdateTime - time.time() > 2):
        arduinoMessagingThread.send(MessageCodes.TEMPERATURE, temp.update())
        lastUpdateTime = time.time() 
    # ESC pressionado
    return window.update(frame) == 27

def stop():
    video.stop()
    cv2.waitKey(500);
    fps.stop(True)
    window.close()
    systemInfo.isRunning = False
    
def main():
    setup()
    
    while systemInfo.isRunning:
        try:
            if(loop() == True):
                break
            
        except KeyboardInterrupt:
            break
    stop()
main()
