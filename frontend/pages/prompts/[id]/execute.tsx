import { useState, useEffect } from 'react';
import { useRouter } from 'next/router';
import Head from 'next/head';
import { Prompt } from '../../../types/prompt';
import { Execution } from '../../../types/execution';
import { getPromptById } from '../../../lib/promptApi';
import { getExecutionsByPromptId, saveExecution } from '../../../lib/executionApi';
import PromptExecutor from '../../../components/prompts/PromptExecutor';
import ExecutionHistory from '../../../components/prompts/ExecutionHistory';
import Link from 'next/link';
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome';
import { faArrowLeft } from '@fortawesome/free-solid-svg-icons';

export default function PromptExecutePage() {
  const router = useRouter();
  const { id } = router.query;
  
  const [prompt, setPrompt] = useState<Prompt | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [executions, setExecutions] = useState<Execution[]>([]);
  const [selectedExecution, setSelectedExecution] = useState<Execution | null>(null);
  
  useEffect(() => {
    async function loadPrompt() {
      if (!id) return;
      
      try {
        setLoading(true);
        const promptData = await getPromptById(id as string);
        setPrompt(promptData);
        
        // Load executions history
        try {
          const executionsData = await getExecutionsByPromptId(id as string);
          setExecutions(executionsData);
        } catch (execError) {
          console.error('Failed to load executions:', execError);
          // Don't fail the whole page if just executions fail to load
        }
        
        setLoading(false);
      } catch (err) {
        console.error('Failed to load prompt:', err);
        setError(err instanceof Error ? err.message : 'Failed to load prompt');
        setLoading(false);
      }
    }
    
    loadPrompt();
  }, [id]);
  
  const handleExecutionComplete = async (execution: Execution) => {
    // Add to local state
    setExecutions(prevExecutions => [execution, ...prevExecutions]);
    
    // Save to backend
    try {
      await saveExecution(execution);
    } catch (error) {
      console.error('Failed to save execution:', error);
      // Don't block UI on save failure
    }
  };
  
  const handleSelectExecution = (execution: Execution) => {
    setSelectedExecution(execution);
  };
  
  if (loading) {
    return (
      <div className="min-h-screen bg-gray-100 flex items-center justify-center">
        <div className="text-center">
          <div className="spinner-border text-blue-500" role="status">
            <span className="sr-only">Loading...</span>
          </div>
          <p className="text-gray-600 mt-2">Loading prompt...</p>
        </div>
      </div>
    );
  }
  
  if (error || !prompt) {
    return (
      <div className="min-h-screen bg-gray-100 flex items-center justify-center">
        <div className="bg-white p-8 rounded-lg shadow-md text-center max-w-md w-full">
          <h1 className="text-2xl font-bold text-red-600 mb-4">Error</h1>
          <p className="text-gray-700 mb-6">{error || 'Prompt not found'}</p>
          <Link href="/prompts" className="text-blue-600 hover:text-blue-800">
            Return to prompts
          </Link>
        </div>
      </div>
    );
  }
  
  // Handle both naming conventions
  const promptTitle = prompt.name || prompt.title || 'Untitled Prompt';
  const promptDescription = prompt.description || prompt.content || '';
  
  return (
    <div className="min-h-screen bg-gray-100">
      <Head>
        <title>Execute Prompt: {promptTitle}</title>
      </Head>
      
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="mb-6">
          <Link href={`/prompts/${prompt.id}`} className="text-blue-600 hover:text-blue-800 inline-flex items-center">
            <FontAwesomeIcon icon={faArrowLeft} className="mr-2" />
            Back to prompt
          </Link>
        </div>
        
        <div className="mb-6">
          <h1 className="text-3xl font-bold text-gray-900">{promptTitle}</h1>
          <p className="text-gray-600 mt-2">{promptDescription}</p>
        </div>
        
        <div className="grid grid-cols-1 gap-8">
          <PromptExecutor 
            prompt={prompt}
            onExecutionComplete={handleExecutionComplete}
          />
          
          <ExecutionHistory 
            executions={executions}
            onSelectExecution={handleSelectExecution}
          />
        </div>
      </div>
    </div>
  );
} 