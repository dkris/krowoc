import { useState, useEffect } from 'react';
import Link from 'next/link';
import Layout from '../../components/layout/Layout';
import { PromptList } from '../../components/prompts';
import { getPrompts } from '../../lib/promptApi';
import { Prompt } from '../../types/prompt';
import { useAuth } from '../../lib/AuthContext';

export default function PromptsPage() {
  const { user, isLoading: isAuthLoading } = useAuth();
  const [prompts, setPrompts] = useState<Prompt[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (isAuthLoading) return;
    
    if (!user) {
      setIsLoading(false);
      setError('You must be logged in to view your prompts.');
      return;
    }

    async function loadPrompts() {
      setIsLoading(true);
      try {
        const promptsData = await getPrompts();
        setPrompts(promptsData);
        setError(null);
      } catch (err) {
        console.error('Failed to load prompts:', err);
        setError('Failed to load prompts. Please try again.');
      } finally {
        setIsLoading(false);
      }
    }

    loadPrompts();
  }, [user, isAuthLoading]);

  const handlePromptDeleted = (deletedPromptId: string) => {
    setPrompts((currentPrompts) => 
      currentPrompts.filter((prompt) => prompt.id !== deletedPromptId)
    );
  };

  return (
    <Layout title="My Prompts">
      <div className="flex justify-between items-center mb-6">
        <h1 className="text-2xl font-bold tracking-tight text-gray-900">My Prompts</h1>
        <Link 
          href="/prompts/new" 
          className="inline-flex items-center rounded-md border border-transparent bg-blue-600 px-4 py-2 text-sm font-medium text-white shadow-sm hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2"
        >
          Create New Prompt
        </Link>
      </div>

      {isLoading ? (
        <div className="text-center py-10">
          <p className="text-gray-500">Loading prompts...</p>
        </div>
      ) : error ? (
        <div className="rounded-md bg-red-50 p-4">
          <div className="text-sm text-red-700">{error}</div>
        </div>
      ) : (
        <PromptList 
          prompts={prompts} 
          onPromptDeleted={handlePromptDeleted} 
        />
      )}
    </Layout>
  );
} 