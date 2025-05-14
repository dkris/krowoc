import { useState, useEffect } from 'react';
import { useRouter } from 'next/router';
import Layout from '../../../components/layout/Layout';
import { PromptEditor } from '../../../components/prompts';
import { useAuth } from '../../../lib/AuthContext';
import { Prompt } from '../../../types/prompt';
import { getPromptById } from '../../../lib/promptApi';

export default function EditPromptPage() {
  const router = useRouter();
  const { id } = router.query;
  const { user, isLoading: isAuthLoading } = useAuth();
  const [prompt, setPrompt] = useState<Prompt | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!id || isAuthLoading) return;

    if (!user) {
      setIsLoading(false);
      setError('You must be logged in to edit a prompt.');
      return;
    }

    async function loadPrompt() {
      setIsLoading(true);
      try {
        const promptData = await getPromptById(id as string);
        
        if (!promptData) {
          setError('Prompt not found.');
        } else if (user && promptData.userId !== user.id) {
          setError('You do not have permission to edit this prompt.');
        } else {
          setPrompt(promptData);
          setError(null);
        }
      } catch (err) {
        console.error('Failed to load prompt:', err);
        setError('Failed to load prompt. Please try again.');
      } finally {
        setIsLoading(false);
      }
    }

    loadPrompt();
  }, [id, user, isAuthLoading]);

  const handleSave = (updatedPrompt: Prompt) => {
    router.push('/prompts');
  };

  const handleCancel = () => {
    router.push('/prompts');
  };

  return (
    <Layout title="Edit Prompt">
      <div className="mb-6">
        <h1 className="text-2xl font-bold tracking-tight text-gray-900">Edit Prompt</h1>
      </div>
      
      {isLoading ? (
        <div className="text-center py-10">
          <p className="text-gray-500">Loading prompt...</p>
        </div>
      ) : error ? (
        <div className="rounded-md bg-red-50 p-4">
          <div className="text-sm text-red-700">{error}</div>
        </div>
      ) : prompt ? (
        <div className="bg-white shadow rounded-lg overflow-hidden">
          <div className="p-6">
            <PromptEditor 
              initialPrompt={prompt} 
              onSave={handleSave} 
              onCancel={handleCancel} 
            />
          </div>
        </div>
      ) : null}
    </Layout>
  );
} 