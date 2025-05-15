import React, { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { generateApiKey, listApiKeys, deleteApiKey } from '../../lib/api/userSettingsApi';
import { format } from 'date-fns';

type ProviderKey = {
  id: string;
  provider: string;
  key_prefix: string;
  created_at: string;
  last_used_at: string | null;
};

type TestResult = {
  success: boolean;
  message: string;
};

const ApiKeyManagement = () => {
  const [newKeyValue, setNewKeyValue] = useState('');
  const [selectedProvider, setSelectedProvider] = useState('openai');
  const [isAddingKey, setIsAddingKey] = useState(false);
  const [isTesting, setIsTesting] = useState<Record<string, boolean>>({});
  const [testResults, setTestResults] = useState<Record<string, TestResult>>({});
  const [error, setError] = useState<string | null>(null);
  const queryClient = useQueryClient();

  // Fetch provider API keys
  const { data: providerKeys, isLoading, isError } = useQuery({
    queryKey: ['providerKeys'],
    queryFn: async () => {
      const { data, error } = await listApiKeys();
      if (error) throw error;
      return data as ProviderKey[];
    },
  });

  // Add provider API key mutation
  const addKeyMutation = useMutation({
    mutationFn: async ({ provider, key }: { provider: string, key: string }) => {
      setIsAddingKey(true);
      const { data, error } = await generateApiKey(provider, key);
      if (error) throw error;
      return data;
    },
    onSuccess: () => {
      setNewKeyValue('');
      queryClient.invalidateQueries({ queryKey: ['providerKeys'] });
      setIsAddingKey(false);
    },
    onError: (error) => {
      setError(error.message || 'Failed to add API key');
      setIsAddingKey(false);
    },
  });

  // Delete provider API key mutation
  const deleteKeyMutation = useMutation({
    mutationFn: async (id: string) => {
      const { success, error } = await deleteApiKey(id);
      if (!success) throw error;
      return success;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['providerKeys'] });
    },
    onError: (error) => {
      setError(error.message || 'Failed to delete API key');
    },
  });

  const handleAddKey = (e: React.FormEvent) => {
    e.preventDefault();
    if (!newKeyValue.trim()) {
      setError('Please enter a valid API key');
      return;
    }
    addKeyMutation.mutate({ provider: selectedProvider, key: newKeyValue });
  };

  const handleDeleteKey = (id: string) => {
    if (window.confirm('Are you sure you want to delete this API key? This action cannot be undone.')) {
      deleteKeyMutation.mutate(id);
    }
  };

  const handleTestKey = async (provider: string) => {
    try {
      setIsTesting(prev => ({ ...prev, [provider]: true }));
      
      // Remove the test result while testing
      setTestResults(prev => {
        const newResults = { ...prev };
        delete newResults[provider];
        return newResults;
      });
      
      const token = await fetch('/api/user-settings/test-provider-call/' + provider, {
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('supabase.auth.token')}`
        }
      });
      
      const result = await token.json();
      
      if (token.ok) {
        setTestResults(prev => ({ 
          ...prev, 
          [provider]: { 
            success: true, 
            message: result.message || 'Successfully verified API key'
          }
        }));
      } else {
        setTestResults(prev => ({ 
          ...prev, 
          [provider]: { 
            success: false, 
            message: result.error || 'Failed to verify API key'
          }
        }));
      }
    } catch (err) {
      // TypeScript-safe error handling
      const errorMessage = err instanceof Error ? err.message : 'An unknown error occurred';
      setTestResults(prev => ({ 
        ...prev, 
        [provider]: { 
          success: false, 
          message: errorMessage || 'Failed to test API key'
        }
      }));
    } finally {
      setIsTesting(prev => ({ ...prev, [provider]: false }));
    }
  };

  const formatDate = (dateString: string | null) => {
    if (!dateString) return 'Never';
    return format(new Date(dateString), 'MMM d, yyyy h:mm a');
  };

  const getProviderDisplayName = (provider: string): string => {
    switch(provider) {
      case 'openai': return 'OpenAI';
      case 'anthropic': return 'Anthropic';
      case 'google': return 'Google AI';
      default: return provider;
    }
  };

  const getProviderDescription = (provider: string): string => {
    switch(provider) {
      case 'openai': return 'Powers ChatGPT, GPT-4, and text-embedding models';
      case 'anthropic': return 'Powers Claude and Claude Instant models';
      case 'google': return 'Powers Gemini models and Google AI services';
      default: return '';
    }
  };

  return (
    <div className="space-y-6">
      <div className="bg-white p-6 rounded-lg shadow">
        <h3 className="text-lg font-medium mb-4">Add Provider API Key</h3>
        
        <p className="text-sm text-gray-500 mb-4">
          Add your API keys from providers like OpenAI, Anthropic, and Google to use their models with our application.
          Your keys are stored securely and are used only to make API calls on your behalf.
        </p>
        
        {error && (
          <div className="bg-red-50 border-l-4 border-red-400 p-4 mb-4">
            <div className="flex">
              <div className="flex-shrink-0">
                <svg className="h-5 w-5 text-red-400" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" fill="currentColor">
                  <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clipRule="evenodd" />
                </svg>
              </div>
              <div className="ml-3">
                <p className="text-sm text-red-700">
                  {error}
                </p>
              </div>
            </div>
          </div>
        )}
        
        <form onSubmit={handleAddKey} className="space-y-4">
          <div>
            <label htmlFor="provider" className="block text-sm font-medium text-gray-700 mb-1">
              Provider
            </label>
            <select
              id="provider"
              name="provider"
              value={selectedProvider}
              onChange={(e) => setSelectedProvider(e.target.value)}
              className="shadow-sm focus:ring-indigo-500 focus:border-indigo-500 block w-full sm:text-sm border-gray-300 rounded-md"
              disabled={isAddingKey}
            >
              <option value="openai">OpenAI</option>
              <option value="anthropic">Anthropic</option>
              <option value="google">Google AI</option>
            </select>
            <p className="mt-1 text-xs text-gray-500">
              {getProviderDescription(selectedProvider)}
            </p>
          </div>
          
          <div>
            <label htmlFor="apiKey" className="block text-sm font-medium text-gray-700 mb-1">
              API Key
            </label>
            <input
              type="password"
              id="apiKey"
              name="apiKey"
              value={newKeyValue}
              onChange={(e) => setNewKeyValue(e.target.value)}
              placeholder={`Enter your ${getProviderDisplayName(selectedProvider)} API key`}
              className="shadow-sm focus:ring-indigo-500 focus:border-indigo-500 block w-full sm:text-sm border-gray-300 rounded-md"
              disabled={isAddingKey}
            />
          </div>
          
          <div className="flex items-center pt-2">
            <button
              type="submit"
              disabled={isAddingKey}
              className={`inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md shadow-sm text-white bg-indigo-600 hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500 ${
                isAddingKey ? 'opacity-75 cursor-not-allowed' : ''
              }`}
            >
              {isAddingKey ? 'Adding...' : 'Add Key'}
            </button>
          </div>
        </form>
      </div>

      <div className="bg-white p-6 rounded-lg shadow">
        <h3 className="text-lg font-medium mb-4">Your Provider API Keys</h3>
        
        {isLoading ? (
          <div className="text-center py-4">
            <p className="text-gray-500">Loading API keys...</p>
          </div>
        ) : isError ? (
          <div className="bg-red-50 border-l-4 border-red-400 p-4">
            <div className="flex">
              <div className="flex-shrink-0">
                <svg className="h-5 w-5 text-red-400" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" fill="currentColor">
                  <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clipRule="evenodd" />
                </svg>
              </div>
              <div className="ml-3">
                <p className="text-sm text-red-700">
                  Failed to load API keys. Please try again.
                </p>
              </div>
            </div>
          </div>
        ) : (!providerKeys || providerKeys.length === 0) ? (
          <div className="text-center py-6 bg-gray-50 rounded-lg">
            <p className="text-gray-500">You haven't added any provider API keys yet.</p>
          </div>
        ) : (
          <div className="overflow-x-auto">
            <table className="min-w-full divide-y divide-gray-200">
              <thead>
                <tr>
                  <th className="px-6 py-3 bg-gray-50 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Provider
                  </th>
                  <th className="px-6 py-3 bg-gray-50 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Key Prefix
                  </th>
                  <th className="px-6 py-3 bg-gray-50 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Added
                  </th>
                  <th className="px-6 py-3 bg-gray-50 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Last Used
                  </th>
                  <th className="px-6 py-3 bg-gray-50 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Actions
                  </th>
                </tr>
              </thead>
              <tbody className="bg-white divide-y divide-gray-200">
                {providerKeys.map((key) => (
                  <tr key={key.id}>
                    <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">
                      {getProviderDisplayName(key.provider)}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                      <code className="bg-gray-100 px-2 py-1 rounded text-sm">{key.key_prefix}...</code>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                      {formatDate(key.created_at)}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                      {formatDate(key.last_used_at)}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-right text-sm font-medium space-x-2 flex items-center justify-end">
                      {testResults[key.provider] && (
                        <span className={`text-sm ${testResults[key.provider].success ? 'text-green-600' : 'text-red-600'}`}>
                          {testResults[key.provider].message}
                        </span>
                      )}
                      
                      <button
                        onClick={() => handleTestKey(key.provider)}
                        disabled={isTesting[key.provider]}
                        className={`text-indigo-600 hover:text-indigo-900 ${isTesting[key.provider] ? 'opacity-50 cursor-not-allowed' : ''}`}
                      >
                        {isTesting[key.provider] ? 'Testing...' : 'Test'}
                      </button>
                      
                      <button
                        onClick={() => handleDeleteKey(key.id)}
                        className="text-red-600 hover:text-red-900"
                      >
                        Delete
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </div>
  );
};

export default ApiKeyManagement; 