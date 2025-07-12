'use client';

import { useState, useEffect } from 'react';
import CSVUpload from '../components/CSVUpload';
import AuthForm from '../components/AuthForm';

interface Recommendation {
  movie_id: number;
  title: string;
  vote_average: number;
  vote_count: number;
  genre_ids: string;
  weighted_score: number;
  source_movies: string;
  user_rating: number;
}

interface User {
  id: number;
  username: string;
  email: string;
}

export default function Home() {
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [token, setToken] = useState<string | null>(null);
  const [currentUser, setCurrentUser] = useState<User | null>(null);
  const [isUploading, setIsUploading] = useState(false);
  const [isLoadingRecommendations, setIsLoadingRecommendations] = useState(false);
  const [uploadedFile, setUploadedFile] = useState<File | null>(null);
  const [uploadStatus, setUploadStatus] = useState<string | null>(null);
  const [uploadResult, setUploadResult] = useState<any>(null);
  const [recommendations, setRecommendations] = useState<Recommendation[]>([]);
  const [recommendationsError, setRecommendationsError] = useState<string | null>(null);

  // Check for existing token on component mount
  useEffect(() => {
    const savedToken = localStorage.getItem('authToken');
    if (savedToken) {
      setToken(savedToken);
      setIsAuthenticated(true);
      fetchCurrentUser(savedToken);
    }
  }, []);

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

  const handleLogin = (authToken: string) => {
    setToken(authToken);
    setIsAuthenticated(true);
    localStorage.setItem('authToken', authToken);
    fetchCurrentUser(authToken);
  };

  const handleRegister = (authToken: string) => {
    setToken(authToken);
    setIsAuthenticated(true);
    localStorage.setItem('authToken', authToken);
    fetchCurrentUser(authToken);
  };

  const handleLogout = () => {
    setToken(null);
    setIsAuthenticated(false);
    setCurrentUser(null);
    localStorage.removeItem('authToken');
    setRecommendations([]);
    setRecommendationsError(null);
    setUploadedFile(null);
    setUploadStatus(null);
    setUploadResult(null);
  };

  const handleFileUpload = async (file: File) => {
    if (!token) {
      setUploadStatus('Please login first');
      return;
    }

    setIsUploading(true);
    setUploadStatus('Uploading file...');
    setUploadedFile(file);

    try {
      // Create FormData to send the file
      const formData = new FormData();
      formData.append('file', file);

      // Call the backend API endpoint with authentication
      const response = await fetch('http://localhost:8000/api/ratings/upload', {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`,
        },
        body: formData,
      });

      const result = await response.json();

      if (response.ok) {
        setUploadStatus(`File uploaded successfully! ${result.message || ''}`);
        setUploadResult(result);
        // Clear previous recommendations when new data is uploaded
        setRecommendations([]);
        setRecommendationsError(null);
      } else {
        if (response.status === 401) {
          handleLogout();
          setUploadStatus('Session expired. Please login again.');
        } else {
          setUploadStatus(`Upload failed: ${result.detail || result.error || 'Please try again.'}`);
        }
        setUploadResult(null);
      }
    } catch (error) {
      console.error('Upload error:', error);
      setUploadStatus('Upload failed. Please check if the backend server is running.');
      setUploadResult(null);
    } finally {
      setIsUploading(false);
    }
  };

  const handleGetRecommendations = async () => {
    if (!token) {
      setRecommendationsError('Please login first');
      return;
    }

    setIsLoadingRecommendations(true);
    setRecommendationsError(null);

    try {
      const response = await fetch('http://localhost:8000/api/recommendations?top_n=10', {
        headers: {
          'Authorization': `Bearer ${token}`,
        },
      });
      const result = await response.json();

      if (response.ok) {
        setRecommendations(result.recommendations || []);
        if (result.message) {
          setRecommendationsError(result.message);
        }
      } else {
        if (response.status === 401) {
          handleLogout();
          setRecommendationsError('Session expired. Please login again.');
        } else {
          setRecommendationsError(`Failed to get recommendations: ${result.detail || 'Please try again.'}`);
        }
        setRecommendations([]);
      }
    } catch (error) {
      console.error('Recommendations error:', error);
      setRecommendationsError('Failed to get recommendations. Please check if the backend server is running.');
      setRecommendations([]);
    } finally {
      setIsLoadingRecommendations(false);
    }
  };

  if (!isAuthenticated) {
    return (
      <div className="min-h-screen bg-gray-50 dark:bg-gray-900">
        <div className="container mx-auto px-4 py-8">
          <div className="max-w-2xl mx-auto">
            {/* Header */}
            <div className="text-center mb-8">
              <h1 className="text-3xl font-bold text-gray-900 dark:text-white mb-2">
                Movie Recommendation Engine
              </h1>
              <p className="text-gray-600 dark:text-gray-400">
                Sign in to upload your movie ratings and get personalized recommendations
              </p>
            </div>

            {/* Auth Form */}
            <AuthForm onLogin={handleLogin} onRegister={handleRegister} />
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50 dark:bg-gray-900">
      <div className="container mx-auto px-4 py-8">
        <div className="max-w-4xl mx-auto">
          {/* Header with User Info */}
          <div className="flex justify-between items-center mb-8">
            <div>
              <h1 className="text-3xl font-bold text-gray-900 dark:text-white mb-2">
                Movie Recommendation Engine
              </h1>
              <p className="text-gray-600 dark:text-gray-400">
                Welcome back, {currentUser?.username}! Upload your movie ratings to get started
              </p>
            </div>
            <div className="flex items-center space-x-4">
              <span className="text-sm text-gray-600 dark:text-gray-400">
                {currentUser?.email}
              </span>
              <button
                onClick={handleLogout}
                className="px-4 py-2 text-sm font-medium text-gray-700 dark:text-gray-300 hover:text-gray-900 dark:hover:text-white transition-colors"
              >
                Logout
              </button>
            </div>
          </div>

          {/* Upload Component */}
          <div className="mb-8">
            <CSVUpload 
              onFileUpload={handleFileUpload}
              isLoading={isUploading}
            />
          </div>

          {/* CSV Format Instructions */}
          <div className="bg-blue-50 dark:bg-blue-900/20 border border-blue-200 dark:border-blue-800 rounded-lg p-4 mb-6">
            <h3 className="text-sm font-medium text-blue-900 dark:text-blue-100 mb-2">
              CSV Format Requirements
            </h3>
            <div className="text-xs text-blue-700 dark:text-blue-300 space-y-1">
              <p>• Your CSV file should have columns: <strong>Name</strong> and <strong>Rating</strong></p>
              <p>• <strong>Name</strong>: Movie title (e.g., "The Shawshank Redemption")</p>
              <p>• <strong>Rating</strong>: Rating value (1-10 scale)</p>
              <p>• Example: <code className="bg-blue-100 dark:bg-blue-800 px-1 rounded">Name,Rating</code></p>
            </div>
          </div>

          {/* Status Messages */}
          {uploadStatus && (
            <div className={`p-4 rounded-lg mb-4 ${
              uploadStatus.includes('successfully') 
                ? 'bg-green-50 dark:bg-green-900/20 border border-green-200 dark:border-green-800' 
                : 'bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800'
            }`}>
              <p className={`text-sm ${
                uploadStatus.includes('successfully') 
                  ? 'text-green-600 dark:text-green-400' 
                  : 'text-red-600 dark:text-red-400'
              }`}>
                {uploadStatus}
              </p>
            </div>
          )}

          {/* File Info */}
          {uploadedFile && (
            <div className="bg-white dark:bg-gray-800 rounded-lg p-6 shadow-sm border border-gray-200 dark:border-gray-700 mb-6">
              <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">
                Uploaded File Details
              </h3>
              <div className="space-y-2 text-sm text-gray-600 dark:text-gray-400">
                <p><span className="font-medium">Name:</span> {uploadedFile.name}</p>
                <p><span className="font-medium">Size:</span> {(uploadedFile.size / 1024).toFixed(2)} KB</p>
                <p><span className="font-medium">Type:</span> {uploadedFile.type || 'text/csv'}</p>
                <p><span className="font-medium">Last Modified:</span> {new Date(uploadedFile.lastModified).toLocaleString()}</p>
                {uploadResult && (
                  <>
                    <p><span className="font-medium">Successful Uploads:</span> {uploadResult.successful_uploads || 0}</p>
                    <p><span className="font-medium">Failed Uploads:</span> {uploadResult.failed_uploads || 0}</p>
                    {uploadResult.failed_movies && uploadResult.failed_movies.length > 0 && (
                      <div>
                        <p className="font-medium">Failed Movies:</p>
                        <ul className="list-disc list-inside ml-2 text-xs">
                          {uploadResult.failed_movies.slice(0, 5).map((movie: string, index: number) => (
                            <li key={index}>{movie}</li>
                          ))}
                          {uploadResult.failed_movies.length > 5 && (
                            <li>... and {uploadResult.failed_movies.length - 5} more</li>
                          )}
                        </ul>
                      </div>
                    )}
                  </>
                )}
              </div>
            </div>
          )}

          {/* Recommendations Section */}
          <div className="bg-white dark:bg-gray-800 rounded-lg p-6 shadow-sm border border-gray-200 dark:border-gray-700">
            <div className="flex justify-between items-center mb-4">
              <h3 className="text-lg font-semibold text-gray-900 dark:text-white">
                Movie Recommendations
              </h3>
              <button
                onClick={handleGetRecommendations}
                disabled={isLoadingRecommendations}
                className={`px-4 py-2 rounded-md text-sm font-medium transition-colors ${
                  isLoadingRecommendations
                    ? 'bg-gray-300 dark:bg-gray-600 text-gray-500 dark:text-gray-400 cursor-not-allowed'
                    : 'bg-blue-600 hover:bg-blue-700 text-white'
                }`}
              >
                {isLoadingRecommendations ? 'Loading...' : 'Get Recommendations'}
              </button>
            </div>

            {recommendationsError && (
              <div className="bg-yellow-50 dark:bg-yellow-900/20 border border-yellow-200 dark:border-yellow-800 rounded-md p-3 mb-4">
                <p className="text-sm text-yellow-700 dark:text-yellow-300">{recommendationsError}</p>
              </div>
            )}

            {recommendations.length > 0 && (
              <div className="space-y-3">
                <p className="text-sm text-gray-600 dark:text-gray-400 mb-4">
                  Based on your ratings, here are your personalized movie recommendations:
                </p>
                {recommendations.map((rec, index) => (
                  <div key={rec.movie_id} className="border border-gray-200 dark:border-gray-700 rounded-lg p-4">
                    <div className="flex justify-between items-start">
                      <div className="flex-1">
                        <h4 className="font-medium text-gray-900 dark:text-white">
                          {index + 1}. {rec.title}
                        </h4>
                        <div className="text-sm text-gray-600 dark:text-gray-400 mt-1 space-y-1">
                          <p>Rating: ⭐ {rec.vote_average.toFixed(1)} ({rec.vote_count} votes)</p>
                          <p>Score: {rec.weighted_score.toFixed(2)}</p>
                          {rec.source_movies && (
                            <p className="text-xs">Based on: {rec.source_movies}</p>
                          )}
                        </div>
                      </div>
                      <div className="text-right">
                        <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-blue-100 text-blue-800 dark:bg-blue-900 dark:text-blue-200">
                          #{index + 1}
                        </span>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            )}

            {recommendations.length === 0 && !recommendationsError && !isLoadingRecommendations && (
              <p className="text-sm text-gray-500 dark:text-gray-400">
                Upload some movie ratings and click "Get Recommendations" to see personalized suggestions.
              </p>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
