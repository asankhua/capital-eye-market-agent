import React, { useState } from 'react';
import { api } from '../api';
import { getErrorMessage } from '../error';
import type { AnalysisResponse } from '../types';
import { StockCard } from './StockCard';
import { Loader2, Plus, Bug } from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';

export const Dashboard: React.FC<{ type: 'analyze' | 'compare' | 'portfolio' }> = ({ type }) => {
  const [input1, setInput1] = useState('');
  const [input2, setInput2] = useState('');
  const [portfolioInputs, setPortfolioInputs] = useState<string[]>(['']);
  
  const [isLoading, setIsLoading] = useState(false);
  const [response, setResponse] = useState<AnalysisResponse | null>(null);
  const [error, setError] = useState('');
  const [debugLog, setDebugLog] = useState<string[]>([]);
  const [showDebug, setShowDebug] = useState(false);

  const addDebug = (msg: string) => {
    const timestamp = new Date().toLocaleTimeString('en-IN', { timeZone: 'Asia/Kolkata' });
    setDebugLog(prev => [`[${timestamp}] ${msg}`, ...prev].slice(0, 50));
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsLoading(true);
    setError('');
    setResponse(null);
    addDebug(`Starting ${type} analysis...`);

    try {
      if (type === 'analyze') {
        addDebug(`Analyzing stock: ${input1.trim()}`);
        const res = await api.analyzeStock({ stock: input1.trim() });
        addDebug(`Response received: ${JSON.stringify(res).substring(0, 200)}...`);
        addDebug(`Stocks in response: ${res.stocks?.length || 0}`);
        addDebug(`Recommendation: ${res.recommendation || 'N/A'}`);
        setResponse(res);
      } else if (type === 'compare') {
        addDebug(`Comparing: ${input1.trim()} vs ${input2.trim()}`);
        const res = await api.compareStocks({ stock_a: input1.trim(), stock_b: input2.trim() });
        addDebug(`Response received: ${JSON.stringify(res).substring(0, 200)}...`);
        addDebug(`Stocks compared: ${res.stocks?.length || 0}`);
        setResponse(res);
      } else if (type === 'portfolio') {
        const stocks = portfolioInputs.map(s => s.trim()).filter(s => s);
        addDebug(`Portfolio analysis for ${stocks.length} stocks: ${stocks.join(', ')}`);
        if (stocks.length === 0) throw new Error("Please enter at least one stock");
        const res = await api.portfolioAnalysis({ stocks });
        addDebug(`Response received: ${JSON.stringify(res).substring(0, 200)}...`);
        addDebug(`Stocks analyzed: ${res.stocks?.length || 0}`);
        setResponse(res);
      }
      addDebug('Analysis completed successfully');
    } catch (error: unknown) {
      const errMsg = getErrorMessage(error, 'Error fetching data');
      addDebug(`ERROR: ${errMsg}`);
      console.error('[Dashboard] analysis request failed', error);
      setError(errMsg);
    } finally {
      setIsLoading(false);
      addDebug('Request finished');
    }
  };

  const formStyles = {
    input: {
      padding: '12px 16px',
      borderRadius: '8px',
      border: '1px solid var(--border-color)',
      background: 'rgba(0,0,0,0.2)',
      color: 'inherit',
      fontSize: '15px',
      outline: 'none',
      fontFamily: 'inherit',
      width: '100%',
      minWidth: '200px'
    },
    button: {
      padding: '12px 24px',
      borderRadius: '8px',
      background: 'var(--accent-color)',
      color: '#fff',
      border: 'none',
      fontSize: '15px',
      fontWeight: 500,
      cursor: 'pointer',
      display: 'flex',
      alignItems: 'center',
      gap: '8px'
    }
  };

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '24px', height: '100%' }}>
      <div className="glass-panel" style={{ padding: '24px' }}>
        <h2 style={{ fontSize: '20px', marginBottom: '16px', fontWeight: 600 }}>
          {type === 'analyze' && 'Analyze Single Stock'}
          {type === 'compare' && 'Compare Stocks Head-to-Head'}
          {type === 'portfolio' && 'Analyze Portfolio'}
        </h2>
        
        <form onSubmit={handleSubmit} style={{ display: 'flex', gap: '16px', alignItems: 'flex-start', flexWrap: 'wrap' }}>
          {type === 'analyze' && (
            <input 
              style={formStyles.input} placeholder="Enter Ticker (e.g. AAPL)" 
              value={input1} onChange={e => setInput1(e.target.value)} required 
            />
          )}

          {type === 'compare' && (
            <>
              <input 
                style={formStyles.input} placeholder="Ticker 1 (e.g. AAPL)" 
                value={input1} onChange={e => setInput1(e.target.value)} required 
              />
              <span style={{ padding: '12px 0', opacity: 0.5 }}>VS</span>
              <input 
                style={formStyles.input} placeholder="Ticker 2 (e.g. MSFT)" 
                value={input2} onChange={e => setInput2(e.target.value)} required 
              />
            </>
          )}

          {type === 'portfolio' && (
            <div style={{ display: 'flex', flexDirection: 'column', gap: '8px', width: '100%', maxWidth: '300px' }}>
              {portfolioInputs.map((val, i) => (
                <div key={i} style={{ display: 'flex', gap: '8px' }}>
                  <input 
                    style={formStyles.input} placeholder={`Ticker ${i+1}`} 
                    value={val} onChange={e => {
                      const newVals = [...portfolioInputs];
                      newVals[i] = e.target.value;
                      setPortfolioInputs(newVals);
                    }}
                  />
                  {i === portfolioInputs.length - 1 && (
                    <button type="button" onClick={() => setPortfolioInputs([...portfolioInputs, ''])}
                      style={{...formStyles.button, background: 'rgba(255,255,255,0.1)', padding: '0 12px'}}>
                      <Plus size={16} />
                    </button>
                  )}
                </div>
              ))}
            </div>
          )}

          <motion.button 
            whileHover={{ scale: 1.02 }} whileTap={{ scale: 0.98 }}
            style={{...formStyles.button, marginTop: type === 'portfolio' ? 'auto' : 0}} 
            type="submit" disabled={isLoading}
          >
            {isLoading ? <Loader2 size={18} className="animate-spin" /> : 'Run Analysis'}
          </motion.button>
        </form>
      </div>

      <div style={{ flex: 1, overflowY: 'auto' }}>
        {error && (
          <div style={{ padding: '16px', background: 'rgba(239, 68, 68, 0.1)', color: 'var(--danger)', borderRadius: '12px', border: '1px solid var(--danger)' }}>
            {error}
          </div>
        )}

        {isLoading && (
          <div style={{ padding: '40px', display: 'flex', justifyContent: 'center' }}>
            <Loader2 size={40} className="animate-spin" color="var(--accent-color)" />
          </div>
        )}

        <AnimatePresence>
          {response && !isLoading && !error && (
            <motion.div initial={{opacity: 0, y: 20}} animate={{opacity: 1, y: 0}} style={{ display: 'flex', flexDirection: 'column', gap: '24px' }}>
              <div className="glass-panel" style={{ padding: '24px' }}>
                <h3 style={{ fontSize: '18px', marginBottom: '8px' }}>Verdict: <span style={{ color: 'var(--accent-color)'}}>{response.recommendation}</span></h3>
                <p style={{ color: 'var(--text-secondary)', lineHeight: 1.6 }}>{response.reasoning}</p>
              </div>

              {response.stocks.map(stock => (
                 <StockCard key={stock.stock} data={stock} />
              ))}
            </motion.div>
          )}
        </AnimatePresence>

        {/* Debug Panel */}
        <div style={{ marginTop: '32px', borderTop: '2px dashed var(--border-color)', paddingTop: '16px' }}>
          <button
            onClick={() => setShowDebug(!showDebug)}
            style={{
              display: 'flex',
              alignItems: 'center',
              gap: '8px',
              padding: '8px 16px',
              background: 'rgba(255,255,255,0.1)',
              border: 'none',
              borderRadius: '6px',
              cursor: 'pointer',
              fontSize: '12px',
              color: 'var(--text-secondary)',
            }}
          >
            <Bug size={14} />
            {showDebug ? 'Hide Debug Log' : 'Show Debug Log'}
          </button>
          
          {showDebug && (
            <div style={{
              marginTop: '12px',
              padding: '12px',
              background: '#1f2937',
              borderRadius: '8px',
              fontFamily: 'monospace',
              fontSize: '11px',
              color: '#10b981',
              maxHeight: '300px',
              overflowY: 'auto',
            }}>
              <div style={{ color: '#6b7280', marginBottom: '8px', borderBottom: '1px solid #374151', paddingBottom: '4px' }}>
                Debug Log ({debugLog.length} entries)
              </div>
              {debugLog.length === 0 ? (
                <span style={{ color: '#6b7280' }}>No debug messages yet. Run an analysis to see logs...</span>
              ) : (
                debugLog.map((log, i) => (
                  <div key={i} style={{ marginBottom: '4px', wordBreak: 'break-all' }}>{log}</div>
                ))
              )}
            </div>
          )}
        </div>
      </div>
    </div>
  );
};
