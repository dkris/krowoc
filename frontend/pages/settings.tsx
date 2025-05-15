import React, { useState } from 'react';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { useRouter } from 'next/router';
import Link from 'next/link';
import { useAuth } from '../lib/AuthContext';
import ProtectedRoute from '../components/auth/ProtectedRoute';
import ProfileSettings from '../components/settings/ProfileSettings';
import ApiKeyManagement from '../components/settings/ApiKeyManagement';
import Preferences from '../components/settings/Preferences';

// Create a query client
const queryClient = new QueryClient();

type SettingsTabType = 'profile' | 'api-keys' | 'preferences';

const SettingsPage = () => {
  return (
    <QueryClientProvider client={queryClient}>
      <SettingsContent />
    </QueryClientProvider>
  );
};

const SettingsContent = () => {
  const router = useRouter();
  const { tab = 'profile' } = router.query;
  const [activeTab, setActiveTab] = useState<SettingsTabType>(
    (typeof tab === 'string' ? tab : 'profile') as SettingsTabType
  );
  const { user } = useAuth();

  const handleTabChange = (tab: SettingsTabType) => {
    setActiveTab(tab);
    router.push({
      pathname: '/settings',
      query: { tab },
    }, undefined, { shallow: true });
  };

  const renderTabContent = () => {
    switch (activeTab) {
      case 'profile':
        return <ProfileSettings />;
      case 'api-keys':
        return <ApiKeyManagement />;
      case 'preferences':
        return <Preferences />;
      default:
        return <ProfileSettings />;
    }
  };

  return (
    <ProtectedRoute>
      <div className="py-8">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="mb-8">
            <h1 className="text-2xl font-bold">Settings</h1>
            <p className="text-gray-500 mt-1">
              Manage your account settings and preferences
            </p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
            {/* Sidebar */}
            <div className="col-span-1">
              <div className="bg-white rounded-lg shadow overflow-hidden">
                <div className="p-4 border-b">
                  <div className="flex items-center space-x-3">
                    <div className="bg-indigo-100 rounded-full p-2">
                      <svg className="h-6 w-6 text-indigo-600" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z" />
                      </svg>
                    </div>
                    <div>
                      <p className="font-medium text-gray-900">{user?.user_metadata?.full_name || user?.email}</p>
                      <p className="text-sm text-gray-500">{user?.email}</p>
                    </div>
                  </div>
                </div>
                <nav className="p-2">
                  <button
                    onClick={() => handleTabChange('profile')}
                    className={`w-full text-left px-3 py-2 rounded-md text-sm font-medium ${
                      activeTab === 'profile'
                        ? 'bg-indigo-50 text-indigo-700'
                        : 'text-gray-700 hover:bg-gray-50'
                    }`}
                  >
                    Profile Settings
                  </button>
                  <button
                    onClick={() => handleTabChange('api-keys')}
                    className={`w-full text-left px-3 py-2 rounded-md text-sm font-medium ${
                      activeTab === 'api-keys'
                        ? 'bg-indigo-50 text-indigo-700'
                        : 'text-gray-700 hover:bg-gray-50'
                    }`}
                  >
                    API Keys
                  </button>
                  <button
                    onClick={() => handleTabChange('preferences')}
                    className={`w-full text-left px-3 py-2 rounded-md text-sm font-medium ${
                      activeTab === 'preferences'
                        ? 'bg-indigo-50 text-indigo-700'
                        : 'text-gray-700 hover:bg-gray-50'
                    }`}
                  >
                    Preferences
                  </button>
                </nav>
                <div className="p-4 border-t">
                  <Link href="/dashboard" className="text-sm text-indigo-600 hover:text-indigo-800">
                    ← Back to Dashboard
                  </Link>
                </div>
              </div>
            </div>

            {/* Content */}
            <div className="col-span-1 md:col-span-3">
              {renderTabContent()}
            </div>
          </div>
        </div>
      </div>
    </ProtectedRoute>
  );
};

export default SettingsPage; 