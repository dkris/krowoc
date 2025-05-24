import React from 'react';

/**
 * Utility functions for managing mock mode throughout the application
 */

/**
 * Check if mock mode is enabled
 * @returns boolean indicating if mock mode is enabled
 */
export function isMockMode(): boolean {
  // Check if we're in a browser environment
  if (typeof window === 'undefined') return false;
  
  // Check if the mock parameter is present in the URL
  return window.location.search.includes('mock=true');
}

/**
 * Toggle mock mode in the current URL
 * @param currentPath The current path (optional - defaults to current window.location.pathname)
 * @returns The new URL to navigate to
 */
export function toggleMockMode(currentPath?: string): string {
  const path = currentPath || (typeof window !== 'undefined' ? window.location.pathname : '/');
  
  if (isMockMode()) {
    // Disable mock mode by removing the parameter
    return path;
  } else {
    // Enable mock mode by adding the parameter
    return `${path}?mock=true`;
  }
}

/**
 * React component for displaying a mock mode banner
 */
export function MockModeBanner(): React.ReactNode {
  if (!isMockMode()) return null;
  
  return (
    <div className="bg-amber-50 border-l-4 border-amber-400 p-4 mb-6">
      <div className="flex">
        <div className="flex-shrink-0">
          <svg className="h-5 w-5 text-amber-400" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" fill="currentColor">
            <path fillRule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7-4a1 1 0 11-2 0 1 1 0 012 0zM9 9a1 1 0 000 2v3a1 1 0 001 1h1a1 1 0 100-2v-3a1 1 0 00-1-1H9z" clipRule="evenodd" />
          </svg>
        </div>
        <div className="ml-3">
          <p className="text-sm text-amber-700">
            <span className="font-medium">Mock Mode Active:</span> You are viewing simulated data for demonstration purposes.
          </p>
        </div>
      </div>
    </div>
  );
}

/**
 * React component for a mock mode toggle button
 * @param onToggle Optional callback for when mock mode is toggled
 */
export function MockModeToggle({ onToggle }: { onToggle?: () => void }): React.ReactNode {
  const isInMockMode = isMockMode();
  
  const handleToggle = () => {
    if (onToggle) {
      onToggle();
    }
  };
  
  return (
    <button 
      onClick={handleToggle} 
      className={`px-4 py-2 rounded-md font-medium ${
        isInMockMode ? 'bg-amber-100 text-amber-800 hover:bg-amber-200' : 'bg-blue-100 text-blue-800 hover:bg-blue-200'
      }`}
    >
      {isInMockMode ? 'Disable Mock Mode' : 'Enable Mock Mode'}
    </button>
  );
} 