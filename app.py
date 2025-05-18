import os
import json
from flask import Flask, render_template, request, jsonify, redirect, url_for, flash
from flask_mail import Mail, Message
import tensorflow as tf
from PIL import Image
import numpy as np
from werkzeug.utils import secure_filename
from keras import models

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = '/tmp/uploads'  # Use /tmp for Vercel
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size
app.secret_key = os.environ.get('SECRET_KEY', 'your-secret-key-here')

# Mail settings
app.config['MAIL_SERVER'] = 'smtp.office365.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = os.environ.get('MAIL_EMAIL')
app.config['MAIL_PASSWORD'] = os.environ.get('MAIL_PASSWORD')
app.config['MAIL_DEFAULT_SENDER'] = os.environ.get('MAIL_EMAIL')

# Initialize mail only if credentials are set
mail = None
if app.config['MAIL_USERNAME'] and app.config['MAIL_PASSWORD']:
    mail = Mail(app)
else:
    print("Email credentials not set. Email functionality will be disabled.")

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'webp'}

# Create necessary directories
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
os.makedirs('static/uploads', exist_ok=True)

# Load the model and class names
model = None
bird_species = []

try:
    # For Vercel, we'll need to handle model loading differently
    model_path = os.path.join(os.path.dirname(__file__), 'bird_model.h5')
    classes_path = os.path.join(os.path.dirname(__file__), 'bird_classes.json')
    
    if os.path.exists(model_path):
        model = models.load_model(model_path)
    if os.path.exists(classes_path):
        with open(classes_path, 'r') as f:
            bird_species = json.load(f)
except Exception as e:
    print(f"Warning: Could not load model or classes: {e}")
    bird_species = [
        "ABBOTTS BABBLER", "ABBOTTS BOOBY", "ABYSSINIAN GROUND HORNBILL",
        "AFRICAN CROWNED CRANE", "AFRICAN EMERALD CUCKOO", "AFRICAN FIREFINCH",
        "AFRICAN OYSTER CATCHER", "AFRICAN PIED HORNBILL", "AFRICAN PYGMY GOOSE",
        "ALBATROSS", "ALBERTS TOWHEE", "ALEXANDRINE PARAKEET", "ALPINE CHOUGH",
        "ALTAMIRA YELLOWTHROAT", "AMERICAN AVOCET", "AMERICAN BITTERN",
        "AMERICAN COOT", "AMERICAN FLAMINGO", "AMERICAN GOLDFINCH", "AMERICAN KESTREL"
    ]

# Bird facts dictionary
BIRD_FACTS = {
    'abbotts_babbler': 'The Abbott\'s Babbler is known for its distinctive call and is found in Southeast Asia.',
    'abbotts_booby': 'Abbott\'s Booby is a critically endangered seabird that only nests on Christmas Island.',
    'abyssinian_ground_hornbill': 'The Abyssinian Ground Hornbill is one of the largest species of hornbill.',
    'african_crowned_crane': 'The African Crowned Crane is known for its distinctive golden crown of feathers.',
    'african_emerald_cuckoo': 'The African Emerald Cuckoo has brilliant green plumage and is a brood parasite.',
    'african_firefinch': 'The African Firefinch is known for its bright red coloration in males.',
    'african_oyster_catcher': 'The African Oystercatcher is a distinctive black bird with a bright orange-red bill.',
    'african_pied_hornbill': 'The African Pied Hornbill is known for its large black and white casque.',
    'african_pygmy_goose': 'The African Pygmy Goose is one of the smallest waterfowl species.',
    'albatross': 'Albatrosses are known for having the largest wingspan of any living bird species.',
    'alberts_towhee': 'Albert\'s Towhee is a long-tailed sparrow found in desert scrub habitats.',
    'alexandrine_parakeet': 'The Alexandrine Parakeet is known for its intelligence and ability to mimic human speech.',
    'alpine_chough': 'The Alpine Chough is one of the highest-living birds, found in mountainous regions.',
    'altamira_yellowthroat': 'The Altamira Yellowthroat is a New World warbler found in Mexico.',
    'american_avocet': 'The American Avocet is known for its distinctive upturned bill.',
    'american_bittern': 'The American Bittern is famous for its ability to camouflage in reed beds.',
    'american_coot': 'The American Coot is known for its unique lobed toes and diving ability.',
    'american_flamingo': 'The American Flamingo gets its pink coloration from the carotenoid pigments in its diet.',
    'american_goldfinch': 'The American Goldfinch is known for its bright yellow summer plumage.',
    'american_kestrel': 'The American Kestrel is the smallest falcon in North America.',
    'default': 'Birds are fascinating creatures that have evolved over millions of years!'
}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def process_image(image_path):
    """Process image for prediction"""
    img = Image.open(image_path)
    
    # Convert grayscale to RGB if needed
    if img.mode != 'RGB':
        img = img.convert('RGB')
    
    # Resize to match model's expected input size
    img = img.resize((224, 224))
    
    # Convert to array and preprocess
    img_array = np.array(img)
    img_array = img_array.astype('float32') / 255.0
    img_array = np.expand_dims(img_array, axis=0)
    
    return img_array

def get_species_name(prediction):
    """Convert prediction array to species name and confidence"""
    if not bird_species:
        return "Unknown Bird", 0.0
    
    species_idx = np.argmax(prediction[0])
    confidence = float(prediction[0][species_idx])
    species_name = bird_species[species_idx]
    
    # Convert UPPERCASE to snake_case for display and dictionary lookup
    display_name = ' '.join(word.capitalize() for word in species_name.split())
    species_key = species_name.lower().replace(' ', '_')
    
    return display_name, confidence, species_key

def send_confirmation_email(user_email, feedback_type, name):
    """Send confirmation email to user if mail is configured"""
    if not mail:
        return False
        
    subject_map = {
        'feedback': 'Thank you for your feedback',
        'bug': 'Bug Report Received',
        'feature': 'Feature Request Received',
        'other': 'Feedback Received'
    }
    
    subject = subject_map.get(feedback_type, 'Feedback Received')
    
    html_body = f"""
    <html>
        <body>
            <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
                <h2 style="color: #2d6a4f;">Thank you, {name}!</h2>
                <p>We have received your {feedback_type} submission. Our team will review it carefully.</p>
                <p>Here's what happens next:</p>
                <ul>
                    <li>Our team will review your submission</li>
                    <li>We'll investigate the matter if needed</li>
                    <li>We'll take appropriate action based on your feedback</li>
                </ul>
                <p>We appreciate you taking the time to help us improve our Bird Species Classifier.</p>
                <hr>
                <p style="font-size: 0.9em; color: #666;">
                    This is an automated message. Please do not reply to this email.
                </p>
            </div>
        </body>
    </html>
    """
    
    try:
        msg = Message(
            subject,
            recipients=[user_email],
            html=html_body
        )
        mail.send(msg)
        return True
    except Exception as e:
        print(f"Error sending email: {e}")
        return False

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/bird-facts')
def bird_facts():
    return render_template('bird_facts.html')

@app.route('/predict', methods=['POST'])
def predict():
    if 'file' not in request.files:
        return jsonify({'error': 'No file uploaded'}), 400
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No file selected'}), 400
    
    if not allowed_file(file.filename):
        return jsonify({'error': 'Invalid file type. Please upload JPG, PNG, or WebP images.'}), 400
    
    try:
        filename = secure_filename(file.filename)
        filepath = os.path.join('static/uploads', filename)
        file.save(filepath)
        
        # Process image
        img_array = process_image(filepath)
        
        if model is None:
            # For testing without model
            species = "Northern Cardinal"
            confidence = 0.92
            species_key = "northern_cardinal"
        else:
            # Make prediction
            prediction = model.predict(img_array)
            species, confidence, species_key = get_species_name(prediction)
        
        # Get fact for the species
        fact = BIRD_FACTS.get(species_key, BIRD_FACTS['default'])
        
        result = {
            'species': species,
            'confidence': confidence,
            'fact': fact,
            'image_path': filename
        }
        
        return render_template('result.html', result=result)
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/feedback')
def feedback():
    return render_template('feedback.html')

@app.route('/submit-feedback', methods=['POST'])
def submit_feedback():
    try:
        # Collect feedback data
        feedback_data = {
            'name': request.form.get('name'),
            'email': request.form.get('email'),
            'type': request.form.get('type'),
            'message': request.form.get('message')
        }
        
        # Only attempt to send email if mail is configured
        if mail:
            email_sent = send_confirmation_email(
                feedback_data['email'],
                feedback_data['type'],
                feedback_data['name']
            )
            if email_sent:
                flash('Thank you for your feedback! A confirmation email has been sent.', 'success')
            else:
                flash('Thank you for your feedback! However, there was an issue sending the confirmation email.', 'warning')
        else:
            flash('Thank you for your feedback!', 'success')
            
        return redirect(url_for('home'))
    except Exception as e:
        flash('Error submitting feedback. Please try again.', 'error')
        return redirect(url_for('feedback'))

@app.route('/endangered-birds')
def endangered_birds():
    return render_template('endangered_birds.html')

if __name__ == '__main__':
    app.run(debug=True)