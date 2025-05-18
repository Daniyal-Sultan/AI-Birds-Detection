# Bird Species Classifier

A web application that uses deep learning to classify bird species from uploaded images. Built with Flask, TensorFlow, and Bootstrap.

## Features

- **Bird Image Classification**
  - Upload images of birds (JPG, PNG, WebP)
  - Get instant species predictions with confidence scores
  - View interesting facts about identified birds
  - Mobile-friendly interface
  - Dark mode support with theme persistence

- **Advanced ML Model**
  - Trained on 20 diverse bird species
  - High accuracy (99% on test set)
  - Uses transfer learning with MobileNetV2
  - Robust data augmentation
  - Model checkpointing and early stopping

- **Interactive Bird Facts Page**
  - Learn about different bird species
  - Fascinating facts about bird behavior and abilities
  - Beautiful, responsive card layout
  - Nature-themed design

- **Feedback System**
  - Submit feedback, bug reports, or feature requests
  - Automatic email confirmation (when configured)
  - User-friendly form interface

## Supported Bird Species

The model can identify 20 bird species:
1. Abbott's Babbler
2. Abbott's Booby
3. Abyssinian Ground Hornbill
4. African Crowned Crane
5. African Emerald Cuckoo
6. African Firefinch
7. African Oyster Catcher
8. African Pied Hornbill
9. African Pygmy Goose
10. Albatross
11. Albert's Towhee
12. Alexandrine Parakeet
13. Alpine Chough
14. Altamira Yellowthroat
15. American Avocet
16. American Bittern
17. American Coot
18. American Flamingo
19. American Goldfinch
20. American Kestrel

## Technical Stack

- **Backend**: Flask (Python)
- **ML Model**: TensorFlow/Keras (MobileNetV2)
- **Frontend**: Bootstrap 5, Font Awesome
- **Email**: Flask-Mail
- **Image Processing**: Pillow, NumPy
- **Data Augmentation**: Keras ImageDataGenerator

## Installation

1. Clone the repository
2. Create a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## Configuration

### Email Setup (Optional)
To enable email notifications for feedback:

1. Set environment variables:
   ```bash
   # Windows PowerShell
   $env:MAIL_EMAIL="your.email@lhr.nu.edu.pk"
   $env:MAIL_PASSWORD="your-email-password"

   # Linux/Mac
   export MAIL_EMAIL="your.email@lhr.nu.edu.pk"
   export MAIL_PASSWORD="your-email-password"
   ```

2. The application uses Office 365 SMTP server (smtp.office365.com) by default

### Running the Application

```bash
python app.py
```
The application will be available at `http://localhost:5000`

## Model Architecture and Training

The classification model uses transfer learning with MobileNetV2:

- **Base Model**: MobileNetV2 (pre-trained on ImageNet)
- **Input Size**: 224x224 pixels, RGB
- **Training Parameters**:
  - Batch size: 32
  - Epochs: 10
  - Optimizer: Adam
  - Loss: Categorical Crossentropy
  
- **Data Augmentation**:
  - Rotation range: 20°
  - Width/Height shift: 20%
  - Horizontal flip
  - Fill mode: nearest

- **Performance**:
  - Training accuracy: 95.51%
  - Validation accuracy: 98.00%
  - Test accuracy: 99.00%

## Directory Structure

```
├── app.py                    # Main Flask application
├── BirdModelTraining.py      # Model training script
├── bird_model.h5             # Trained model
├── bird_classes.json         # Class names
├── requirements.txt          # Python dependencies
├── static/                   # Static files (CSS, uploads)
│   ├── css/                 # Stylesheets
│   └── uploads/            # Image upload directory
├── templates/               # HTML templates
├── dataset/                # Training dataset
│   ├── train/             # Training images
│   ├── valid/             # Validation images
│   └── test/              # Test images
└── uploads/                # Temporary upload directory
```

## Usage

1. Start the Flask application
2. Upload a bird image through the web interface
3. The model will:
   - Process the image
   - Identify the bird species
   - Display the prediction confidence
   - Show an interesting fact about the species

## Credits

Developed by Daniyal Sultan Malik in 2025 via Cursor and the power of Generative AI.

## License

© 2025 Bird Species Classifier. All rights reserved. 