import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from app.services.recommender import recommend_clustered
from app.database import SessionLocal
from app.models.models import User, Rating, Movie
from sqlalchemy import desc

def test_cluster_diversity():
    """Test the diversity of clusters and recommendations"""
    print("Testing cluster diversity and one-recommendation-per-cluster...")
    
    db = SessionLocal()
    
    try:
        
        user = db.query(User).first()
        
        if not user:
            print("No users found in database. Please create a user first.")
            return
        
        print(f"Testing with user: {user.username} (ID: {user.id})")
        
        user_ratings = db.query(Rating, Movie).join(Movie).filter(
            Rating.user_id == user.id
        ).order_by(desc(Rating.rating)).all()
        
        print(f"\n📊 USER RATINGS ANALYSIS:")
        print(f"{'='*60}")
        print(f"Total rated movies: {len(user_ratings)}")
        
        if user_ratings:
            print(f"\nTop 15 rated movies:")
            for i, (rating, movie) in enumerate(user_ratings[:15]):
                print(f"  {i+1:2d}. {movie.title} - Rating: {rating.rating}")
        
        print(f"\n🎯 CLUSTER-BASED RECOMMENDATIONS:")
        print(f"{'='*60}")
        recommendations = recommend_clustered(user.id, db, top_n=6, n_clusters=6)
        
        if recommendations is not None and not recommendations.empty:
            print(f"\n✅ SUCCESS: Generated {len(recommendations)} recommendations")
            print(f"\n📋 RECOMMENDATIONS BY CLUSTER:")
            print(f"{'='*60}")
            
            cluster_recommendations = {}
            for idx, row in recommendations.iterrows():
                cluster_id = row.get('cluster_id', idx + 1)
                if cluster_id not in cluster_recommendations:
                    cluster_recommendations[cluster_id] = []
                cluster_recommendations[cluster_id].append(row)
            
            for cluster_id in sorted(cluster_recommendations.keys()):
                rec = cluster_recommendations[cluster_id][0]
                source_movie = rec['source_movie']
                
                print(f"\n🎬 CLUSTER {cluster_id}:")
                print(f"   📽️  Source: {source_movie}")
                print(f"   🎯 Recommendation: {rec['title']}")
                print(f"   ⭐ Rating: {rec['vote_average']:.1f} ({rec['vote_count']:,} votes)")
                print(f"   📈 Score: {rec['weighted_score']:.2f}")
                print(f"   🎭 Genres: {rec['genre_ids']}")
                
                if rec.get('poster_path'):
                    print(f"   🖼️  Poster: {rec['poster_path']}")
            
            print(f"\n🔍 DIVERSITY ANALYSIS:")
            print(f"{'='*60}")
            
            unique_sources = set()
            for idx, row in recommendations.iterrows():
                unique_sources.add(row['source_movie'])
            
            print(f"Unique source movies: {len(unique_sources)}")
            print(f"Total recommendations: {len(recommendations)}")
            print(f"Diversity ratio: {len(unique_sources)}/{len(recommendations)} = {len(unique_sources)/len(recommendations)*100:.1f}%")
            
            if len(unique_sources) == len(recommendations):
                print("✅ PERFECT DIVERSITY: Each recommendation comes from a different source!")
            else:
                print("⚠️  Some recommendations share the same source movie")
            
            print(f"\n📽️  ALL SOURCE MOVIES:")
            for i, source in enumerate(sorted(unique_sources), 1):
                print(f"  {i:2d}. {source}")
                
        else:
            print("❌ No recommendations generated")
            
    except Exception as e:
        print(f"❌ Error testing cluster diversity: {e}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()

if __name__ == "__main__":
    test_cluster_diversity() 