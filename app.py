import os
import json
import random
from flask import Flask, render_template, request, jsonify, redirect, url_for, flash
from flask_mail import Mail, Message
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 5 * 1024 * 1024  # 5MB max file size for faster processing
app.secret_key = os.environ.get('SECRET_KEY', 'your-secret-key-here')

# Mail settings
app.config['MAIL_SERVER'] = 'smtp.office365.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = os.environ.get('MAIL_EMAIL')
app.config['MAIL_PASSWORD'] = os.environ.get('MAIL_PASSWORD')
app.config['MAIL_DEFAULT_SENDER'] = os.environ.get('MAIL_EMAIL')

# Initialize mail
mail = Mail(app) if app.config['MAIL_USERNAME'] and app.config['MAIL_PASSWORD'] else None

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'webp'}

# Hardcoded bird species list for serverless environment
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

def get_demo_prediction():
    """Get a demo prediction for testing"""
    species_name = random.choice(bird_species)
    confidence = round(random.uniform(0.85, 0.99), 3)
    species_key = species_name.lower().replace(' ', '_')
    return species_name, confidence, species_key

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
    if file.filename == '' or not allowed_file(file.filename):
        return jsonify({'error': 'Invalid file type. Please upload JPG, PNG, or WebP images.'}), 400
    
    try:
        # Get demo prediction
        species, confidence, species_key = get_demo_prediction()
        
        # Get fact for the species
        fact = BIRD_FACTS.get(species_key, BIRD_FACTS['default'])
        
        result = {
            'species': ' '.join(word.capitalize() for word in species.split('_')),
            'confidence': confidence,
            'fact': fact,
            'image_path': secure_filename(file.filename)
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

# Health check endpoint for Vercel
@app.route('/health')
def health_check():
    return jsonify({'status': 'healthy'}), 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 3000)))