import React, { useState } from 'react';
import { api } from '../api';
import { getErrorMessage } from '../error';
import type { AnalysisResponse, IntentResponse } from '../types';
import { Loader2, Send } from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';
import { StockCard } from './StockCard';

const ANALYSIS_TYPE_LABELS: Record<string, string> = {
  single: 'Single Stock Analysis',
  compare: 'Stock Comparison',
  portfolio: 'Portfolio Analysis',
};

const IntentBadges: React.FC<{ intent: IntentResponse }> = ({ intent }) => (
  <div style={{ display: 'flex', flexWrap: 'wrap', gap: '8px', marginBottom: '16px' }}>
    <span style={{
      padding: '4px 12px',
      borderRadius: '16px',
      fontSize: '13px',
      fontWeight: 600,
      background: '#dbeafe',
      color: '#1e40af',
      border: '1px solid #93c5fd',
    }}>
      {ANALYSIS_TYPE_LABELS[intent.analysis_type] || intent.analysis_type}
    </span>
    {intent.stocks.map(ticker => (
      <span key={ticker} style={{
        padding: '4px 12px',
        borderRadius: '16px',
        fontSize: '13px',
        fontWeight: 600,
        background: '#d1fae5',
        color: '#059669',
        border: '1px solid #6ee7b7',
      }}>
        {ticker}
      </span>
    ))}
    {intent.parsed_query && (
      <span style={{ fontSize: '12px', color: '#64748b', alignSelf: 'center' }}>
        Parsed: {intent.parsed_query}
      </span>
    )}
  </div>
);

export const ChatPanel: React.FC = () => {
  const [query, setQuery] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [loadingStage, setLoadingStage] = useState('');
  const [response, setResponse] = useState<AnalysisResponse | null>(null);
  const [intent, setIntent] = useState<IntentResponse | null>(null);
  const [error, setError] = useState('');

  const handleSend = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!query.trim()) return;

    setIsLoading(true);
    setError('');
    setResponse(null);
    setIntent(null);

    try {
      // Step 1: Parse intent to show detected stocks/type
      setLoadingStage('Understanding your query...');
      const intentResult = await api.parseIntent({ query });
      setIntent(intentResult);

      if (!intentResult.stocks || intentResult.stocks.length === 0) {
        setError('Could not identify any stocks in your query. Try mentioning specific stock names like Reliance, TCS, Infosys, etc.');
        setIsLoading(false);
        return;
      }

      // Step 2: Run full analysis
      setLoadingStage('Running analysis...');
      const res = await api.chat({ query });
      setResponse(res);
    } catch (error: unknown) {
      console.error('[ChatPanel] request failed', error);
      const errorMsg = getErrorMessage(error, 'Error communicating with AI');
      setError(errorMsg);
    } finally {
      setIsLoading(false);
      setLoadingStage('');
    }
  };

  return (
    <div style={{ display: 'flex', flexDirection: 'column', height: '100%', gap: '12px' }}>

      {/* Response Area */}
      <div style={{ flex: 1, overflowY: 'auto', display: 'flex', flexDirection: 'column', gap: '16px' }}>
        {!response && !isLoading && !error && !intent && (
          <div style={{ display: 'flex', flexDirection: 'column', gap: '16px', height: '100%' }}>
            {/* Welcome Card */}
            <div style={{ 
              margin: 'auto', 
              textAlign: 'center', 
              padding: '40px',
              background: '#ffffff',
              borderRadius: '16px',
              border: '1px solid #e2e8f0',
            }}>
              <h3 style={{ fontSize: '24px', fontWeight: 700, color: '#0f172a', marginBottom: '12px' }}>
                Welcome to CapitalEye Pro
              </h3>
              <p style={{ fontSize: '16px', color: '#64748b', marginBottom: '8px' }}>
                Professional AI-Powered Market Analysis
              </p>
              <p style={{ fontSize: '14px', color: '#94a3b8' }}>
                Ask about stocks like "How is Reliance doing?" or "Compare TCS and Infosys"
              </p>
            </div>
          </div>
        )}

        {isLoading && (
          <div style={{ margin: 'auto', display: 'flex', flexDirection: 'column', alignItems: 'center', gap: '12px' }}>
            {intent && <IntentBadges intent={intent} />}
            <Loader2 size={32} className="animate-spin" color="#2563eb" />
            <p style={{ color: '#64748b' }}>{loadingStage}</p>
          </div>
        )}

        {error && (
          <motion.div initial={{opacity:0}} animate={{opacity:1}}>
            {intent && <IntentBadges intent={intent} />}
            <div style={{ padding: '16px', background: '#fee2e2', color: '#dc2626', borderRadius: '12px', border: '1px solid #fecaca' }}>
              {error}
            </div>
          </motion.div>
        )}

        <AnimatePresence>
          {response && (
            <motion.div
              initial={{opacity: 0, y: 20}} animate={{opacity: 1, y: 0}}
              style={{ display: 'flex', flexDirection: 'column', gap: '16px' }}
            >
              {intent && <IntentBadges intent={intent} />}

              <div style={{ 
                padding: '20px', 
                background: '#ffffff',
                borderRadius: '12px',
                border: '1px solid #e2e8f0',
                boxShadow: '0 1px 3px 0 rgba(0, 0, 0, 0.1)',
              }}>
                <h3 style={{ fontSize: '18px', marginBottom: '8px', fontWeight: 600 }}>
                  AI Recommendation: <span style={{ color: '#2563eb' }}>{response.recommendation}</span>
                </h3>
                <p style={{ color: '#475569', lineHeight: 1.6 }}>{response.reasoning}</p>
              </div>

              {response.stocks.map(stock => (
                <StockCard key={stock.stock} data={stock} />
              ))}
            </motion.div>
          )}
        </AnimatePresence>
      </div>

      {/* Input Area */}
      <form onSubmit={handleSend} style={{ position: 'relative', marginTop: '16px' }}>
        <input
          type="text"
          value={query}
          onChange={(e) => {
            setQuery(e.target.value);
          }}
          placeholder="Ask about stocks, market trends, or get analysis..."
          style={{
            width: '100%',
            padding: '16px 50px 16px 20px',
            fontSize: '16px',
            border: '1px solid #e2e8f0',
            borderRadius: '12px',
            color: '#0f172a',
            background: '#ffffff',
            outline: 'none',
            boxShadow: '0 1px 3px 0 rgba(0, 0, 0, 0.1)',
          }}
          disabled={isLoading}
        />
        <button
          type="submit"
          disabled={!query.trim() || isLoading}
          style={{
            position: 'absolute',
            right: '8px',
            top: '8px',
            bottom: '8px',
            width: '40px',
            background: query.trim() && !isLoading ? '#2563eb' : 'transparent',
            border: 'none',
            borderRadius: '10px',
            color: query.trim() && !isLoading ? '#fff' : '#94a3b8',
            cursor: query.trim() && !isLoading ? 'pointer' : 'not-allowed',
            transition: 'all 0.2s',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center'
          }}
        >
          {isLoading ? <Loader2 size={18} className="animate-spin" /> : <Send size={18} />}
        </button>
      </form>
    </div>
  );
};
