import cv2
import face_recognition
import numpy as np
from pymilvus import connections, Collection, FieldSchema, CollectionSchema, DataType, utility
import pickle
import time


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
        # Define schema for face embeddings
        fields = [
            FieldSchema(name="id", dtype=DataType.INT64, is_primary=True, auto_id=True),
            FieldSchema(name="name", dtype=DataType.VARCHAR, max_length=100),
            FieldSchema(name="embedding", dtype=DataType.FLOAT_VECTOR, dim=128)
        ]

        schema = CollectionSchema(fields=fields, description="Face embeddings collection")

        # Create collection if it doesn't exist
        if not utility.has_collection(self.collection_name):
            print(f"Creating collection: {self.collection_name}")
            self.collection = Collection(name=self.collection_name, schema=schema)

            # Create index for fast similarity search
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

        # Load collection into memory
        self.collection.load()

    def register_face(self, image, name):
        """Register a new face in the database"""
        # Detect face and get encoding
        face_locations = face_recognition.face_locations(image)

        if len(face_locations) == 0:
            print("No face detected in the image!")
            return False

        if len(face_locations) > 1:
            print("Multiple faces detected! Please provide an image with only one face.")
            return False

        # Get face encoding (128-dimensional vector)
        face_encoding = face_recognition.face_encodings(image, face_locations)[0]

        # Insert into Milvus
        entities = [
            [name],  # name field
            [face_encoding.tolist()]  # embedding field
        ]

        try:
            self.collection.insert(entities)
            self.collection.flush()
            print(f"Successfully registered face for: {name}")
            return True
        except Exception as e:
            print(f"Error registering face: {e}")
            return False

    def recognize_face(self, image, tolerance=0.6):
        """Recognize faces in the given image"""
        # Detect faces in the image
        face_locations = face_recognition.face_locations(image)

        if len(face_locations) == 0:
            return []

        # Get face encodings
        face_encodings = face_recognition.face_encodings(image, face_locations)

        results = []

        for face_encoding, face_location in zip(face_encodings, face_locations):
            # Search for similar faces in Milvus
            search_params = {"metric_type": "L2", "params": {"nprobe": 10}}

            result = self.collection.search(
                data=[face_encoding.tolist()],
                anns_field="embedding",
                param=search_params,
                limit=1,
                output_fields=["name"]
            )

            # Check if we found a match within tolerance
            if len(result[0]) > 0:
                distance = result[0][0].distance
                # Convert L2 distance to similarity (lower is better)
                # Typical face_recognition tolerance is 0.6
                if distance < tolerance:
                    name = result[0][0].entity.get('name')
                    confidence = 1 - (distance / tolerance)
                    results.append({
                        'name': name,
                        'location': face_location,
                        'confidence': confidence
                    })
                else:
                    results.append({
                        'name': 'Unknown',
                        'location': face_location,
                        'confidence': 0
                    })
            else:
                results.append({
                    'name': 'Unknown',
                    'location': face_location,
                    'confidence': 0
                })

        return results

    def list_registered_faces(self):
        """List all registered faces"""
        try:
            # Query all names from the collection
            result = self.collection.query(
                expr="id > 0",
                output_fields=["name", "id"]
            )

            if result:
                print("\nRegistered faces:")
                for item in result:
                    print(f"  - {item['name']} (ID: {item['id']})")
                return [item['name'] for item in result]
            else:
                print("No faces registered yet.")
                return []
        except Exception as e:
            print(f"Error listing faces: {e}")
            return []


def register_mode(system):
    """Mode for registering new faces"""
    print("\n=== FACE REGISTRATION MODE ===")
    print("Press 'c' to capture and register a face")
    print("Press 'q' to quit registration mode")

    cap = cv2.VideoCapture(0)

    while True:
        ret, frame = cap.read()
        if not ret:
            print("Failed to grab frame")
            break

        # Display the frame
        cv2.imshow('Register Face - Press C to Capture', frame)

        key = cv2.waitKey(1) & 0xFF

        if key == ord('c'):
            # Ask for name
            cap.release()
            cv2.destroyAllWindows()

            name = input("Enter the person's name: ").strip()
            if name:
                # Convert BGR to RGB
                rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                system.register_face(rgb_frame, name)

            # Restart camera
            cap = cv2.VideoCapture(0)

        elif key == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()


def recognition_mode(system):
    """Mode for real-time face recognition"""
    print("\n=== FACE RECOGNITION MODE ===")
    print("Press 'q' to quit")

    cap = cv2.VideoCapture(0)

    # Process every N frames for better performance
    process_every_n_frames = 2
    frame_count = 0

    while True:
        ret, frame = cap.read()
        if not ret:
            print("Failed to grab frame")
            break

        frame_count += 1

        # Only process every Nth frame
        if frame_count % process_every_n_frames == 0:
            # Convert BGR to RGB
            rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

            # Recognize faces
            results = system.recognize_face(rgb_frame)

            # Draw boxes and names
            for result in results:
                top, right, bottom, left = result['location']
                name = result['name']
                confidence = result['confidence']

                # Draw rectangle
                color = (0, 255, 0) if name != 'Unknown' else (0, 0, 255)
                cv2.rectangle(frame, (left, top), (right, bottom), color, 2)

                # Draw label
                label = f"{name}"
                if name != 'Unknown':
                    label += f" ({confidence:.2f})"

                cv2.rectangle(frame, (left, bottom - 35), (right, bottom), color, cv2.FILLED)
                cv2.putText(frame, label, (left + 6, bottom - 6),
                            cv2.FONT_HERSHEY_DUPLEX, 0.6, (255, 255, 255), 1)

        # Display the frame
        cv2.imshow('Face Recognition - Press Q to Quit', frame)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()


def main():
    """Main function"""
    print("=" * 50)
    print("FACE RECOGNITION SYSTEM")
    print("=" * 50)

    # Initialize the system
    try:
        system = FaceRecognitionSystem()
    except Exception as e:
        print(f"\nError: {e}")
        print("\nMake sure Milvus is running in Docker!")
        print("Run: docker-compose up -d")
        return

    while True:
        print("\n" + "=" * 50)
        print("MAIN MENU")
        print("=" * 50)
        print("1. Register new face")
        print("2. Start face recognition")
        print("3. List registered faces")
        print("4. Exit")

        choice = input("\nEnter your choice (1-4): ").strip()

        if choice == '1':
            register_mode(system)
        elif choice == '2':
            recognition_mode(system)
        elif choice == '3':
            system.list_registered_faces()
        elif choice == '4':
            print("Goodbye!")
            break
        else:
            print("Invalid choice! Please try again.")


if __name__ == "__main__":
    main()