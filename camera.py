import io
import time
import picamera
from basecamera import BaseCamera


class Camera(BaseCamera):
    @staticmethod
    def frames():
        with picamera.PiCamera() as camera:
            # let camera warm up
            time.sleep(2)

            camera.resolution = (320, 240)
            camera.hflip = True
            camera.vflip = True
            camera.framerate = 20
            flag = True
            stream = io.BytesIO()
            for _ in camera.capture_continuous(stream, 'jpeg',
                                                 use_video_port=True):
                # return current frame
                stream.seek(0)
                if flag:
                    yield stream.read()
                flag = not flag

                # reset stream for next frame
                stream.seek(0)
                stream.truncate()
