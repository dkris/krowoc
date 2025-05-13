import React from 'react'
import type { NextPage } from 'next'
import Head from 'next/head'

const Home: NextPage = () => {
  return (
    <>
      <Head>
        <title>Krowoc - Home</title>
      </Head>

      <div className="space-y-8">
        <div className="text-center py-12 bg-primary-50 rounded-xl">
          <h1 className="text-4xl font-bold text-gray-900 mb-4">
            Welcome to{' '}
            <span className="text-primary-600">
              Krowoc
            </span>
          </h1>
          <p className="text-xl text-gray-600 max-w-2xl mx-auto">
            Manage and execute prompts across multiple LLM providers
          </p>
        </div>
        
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          <div className="bg-white p-6 rounded-xl shadow-sm hover:shadow-md transition-shadow">
            <h3 className="text-xl font-semibold mb-2">Dashboard</h3>
            <p className="text-gray-600 mb-4">View your usage metrics and analytics</p>
            <a href="/dashboard" className="text-primary-600 hover:text-primary-700 font-medium">
              Go to Dashboard →
            </a>
          </div>
          
          <div className="bg-white p-6 rounded-xl shadow-sm hover:shadow-md transition-shadow">
            <h3 className="text-xl font-semibold mb-2">Prompts</h3>
            <p className="text-gray-600 mb-4">Create and manage your prompts</p>
            <a href="/prompts" className="text-primary-600 hover:text-primary-700 font-medium">
              Manage Prompts →
            </a>
          </div>
          
          <div className="bg-white p-6 rounded-xl shadow-sm hover:shadow-md transition-shadow">
            <h3 className="text-xl font-semibold mb-2">Settings</h3>
            <p className="text-gray-600 mb-4">Configure your API keys and preferences</p>
            <a href="/settings" className="text-primary-600 hover:text-primary-700 font-medium">
              Go to Settings →
            </a>
          </div>
        </div>
      </div>
    </>
  )
}

export default Home 