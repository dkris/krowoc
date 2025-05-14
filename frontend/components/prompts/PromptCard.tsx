import Link from 'next/link';
import { Prompt } from '../../types/prompt';

interface PromptCardProps {
  prompt: Prompt;
  onDelete?: (id: string) => void;
}

export default function PromptCard({ prompt, onDelete }: PromptCardProps) {
  const handleDelete = (e: React.MouseEvent) => {
    e.preventDefault();
    if (window.confirm('Are you sure you want to delete this prompt?') && onDelete) {
      onDelete(prompt.id);
    }
  };

  const formatDate = (dateString: string) => {
    const date = new Date(dateString);
    return date.toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
    });
  };

  return (
    <div className="bg-white overflow-hidden shadow rounded-lg hover:shadow-md transition-shadow">
      <div className="p-5">
        <Link href={`/prompts/${prompt.id}`} className="block">
          <h3 className="text-lg font-medium text-gray-900 truncate">{prompt.title}</h3>
        </Link>
        <p className="mt-2 text-sm text-gray-600 line-clamp-2">{prompt.content}</p>
        <div className="mt-4 flex items-center">
          <span className="text-xs text-gray-500">
            {formatDate(prompt.updatedAt)}
          </span>
          <span className="mx-2 text-gray-300">•</span>
          <span className="text-xs text-gray-500">
            {prompt.isPublic ? 'Public' : 'Private'}
          </span>
        </div>
        {prompt.tags && prompt.tags.length > 0 && (
          <div className="mt-2 flex flex-wrap gap-1">
            {prompt.tags.map((tag) => (
              <span 
                key={tag} 
                className="inline-flex items-center px-2 py-0.5 rounded text-xs font-medium bg-blue-100 text-blue-800"
              >
                {tag}
              </span>
            ))}
          </div>
        )}
      </div>
      {onDelete && (
        <div className="bg-gray-50 px-5 py-3">
          <div className="flex justify-end space-x-3">
            <Link 
              href={`/prompts/edit/${prompt.id}`}
              className="text-sm font-medium text-blue-600 hover:text-blue-500"
            >
              Edit
            </Link>
            <button
              onClick={handleDelete}
              className="text-sm font-medium text-red-600 hover:text-red-500"
            >
              Delete
            </button>
          </div>
        </div>
      )}
    </div>
  );
} 