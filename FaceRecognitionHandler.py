# FaceRecognitionHandler.py
# Handles all face detection and recognition operations

import face_recognition
import Constants
from DbHandler import FaceDatabase


class FaceRecognitionHandler:

    def __init__(self):
        self.database = FaceDatabase()

    def detect_face(self, image):
        face_locations = face_recognition.face_locations(image)

        if len(face_locations) == 0:
            return None, "No face detected in the image!"

        if len(face_locations) > 1:
            return None, "Multiple faces detected! Please show only one face."

        face_encodings = face_recognition.face_encodings(image, face_locations)

        if len(face_encodings) == 0:
            return None, "Could not extract face features!"

        return (face_locations[0], face_encodings[0]), None

    def register_face(self, image, name):
        face_data, error = self.detect_face(image)
        if error:
            return False, error

        face_location, face_encoding = face_data

        is_duplicate, existing_name = self._check_duplicate_face(face_encoding)
        if is_duplicate:
            return False, f"This face is already registered as '{existing_name}'"

        # Step 3: Store the face in the database
        success = self.database.insert_face(name, face_encoding.tolist())

        if success:
            return True, f"Successfully registered face for: {name}"
        else:
            return False, "Failed to save face to database"

    def recognize_face(self, image):
        """
        Recognize a face in the image.

        Args:
            image: RGB image array

        Returns:
            tuple: (name: str or None, confidence: float or error_message: str)
        """
        # Step 1: Detect the face
        face_data, error = self.detect_face(image)
        if error:
            return None, error

        face_location, face_encoding = face_data

        # Step 2: Search for similar faces in the database
        results = self.database.search_similar_face(face_encoding.tolist(), limit=1)

        if not results or len(results[0]) == 0:
            return None, "Face not found in database"

        # Step 3: Check if the match is good enough
        distance = results[0][0].distance

        if distance < Constants.FACE_RECOGNITION_TOLERANCE:
            # Face recognized!
            name = results[0][0].entity.get('name')
            confidence = 1 - (distance / Constants.FACE_RECOGNITION_TOLERANCE)
            return name, confidence
        else:
            # Face not similar enough
            return None, "Face not recognized"

    def _check_duplicate_face(self, face_encoding):
        try:
            results = self.database.search_similar_face(face_encoding.tolist(), limit=1)

            if results and len(results[0]) > 0:
                distance = results[0][0].distance

                if distance < Constants.DUPLICATE_FACE_THRESHOLD:
                    existing_name = results[0][0].entity.get('name')
                    return True, existing_name

            return False, None
        except Exception as e:
            print(f"Error checking for duplicate: {e}")
            return False, None

    def list_all_faces(self):
        faces = self.database.get_all_faces()

        if faces:
            for face in faces:
                print(f"  - {face['name']} (ID: {face['id']})")
            return [face['name'] for face in faces]
        else:
            print("No faces registered yet.")
            return []