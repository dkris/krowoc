import { useRouter } from 'next/router';
import Layout from '../../components/layout/Layout';
import { PromptEditor } from '../../components/prompts';
import { useAuth } from '../../lib/AuthContext';
import { Prompt } from '../../types/prompt';

export default function NewPromptPage() {
  const router = useRouter();
  const { user, isLoading } = useAuth();

  const handleSave = (prompt: Prompt) => {
    router.push('/prompts');
  };

  const handleCancel = () => {
    router.push('/prompts');
  };

  if (isLoading) {
    return (
      <Layout title="Create New Prompt">
        <div className="text-center py-10">
          <p className="text-gray-500">Loading...</p>
        </div>
      </Layout>
    );
  }

  if (!user) {
    return (
      <Layout title="Create New Prompt">
        <div className="rounded-md bg-red-50 p-4">
          <div className="text-sm text-red-700">
            You must be logged in to create a prompt.
          </div>
        </div>
      </Layout>
    );
  }

  return (
    <Layout title="Create New Prompt">
      <div className="mb-6">
        <h1 className="text-2xl font-bold tracking-tight text-gray-900">Create New Prompt</h1>
      </div>
      
      <div className="bg-white shadow rounded-lg overflow-hidden">
        <div className="p-6">
          <PromptEditor onSave={handleSave} onCancel={handleCancel} />
        </div>
      </div>
    </Layout>
  );
} 