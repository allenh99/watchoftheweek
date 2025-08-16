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
  // Create a map to group providers by name
  const providerMap = new Map();

  // Helper function to add provider to map
  const addProvider = (provider: [string, number, string], type: string) => {
    const [name, id, logo] = provider;
    if (!providerMap.has(name)) {
      providerMap.set(name, {
        name,
        id,
        logo,
        types: [],
        logoPath: logo
      });
    }
    providerMap.get(name).types.push(type);
  };

  // Add all providers to the map
  (streamingData.flatrate || []).forEach(provider => addProvider(provider, 'stream'));
  (streamingData.free || []).forEach(provider => addProvider(provider, 'free'));
  (streamingData.ads || []).forEach(provider => addProvider(provider, 'ads'));
  (streamingData.rent || []).forEach(provider => addProvider(provider, 'rent'));
  (streamingData.buy || []).forEach(provider => addProvider(provider, 'buy'));

  const allProviders = Array.from(providerMap.values());
  
  if (allProviders.length === 0) {
    return (
      <div className="bg-gray-800 rounded-lg p-4">
        <h4 className="text-sm font-medium text-white mb-2" style={{ fontFamily: 'var(--font-roboto)' }}>
          Where to Watch
        </h4>
        <p className="text-sm text-gray-400">
          Streaming information not available
        </p>
      </div>
    );
  }

  // Helper function to get action buttons for a provider
  const getActionButtons = (types: string[]) => {
    const buttons = [];
    
    if (types.includes('stream')) {
      buttons.push(
        <button key="play" className="bg-gray-700 hover:bg-gray-600 text-white text-xs px-3 py-1 rounded transition-colors mr-2">
          PLAY
        </button>
      );
    }
    
    if (types.includes('free')) {
      buttons.push(
        <button key="play-free" className="bg-gray-700 hover:bg-gray-600 text-white text-xs px-3 py-1 rounded transition-colors mr-2">
          PLAY
        </button>
      );
    }
    
    if (types.includes('ads')) {
      buttons.push(
        <button key="play-ads" className="bg-gray-700 hover:bg-gray-600 text-white text-xs px-3 py-1 rounded transition-colors mr-2">
          PLAY
        </button>
      );
    }
    
    if (types.includes('rent')) {
      buttons.push(
        <button key="rent" className="bg-gray-700 hover:bg-gray-600 text-white text-xs px-3 py-1 rounded transition-colors mr-2">
          RENT
        </button>
      );
    }
    
    if (types.includes('buy')) {
      buttons.push(
        <button key="buy" className="bg-gray-700 hover:bg-gray-600 text-white text-xs px-3 py-1 rounded transition-colors">
          BUY
        </button>
      );
    }
    
    return buttons;
  };

  return (
    <div className="bg-gray-800 rounded-lg p-4">
      <h4 className="text-sm font-medium text-white mb-4" style={{ fontFamily: 'var(--font-roboto)' }}>
        Where to Watch
      </h4>
      
      <div className="space-y-3">
        {allProviders.map((provider, index) => (
          <div key={index} className="flex items-center justify-between py-3 border-b border-gray-700 last:border-b-0">
            <div className="flex items-center space-x-3 ">
                             {provider.logoPath && (
                 <img
                   src={`https://image.tmdb.org/t/p/w45${provider.logoPath}`}
                   alt={provider.name}
                   className="w-6 h-6 object-contain"
                   onError={(e) => { e.currentTarget.style.display = 'none'; }}
                 />
               )}
              <span className="text-sm font-medium text-white">
                {provider.name}
              </span>
            </div>
            <div className="flex">
              {getActionButtons(provider.types)}
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};

export default function WeeklyRecommendation() {
  // Add Inter font to the page
  useEffect(() => {
    const link = document.createElement('link');
    link.href = 'https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap';
    link.rel = 'stylesheet';
    document.head.appendChild(link);
  }, []);
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
      
      const url = forceNew 
        ? `http://localhost:8000/api/weekly-recommendation/${currentUser.id}?force_new=true`
        : `http://localhost:8000/api/weekly-recommendation/${currentUser.id}`;
      
      const response = await fetch(url, {
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
      fetchWeeklyRecommendation(false); // Explicitly pass false
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

  const getYearFromDate = (dateString?: string) => {
    if (!dateString) return '';
    return new Date(dateString).getFullYear().toString();
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-900 py-8">
        <div className="max-w-4xl mx-auto px-4">
          <div className="text-center">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-green-500 mx-auto"></div>
            <p className="mt-4 text-gray-400">Loading your weekly recommendation...</p>
          </div>
        </div>
      </div>
    );
  }

  if (error && error === 'Please login first') {
    return (
      <div className="min-h-screen bg-gray-900 py-8">
        <div className="max-w-4xl mx-auto px-4">
          <div className="bg-blue-900/20 border border-blue-800 rounded-lg p-6 text-center">
            <h2 className="text-xl font-semibold text-blue-200 mb-2">Authentication Required</h2>
            <p className="text-blue-300 mb-4">Please login to view your weekly recommendation</p>
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
      <div className="min-h-screen bg-gray-900 py-8">
        <div className="max-w-4xl mx-auto px-4">
          <div className="bg-red-900/20 border border-red-800 rounded-lg p-6">
            <h2 className="text-xl font-semibold text-red-200 mb-2">Error</h2>
            <p className="text-red-300">{error}</p>
            <button
              onClick={() => fetchWeeklyRecommendation(false)}
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
    <div className="min-h-screen bg-gray-900 -mt-4 pt-0">

      {recommendation ? (
        <div className="relative -mt-12">
          {/* Backdrop Image - Full width from top */}
          {recommendation.backdrop_path && (
            <div className="relative h-[70vh] w-full overflow-hidden">
              <div className="absolute inset-0 bg-gradient-to-b from-transparent via-transparent to-gray-900 z-10"></div>
              <img
                src={`https://image.tmdb.org/t/p/original${recommendation.backdrop_path}`}
                alt={recommendation.title}
                className="w-full h-full object-cover"
                onError={(e) => { e.currentTarget.style.display = 'none'; }}
              />
            </div>
          )}

          {/* Main Content */}
          <div className="max-w-7xl mx-auto px-4 -mt-16 relative z-20">
            {/* Movie Content - No distinct box */}
            <div className="relative">
              {recommendation.is_new && (
                <div className="bg-black text-white px-4 py-2 text-center font-semibold text-sm rounded-lg mb-6 inline-block">
                  Your watch of the week is...
                </div>
              )}
              
              <div className="space-y-8">
                <div className="flex flex-col lg:flex-row gap-8">
                  {/* Poster */}
                  <div className="flex-shrink-0">
                    {recommendation.poster_path ? (
                      <img
                        src={`https://image.tmdb.org/t/p/w500${recommendation.poster_path}`}
                        alt={recommendation.title}
                        className="w-80 h-[30rem] object-cover rounded-lg shadow-lg"
                        onError={(e) => { e.currentTarget.style.display = 'none'; }}
                      />
                    ) : (
                      <div className="w-80 h-[30rem] bg-gray-700 rounded-lg flex items-center justify-center">
                        <span className="text-gray-400">No poster available</span>
                      </div>
                    )}
                  </div>

                  {/* Movie Details */}
                  <div className="flex-1">
                    <h2 className="text-7xl font-bold text-white mb-4 tracking-tight leading-tight" style={{ fontFamily: 'var(--font-dm-serif-display)' }}>
                      {recommendation.title}
                    </h2>
                    
                    {/* Director and Year on same line */}
                    <div className="flex items-center gap-6 mb-6 text-gray-300">
                      {recommendation.release_date && (
                        <span className="text-lg font-light underline" style={{ fontFamily: 'var(--font-roboto)' }}>{getYearFromDate(recommendation.release_date)}</span>
                      )}
                      {recommendation.director && (
                        <span className="text-lg font-normal underline" style={{ fontFamily: 'var(--font-roboto)' }}>Directed by {recommendation.director}</span>
                      )}
                    </div>

                    {/* Tagline */}
                    {recommendation.tagline && (
                      <p className="text-lg font-medium text-gray-400 mb-8 tracking-wide uppercase" style={{ fontFamily: 'var(--font-roboto)' }}>
                        {recommendation.tagline}
                      </p>
                    )}
                    
                    {/* Overview */}
                    {recommendation.overview && (
                      <p className="text-gray-300 mb-8 leading-relaxed text-lg font-normal max-w-3xl" style={{ fontFamily: 'var(--font-source-serif)' }}>
                        {recommendation.overview}
                      </p>
                    )}

                    {/* Source Movie Info */}
                    {recommendation.source_movie && (
                      <div className="mb-8 p-4 bg-gray-800/80 backdrop-blur-sm rounded-lg">
                        <span className="text-sm font-medium text-gray-400">Based on your rating of</span>
                        <p className="text-lg font-semibold text-white">
                          {recommendation.source_movie}
                          {recommendation.user_rating && (
                            <span className="text-sm text-gray-400 ml-2 font-normal">
                              (you rated it {recommendation.user_rating}/5)
                            </span>
                          )}
                        </p>
                      </div>
                    )}

                    {/* Generated Date */}
                    {recommendation.generated_date && (
                      <div className="text-sm text-gray-500 mb-6 font-light">
                        Generated on {formatDate(recommendation.generated_date)}
                      </div>
                    )}
                  </div>

                  {/* Where to Watch - Right Side */}
                  {recommendation.streaming_data && (
                    <div className="flex-shrink-0 w-80">
                      <StreamingOptions streamingData={recommendation.streaming_data} />
                    </div>
                  )}
                </div>

                {/* Status Panel - Below Overview */}
                {status && (
                  <div className="p-6 border-t border-gray-700">
                    <div className="flex items-center justify-between">
                      <div>
                        {status.has_recommendation ? (
                          <div className="space-y-1">
                            <p className="text-base text-gray-400 font-normal">
                              {status.days_until_new > 0 
                                ? `${status.days_until_new} days until new recommendation`
                                : 'New recommendation available!'
                              }
                            </p>
                            {status.last_generated && (
                              <p className="text-sm text-gray-500 font-light">
                                Last generated: {formatDate(status.last_generated)}
                              </p>
                            )}
                          </div>
                        ) : (
                          <p className="text-base text-gray-400 font-normal">
                            No recommendation yet
                          </p>
                        )}
                      </div>
                      {status.can_generate_new && (
                        <button
                          onClick={handleGenerateNew}
                          className="bg-green-600 hover:bg-green-700 text-white px-4 py-2 rounded-lg transition-colors text-sm font-medium"
                        >
                          Generate New
                        </button>
                      )}
                    </div>
                  </div>
                )}
              </div>
            </div>
          </div>
        </div>
      ) : (
        <div className="max-w-4xl mx-auto px-4 py-8">
          <div className="bg-gray-800 rounded-lg shadow-md p-8 text-center">
            <h3 className="text-xl font-semibold text-white mb-4">
              No Recommendation Available
            </h3>
            <p className="text-gray-400 mb-6">
              Rate some movies to get your first weekly recommendation!
            </p>
            <button
              onClick={() => fetchWeeklyRecommendation(true)}
              className="bg-green-600 hover:bg-green-700 text-white px-6 py-3 rounded-lg transition-colors"
            >
              Try Generating
            </button>
          </div>
        </div>
      )}
    </div>
  );
} 