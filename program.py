from flask import Flask, render_template, Response, jsonify, request
import cv2
import face_recognition
import numpy as np
from pymilvus import connections, Collection, FieldSchema, CollectionSchema, DataType, utility
import time
import base64

app = Flask(__name__)


class FaceRecognitionSystem:
    def __init__(self, collection_name="faces"):
        """Initialize the face recognition system with Milvus connection"""
        self.collection_name = collection_name
        self.connect_to_milvus()
        self.setup_collection()

    def connect_to_milvus(self, max_retries=5):
        """Connect to Milvus database running in Docker"""
        print("Connecting to Milvus...")
        for attempt in range(max_retries):
            try:
                connections.connect(
                    alias="default",
                    host='localhost',
                    port='19530'
                )
                print("Successfully connected to Milvus!")
                return
            except Exception as e:
                print(f"Connection attempt {attempt + 1} failed: {e}")
                if attempt < max_retries - 1:
                    print("Retrying in 5 seconds...")
                    time.sleep(5)
                else:
                    raise Exception("Failed to connect to Milvus after multiple attempts")

    def setup_collection(self):
        """Create or load the face embeddings collection"""
        fields = [
            FieldSchema(name="id", dtype=DataType.INT64, is_primary=True, auto_id=True),
            FieldSchema(name="name", dtype=DataType.VARCHAR, max_length=100),
            FieldSchema(name="embedding", dtype=DataType.FLOAT_VECTOR, dim=128)
        ]

        schema = CollectionSchema(fields=fields, description="Face embeddings collection")

        if not utility.has_collection(self.collection_name):
            print(f"Creating collection: {self.collection_name}")
            self.collection = Collection(name=self.collection_name, schema=schema)

            index_params = {
                "index_type": "IVF_FLAT",
                "metric_type": "L2",
                "params": {"nlist": 128}
            }
            self.collection.create_index(field_name="embedding", index_params=index_params)
            print("Collection created successfully!")
        else:
            print(f"Loading existing collection: {self.collection_name}")
            self.collection = Collection(name=self.collection_name)

        self.collection.load()

    def register_face(self, image, name):
        """Register a new face in the database"""
        face_locations = face_recognition.face_locations(image)

        if len(face_locations) == 0:
            return False, "No face detected in the image!"

        if len(face_locations) > 1:
            return False, "Multiple faces detected! Please show only one face."

        face_encoding = face_recognition.face_encodings(image, face_locations)[0]

        # Check if this face is already registered
        search_params = {"metric_type": "L2", "params": {"nprobe": 10}}

        try:
            result = self.collection.search(
                data=[face_encoding.tolist()],
                anns_field="embedding",
                param=search_params,
                limit=1,
                output_fields=["name"]
            )

            # If we find a very similar face (distance < 0.4), it's likely already registered
            if len(result[0]) > 0 and result[0][0].distance < 0.4:
                existing_name = result[0][0].entity.get('name')
                return False, f"This face is already registered as '{existing_name}'"
        except Exception as e:
            print(f"Error checking for duplicate: {e}")

        # Proceed with registration
        entities = [
            [name],
            [face_encoding.tolist()]
        ]

        try:
            self.collection.insert(entities)
            self.collection.flush()
            return True, f"Successfully registered face for: {name}"
        except Exception as e:
            return False, f"Error registering face: {e}"

    def recognize_face(self, image, tolerance=0.6):
        """Recognize faces in the given image"""
        face_locations = face_recognition.face_locations(image)

        if len(face_locations) == 0:
            return None, "No face detected"

        face_encodings = face_recognition.face_encodings(image, face_locations)

        if len(face_encodings) == 0:
            return None, "Could not encode face"

        face_encoding = face_encodings[0]

        search_params = {"metric_type": "L2", "params": {"nprobe": 10}}

        result = self.collection.search(
            data=[face_encoding.tolist()],
            anns_field="embedding",
            param=search_params,
            limit=1,
            output_fields=["name"]
        )

        if len(result[0]) > 0:
            distance = result[0][0].distance
            if distance < tolerance:
                name = result[0][0].entity.get('name')
                confidence = 1 - (distance / tolerance)
                return name, confidence

        return None, "Face not recognized"


# Initialize the system
try:
    face_system = FaceRecognitionSystem()
except Exception as e:
    print(f"Error initializing face recognition system: {e}")
    face_system = None

# Camera management
camera = None


def get_camera():
    global camera
    if camera is None or not camera.isOpened():
        camera = cv2.VideoCapture(0)
        # Give camera time to initialize
        import time
        time.sleep(0.5)
    return camera


def release_camera():
    global camera
    if camera is not None:
        camera.release()
        camera = None


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/video_feed')
def video_feed():
    def generate():
        cap = get_camera()
        try:
            while True:
                success, frame = cap.read()
                if not success:
                    break

                # Flip horizontally for mirror effect
                frame = cv2.flip(frame, 1)

                ret, buffer = cv2.imencode('.jpg', frame)
                if not ret:
                    break

                frame_bytes = buffer.tobytes()

                yield (b'--frame\r\n'
                       b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')
        except GeneratorExit:
            # Client disconnected
            pass

    return Response(generate(), mimetype='multipart/x-mixed-replace; boundary=frame')


@app.route('/capture_frame')
def capture_frame():
    cap = get_camera()
    success, frame = cap.read()

    if not success:
        return jsonify({'success': False, 'message': 'Failed to capture frame'})

    # Convert to RGB
    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

    # Encode frame to base64
    ret, buffer = cv2.imencode('.jpg', frame)
    jpg_as_text = base64.b64encode(buffer).decode('utf-8')

    return jsonify({
        'success': True,
        'frame': jpg_as_text,
        'rgb_frame': rgb_frame.tolist()  # For processing
    })


@app.route('/register', methods=['POST'])
def register():
    data = request.json
    name = data.get('name')

    if not name:
        return jsonify({'success': False, 'message': 'Name is required'})

    cap = get_camera()
    success, frame = cap.read()

    if not success:
        return jsonify({'success': False, 'message': 'Failed to capture frame'})

    # Flip horizontally to match video feed
    frame = cv2.flip(frame, 1)
    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

    success, message = face_system.register_face(rgb_frame, name)

    return jsonify({'success': success, 'message': message})


@app.route('/recognize')
def recognize():
    cap = get_camera()
    success, frame = cap.read()

    if not success:
        return jsonify({'success': False, 'message': 'Failed to capture frame'})

    # Flip horizontally to match video feed
    frame = cv2.flip(frame, 1)
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
    release_camera()
    return jsonify({'success': True})


if __name__ == '__main__':
    app.run(debug=True, threaded=True)