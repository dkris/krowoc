import React, { useState, useEffect } from 'react';
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import { updateUserPreferences, getUserPreferences } from '../../lib/api/userSettingsApi';

type PreferenceType = {
  theme: 'light' | 'dark' | 'system';
  notifications_enabled: boolean;
  email_notifications: boolean;
};

const Preferences = () => {
  const [preferences, setPreferences] = useState<PreferenceType>({
    theme: 'system',
    notifications_enabled: true,
    email_notifications: true,
  });
  const [isSaving, setIsSaving] = useState(false);
  const [message, setMessage] = useState<{ type: 'success' | 'error'; text: string } | null>(null);
  const queryClient = useQueryClient();

  // Fetch user preferences
  const { data: userPreferences, isLoading } = useQuery({
    queryKey: ['userPreferences'],
    queryFn: async () => {
      const { data, error } = await getUserPreferences();
      if (error) throw error;
      return data as PreferenceType;
    },
  });

  useEffect(() => {
    if (userPreferences) {
      setPreferences(userPreferences);
    }
  }, [userPreferences]);

  const updatePreferencesMutation = useMutation({
    mutationFn: async (newPreferences: PreferenceType) => {
      setIsSaving(true);
      const { data, error } = await updateUserPreferences(newPreferences);
      if (error) throw error;
      return data;
    },
    onSuccess: () => {
      setMessage({ type: 'success', text: 'Preferences updated successfully' });
      queryClient.invalidateQueries({ queryKey: ['userPreferences'] });
      setIsSaving(false);
      setTimeout(() => setMessage(null), 3000);
    },
    onError: (error) => {
      setMessage({ type: 'error', text: error.message || 'Failed to update preferences' });
      setIsSaving(false);
    },
  });

  const handleThemeChange = (e: React.ChangeEvent<HTMLSelectElement>) => {
    const value = e.target.value as 'light' | 'dark' | 'system';
    setPreferences((prev) => ({ ...prev, theme: value }));
  };

  const handleToggleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const { name, checked } = e.target;
    setPreferences((prev) => ({ ...prev, [name]: checked }));
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    updatePreferencesMutation.mutate(preferences);
  };

  if (isLoading) {
    return (
      <div className="bg-white p-6 rounded-lg shadow">
        <div className="animate-pulse">
          <div className="h-6 bg-gray-200 rounded w-1/4 mb-6"></div>
          <div className="space-y-4">
            <div className="h-10 bg-gray-200 rounded"></div>
            <div className="h-10 bg-gray-200 rounded"></div>
            <div className="h-10 bg-gray-200 rounded"></div>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="bg-white p-6 rounded-lg shadow">
      <h3 className="text-lg font-medium mb-4">Preferences</h3>
      
      {message && (
        <div 
          className={`mb-4 p-4 rounded ${
            message.type === 'success' ? 'bg-green-50 text-green-800' : 'bg-red-50 text-red-800'
          }`}
        >
          {message.text}
        </div>
      )}
      
      <form onSubmit={handleSubmit} className="space-y-6">
        <div>
          <label htmlFor="theme" className="block text-sm font-medium text-gray-700 mb-1">
            Theme
          </label>
          <select
            id="theme"
            name="theme"
            value={preferences.theme}
            onChange={handleThemeChange}
            className="shadow-sm focus:ring-indigo-500 focus:border-indigo-500 block w-full sm:text-sm border-gray-300 rounded-md"
          >
            <option value="light">Light</option>
            <option value="dark">Dark</option>
            <option value="system">System Default</option>
          </select>
        </div>
        
        <div className="space-y-4">
          <h4 className="text-sm font-medium text-gray-700">Notifications</h4>
          
          <div className="flex items-center">
            <input
              id="notifications_enabled"
              name="notifications_enabled"
              type="checkbox"
              checked={preferences.notifications_enabled}
              onChange={handleToggleChange}
              className="h-4 w-4 text-indigo-600 focus:ring-indigo-500 border-gray-300 rounded"
            />
            <label htmlFor="notifications_enabled" className="ml-2 block text-sm text-gray-700">
              Enable in-app notifications
            </label>
          </div>
          
          <div className="flex items-center">
            <input
              id="email_notifications"
              name="email_notifications"
              type="checkbox"
              checked={preferences.email_notifications}
              onChange={handleToggleChange}
              className="h-4 w-4 text-indigo-600 focus:ring-indigo-500 border-gray-300 rounded"
            />
            <label htmlFor="email_notifications" className="ml-2 block text-sm text-gray-700">
              Receive email notifications
            </label>
          </div>
        </div>
        
        <div className="pt-4">
          <button
            type="submit"
            disabled={isSaving}
            className={`inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md shadow-sm text-white bg-indigo-600 hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500 ${
              isSaving ? 'opacity-75 cursor-not-allowed' : ''
            }`}
          >
            {isSaving ? 'Saving...' : 'Save Changes'}
          </button>
        </div>
      </form>
    </div>
  );
};

export default Preferences; 