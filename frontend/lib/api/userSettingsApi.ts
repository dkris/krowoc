import { supabase } from '../supabase';

// Provider API Key Management
export const generateApiKey = async (provider: string, key: string) => {
  try {
    const { data: user } = await supabase.auth.getUser();
    const token = await supabase.auth.getSession().then(session => session.data.session?.access_token);
    
    if (!token) {
      throw new Error('User not authenticated');
    }
    
    const response = await fetch('/api/user-settings/api-keys', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${token}`
      },
      body: JSON.stringify({ provider, key })
    });
    
    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.error || 'Failed to add provider API key');
    }
    
    const data = await response.json();
    return { data, error: null };
  } catch (error) {
    return { data: null, error };
  }
};

export const listApiKeys = async () => {
  try {
    const { data: user } = await supabase.auth.getUser();
    const token = await supabase.auth.getSession().then(session => session.data.session?.access_token);
    
    if (!token) {
      throw new Error('User not authenticated');
    }
    
    const response = await fetch('/api/user-settings/api-keys', {
      method: 'GET',
      headers: {
        'Authorization': `Bearer ${token}`
      }
    });
    
    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.error || 'Failed to list provider API keys');
    }
    
    const data = await response.json();
    return { data, error: null };
  } catch (error) {
    return { data: null, error };
  }
};

export const deleteApiKey = async (id: string) => {
  try {
    const { data: user } = await supabase.auth.getUser();
    const token = await supabase.auth.getSession().then(session => session.data.session?.access_token);
    
    if (!token) {
      throw new Error('User not authenticated');
    }
    
    const response = await fetch(`/api/user-settings/api-keys/${id}`, {
      method: 'DELETE',
      headers: {
        'Authorization': `Bearer ${token}`
      }
    });
    
    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.error || 'Failed to delete provider API key');
    }
    
    return { success: true, error: null };
  } catch (error) {
    return { success: false, error };
  }
};

// User Profile Settings
export const updateUserProfile = async (profile: {
  full_name?: string;
  avatar_url?: string;
  company?: string;
  job_title?: string;
  timezone?: string;
}) => {
  try {
    const { data: user } = await supabase.auth.getUser();
    
    if (!user.user) {
      throw new Error('No user found');
    }
    
    const { data, error } = await supabase.auth.updateUser({
      data: {
        ...user.user.user_metadata,
        ...profile,
      },
    });
    
    if (error) throw error;
    return { data, error: null };
  } catch (error) {
    return { data: null, error };
  }
};

// User Preferences
export const updateUserPreferences = async (preferences: {
  theme?: 'light' | 'dark' | 'system';
  notifications_enabled?: boolean;
  email_notifications?: boolean;
}) => {
  try {
    const token = await supabase.auth.getSession().then(session => session.data.session?.access_token);
    
    if (!token) {
      throw new Error('User not authenticated');
    }
    
    const response = await fetch('/api/user-settings/preferences', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${token}`
      },
      body: JSON.stringify(preferences)
    });
    
    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.error || 'Failed to update preferences');
    }
    
    const data = await response.json();
    return { data: data.data, error: null };
  } catch (error) {
    return { data: null, error };
  }
};

export const getUserPreferences = async () => {
  try {
    const token = await supabase.auth.getSession().then(session => session.data.session?.access_token);
    
    if (!token) {
      throw new Error('User not authenticated');
    }
    
    const response = await fetch('/api/user-settings/preferences', {
      method: 'GET',
      headers: {
        'Authorization': `Bearer ${token}`
      }
    });
    
    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.error || 'Failed to get preferences');
    }
    
    const result = await response.json();
    
    // Default preferences if none found or there's an error
    if (!result.success || !result.data) {
      return { 
        data: {
          theme: 'system',
          notifications_enabled: true,
          email_notifications: true,
        }, 
        error: null 
      };
    }
    
    return { data: result.data, error: null };
  } catch (error) {
    return { 
      data: {
        theme: 'system',
        notifications_enabled: true,
        email_notifications: true,
      }, 
      error 
    };
  }
}; 