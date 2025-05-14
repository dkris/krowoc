import { useState, useEffect } from 'react';
import { useRouter } from 'next/router';
import Link from 'next/link';
import Layout from '../../components/layout/Layout';
import { useAuth } from '../../lib/AuthContext';
import { Prompt } from '../../types/prompt';
import { getPromptById, deletePrompt } from '../../lib/promptApi';

export default function PromptDetailPage() {
  const router = useRouter();
  const { id } = router.query;
  const { user, isLoading: isAuthLoading } = useAuth();
  const [prompt, setPrompt] = useState<Prompt | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [isDeleting, setIsDeleting] = useState(false);

  useEffect(() => {
    if (!id) return;

    async function loadPrompt() {
      setIsLoading(true);
      try {
        const promptData = await getPromptById(id as string);
        
        if (!promptData) {
          setError('Prompt not found.');
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
  }, [id]);

  const handleDelete = async () => {
    if (!prompt || isDeleting) return;
    
    if (window.confirm('Are you sure you want to delete this prompt?')) {
      setIsDeleting(true);
      try {
        await deletePrompt(prompt.id);
        router.push('/prompts');
      } catch (error) {
        console.error('Failed to delete prompt:', error);
        alert('Failed to delete prompt. Please try again.');
        setIsDeleting(false);
      }
    }
  };

  const formatDate = (dateString: string) => {
    const date = new Date(dateString);
    return date.toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'long',
      day: 'numeric',
    });
  };

  const isOwner = user && prompt && user.id === prompt.userId;

  return (
    <Layout title={prompt ? prompt.title : 'Prompt Detail'}>
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
            <div className="flex justify-between items-start">
              <h1 className="text-2xl font-bold text-gray-900">{prompt.title}</h1>
              {isOwner && (
                <div className="flex space-x-2">
                  <Link 
                    href={`/prompts/edit/${prompt.id}`}
                    className="inline-flex items-center px-3 py-1.5 border border-gray-300 text-sm font-medium rounded text-gray-700 bg-white hover:bg-gray-50"
                  >
                    Edit
                  </Link>
                  <button
                    onClick={handleDelete}
                    disabled={isDeleting}
                    className="inline-flex items-center px-3 py-1.5 border border-transparent text-sm font-medium rounded text-white bg-red-600 hover:bg-red-700 disabled:opacity-50"
                  >
                    {isDeleting ? 'Deleting...' : 'Delete'}
                  </button>
                </div>
              )}
            </div>
            
            <div className="mt-2 flex items-center text-sm text-gray-500">
              <span>{formatDate(prompt.createdAt)}</span>
              <span className="mx-2">•</span>
              <span>{prompt.isPublic ? 'Public' : 'Private'}</span>
            </div>
            
            {prompt.tags && prompt.tags.length > 0 && (
              <div className="mt-3 flex flex-wrap gap-1">
                {prompt.tags.map((tag) => (
                  <span 
                    key={tag} 
                    className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-blue-100 text-blue-800"
                  >
                    {tag}
                  </span>
                ))}
              </div>
            )}
            
            <div className="mt-6 border-t border-gray-200 pt-6">
              <pre className="whitespace-pre-wrap text-gray-800 font-mono text-sm bg-gray-50 p-4 rounded-md">
                {prompt.content}
              </pre>
            </div>
          </div>
        </div>
      ) : null}
      
      <div className="mt-6">
        <Link 
          href="/prompts"
          className="text-blue-600 hover:text-blue-500"
        >
          ← Back to Prompts
        </Link>
      </div>
    </Layout>
  );
} 