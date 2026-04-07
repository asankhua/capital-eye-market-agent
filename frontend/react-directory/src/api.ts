import axios from 'axios';
import { debugLogger } from './debug-logger';
import type {
  AnalysisResponse,
  AnalyzeStockRequest,
  CompareStocksRequest,
  IntentResponse,
  PortfolioRequest,
  ChatRequest,
  WatchlistItem,
  ScreenerRequest,
  ScreenerResponse,
  RiskMetricsRequest,
  RiskMetricsResponse,
  CorrelationRequest,
  CorrelationResponse,
  EarningsInfo,
  EarningsCalendarResponse,
  DividendInfo,
  HistoricalAnalysisResponse,
  ExportRequest
} from './types';

const API_BASE_URL = import.meta.env.VITE_API_URL || '';

const apiClient = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Add request/response interceptors for logging
apiClient.interceptors.request.use((config) => {
  (config as unknown as Record<string, unknown>).startTime = Date.now();
  return config;
});

apiClient.interceptors.response.use(
  (response) => {
    const config = response.config as unknown as Record<string, unknown>;
    const duration = Date.now() - (config.startTime as number || 0);
    const url = (config.url as string) || 'unknown';
    debugLogger.logApiResponse(url, response.data, duration);
    return response;
  },
  (error) => {
    if (error.config) {
      const config = error.config as unknown as Record<string, unknown>;
      const duration = Date.now() - (config.startTime as number || 0);
      const url = (config.url as string) || 'unknown';
      debugLogger.logApiError(url, error.message, duration);
    }
    return Promise.reject(error);
  }
);

export const api = {
  analyzeStock: async (request: AnalyzeStockRequest): Promise<AnalysisResponse> => {
    debugLogger.logApiRequest('/analyze_stock', request);
    const response = await apiClient.post<AnalysisResponse>('/analyze_stock', request);
    return response.data;
  },

  compareStocks: async (request: CompareStocksRequest): Promise<AnalysisResponse> => {
    debugLogger.logApiRequest('/compare_stocks', request);
    const response = await apiClient.post<AnalysisResponse>('/compare_stocks', request);
    return response.data;
  },

  portfolioAnalysis: async (request: PortfolioRequest): Promise<AnalysisResponse> => {
    debugLogger.logApiRequest('/portfolio_analysis', request);
    const response = await apiClient.post<AnalysisResponse>('/portfolio_analysis', request);
    return response.data;
  },

  chat: async (request: ChatRequest): Promise<AnalysisResponse> => {
    debugLogger.logApiRequest('/chat', request);
    const response = await apiClient.post<AnalysisResponse>('/chat', request);
    return response.data;
  },

  parseIntent: async (request: ChatRequest): Promise<IntentResponse> => {
    debugLogger.logApiRequest('/parse_intent', request);
    const response = await apiClient.post<IntentResponse>('/parse_intent', request);
    return response.data;
  },

  // ── Watchlist API ─────────────────────────────────────────────────
  getWatchlist: async (): Promise<WatchlistItem[]> => {
    debugLogger.logApiRequest('/watchlist', {});
    const response = await apiClient.get<WatchlistItem[]>('/watchlist');
    return response.data;
  },

  addToWatchlist: async (ticker: string, notes: string = ''): Promise<{success: boolean; ticker: string}> => {
    debugLogger.logApiRequest(`/watchlist/${ticker}`, { notes });
    const response = await apiClient.post(`/watchlist/${ticker}`, null, { params: { notes } });
    return response.data;
  },

  removeFromWatchlist: async (ticker: string): Promise<{success: boolean; ticker: string}> => {
    debugLogger.logApiRequest(`DELETE /watchlist/${ticker}`, {});
    const response = await apiClient.delete(`/watchlist/${ticker}`);
    return response.data;
  },

  // ── Stock Screener API ────────────────────────────────────────────
  screenStocks: async (request: ScreenerRequest): Promise<ScreenerResponse> => {
    debugLogger.logApiRequest('/screener', request);
    const response = await apiClient.post<ScreenerResponse>('/screener', request);
    return response.data;
  },

  // ── Risk Metrics API ──────────────────────────────────────────────
  getRiskMetrics: async (request: RiskMetricsRequest): Promise<RiskMetricsResponse> => {
    debugLogger.logApiRequest('/risk_metrics', request);
    const response = await apiClient.post<RiskMetricsResponse>('/risk_metrics', request);
    return response.data;
  },

  // ── Correlation API ──────────────────────────────────────────────
  getCorrelation: async (request: CorrelationRequest): Promise<CorrelationResponse> => {
    debugLogger.logApiRequest('/correlation', request);
    const response = await apiClient.post<CorrelationResponse>('/correlation', request);
    return response.data;
  },

  // ── Earnings API ─────────────────────────────────────────────────
  getEarnings: async (ticker: string): Promise<EarningsInfo> => {
    debugLogger.logApiRequest(`/earnings/${ticker}`, {});
    const response = await apiClient.get<EarningsInfo>(`/earnings/${ticker}`);
    return response.data;
  },

  getEarningsCalendar: async (days: number = 30): Promise<EarningsCalendarResponse> => {
    debugLogger.logApiRequest('/earnings_calendar', { days });
    const response = await apiClient.get<EarningsCalendarResponse>('/earnings_calendar', { params: { days } });
    return response.data;
  },

  // ── Dividend API ──────────────────────────────────────────────────
  getDividends: async (ticker: string): Promise<DividendInfo> => {
    debugLogger.logApiRequest(`/dividends/${ticker}`, {});
    const response = await apiClient.get<DividendInfo>(`/dividends/${ticker}`);
    return response.data;
  },

  // ── NSE Dividend API ─────────────────────────────────────────────
  getMoneyControlDividends: async (ticker?: string): Promise<DividendInfo & { source: string }> => {
    debugLogger.logApiRequest('/nse/dividends', { ticker });
    const response = await apiClient.get('/nse/dividends', { params: { ticker } });
    return response.data;
  },

  // ── Get All NSE Dividends ─────────────────────────────────────────
  getAllMoneyControlDividends: async (): Promise<{ announcements: any[], count: number, search_date: string, source: string }> => {
    debugLogger.logApiRequest('/nse/dividends', {});
    const response = await apiClient.get('/nse/dividends');
    return response.data;
  },

  // ── Historical Analysis API ──────────────────────────────────────
  getHistoricalAnalysis: async (ticker: string, limit: number = 30): Promise<HistoricalAnalysisResponse> => {
    debugLogger.logApiRequest(`/historical/${ticker}`, { limit });
    const response = await apiClient.get<HistoricalAnalysisResponse>(`/historical/${ticker}`, { params: { limit } });
    return response.data;
  },

  // ── Export API ───────────────────────────────────────────────────
  exportReport: async (request: ExportRequest): Promise<Blob> => {
    debugLogger.logApiRequest('/export', request);
    const response = await apiClient.post('/export', request, { responseType: 'blob' });
    return response.data;
  },

  // ── Finnhub API ───────────────────────────────────────────────────
  getFinnhubEarningsCalendar: async (fromDate?: string, toDate?: string, symbol?: string): Promise<{earnings: any[], count: number}> => {
    debugLogger.logApiRequest('/finnhub/earnings_calendar', { fromDate, toDate, symbol });
    const response = await apiClient.get('/finnhub/earnings_calendar', { params: { from_date: fromDate, to_date: toDate, symbol } });
    return response.data;
  },

  getFinnhubMarketMovers: async (type: string = 'gainers'): Promise<{movers: any[], type: string, count: number}> => {
    debugLogger.logApiRequest('/finnhub/market_movers', { type });
    const response = await apiClient.get('/finnhub/market_movers', { params: { type } });
    return response.data;
  },

  getFinnhubNews: async (category: string = 'general', symbol?: string): Promise<{news: any[], count: number}> => {
    debugLogger.logApiRequest('/finnhub/news', { category, symbol });
    const response = await apiClient.get('/finnhub/news', { params: { category, symbol } });
    return response.data;
  },

  getFinnhubSectorPerformance: async (): Promise<{sectors: any[], count: number}> => {
    debugLogger.logApiRequest('/finnhub/sector_performance', {});
    const response = await apiClient.get('/finnhub/sector_performance');
    return response.data;
  },

  // ── NSE Market Movers API ─────────────────────────────────────────
  getNSEMarketMovers: async (type: string = 'gainers'): Promise<{movers: any[], type: string, count: number, source: string}> => {
    debugLogger.logApiRequest('/twelve_data/market_movers', { type });
    const response = await apiClient.get('/twelve_data/market_movers', { params: { type } });
    return response.data;
  },

  // ── NSE Sector API ───────────────────────────────────────────────
  getNSESectorPerformance: async (): Promise<{sectors: any[], count: number, source: string}> => {
    debugLogger.logApiRequest('/finnhub/sector_performance', {});
    const response = await apiClient.get('/finnhub/sector_performance');
    return response.data;
  },
  getTwelveDataMarketOverview: async (): Promise<any> => {
    debugLogger.logApiRequest('/twelve_data/market_overview', {});
    const response = await apiClient.get('/twelve_data/market_overview');
    return response.data;
  },

  getTwelveDataIndices: async (): Promise<{indices: any[], count: number}> => {
    debugLogger.logApiRequest('/twelve_data/indices', {});
    const response = await apiClient.get('/twelve_data/indices');
    return response.data;
  },

  getTwelveDataMarketMovers: async (type: string = 'gainers'): Promise<{movers: any[], type: string, count: number}> => {
    debugLogger.logApiRequest('/twelve_data/market_movers', { type });
    const response = await apiClient.get('/twelve_data/market_movers', { params: { type } });
    return response.data;
  },

  // ── Indian Stock News API ──────────────────────────────────────────
  getIndianMarketNews: async (max_results: number = 10): Promise<{news: any[], count: number, source: string}> => {
    debugLogger.logApiRequest('/indian_news/market', { max_results });
    const response = await apiClient.get('/indian_news/market', { params: { max_results } });
    return response.data;
  },

  getIndianCompanyNews: async (symbol: string, max_results: number = 5): Promise<{symbol: string, news: any[], count: number, source: string}> => {
    debugLogger.logApiRequest(`/indian_news/company/${symbol}`, { max_results });
    const response = await apiClient.get(`/indian_news/company/${symbol}`, { params: { max_results } });
    return response.data;
  },

  getIndianCategoryNews: async (category: string, max_results: number = 10): Promise<{news: any[], count: number, category: string, source: string}> => {
    debugLogger.logApiRequest(`/indian_news/category/${category}`, { max_results });
    const response = await apiClient.get(`/indian_news/category/${category}`, { params: { max_results } });
    return response.data;
  },
};
