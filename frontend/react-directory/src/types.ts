// TypeScript interfaces reflecting backend schemas

export type AnalysisType = 'single' | 'compare' | 'portfolio' | 'chat';
export type Recommendation = 'BUY' | 'HOLD' | 'SELL';

export interface FundamentalAnalysis {
  revenue: string;
  pe_ratio?: number;
  earnings_growth: string;
  market_cap: string;
  debt: string;
  profit_margin: string;
  score: number;
  summary: string;
}

export interface TechnicalAnalysis {
  rsi?: number;
  macd: string;
  ma50?: number;
  ma200?: number;
  trend: string;
  score: number;
  summary: string;
}

export interface SentimentAnalysis {
  positive_signals: string[];
  negative_signals: string[];
  score: number;
  summary: string;
}

export interface NewsArticle {
  title: string;
  publisher: string;
  link: string;
  publish_time: string;
  summary: string;
}

export interface StockAnalysis {
  stock: string;
  fundamental: FundamentalAnalysis;
  technical: TechnicalAnalysis;
  sentiment: SentimentAnalysis;
  news?: NewsArticle[];
}

export interface AnalysisResponse {
  analysis_type: AnalysisType;
  stocks: StockAnalysis[];
  recommendation: Recommendation;
  reasoning: string;
}

export interface AnalyzeStockRequest {
  stock: string;
}

export interface CompareStocksRequest {
  stock_a: string;
  stock_b: string;
}

export interface PortfolioRequest {
  stocks: string[];
}

export interface ChatRequest {
  query: string;
}

export interface IntentResponse {
  stocks: string[];
  analysis_type: string;
  parsed_query: string;
}

// ── Advanced Feature Types ─────────────────────────────────────────

export interface WatchlistItem {
  ticker: string;
  added_at: number;
  notes: string;
}

export interface HistoricalAnalysisResponse {
  ticker: string;
  history: Array<{
    analysis: unknown;
    created_at: number;
  }>;
  count: number;
}
