from flask import Flask, render_template, Response, jsonify, request
import cv2
import Constants
from CameraHandler import get_camera
from FaceRecognitionHandler import FaceRecognitionHandler

app = Flask(__name__)
try:
    face_system = FaceRecognitionHandler()
    print("\nSystem ready!")
except Exception as e:
    print(f"\nError: {e}")
    print("\nMake sure Milvus is running!")
    print("Run: docker-compose up -d")
    face_system = None

print("=" * 60)

@app.route('/')
def index():
    return render_template('index.html')


@app.route('/video_feed')
def video_feed():
    camera = get_camera()
    return Response(
        camera.generate_video_stream(),
        mimetype='multipart/x-mixed-replace; boundary=frame'
    )


@app.route('/register', methods=['POST'])
def register():
    data = request.json
    name = data.get('name', '').strip()

    if not name:
        return jsonify({
            'success': False,
            'message': 'Name is required'
        })

    camera = get_camera()
    frame = camera.capture_frame()

    if frame is None:
        return jsonify({
            'success': False,
            'message': 'Failed to capture frame'
        })

    # Convert from BGR (OpenCV format) to RGB (face_recognition format)
    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

    success, message = face_system.register_face(rgb_frame, name)

    return jsonify({
        'success': success,
        'message': message
    })


@app.route('/recognize')
def recognize():
    camera = get_camera()
    frame = camera.capture_frame()

    if frame is None:
        return jsonify({
            'success': False,
            'message': 'Failed to capture frame'
        })

    # Convert from BGR to RGB
    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

    name, info = face_system.recognize_face(rgb_frame)

    if name:
        return jsonify({
            'success': True,
            'name': name,
            'confidence': info
        })
    else:
        return jsonify({
            'success': False,
            'message': info
        })


@app.route('/stop_camera')
def stop_camera():
    camera = get_camera()
    camera.close()
    return jsonify({'success': True})

if __name__ == '__main__':
    print("\n")
    print(f"\nServer will start at: http://{Constants.FLASK_HOST}:{Constants.FLASK_PORT}")
    print("\nPress Ctrl+C to stop the server")
    print("\n")

    app.run(
        host=Constants.FLASK_HOST,
        port=Constants.FLASK_PORT,
        debug=Constants.FLASK_DEBUG,
        threaded=True
    )