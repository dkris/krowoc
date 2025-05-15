import React, { useState, useEffect } from 'react';
import { useMutation } from '@tanstack/react-query';
import { useAuth } from '../../lib/AuthContext';
import { updateUserProfile } from '../../lib/api/userSettingsApi';

const ProfileSettings = () => {
  const { user } = useAuth();
  const [profileData, setProfileData] = useState({
    full_name: '',
    company: '',
    job_title: '',
    timezone: 'UTC',
  });
  const [isSaving, setIsSaving] = useState(false);
  const [message, setMessage] = useState<{ type: 'success' | 'error'; text: string } | null>(null);

  useEffect(() => {
    if (user && user.user_metadata) {
      setProfileData({
        full_name: user.user_metadata.full_name || '',
        company: user.user_metadata.company || '',
        job_title: user.user_metadata.job_title || '',
        timezone: user.user_metadata.timezone || 'UTC',
      });
    }
  }, [user]);

  const updateProfileMutation = useMutation({
    mutationFn: async (profile: typeof profileData) => {
      setIsSaving(true);
      const { data, error } = await updateUserProfile(profile);
      if (error) throw error;
      return data;
    },
    onSuccess: () => {
      setMessage({ type: 'success', text: 'Profile updated successfully' });
      setIsSaving(false);
      setTimeout(() => setMessage(null), 3000);
    },
    onError: (error) => {
      setMessage({ type: 'error', text: error.message || 'Failed to update profile' });
      setIsSaving(false);
    },
  });

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement>) => {
    const { name, value } = e.target;
    setProfileData((prev) => ({ ...prev, [name]: value }));
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    updateProfileMutation.mutate(profileData);
  };

  const timezones = [
    'UTC',
    'America/New_York',
    'America/Chicago',
    'America/Denver',
    'America/Los_Angeles',
    'Europe/London',
    'Europe/Paris',
    'Asia/Tokyo',
    'Asia/Singapore',
    'Australia/Sydney',
  ];

  return (
    <div className="bg-white p-6 rounded-lg shadow">
      <h3 className="text-lg font-medium mb-4">Profile Settings</h3>
      
      {message && (
        <div 
          className={`mb-4 p-4 rounded ${
            message.type === 'success' ? 'bg-green-50 text-green-800' : 'bg-red-50 text-red-800'
          }`}
        >
          {message.text}
        </div>
      )}
      
      <form onSubmit={handleSubmit} className="space-y-4">
        <div>
          <label htmlFor="full_name" className="block text-sm font-medium text-gray-700 mb-1">
            Full Name
          </label>
          <input
            type="text"
            id="full_name"
            name="full_name"
            value={profileData.full_name}
            onChange={handleInputChange}
            className="shadow-sm focus:ring-indigo-500 focus:border-indigo-500 block w-full sm:text-sm border-gray-300 rounded-md"
          />
        </div>
        
        <div>
          <label htmlFor="company" className="block text-sm font-medium text-gray-700 mb-1">
            Company/Organization
          </label>
          <input
            type="text"
            id="company"
            name="company"
            value={profileData.company}
            onChange={handleInputChange}
            className="shadow-sm focus:ring-indigo-500 focus:border-indigo-500 block w-full sm:text-sm border-gray-300 rounded-md"
          />
        </div>
        
        <div>
          <label htmlFor="job_title" className="block text-sm font-medium text-gray-700 mb-1">
            Job Title
          </label>
          <input
            type="text"
            id="job_title"
            name="job_title"
            value={profileData.job_title}
            onChange={handleInputChange}
            className="shadow-sm focus:ring-indigo-500 focus:border-indigo-500 block w-full sm:text-sm border-gray-300 rounded-md"
          />
        </div>
        
        <div>
          <label htmlFor="timezone" className="block text-sm font-medium text-gray-700 mb-1">
            Timezone
          </label>
          <select
            id="timezone"
            name="timezone"
            value={profileData.timezone}
            onChange={handleInputChange}
            className="shadow-sm focus:ring-indigo-500 focus:border-indigo-500 block w-full sm:text-sm border-gray-300 rounded-md"
          >
            {timezones.map((tz) => (
              <option key={tz} value={tz}>
                {tz.replace('_', ' ')}
              </option>
            ))}
          </select>
          <p className="mt-1 text-sm text-gray-500">
            Your timezone is used for displaying dates and times.
          </p>
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

export default ProfileSettings; 