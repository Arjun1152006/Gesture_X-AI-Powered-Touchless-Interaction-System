import numpy as np
import pickle
import os
from sklearn.ensemble import RandomForestClassifier
from sklearn.svm import SVC
from sklearn.neural_network import MLPClassifier
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, confusion_matrix
import joblib

class GestureClassifier:
    def __init__(self, model_type='random_forest'):
        self.model_type = model_type
        self.model = None
        self.scaler = StandardScaler()
        self.label_map = {}
        self.reverse_label_map = {}
        self.training_history = []
        
    def create_model(self):
        """Create ML model based on type"""
        if self.model_type == 'random_forest':
            self.model = RandomForestClassifier(
                n_estimators=100,
                max_depth=20,
                random_state=42,
                n_jobs=-1
            )
        elif self.model_type == 'svm':
            self.model = SVC(
                kernel='rbf',
                C=10,
                gamma='scale',
                probability=True
            )
        elif self.model_type == 'neural_network':
            self.model = MLPClassifier(
                hidden_layer_sizes=(128, 64, 32),
                activation='relu',
                max_iter=1000,
                random_state=42
            )
        return self.model
    
    def train(self, X, y, labels, test_size=0.2):
        """Train the gesture classifier"""
        print("\n🧠 Training Gesture Classifier...")
        print("=" * 50)
        
        # Create label mapping
        unique_labels = np.unique(y)
        self.label_map = {i: labels[i] for i in range(len(labels))}
        self.reverse_label_map = {labels[i]: i for i in range(len(labels))}
        
        # Split data
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=test_size, random_state=42, stratify=y
        )
        
        # Normalize features
        X_train_scaled = self.scaler.fit_transform(X_train)
        X_test_scaled = self.scaler.transform(X_test)
        
        # Create and train model
        if self.model is None:
            self.create_model()
        
        self.model.fit(X_train_scaled, y_train)
        
        # Evaluate
        y_pred = self.model.predict(X_test_scaled)
        accuracy = accuracy_score(y_test, y_pred)
        
        print(f"✅ Model Type: {self.model_type}")
        print(f"✅ Training samples: {len(X_train)}")
        print(f"✅ Test samples: {len(X_test)}")
        print(f"✅ Features: {X.shape[1]}")
        print(f"✅ Gestures: {len(labels)}")
        print(f"🎯 Accuracy: {accuracy*100:.2f}%")
        
        # Confusion matrix
        cm = confusion_matrix(y_test, y_pred)
        print("\n📊 Confusion Matrix:")
        print(cm)
        
        # Store history
        self.training_history.append({
            'accuracy': accuracy,
            'samples': len(X),
            'features': X.shape[1],
            'gestures': labels
        })
        
        return accuracy
    
    def predict(self, features):
        """Predict gesture from features"""
        if self.model is None or self.scaler is None:
            return None, 0
        
        features_scaled = self.scaler.transform([features])
        
        # Get prediction and probability
        pred_idx = self.model.predict(features_scaled)[0]
        probabilities = self.model.predict_proba(features_scaled)[0]
        confidence = np.max(probabilities)
        
        gesture_name = self.label_map.get(pred_idx, "unknown")
        
        return gesture_name, confidence
    
    def save_model(self, filepath="gesture_models/gesture_model.pkl"):
        """Save trained model to file"""
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        
        model_data = {
            'model': self.model,
            'scaler': self.scaler,
            'label_map': self.label_map,
            'reverse_label_map': self.reverse_label_map,
            'model_type': self.model_type,
            'training_history': self.training_history
        }
        
        with open(filepath, 'wb') as f:
            pickle.dump(model_data, f)
        
        print(f"✅ Model saved to: {filepath}")
    
    def load_model(self, filepath="gesture_models/gesture_model.pkl"):
        """Load trained model from file"""
        if not os.path.exists(filepath):
            print(f"❌ Model file not found: {filepath}")
            return False
        
        with open(filepath, 'rb') as f:
            model_data = pickle.load(f)
        
        self.model = model_data['model']
        self.scaler = model_data['scaler']
        self.label_map = model_data['label_map']
        self.reverse_label_map = model_data['reverse_label_map']
        self.model_type = model_data['model_type']
        self.training_history = model_data.get('training_history', [])
        
        print(f"✅ Model loaded from: {filepath}")
        print(f"📊 Gestures: {list(self.label_map.values())}")
        return True