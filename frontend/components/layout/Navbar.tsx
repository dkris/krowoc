import React from 'react';
import Link from 'next/link';

export const Navbar: React.FC = () => {
  return (
    <nav className="bg-white shadow-sm">
      <div className="container mx-auto py-4">
        <div className="flex items-center justify-between">
          <div className="flex items-center">
            <Link href="/" className="text-2xl font-bold text-primary-600">
              Krowoc
            </Link>
          </div>
          
          <div className="hidden md:flex space-x-8">
            <Link href="/dashboard" className="text-gray-700 hover:text-primary-600 transition-colors">
              Dashboard
            </Link>
            <Link href="/prompts" className="text-gray-700 hover:text-primary-600 transition-colors">
              Prompts
            </Link>
            <Link href="/settings" className="text-gray-700 hover:text-primary-600 transition-colors">
              Settings
            </Link>
          </div>
          
          <div>
            <button className="btn btn-primary">
              Sign In
            </button>
          </div>
        </div>
      </div>
    </nav>
  );
}; 