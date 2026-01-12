from pymilvus import connections, Collection, FieldSchema, CollectionSchema, DataType, utility
import time
import Constants


class FaceDatabase:
    def __init__(self):
        self.collection_name = Constants.COLLECTION_NAME
        self.collection = None
        self.connect()
        self.setup_collection()

    def connect(self, max_retries=5):
        print("Connecting to Milvus database...")

        for attempt in range(max_retries):
            try:
                connections.connect(
                    alias="default",
                    host=Constants.MILVUS_HOST,
                    port=Constants.MILVUS_PORT
                )
                return
            except Exception as e:
                print(f"Connection attempt {attempt + 1} failed: {e}")
                if attempt < max_retries - 1:
                    print("Retrying in 5 seconds...")
                    time.sleep(5)
                else:
                    raise Exception("Failed to connect to database after multiple attempts")

    def setup_collection(self):
        fields = [
            FieldSchema(name="id", dtype=DataType.INT64, is_primary=True, auto_id=True),
            FieldSchema(name="name", dtype=DataType.VARCHAR, max_length=100),
            FieldSchema(name="embedding", dtype=DataType.FLOAT_VECTOR, dim=128)
        ]

        schema = CollectionSchema(fields=fields, description="Face embeddings collection")

        if not utility.has_collection(self.collection_name):
            print(f"Creating new collection: {self.collection_name}")
            self.collection = Collection(name=self.collection_name, schema=schema)

            index_params = {
                "index_type": "IVF_FLAT",
                "metric_type": "L2",  # Euclidean distance
                "params": {"nlist": 128}
            }
            self.collection.create_index(field_name="embedding", index_params=index_params)
            print("Collection created successfully!")
        else:
            print(f"Loading existing collection: {self.collection_name}")
            self.collection = Collection(name=self.collection_name)

        self.collection.load()

    def insert_face(self, name, embedding):
        entities = [
            [name],
            [embedding]
        ]

        try:
            self.collection.insert(entities)
            self.collection.flush()
            return True
        except Exception as e:
            print(f"Error inserting face: {e}")
            return False

    def search_similar_face(self, embedding, limit=1):
        search_params = {
            "metric_type": "L2",
            "params": {"nprobe": 10}
        }

        try:
            results = self.collection.search(
                data=[embedding],
                anns_field="embedding",
                param=search_params,
                limit=limit,
                output_fields=["name"]
            )
            return results
        except Exception as e:
            print(f"Error searching faces: {e}")
            return None