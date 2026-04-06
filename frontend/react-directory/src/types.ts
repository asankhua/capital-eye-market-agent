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

export interface ScreenerRequest {
  min_pe?: number;
  max_pe?: number;
  min_market_cap?: number;
  min_profit_margin?: number;
  max_debt_to_equity?: number;
  min_roe?: number;
  sector?: string;
  limit: number;
}

export interface ScreenerResult {
  ticker: string;
  company_name: string;
  pe_ratio?: number;
  market_cap?: number;
  profit_margin?: number;
  debt_to_equity?: number;
  roe?: number;
  current_price?: number;
  sector: string;
}

export interface ScreenerResponse {
  results: ScreenerResult[];
  count: number;
  criteria: Record<string, unknown>;
}

export interface RiskMetricsRequest {
  tickers: string[];
  period: string;
}

export interface SharpeRatio {
  ticker: string;
  sharpe_ratio?: number;
  annual_return?: number;
  annual_volatility?: number;
  error?: string;
}

export interface BetaMetrics {
  ticker: string;
  beta?: number;
  correlation?: number;
  market_index: string;
  interpretation: string;
  error?: string;
}

export interface VaRMetrics {
  ticker: string;
  var_daily_percent?: number;
  var_amount?: number;
  confidence: number;
  current_price?: number;
  interpretation: string;
  error?: string;
}

export interface RiskMetricsResponse {
  sharpe_ratios: SharpeRatio[];
  betas: BetaMetrics[];
  var_metrics: VaRMetrics[];
}

export interface CorrelationRequest {
  tickers: string[];
  period: string;
}

export interface CorrelationResponse {
  tickers: string[];
  matrix: Record<string, Record<string, number | null>>;
  period: string;
  data_points: number;
}

export interface EarningsInfo {
  ticker: string;
  earnings_date?: string;
  eps_estimate?: number;
  revenue_estimate?: number;
  eps_actual?: number;
  forward_eps?: number;
  next_earnings?: string;
  error?: string;
}

export interface EarningsCalendarResponse {
  earnings: EarningsInfo[];
  days_ahead: number;
}

export interface DividendInfo {
  ticker: string;
  dividend_rate?: number;
  dividend_yield?: number;
  ex_dividend_date?: string;
  payout_ratio?: number;
  five_year_avg_yield?: number;
  history: Array<{
    ex_date: string;
    payment_date?: string;
    amount: number;
    yield_percent?: number;
  }>;
  error?: string;
}

export interface HistoricalAnalysisResponse {
  ticker: string;
  history: Array<{
    analysis: unknown;
    created_at: number;
  }>;
  count: number;
}

export interface ExportRequest {
  ticker: string;
  format: 'pdf' | 'csv' | 'json';
}
