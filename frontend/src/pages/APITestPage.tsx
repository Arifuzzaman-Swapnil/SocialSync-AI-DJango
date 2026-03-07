import { useState } from 'react';
import api from '../services/api';

interface TestResult {
  status: 'ok' | 'error';
  response?: string;
  model?: string;
  provider?: string;
  tokens_used?: number;
  error?: string;
}

export function APITestPage() {
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<TestResult | null>(null);

  const runTest = async () => {
    setLoading(true);
    setResult(null);
    try {
      const { data } = await api.post('/test-claude/');
      setResult(data);
    } catch (err: any) {
      const errData = err.response?.data;
      setResult({
        status: 'error',
        error: errData?.error || err.message || 'Network error',
      });
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="max-w-xl mx-auto py-12 px-4">
      <h1 className="text-2xl font-bold text-gray-900 dark:text-white mb-2">
        Claude API Test
      </h1>
      <p className="text-gray-500 dark:text-gray-400 mb-8">
        Click the button to send a test request to the Claude API and verify connectivity.
      </p>

      <button
        onClick={runTest}
        disabled={loading}
        className="px-6 py-3 bg-indigo-600 text-white rounded-lg font-medium hover:bg-indigo-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
      >
        {loading ? 'Testing...' : 'Test Claude API'}
      </button>

      {result && (
        <div
          className={`mt-8 p-6 rounded-lg border ${
            result.status === 'ok'
              ? 'bg-green-50 border-green-200 dark:bg-green-900/20 dark:border-green-800'
              : 'bg-red-50 border-red-200 dark:bg-red-900/20 dark:border-red-800'
          }`}
        >
          <h2
            className={`text-lg font-semibold mb-3 ${
              result.status === 'ok'
                ? 'text-green-800 dark:text-green-300'
                : 'text-red-800 dark:text-red-300'
            }`}
          >
            {result.status === 'ok' ? 'API Working' : 'API Error'}
          </h2>

          <dl className="space-y-2 text-sm">
            {result.response && (
              <div>
                <dt className="font-medium text-gray-600 dark:text-gray-400">Response</dt>
                <dd className="text-gray-900 dark:text-white">{result.response}</dd>
              </div>
            )}
            {result.model && (
              <div>
                <dt className="font-medium text-gray-600 dark:text-gray-400">Model</dt>
                <dd className="text-gray-900 dark:text-white font-mono">{result.model}</dd>
              </div>
            )}
            {result.provider && (
              <div>
                <dt className="font-medium text-gray-600 dark:text-gray-400">Provider</dt>
                <dd className="text-gray-900 dark:text-white">{result.provider}</dd>
              </div>
            )}
            {result.tokens_used !== undefined && (
              <div>
                <dt className="font-medium text-gray-600 dark:text-gray-400">Tokens Used</dt>
                <dd className="text-gray-900 dark:text-white">{result.tokens_used}</dd>
              </div>
            )}
            {result.error && (
              <div>
                <dt className="font-medium text-gray-600 dark:text-gray-400">Error</dt>
                <dd className="text-red-700 dark:text-red-300 font-mono text-xs break-all">
                  {result.error}
                </dd>
              </div>
            )}
          </dl>
        </div>
      )}
    </div>
  );
}
