import { useState } from 'react';
import { Provider } from '@supabase/supabase-js';
import { signIn, signUp, signInWithProvider, resetPassword } from './supabase';

type AuthFormData = {
  email: string;
  password: string;
};

type AuthFormErrors = {
  email?: string;
  password?: string;
  general?: string;
};

export default function useAuthForm(type: 'login' | 'signup' | 'reset') {
  const [isLoading, setIsLoading] = useState(false);
  const [errors, setErrors] = useState<AuthFormErrors>({});
  const [success, setSuccess] = useState(false);

  // Validate email format
  const validateEmail = (email: string): boolean => {
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    return emailRegex.test(email);
  };

  // Validate form inputs
  const validateForm = (data: AuthFormData): boolean => {
    const newErrors: AuthFormErrors = {};
    
    if (!data.email || !validateEmail(data.email)) {
      newErrors.email = 'Please enter a valid email address';
    }
    
    if (type !== 'reset' && (!data.password || data.password.length < 6)) {
      newErrors.password = 'Password must be at least 6 characters';
    }
    
    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  // Handle form submission
  const handleSubmit = async (data: AuthFormData) => {
    if (!validateForm(data)) {
      return;
    }
    
    setIsLoading(true);
    setErrors({});
    setSuccess(false);
    
    try {
      let result;
      
      if (type === 'login') {
        result = await signIn(data.email, data.password);
      } else if (type === 'signup') {
        result = await signUp(data.email, data.password);
      } else if (type === 'reset') {
        result = await resetPassword(data.email);
      }
      
      if (result?.error) {
        setErrors({ general: result.error.message });
      } else {
        setSuccess(true);
      }
    } catch (error) {
      setErrors({ general: 'An unexpected error occurred' });
    } finally {
      setIsLoading(false);
    }
  };

  // Handle social provider sign-in
  const handleProviderSignIn = async (provider: Provider) => {
    setIsLoading(true);
    setErrors({});
    
    try {
      const result = await signInWithProvider(provider);
      if (result.error) {
        setErrors({ general: result.error.message });
      }
    } catch (error) {
      setErrors({ general: 'An unexpected error occurred' });
    } finally {
      setIsLoading(false);
    }
  };

  return {
    isLoading,
    errors,
    success,
    handleSubmit,
    handleProviderSignIn,
  };
} 