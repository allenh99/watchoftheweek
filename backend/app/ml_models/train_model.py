import sys
import os
# Add the backend directory to the path so we can import from app
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from app.ml_models.ml_models import train_and_save_model

def main():
    """Train and save the recommendation model"""
    print("Training recommendation model...")
    
    try:
        # Train and save the model
        model_data = train_and_save_model()
        
        print("Model training completed successfully!")
        print(f"Model saved with {len(model_data['movie_data'])} movies")
        print(f"Features used: {len(model_data['feature_columns'])}")
        print(f"Genres included: {len(model_data['all_genres'])}")
        
    except Exception as e:
        print(f"Error training model: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main() 