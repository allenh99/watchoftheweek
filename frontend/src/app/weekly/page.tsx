'use client';

import { useState, useEffect } from 'react';

interface StreamingOption {
  provider_name: string;
  provider_id: number;
  logo_path: string;
}

interface StreamingData {
  flatrate: [string, number, string][];
  free: [string, number, string][];
  ads: [string, number, string][];
  buy: [string, number, string][];
  rent: [string, number, string][];
}

interface WeeklyRecommendation {
  movie_id: number;
  title: string;
  vote_average?: number;
  vote_count?: number;
  genre_ids?: string;
  poster_path?: string;
  overview?: string;
  source_movie?: string;
  user_rating?: number;
  is_new?: boolean;
  generated_date?: string;
  streaming_data?: StreamingData;
  release_date?: string;
  backdrop_path?: string;
  tagline?: string;
  director?: string;
}

interface User {
  id: number;
  username: string;
  email: string;
}

interface WeeklyStatus {
  has_recommendation: boolean;
  days_until_new: number;
  can_generate_new: boolean;
  last_generated?: string;
}

// Streaming Options Component
const StreamingOptions = ({ streamingData }: { streamingData: StreamingData }) => {
  // Combine all streaming options into one array
  const allProviders = [
    ...(streamingData.free || []),
    ...(streamingData.flatrate || []),
    ...(streamingData.ads || []),
    ...(streamingData.rent || []),
    ...(streamingData.buy || [])
  ];
  
  // Remove duplicates based on provider name
  const uniqueProviders = allProviders.filter((provider, index, self) => 
    index === self.findIndex(p => p[0] === provider[0])
  );
  
  if (uniqueProviders.length === 0) {
    return (
      <div className="bg-gray-50 dark:bg-gray-700 rounded-lg p-4">
        <h4 className="text-sm font-medium text-gray-900 dark:text-white mb-2">
          Where to Watch
        </h4>
        <p className="text-sm text-gray-500 dark:text-gray-400">
          Streaming information not available
        </p>
      </div>
    );
  }

  return (
    <div className="bg-gray-50 dark:bg-gray-700 rounded-lg p-4">
      <h4 className="text-sm font-medium text-gray-900 dark:text-white mb-3">
        Where to Watch
      </h4>
      
      <div className="flex flex-wrap gap-2">
        {uniqueProviders.map((provider, index) => (
          <div key={index} className="flex items-center space-x-2 bg-white dark:bg-gray-600 rounded-lg px-3 py-2">
            {provider[2] && (
              <img
                src={`https://image.tmdb.org/t/p/w45${provider[2]}`}
                alt={provider[0]}
                className="w-6 h-6 object-contain"
                onError={(e) => { e.currentTarget.style.display = 'none'; }}
              />
            )}
            <span className="text-xs font-medium text-gray-700 dark:text-gray-300">
              {provider[0]}
            </span>
          </div>
        ))}
      </div>
    </div>
  );
};

export default function WeeklyRecommendation() {
  const [recommendation, setRecommendation] = useState<WeeklyRecommendation | null>(null);
  const [status, setStatus] = useState<WeeklyStatus | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [token, setToken] = useState<string | null>(null);
  const [currentUser, setCurrentUser] = useState<User | null>(null);

  const fetchCurrentUser = async (authToken: string) => {
    try {
      const response = await fetch('http://localhost:8000/api/auth/me', {
        headers: {
          'Authorization': `Bearer ${authToken}`,
        },
      });

      if (response.ok) {
        const user = await response.json();
        setCurrentUser(user);
      } else {
        // Token is invalid, clear it
        handleLogout();
      }
    } catch (error) {
      console.error('Error fetching user:', error);
      handleLogout();
    }
  };

  const handleLogout = () => {
    setToken(null);
    setCurrentUser(null);
    localStorage.removeItem('authToken');
    // Redirect to home page
    window.location.href = '/';
  };

  const fetchWeeklyRecommendation = async (forceNew: boolean = false) => {
    if (!currentUser) {
      setError('Please login first');
      return;
    }

    try {
      setLoading(true);
      setError(null);
      
      const response = await fetch(`http://localhost:8000/api/weekly-recommendation/${currentUser.id}?force_new=${forceNew}`, {
        credentials: 'include'
      });
      console.log(response);
      if (!response.ok) {
        throw new Error('Failed to fetch weekly recommendation');
      }
      
      const data = await response.json();
      // Combine recommendation with streaming data
      const recommendationWithStreaming = {
        ...data.recommendation,
        streaming_data: data.streaming_data
      };
      setRecommendation(recommendationWithStreaming);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'An error occurred');
    } finally {
      setLoading(false);
    }
  };

  const fetchStatus = async () => {
    if (!currentUser) {
      return;
    }

    try {
      const response = await fetch(`http://localhost:8000/api/weekly-recommendation-status/${currentUser.id}`, {
        credentials: 'include'
      });
      
      if (response.ok) {
        const data = await response.json();
        setStatus(data.status);
        console.log(data)
      }
    } catch (err) {
      console.error('Failed to fetch status:', err);
    }
  };

  useEffect(() => {
    const savedToken = localStorage.getItem('authToken');
    if (savedToken) {
      setToken(savedToken);
      fetchCurrentUser(savedToken);
    } else {
      setLoading(false);
      setError('Please login first');
    }
  }, []);

  useEffect(() => {
    if (currentUser) {
      fetchWeeklyRecommendation();
      fetchStatus();
    }
  }, [currentUser]);

  const handleGenerateNew = () => {
    fetchWeeklyRecommendation(true);
    fetchStatus();
  };

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString('en-US', {
      weekday: 'long',
      year: 'numeric',
      month: 'long',
      day: 'numeric'
    });
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 dark:bg-gray-900 py-8">
        <div className="max-w-4xl mx-auto px-4">
          <div className="text-center">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-green-500 mx-auto"></div>
            <p className="mt-4 text-gray-600 dark:text-gray-400">Loading your weekly recommendation...</p>
          </div>
        </div>
      </div>
    );
  }

  if (error && error === 'Please login first') {
    return (
      <div className="min-h-screen bg-gray-50 dark:bg-gray-900 py-8">
        <div className="max-w-4xl mx-auto px-4">
          <div className="bg-blue-50 dark:bg-blue-900/20 border border-blue-200 dark:border-blue-800 rounded-lg p-6 text-center">
            <h2 className="text-xl font-semibold text-blue-800 dark:text-blue-200 mb-2">Authentication Required</h2>
            <p className="text-blue-600 dark:text-blue-300 mb-4">Please login to view your weekly recommendation</p>
            <button
              onClick={() => window.location.href = '/'}
              className="bg-blue-600 hover:bg-blue-700 text-white px-6 py-2 rounded transition-colors"
            >
              Go to Login
            </button>
          </div>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="min-h-screen bg-gray-50 dark:bg-gray-900 py-8">
        <div className="max-w-4xl mx-auto px-4">
          <div className="bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-lg p-6">
            <h2 className="text-xl font-semibold text-red-800 dark:text-red-200 mb-2">Error</h2>
            <p className="text-red-600 dark:text-red-300">{error}</p>
            <button
              onClick={() => fetchWeeklyRecommendation()}
              className="mt-4 bg-red-600 hover:bg-red-700 text-white px-4 py-2 rounded transition-colors"
            >
              Try Again
            </button>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50 dark:bg-gray-900 py-8">
      <div className="max-w-4xl mx-auto px-4">
        <div className="text-center mb-8">
          <h1 className="text-4xl font-bold text-gray-900 dark:text-white mb-2">
            Movie of the Week
          </h1>
          <p className="text-lg text-gray-600 dark:text-gray-400">
            Your personalized weekly recommendation
          </p>
        </div>

        {status && (
          <div className="bg-white dark:bg-gray-800 rounded-lg shadow-md p-6 mb-8">
            <div className="flex items-center justify-between">
              <div>
                <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-2">
                  Weekly Status
                </h3>
                {status.has_recommendation ? (
                  <div className="space-y-1">
                    <p className="text-sm text-gray-600 dark:text-gray-400">
                      {status.days_until_new > 0 
                        ? `${status.days_until_new} days until new recommendation`
                        : 'New recommendation available!'
                      }
                    </p>
                    {status.last_generated && (
                      <p className="text-xs text-gray-500 dark:text-gray-500">
                        Last generated: {formatDate(status.last_generated)}
                      </p>
                    )}
                  </div>
                ) : (
                  <p className="text-sm text-gray-600 dark:text-gray-400">
                    No recommendation yet
                  </p>
                )}
              </div>
              <div>
                {status.can_generate_new && (
                  <button
                    onClick={handleGenerateNew}
                    className="bg-green-600 hover:bg-green-700 text-white px-4 py-2 rounded-lg transition-colors"
                  >
                    Generate New
                  </button>
                )}
              </div>
            </div>
          </div>
        )}

        {recommendation ? (
          <div className="bg-white dark:bg-gray-800 rounded-lg shadow-lg overflow-hidden">
            {recommendation.is_new && (
              <div className="bg-green-500 text-white px-4 py-2 text-center font-semibold">
                your watch of the week is...
              </div>
            )}
            
            <div className="p-8">
              <div className="flex flex-col lg:flex-row gap-8">
                <div className="flex-shrink-0">
                  {recommendation.poster_path ? (
                    <img
                      src={`https://image.tmdb.org/t/p/w500${recommendation.poster_path}`}
                      alt={recommendation.title}
                      className="w-64 h-96 object-cover rounded-lg shadow-md"
                      onError={(e) => { e.currentTarget.style.display = 'none'; }}
                    />
                  ) : (
                    <div className="w-64 h-96 bg-gray-200 dark:bg-gray-700 rounded-lg flex items-center justify-center">
                      <span className="text-gray-500 dark:text-gray-400">No poster available</span>
                    </div>
                  )}
                  {recommendation.backdrop_path && (
                    <div className="text-sm text-gray-500 dark:text-gray-400 mb-6">
                      <img
                      src={`https://image.tmdb.org/t/p/w500${recommendation.backdrop_path}`}
                      alt={recommendation.title}
                      className="w-64 h-96 object-cover rounded-lg shadow-md"
                      onError={(e) => { e.currentTarget.style.display = 'none'; }}
                      />
                    </div>
                  )}
                </div>

                {/* Details */}
                <div className="flex-1">
                  <h2 className="text-3xl font-bold text-gray-900 dark:text-white mb-4">
                    {recommendation.title}
                  </h2>
                  
                  {recommendation.overview && (
                    <p className="text-gray-600 dark:text-gray-300 mb-6 leading-relaxed">
                      {recommendation.overview}
                    </p>
                  )}

                  <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-6">
                    
                    {recommendation.source_movie && (
                      <div>
                        <span className="text-sm font-medium text-gray-500 dark:text-gray-400">Based on</span>
                        <p className="text-lg font-semibold text-gray-900 dark:text-white">
                          {recommendation.source_movie}
                          {recommendation.user_rating && (
                            <span className="text-sm text-gray-500 dark:text-gray-400 ml-2">
                              (you rated it {recommendation.user_rating}/5)
                            </span>
                          )}
                        </p>
                      </div>
                    )}
                  </div>

                  {recommendation.generated_date && (
                    <div className="text-sm text-gray-500 dark:text-gray-400 mb-6">
                      Generated on {formatDate(recommendation.generated_date)}
                    </div>
                  )}

                  {/* Streaming Options */}
                  {recommendation.streaming_data && (
                    <div className="mt-6">
                      <StreamingOptions streamingData={recommendation.streaming_data} />
                    </div>
                  )}
                </div>
              </div>
            </div>
          </div>
        ) : (
          <div className="bg-white dark:bg-gray-800 rounded-lg shadow-md p-8 text-center">
            <h3 className="text-xl font-semibold text-gray-900 dark:text-white mb-4">
              No Recommendation Available
            </h3>
            <p className="text-gray-600 dark:text-gray-400 mb-6">
              Rate some movies to get your first weekly recommendation!
            </p>
            <button
              onClick={() => fetchWeeklyRecommendation(true)}
              className="bg-green-600 hover:bg-green-700 text-white px-6 py-3 rounded-lg transition-colors"
            >
              Try Generating
            </button>
          </div>
        )}
      </div>
    </div>
  );
} 