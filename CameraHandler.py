import cv2
import time
import Constants


class Camera:
    def __init__(self):
        self.camera = None

    def open(self):
        if self.camera is None or not self.camera.isOpened():
            try:
                self.camera = cv2.VideoCapture(Constants.CAMERA_INDEX)
                time.sleep(Constants.CAMERA_INIT_DELAY)

                if self.camera.isOpened():
                    return True
                else:
                    print("Failed to open camera")
                    return False
            except Exception as e:
                print(f"Error opening camera: {e}")
                return False
        return True

    def close(self):
        if self.camera is not None:
            self.camera.release()
            self.camera = None
            print("Camera closed")

    def capture_frame(self):
        if self.camera is None or not self.camera.isOpened():
            print("Camera is not open")
            return None

        success, frame = self.camera.read()

        if success:
            frame = cv2.flip(frame, 1)
            return frame
        else:
            print("Failed to capture frame")
            return None

    def generate_video_stream(self):
        if not self.open():
            return

        try:
            while True:
                frame = self.capture_frame()
                if frame is None:
                    break

                # Encode frame as JPEG
                ret, buffer = cv2.imencode('.jpg', frame)
                if not ret:
                    break

                frame_bytes = buffer.tobytes()

                # Yield frame in HTTP streaming format
                yield (b'--frame\r\n'
                       b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')
        except GeneratorExit:
            pass
        except Exception as e:
            print(f"Error in video stream: {e}")

    def is_opened(self):
        return self.camera is not None and self.camera.isOpened()


_camera_instance = None


def get_camera():
    global _camera_instance
    if _camera_instance is None:
        _camera_instance = Camera()
    return _camera_instance