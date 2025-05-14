export interface Prompt {
  id: string;
  title: string;
  content: string;
  createdAt: string;
  updatedAt: string;
  userId: string;
  tags?: string[];
  isPublic?: boolean;
}

export type CreatePromptInput = Omit<Prompt, 'id' | 'createdAt' | 'updatedAt' | 'userId'>;
export type UpdatePromptInput = Partial<CreatePromptInput>; 