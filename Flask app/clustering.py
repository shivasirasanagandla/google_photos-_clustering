import cv2
from mtcnn import MTCNN
import face_recognition
import os
from tqdm import tqdm
from sklearn.cluster import DBSCAN
import logging
import contextlib
import tensorflow as tf
import warnings


# Suppress TensorFlow logging
# Suppress TensorFlow logs at level 3 (ERROR)
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'
tf.get_logger().setLevel('ERROR')

# Configure logging to suppress logs from TensorFlow and MTCNN
logging.getLogger('tensorflow').setLevel(logging.FATAL)
logging.getLogger('mtcnn').setLevel(logging.ERROR)

# Suppress warnings
warnings.filterwarnings('ignore')

# Function to suppress stdout and stderr


@contextlib.contextmanager
def suppress_output():
    with open(os.devnull, 'w', encoding='utf-8') as fnull:
        with contextlib.redirect_stdout(fnull), contextlib.redirect_stderr(fnull):
            yield


def detect_faces_mtcnn(image):
    """
    Detect faces using MTCNN and return bounding boxes in a format compatible with face_recognition.
    """
    with suppress_output():
        # Initialize the MTCNN detector without printing logs
        detector = MTCNN()

        # Detect faces in the image
        faces = detector.detect_faces(image)

        # Filter faces with confidence higher than 0.70 and extract their bounding boxes
        rectangles = []
        for face in faces:
            if face['confidence'] > 0.50:
                x, y, width, height = face['box']
                # Convert to top, right, bottom, left format
                top, right, bottom, left = y, x + width, y + height, x
                rectangles.append((top, right, bottom, left))

        return rectangles




def get_embeddings(rgb_image, face_locations):
    """
    Extract face embeddings from the given image based on face locations.
    Args:
    rgb_image (np.array): RGB image from which to extract embeddings.
    face_locations (list): List of face locations in (top, right, bottom, left) format.
    Returns:
    list: List of face encodings.
    """
    if not face_locations:
        return []
    # Compute face embeddings
    face_encodings = face_recognition.face_encodings(rgb_image, face_locations)
    return face_encodings


def process_images(dirpath):
    """
    Process images in the given directory to extract face embeddings.
    Args:
    dirpath (str): Path to the directory containing images.
    Returns:
    list, list: List of embeddings and list of corresponding image paths.
    """
    embeddings = []
    image_paths = []

    # Iterate over all files in the directory
    for filename in tqdm(os.listdir(dirpath)):
        file_path = os.path.join(dirpath, filename)
        image = cv2.imread(file_path)

        # Check if the image was loaded successfully
        if image is None:
            print(f"Error: Could not load image from {file_path}")
            continue

        # Convert the image from BGR to RGB for face_recognition
        rgb_image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

        # Detect faces and extract face images
        face_locations = detect_faces_mtcnn(rgb_image)

        # Extract embeddings for each detected face
        face_encodings = get_embeddings(rgb_image, face_locations)

        for encoding in face_encodings:
            embeddings.append(encoding)
            image_paths.append(file_path)

    return embeddings, image_paths




def cluster(uploads_path):
    embeddings, image_paths = process_images(uploads_path)
    # Perform clustering
    cluster_labels = []
    try:
        # Use DBSCAN for clustering
        eps = 0.54  # Example epsilon value
        min_samples = 3  # Example min_samples value
        dbscan = DBSCAN(eps=eps, min_samples=min_samples)
        cluster_labels = dbscan.fit_predict(embeddings)
    
    except Exception as e:
        print(f"Error in clustering: {str(e)}")
    
    return cluster_labels ,image_paths


if __name__ == "__main__":
    # Example usage when run as a script
    upload_folder = 'server/uploads'
    labels, paths = cluster(os.path.join(os.curdir, upload_folder))
    print("Cluster Labels:", labels)
    print("Image Paths:", paths)
