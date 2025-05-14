import { useState } from 'react';
import { Prompt } from '../../types/prompt';
import PromptCard from './PromptCard';
import { deletePrompt } from '../../lib/promptApi';

interface PromptListProps {
  prompts: Prompt[];
  onPromptDeleted?: (deletedPromptId: string) => void;
}

export default function PromptList({ prompts, onPromptDeleted }: PromptListProps) {
  const [isDeleting, setIsDeleting] = useState(false);

  const handleDelete = async (id: string) => {
    if (isDeleting) return;
    
    setIsDeleting(true);
    try {
      await deletePrompt(id);
      if (onPromptDeleted) {
        onPromptDeleted(id);
      }
    } catch (error) {
      console.error('Failed to delete prompt:', error);
      alert('Failed to delete prompt. Please try again.');
    } finally {
      setIsDeleting(false);
    }
  };

  if (prompts.length === 0) {
    return (
      <div className="text-center py-10">
        <p className="text-gray-500">No prompts found.</p>
      </div>
    );
  }

  return (
    <div className="grid grid-cols-1 gap-6 sm:grid-cols-2 lg:grid-cols-3">
      {prompts.map((prompt) => (
        <PromptCard 
          key={prompt.id} 
          prompt={prompt} 
          onDelete={handleDelete}
        />
      ))}
    </div>
  );
} 