'use client';

import { useState, useEffect } from 'react';

interface Recommendation {
  movie_id: number;
  title: string;
  vote_average: number;
  vote_count: number;
  genre_ids: string;
  weighted_score: number;
  source_movies: string;
  user_rating: number;
  poster_path?: string;
}

export default function FilmsPage() {
  const [recommendations, setRecommendations] = useState<Recommendation[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [token, setToken] = useState<string | null>(null);

  useEffect(() => {
    const savedToken = localStorage.getItem('authToken');
    setToken(savedToken);
  }, []);

  const handleGetRecommendations = async () => {
    if (!token) {
      setError('Please login first');
      return;
    }

    setIsLoading(true);
    setError(null);

    try {
      const response = await fetch('http://localhost:8000/api/recommendations?top_n=12', {
        headers: {
          'Authorization': `Bearer ${token}`,
        },
      });
      const result = await response.json();
      console.log(result);
      if (response.ok) {
        setRecommendations(result.recommendations || []);
      } else {
        if (response.status === 401) {
          setError('Session expired. Please login again.');
        } else {
          setError(`Failed to get recommendations: ${result.detail || 'Please try again.'}`);
        }
        setRecommendations([]);
      }
    } catch (error) {
      console.error('Recommendations error:', error);
      setError('Failed to get recommendations. Please check if the backend server is running.');
      setRecommendations([]);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-gray-50 dark:bg-gray-900">
      <div className="container mx-auto px-4 py-8">
        <div className="max-w-6xl mx-auto">
          {/* Header */}
          <div className="text-center mb-8">
            <h1 className="text-3xl font-bold text-gray-900 dark:text-white mb-2">
              Discover Films
            </h1>
            <p className="text-gray-600 dark:text-gray-400">
              Get personalized movie recommendations based on your ratings
            </p>
          </div>

          {/* Get Recommendations Button */}
          <div className="text-center mb-8">
            <button
              onClick={handleGetRecommendations}
              disabled={isLoading || !token}
              className="bg-green-500 hover:bg-green-600 disabled:bg-gray-400 text-white font-bold px-6 py-3 rounded-lg transition-colors"
            >
              {isLoading ? 'Loading...' : 'Get Recommendations'}
            </button>
            {!token && (
              <p className="text-red-500 mt-2">Please login to get recommendations</p>
            )}
          </div>

          {/* Error Display */}
          {error && (
            <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded mb-6">
              {error}
            </div>
          )}

          {/* Recommendations Grid */}
          {recommendations.length > 0 && (
            <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-6 gap-2">
              {recommendations.map((movie, index) => (
                <div
                  key={movie.movie_id}
                  className="bg-white dark:bg-gray-800 rounded-lg shadow-md overflow-hidden hover:shadow-lg transition-shadow flex flex-col items-center p-2"
                >
                  {movie.poster_path && (
                    <div className="w-24 aspect-[2/3] overflow-hidden mb-2">
                      <img
                        src={`https://image.tmdb.org/t/p/w500${movie.poster_path}`}
                        alt={movie.title}
                        className="w-full h-full object-cover"
                        onError={(e) => {
                          e.currentTarget.style.display = 'none';
                        }}
                      />
                    </div>
                  )}
                  <div className="w-full">
                    <h3 className="text-sm font-semibold text-gray-900 dark:text-white mb-1 truncate">
                      {movie.title}
                    </h3>
                    <div className="space-y-1 text-xs text-gray-600 dark:text-gray-400">
                      <p>Rating: ⭐ {movie.vote_average.toFixed(1)}</p>
                      <p>Votes: {movie.vote_count.toLocaleString()}</p>
                      <p>Score: {movie.weighted_score.toFixed(2)}</p>
                      {movie.genre_ids && (
                        <p>Genres: {movie.genre_ids }</p>
                      )}
                    </div>
                  </div>
                </div>
              ))}
            </div>
          )}

          {/* Empty State */}
          {!isLoading && !error && recommendations.length === 0 && token && (
            <div className="text-center py-12">
              <p className="text-gray-500 dark:text-gray-400">
                Click "Get Recommendations" to see your personalized movie suggestions
              </p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
} 