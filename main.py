from flask import Flask, Response, send_from_directory
from flask_cors import CORS
from picamera2 import Picamera2
import io
import time
from PIL import Image

app = Flask(__name__)
CORS(app)  # Ajoutez cette ligne pour activer CORS

# Initialiser la caméra
picam2 = Picamera2()

# Configurer la caméra pour une capture
camera_config = picam2.create_still_configuration(main={"size": (1280, 720)}, buffer_count=1)
picam2.configure(camera_config)

# Activer l'autofocus
picam2.set_controls({"AfMode": 2})  # 2 = Mode Autofocus Continu

# Démarrer la caméra
picam2.start()

properties = picam2.camera_properties
print(properties)

def generate_frames():
    stream = io.BytesIO()
    while True:

        # Capturer l'image en tant que tableau numpy
        image_array = picam2.capture_array()

        # Convertir le tableau numpy en flux JPEG
        stream = io.BytesIO()
        image = Image.fromarray(image_array)
        image.save(stream, format='JPEG')  # Encoder en JPEG
        stream.seek(0)
        
        # Générer les données pour le streaming
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + stream.read() + b'\r\n')
        
        # Réinitialiser le flux pour la prochaine capture
        stream.seek(0)
        stream.truncate()

@app.route('/')
def index():
    return "PiCamera2 video stream is running. Go to /video to watch the stream."

@app.route('/video')
def video_feed():
    return Response(generate_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/image')
def get_image():
    stream = io.BytesIO()
    picam2.start()
    picam2.capture_file(stream, format='jpeg')
    picam2.stop()
    stream.seek(0)
    return Response(stream.read(), mimetype='image/jpeg')


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
