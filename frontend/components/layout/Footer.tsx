import React from 'react';

export const Footer: React.FC = () => {
  return (
    <footer className="bg-gray-100">
      <div className="container mx-auto py-6">
        <div className="flex flex-col md:flex-row justify-between items-center">
          <div className="mb-4 md:mb-0">
            <p className="text-gray-600">
              © {new Date().getFullYear()} Krowoc. All rights reserved.
            </p>
          </div>
          
          <div className="flex space-x-6">
            <a href="#" className="text-gray-600 hover:text-primary-600 transition-colors">
              Privacy Policy
            </a>
            <a href="#" className="text-gray-600 hover:text-primary-600 transition-colors">
              Terms of Service
            </a>
            <a href="#" className="text-gray-600 hover:text-primary-600 transition-colors">
              Contact
            </a>
          </div>
        </div>
      </div>
    </footer>
  );
}; 