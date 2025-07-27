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
  cluster_id?: number;
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
            <div className="space-y-6">
              {/* Source Movies Summary */}
              <div className="bg-white dark:bg-gray-800 rounded-lg p-4 shadow-sm border border-gray-200 dark:border-gray-700">
                <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-3">
                  Based on your ratings of:
                </h3>
                <div className="flex flex-wrap gap-2">
                  {Array.from(new Set(recommendations.map(r => 
                    Array.isArray(r.source_movies) ? r.source_movies : [r.source_movies]
                  ).flat())).map((sourceMovie, index) => (
                    <span
                      key={index}
                      className="bg-green-100 dark:bg-green-900 text-green-800 dark:text-green-200 px-3 py-1 rounded-full text-sm font-medium"
                    >
                      {sourceMovie}
                    </span>
                  ))}
                </div>
              </div>

              {/* Movie Recommendations */}
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
                      {movie.cluster_id && (
                        <span className="ml-2 bg-purple-100 dark:bg-purple-900 text-purple-800 dark:text-purple-200 px-1.5 py-0.5 rounded text-xs font-medium">
                          C{movie.cluster_id}
                        </span>
                      )}
                    </h3>
                      <div className="space-y-1 text-xs text-gray-600 dark:text-gray-400">
                        <p>Rating: ⭐ {movie.vote_average.toFixed(1)}</p>
                        <p>Votes: {movie.vote_count.toLocaleString()}</p>
                        <p>Score: {movie.weighted_score.toFixed(2)}</p>
                        {movie.genre_ids && (
                          <p>Genres: {movie.genre_ids }</p>
                        )}
                        {/* Source Movies for this recommendation */}
                        <div className="mt-2 pt-2 border-t border-gray-200 dark:border-gray-600">
                          <p className="text-xs text-gray-500 dark:text-gray-400 mb-1">
                            Based on:
                          </p>
                          <div className="flex flex-wrap gap-1">
                            {Array.isArray(movie.source_movies) ? 
                              (movie.source_movies as string[]).map((source: string, idx: number) => (
                                <span
                                  key={idx}
                                  className="bg-blue-100 dark:bg-blue-900 text-blue-800 dark:text-blue-200 px-1 py-0.5 rounded text-xs"
                                >
                                  {source}
                                </span>
                              ))
                              : 
                              <span className="bg-blue-100 dark:bg-blue-900 text-blue-800 dark:text-blue-200 px-1 py-0.5 rounded text-xs">
                                {movie.source_movies}
                              </span>
                            }
                          </div>
                        </div>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
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