'use client';

import { useState, useEffect } from 'react';
import CSVUpload from '../../components/CSVUpload';

interface User {
  id: number;
  username: string;
  email: string;
}

export default function UploadPage() {
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [token, setToken] = useState<string | null>(null);
  const [currentUser, setCurrentUser] = useState<User | null>(null);
  const [isUploading, setIsUploading] = useState(false);
  const [uploadedFile, setUploadedFile] = useState<File | null>(null);
  const [uploadStatus, setUploadStatus] = useState<string | null>(null);
  const [uploadResult, setUploadResult] = useState<any>(null);

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

  const handleLogout = () => {
    setToken(null);
    setIsAuthenticated(false);
    setCurrentUser(null);
    localStorage.removeItem('authToken');
    setUploadedFile(null);
    setUploadStatus(null);
    setUploadResult(null);
    // Redirect to home page
    window.location.href = '/';
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
      const formData = new FormData();
      formData.append('file', file);

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

  if (!isAuthenticated) {
    return (
      <div className="min-h-screen bg-gray-50 dark:bg-gray-900">
        <div className="container mx-auto px-4 py-8">
          <div className="max-w-2xl mx-auto">
            <div className="bg-white dark:bg-gray-800 rounded-lg shadow-md p-6">
              <h2 className="text-2xl font-bold text-gray-900 dark:text-white mb-4">
                Access Denied
              </h2>
              <p className="text-gray-600 dark:text-gray-400 mb-4">
                Please login to upload your movie ratings.
              </p>
              <a
                href="/"
                className="bg-green-500 hover:bg-green-600 text-white font-bold px-4 py-2 rounded"
              >
                Go to Login
              </a>
            </div>
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
                Upload
              </h1>
              <p className="text-gray-600 dark:text-gray-400 m-4">
                Welcome back, {currentUser?.username}! Upload your movie ratings to get personalized recommendations. currently supports: csv files
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

          {/* Next Steps */}
          {uploadResult && uploadResult.successful_uploads > 0 && (
            <div className="bg-green-50 dark:bg-green-900/20 border border-green-200 dark:border-green-800 rounded-lg p-6">
              <h3 className="text-lg font-semibold text-green-900 dark:text-green-100 mb-2">
                Upload Successful! 🎉
              </h3>
              <p className="text-green-700 dark:text-green-300 mb-4">
                Your movie ratings have been uploaded successfully. You can now get personalized recommendations.
              </p>
              <div className="flex space-x-4">
                <a
                  href="/weekly"
                  className="bg-green-500 hover:bg-green-600 text-white font-bold px-4 py-2 rounded transition-colors"
                >
                  Get Recommendations
                </a>
                <a
                  href="/"
                  className="bg-gray-500 hover:bg-gray-600 text-white font-bold px-4 py-2 rounded transition-colors"
                >
                  Back to Dashboard
                </a>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
} 