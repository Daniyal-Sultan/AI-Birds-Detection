import tensorflow as tf
from keras import layers, models
from keras.applications import MobileNetV2
from keras.preprocessing.image import ImageDataGenerator
import os
import json
from scipy import ndimage

# Define parameters
IMG_SIZE = 224  # MobileNetV2 default input size
BATCH_SIZE = 32
EPOCHS = 10

# Get bird species from the dataset directory
def get_bird_species():
    train_dir = 'dataset/train'
    return sorted([d for d in os.listdir(train_dir) 
                  if os.path.isdir(os.path.join(train_dir, d))])

# Get the bird species list
BIRD_SPECIES = get_bird_species()

def create_model(num_classes):
    # Load pre-trained MobileNetV2 without top layers
    base_model = MobileNetV2(
        weights='imagenet',
        include_top=False,
        input_shape=(IMG_SIZE, IMG_SIZE, 3)
    )
    
    # Freeze the base model layers
    base_model.trainable = False
    
    # Create new model on top
    model = models.Sequential([
        base_model,
        layers.GlobalAveragePooling2D(),
        layers.Dense(128, activation='relu'),
        layers.Dropout(0.2),
        layers.Dense(num_classes, activation='softmax')
    ])
    
    return model

def prepare_data():
    # Data augmentation for training
    train_datagen = ImageDataGenerator(
        rescale=1./255,
        rotation_range=20,
        width_shift_range=0.2,
        height_shift_range=0.2,
        horizontal_flip=True,
        fill_mode='nearest',
        validation_split=0.2
    )
    
    # Only rescaling for validation
    val_datagen = ImageDataGenerator(
        rescale=1./255
    )
    
    # Load training data
    train_generator = train_datagen.flow_from_directory(
        'dataset/train',
        target_size=(IMG_SIZE, IMG_SIZE),
        batch_size=BATCH_SIZE,
        class_mode='categorical',
        shuffle=True
    )
    
    # Load validation data
    validation_generator = val_datagen.flow_from_directory(
        'dataset/valid',
        target_size=(IMG_SIZE, IMG_SIZE),
        batch_size=BATCH_SIZE,
        class_mode='categorical',
        shuffle=False
    )
    
    # Load test data
    test_generator = val_datagen.flow_from_directory(
        'dataset/test',
        target_size=(IMG_SIZE, IMG_SIZE),
        batch_size=BATCH_SIZE,
        class_mode='categorical',
        shuffle=False
    )
    
    return train_generator, validation_generator, test_generator

def train_model():
    print("Number of bird species:", len(BIRD_SPECIES))
    print("\nTraining model for the following species:")
    for i, species in enumerate(BIRD_SPECIES, 1):
        print(f"{i}. {species}")
    
    # Create and compile model
    model = create_model(len(BIRD_SPECIES))
    model.compile(
        optimizer='adam',
        loss='categorical_crossentropy',
        metrics=['accuracy']
    )
    
    # Prepare data generators
    train_generator, validation_generator, test_generator = prepare_data()
    
    # Create callbacks
    checkpoint_cb = tf.keras.callbacks.ModelCheckpoint(
        'bird_model_checkpoint.h5',
        save_best_only=True
    )
    early_stopping_cb = tf.keras.callbacks.EarlyStopping(
        monitor='val_accuracy',
        patience=3,
        restore_best_weights=True
    )
    
    # Train the model
    history = model.fit(
        train_generator,
        epochs=EPOCHS,
        validation_data=validation_generator,
        callbacks=[checkpoint_cb, early_stopping_cb]
    )
    
    # Evaluate on test set
    test_loss, test_accuracy = model.evaluate(test_generator)
    print(f"\nTest accuracy: {test_accuracy:.2%}")
    
    # Save the final model
    model.save('bird_model.h5')
    
    # Save class names
    with open('bird_classes.json', 'w') as f:
        json.dump(BIRD_SPECIES, f)
    
    print("\nModel and class names saved successfully!")

if __name__ == '__main__':
    train_model() 