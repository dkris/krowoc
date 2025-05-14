import { supabase } from './supabase';
import { Prompt, CreatePromptInput, UpdatePromptInput } from '../types/prompt';

export async function getPrompts(): Promise<Prompt[]> {
  const { data, error } = await supabase
    .from('prompts')
    .select('*')
    .order('createdAt', { ascending: false });

  if (error) throw error;
  return data || [];
}

export async function getPromptById(id: string): Promise<Prompt | null> {
  const { data, error } = await supabase
    .from('prompts')
    .select('*')
    .eq('id', id)
    .single();

  if (error) throw error;
  return data;
}

export async function createPrompt(prompt: CreatePromptInput): Promise<Prompt> {
  const { data, error } = await supabase
    .from('prompts')
    .insert([prompt])
    .select()
    .single();

  if (error) throw error;
  return data;
}

export async function updatePrompt(id: string, updates: UpdatePromptInput): Promise<Prompt> {
  const { data, error } = await supabase
    .from('prompts')
    .update(updates)
    .eq('id', id)
    .select()
    .single();

  if (error) throw error;
  return data;
}

export async function deletePrompt(id: string): Promise<void> {
  const { error } = await supabase
    .from('prompts')
    .delete()
    .eq('id', id);

  if (error) throw error;
} 