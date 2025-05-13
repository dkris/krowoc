import type { AppProps } from 'next/app';
import { Layout } from '../components/layout';
import '../styles/globals.css';
import { AuthProvider } from '../lib/AuthContext';

export default function App({ Component, pageProps }: AppProps) {
  return (
    <AuthProvider>
      <Layout>
        <Component {...pageProps} />
      </Layout>
    </AuthProvider>
  );
} 