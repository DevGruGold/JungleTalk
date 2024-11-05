# First, ensure you run these installation commands in a separate cell:
"""
!pip install flask flask-cors librosa transformers tensorflow
"""

import os
import torch
import librosa
import numpy as np
import flask
import transformers
from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
from google.colab import drive
from transformers import pipeline
import tensorflow as tf
from tensorflow.keras.applications import VGG16
import io
import wave

# Mount Google Drive
drive.mount('/content/drive')

# Create application directory structure
def create_app_structure():
    base_path = "/content/drive/MyDrive/HablaJungla"
    directories = [
        "",
        "/static",
        "/static/css",
        "/static/js",
        "/static/audio",
        "/templates",
    ]
    
    for dir in directories:
        full_path = base_path + dir
        if not os.path.exists(full_path):
            os.makedirs(full_path)
    
    return base_path

# Initialize Flask application
app = Flask(__name__)
CORS(app)

# Audio processing utilities
class AudioProcessor:
    def __init__(self):
        self.sample_rate = 44100
        
    def process_audio_file(self, audio_file):
        audio_data, _ = librosa.load(audio_file, sr=self.sample_rate)
        features = librosa.feature.mfcc(y=audio_data, 
                                      sr=self.sample_rate,
                                      n_mfcc=13)
        return features

# Animal sound classifier
class AnimalSoundClassifier:
    def __init__(self):
        self.model = VGG16(
            weights='imagenet',
            include_top=False,
            input_shape=(224, 224, 3)
        )
        self.classes = ['dog', 'cat', 'bird', 'lion', 'elephant']
        
    def classify_sound(self, features):
        try:
            # Prepare features for VGG16
            target_length = 224
            current_length = features.shape[1]
            
            if current_length < target_length:
                padding = np.zeros((features.shape[0], target_length - current_length))
                features = np.hstack((features, padding))
            else:
                features = features[:, :target_length]
            
            input_tensor = np.expand_dims(features, axis=-1)
            input_tensor = np.expand_dims(input_tensor, axis=0)
            input_tensor = np.repeat(input_tensor, 3, axis=-1)
            
            predictions = self.model.predict(input_tensor, verbose=0)
            prediction_sum = np.sum(predictions, axis=(1, 2))
            predicted_class = self.classes[np.argmax(prediction_sum) % len(self.classes)]
            
            return predicted_class
            
        except Exception as e:
            print(f"Classification error: {e}")
            return 'unknown'

# Dialogue generator
class DialogueGenerator:
    def __init__(self):
        self.generator = pipeline('text-generation', 
                                model='distilgpt2',
                                max_length=50)
        self.templates = {
            'dog': "A playful dog says: ",
            'cat': "A sassy cat declares: ",
            'bird': "A chatty bird announces: ",
            'lion': "A majestic lion proclaims: ",
            'elephant': "A wise elephant shares: "
        }
    
    def generate_dialogue(self, animal_type):
        prompt = self.templates.get(animal_type, "An animal says: ")
        response = self.generator(prompt, num_return_sequences=1)
        return response[0]['generated_text']

# Flask routes
@app.route('/')
def home():
    return render_template('index.html')

@app.route('/process_audio', methods=['POST'])
def process_audio():
    if 'audio' not in request.files:
        return jsonify({'error': 'No audio file provided'}), 400
    
    audio_file = request.files['audio']
    
    # Process the audio
    audio_processor = AudioProcessor()
    features = audio_processor.process_audio_file(audio_file)
    
    animal_type = animal_classifier.classify_sound(features)
    dialogue = dialogue_generator.generate_dialogue(animal_type)
    
    return jsonify({
        'animal_type': animal_type,
        'dialogue': dialogue
    })

def create_html_template(base_path):
    html_content = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Habla Jungla - Animal Sound Translator</title>
        <link rel="stylesheet" href="{{ url_for('static', filename='css/style.css') }}">
    </head>
    <body>
        <div class="container">
            <h1>🌴 Habla Jungla 🦁</h1>
            <p class="subtitle">Your Animal Sound Translator</p>
            <div class="recorder">
                <button id="recordButton" class="primary-button">Start Recording</button>
                <button id="stopButton" class="secondary-button" disabled>Stop Recording</button>
                <div id="recordingStatus"></div>
            </div>
            <div class="result">
                <div id="animalType"></div>
                <div id="dialogue"></div>
            </div>
        </div>
        <script src="{{ url_for('static', filename='js/main.js') }}"></script>
    </body>
    </html>
    """
    
    with open(f"{base_path}/templates/index.html", "w") as f:
        f.write(html_content)

def create_css_file(base_path):
    css_content = """
    body {
        font-family: 'Arial', sans-serif;
        margin: 0;
        padding: 20px;
        background-color: #f4f9f4;
    }
    
    .container {
        max-width: 800px;
        margin: 0 auto;
        background-color: white;
        padding: 30px;
        border-radius: 15px;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    }
    
    h1 {
        color: #2c5530;
        text-align: center;
        margin-bottom: 10px;
    }
    
    .subtitle {
        text-align: center;
        color: #666;
        margin-bottom: 30px;
    }
    
    .recorder {
        text-align: center;
        margin: 30px 0;
    }
    
    .primary-button {
        padding: 12px 24px;
        margin: 0 10px;
        border: none;
        border-radius: 25px;
        background-color: #4CAF50;
        color: white;
        cursor: pointer;
        font-size: 16px;
        transition: all 0.3s ease;
    }
    
    .secondary-button {
        padding: 12px 24px;
        margin: 0 10px;
        border: none;
        border-radius: 25px;
        background-color: #ff6b6b;
        color: white;
        cursor: pointer;
        font-size: 16px;
        transition: all 0.3s ease;
    }
    
    button:disabled {
        background-color: #cccccc;
        cursor: not-allowed;
    }
    
    .result {
        margin-top: 30px;
        padding: 20px;
        border: 2px solid #e0e0e0;
        border-radius: 10px;
        background-color: #fafafa;
    }
    
    #recordingStatus {
        margin-top: 15px;
        color: #666;
        font-style: italic;
    }
    
    #animalType {
        font-weight: bold;
        color: #2c5530;
        margin-bottom: 10px;
    }
    
    #dialogue {
        color: #444;
        line-height: 1.5;
    }
    """
    
    with open(f"{base_path}/static/css/style.css", "w") as f:
        f.write(css_content)

def create_js_file(base_path):
    js_content = """
    let mediaRecorder;
    let audioChunks = [];
    
    const recordButton = document.getElementById('recordButton');
    const stopButton = document.getElementById('stopButton');
    
    recordButton.addEventListener('click', startRecording);
    stopButton.addEventListener('click', stopRecording);
    
    async function startRecording() {
        try {
            const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
            mediaRecorder = new MediaRecorder(stream);
            
            mediaRecorder.ondataavailable = (event) => {
                audioChunks.push(event.data);
            };
            
            mediaRecorder.onstop = async () => {
                const audioBlob = new Blob(audioChunks, { type: 'audio/wav' });
                const formData = new FormData();
                formData.append('audio', audioBlob);
                
                try {
                    document.getElementById('recordingStatus').textContent = 'Processing...';
                    
                    const response = await fetch('/process_audio', {
                        method: 'POST',
                        body: formData
                    });
                    
                    const result = await response.json();
                    
                    document.getElementById('animalType').textContent = 
                        `🎯 Detected Animal: ${result.animal_type}`;
                    document.getElementById('dialogue').textContent = 
                        `💭 ${result.dialogue}`;
                    
                    document.getElementById('recordingStatus').textContent = '';
                    
                } catch (error) {
                    console.error('Error:', error);
                    document.getElementById('recordingStatus').textContent = 
                        '❌ Error processing audio';
                }
                
                audioChunks = [];
            };
            
            mediaRecorder.start();
            document.getElementById('recordingStatus').textContent = '🎤 Recording...';
            recordButton.disabled = true;
            stopButton.disabled = false;
            
        } catch (err) {
            console.error('Error:', err);
            document.getElementById('recordingStatus').textContent = 
                '❌ Error accessing microphone';
        }
    }
    
    function stopRecording() {
        mediaRecorder.stop();
        recordButton.disabled = false;
        stopButton.disabled = true;
    }
    """
    
    with open(f"{base_path}/static/js/main.js", "w") as f:
        f.write(js_content)

def setup_habla_jungla():
    try:
        # Create directory structure
        base_path = create_app_structure()
        
        # Create frontend files
        create_html_template(base_path)
        create_css_file(base_path)
        create_js_file(base_path)
        
        # Initialize classifiers
        global animal_classifier, dialogue_generator
        animal_classifier = AnimalSoundClassifier()
        dialogue_generator = DialogueGenerator()
        
        # Start Flask app
        print("Starting Habla Jungla...")
        app.run(port=5000)
        
    except Exception as e:
        print(f"Error during setup: {str(e)}")
        raise

if __name__ == "__main__":
    setup_habla_jungla()
