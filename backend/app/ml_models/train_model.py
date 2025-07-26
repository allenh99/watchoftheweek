import sys
import os
# Add the backend directory to the path so we can import from app
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from app.ml_models.ml_models import train_and_save_model, get_movie_recommendations

def main():
    """Train and save the recommendation model"""
    print("Training recommendation model...")
    
    try:
        # Train and save the model using films.csv instead of top_rated_movies.csv
        model_data = train_and_save_model(csv_file='app/data/films.csv')
        
        if model_data is None:
            print("❌ Model training failed!")
            return
        
        print("Model training completed successfully!")
        print(f"Model saved with {len(model_data['movie_data'])} movies")
        print(f"Features used: {len(model_data['feature_columns'])}")
        print(f"Genres included: {len(model_data['all_genres'])}")
        print(f"Languages included: {len(model_data.get('all_languages', []))}")
        print(f"Cast members included: {len(model_data.get('all_cast', []))}")
        print(f"Directors included: {len(model_data.get('all_directors', []))}")
        
        print("\nTesting model with poster_path...")
        test_recommendations = get_movie_recommendations("The Shawshank Redemption", top_n=3)
        
        if test_recommendations is not None and not test_recommendations.empty:
            print("Model test successful")
            print("Sample recommendations:")
            for idx, row in test_recommendations.head(3).iterrows():
                print(f"  - {row['title']} (Poster: {row.get('poster_path', 'N/A')})")
            
            if 'poster_path' in test_recommendations.columns:
                print("poster_path is included in recommendations!")
            else:
                print("poster_path is NOT included in recommendations")
        else:
            print("Model test failed - no recommendations generated")
        
    except Exception as e:
        print(f"Error training model: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main() 