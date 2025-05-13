import React from 'react'
import type { NextPage } from 'next'

const Home: NextPage = () => {
  return (
    <div className="flex flex-col items-center justify-center py-2">
      <h1 className="text-6xl font-bold">
        Welcome to{' '}
        <span className="text-blue-600">
          Krowoc
        </span>
      </h1>

      <p className="mt-3 text-2xl">
        Manage and execute prompts across multiple LLM providers
      </p>

      <div className="mt-6 flex max-w-4xl flex-wrap items-center justify-around sm:w-full">
        <a
          href="/dashboard"
          className="mt-6 w-96 rounded-xl border p-6 text-left hover:text-blue-600 focus:text-blue-600"
        >
          <h3 className="text-2xl font-bold">Dashboard &rarr;</h3>
          <p className="mt-4 text-xl">
            View your usage metrics and analytics
          </p>
        </a>

        <a
          href="/prompts"
          className="mt-6 w-96 rounded-xl border p-6 text-left hover:text-blue-600 focus:text-blue-600"
        >
          <h3 className="text-2xl font-bold">Prompts &rarr;</h3>
          <p className="mt-4 text-xl">
            Create and manage your prompts
          </p>
        </a>

        <a
          href="/settings"
          className="mt-6 w-96 rounded-xl border p-6 text-left hover:text-blue-600 focus:text-blue-600"
        >
          <h3 className="text-2xl font-bold">Settings &rarr;</h3>
          <p className="mt-4 text-xl">
            Configure your API keys and preferences
          </p>
        </a>
      </div>
    </div>
  )
}

export default Home 