import { useState, useEffect } from 'react';
import { useRouter } from 'next/router';
import { CreatePromptInput, Prompt } from '../../types/prompt';
import { createPrompt, updatePrompt } from '../../lib/promptApi';

interface PromptEditorProps {
  initialPrompt?: Prompt;
  onSave?: (prompt: Prompt) => void;
  onCancel?: () => void;
}

export default function PromptEditor({ initialPrompt, onSave, onCancel }: PromptEditorProps) {
  const router = useRouter();
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [prompt, setPrompt] = useState<CreatePromptInput>({
    title: '',
    content: '',
    isPublic: false,
    tags: [],
  });

  useEffect(() => {
    if (initialPrompt) {
      setPrompt({
        title: initialPrompt.title,
        content: initialPrompt.content,
        isPublic: initialPrompt.isPublic,
        tags: initialPrompt.tags,
      });
    }
  }, [initialPrompt]);

  const handleChange = (e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement>) => {
    const { name, value } = e.target;
    setPrompt((prev) => ({ ...prev, [name]: value }));
  };

  const handleTogglePublic = () => {
    setPrompt((prev) => ({ ...prev, isPublic: !prev.isPublic }));
  };

  const handleTagsChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const tagsInput = e.target.value;
    const tagsArray = tagsInput.split(',').map(tag => tag.trim()).filter(Boolean);
    setPrompt((prev) => ({ ...prev, tags: tagsArray }));
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsSubmitting(true);
    setError(null);

    try {
      let savedPrompt: Prompt;

      if (initialPrompt) {
        savedPrompt = await updatePrompt(initialPrompt.id, prompt);
      } else {
        savedPrompt = await createPrompt(prompt);
      }

      if (onSave) {
        onSave(savedPrompt);
      } else {
        router.push(`/prompts/${savedPrompt.id}`);
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : 'An error occurred while saving the prompt');
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <form onSubmit={handleSubmit} className="space-y-6">
      {error && (
        <div className="rounded-md bg-red-50 p-4 mb-4">
          <div className="text-sm text-red-700">{error}</div>
        </div>
      )}

      <div>
        <label htmlFor="title" className="block text-sm font-medium text-gray-700">
          Title
        </label>
        <input
          type="text"
          id="title"
          name="title"
          value={prompt.title}
          onChange={handleChange}
          required
          className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 sm:text-sm"
          placeholder="Enter a descriptive title for your prompt"
        />
      </div>

      <div>
        <label htmlFor="content" className="block text-sm font-medium text-gray-700">
          Prompt Content
        </label>
        <textarea
          id="content"
          name="content"
          rows={10}
          value={prompt.content}
          onChange={handleChange}
          required
          className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 sm:text-sm"
          placeholder="Write your prompt content here..."
        />
      </div>

      <div>
        <label htmlFor="tags" className="block text-sm font-medium text-gray-700">
          Tags (comma separated)
        </label>
        <input
          type="text"
          id="tags"
          name="tags"
          value={prompt.tags?.join(', ') || ''}
          onChange={handleTagsChange}
          className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 sm:text-sm"
          placeholder="coding, writing, marketing, etc."
        />
      </div>

      <div className="flex items-center">
        <input
          id="isPublic"
          name="isPublic"
          type="checkbox"
          checked={prompt.isPublic || false}
          onChange={handleTogglePublic}
          className="h-4 w-4 rounded border-gray-300 text-blue-600 focus:ring-blue-500"
        />
        <label htmlFor="isPublic" className="ml-2 block text-sm text-gray-700">
          Make this prompt public
        </label>
      </div>

      <div className="flex justify-end space-x-3">
        {onCancel && (
          <button
            type="button"
            onClick={onCancel}
            className="rounded-md border border-gray-300 bg-white px-4 py-2 text-sm font-medium text-gray-700 shadow-sm hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2"
          >
            Cancel
          </button>
        )}
        <button
          type="submit"
          disabled={isSubmitting}
          className="inline-flex justify-center rounded-md border border-transparent bg-blue-600 px-4 py-2 text-sm font-medium text-white shadow-sm hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 disabled:opacity-50"
        >
          {isSubmitting ? 'Saving...' : initialPrompt ? 'Update Prompt' : 'Create Prompt'}
        </button>
      </div>
    </form>
  );
} 