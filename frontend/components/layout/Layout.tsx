import React from 'react';
import Head from 'next/head';
import { Navbar } from './Navbar';
import { Footer } from './Footer';

type LayoutProps = {
  children: React.ReactNode;
};

export const Layout: React.FC<LayoutProps> = ({ children }) => {
  return (
    <div className="flex flex-col min-h-screen">
      <Head>
        <title>Krowoc</title>
        <meta name="description" content="Manage and execute prompts across multiple LLM providers" />
        <link rel="icon" href="/favicon.ico" />
      </Head>
      
      <Navbar />
      
      <main className="flex-grow">
        <div className="container py-8">
          {children}
        </div>
      </main>
      
      <Footer />
    </div>
  );
}; 