class VideoStream:
    def __init__(self, src=0, usePiCamera=False, resolution=(320, 240), framerate=32):
        # check to see if the picamera module should be used
        if usePiCamera:
            # only import the picamera packages unless we are
            # explicity told to do so -- this helps remove the
            # requirement of `picamera[array]` from desktops or
            # laptops that still want to use the `imutils` package
            from .PiVideoStream import PiVideoStream
            
            # initialize the picamera stream and allow the camera
            # sensor to warmup
            self.stream = PiVideoStream(resolution=resolution, framerate=framerate)
            
            #Usando a Câmera do Raspberry Pi precisamos dar um tempinho pra ela "esquentar"
            
        # otherwise, we are using OpenCV so initialize the webcam
        # stream
        else:
            from .WebcamVideoStream import WebcamVideoStream
            self.stream = WebcamVideoStream(src=src,resolution=resolution,framerate=framerate)
      
        self.__resolution = self.stream.resolution
        
    def setCameraFocalLenght(self, focalLenght):
        self.focalLenght = focalLenght
    
    def calculateDistance(self, dimensionInPixels, dimensionInMeters):
        "Retorna a distancia do objeto em metros"
        if(dimensionInPixels == 0):
            return 0
        
        distance = (dimensionInMeters * self.focalLenght) / dimensionInPixels
        return distance
    
    @property
    def resolution(self):
        return self.__resolution
        
    def start(self):
        # start the threaded video stream
        return self.stream.start()
 
    def update(self):
        # grab the next frame from the stream
        self.stream.update()
 
    def read(self):
        # return the current frame
        return self.stream.read()
 
    def stop(self):
        # stop the thread and release any resources
        self.stream.stop()