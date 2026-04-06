import React from 'react';
import {
  AreaChart,
  Area,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  ReferenceLine,
} from 'recharts';
import type { TechnicalAnalysis } from '../types';

interface StockChartProps {
  stock: string;
  technical: TechnicalAnalysis;
}

// Generate mock price data based on trend and levels
const generateMockData = (trend: string, ma50?: number, ma200?: number) => {
  const data = [];
  const days = 30;
  const basePrice = ma50 || 100;
  const trendMultiplier = trend.toLowerCase().includes('bull') ? 1 : trend.toLowerCase().includes('bear') ? -1 : 0;
  
  for (let i = 0; i < days; i++) {
    const day = new Date();
    day.setDate(day.getDate() - (days - i));
    
    // Generate price with some randomness and trend
    const randomWalk = (Math.random() - 0.5) * basePrice * 0.02;
    const trendComponent = trendMultiplier * (i / days) * basePrice * 0.05;
    const price = basePrice + randomWalk + trendComponent;
    
    data.push({
      date: day.toLocaleDateString('en-US', { month: 'short', day: 'numeric' }),
      price: Math.round(price * 100) / 100,
      ma50: ma50,
      ma200: ma200,
    });
  }
  return data;
};

export const StockChart: React.FC<StockChartProps> = ({ stock, technical }) => {
  const { trend, ma50, ma200 } = technical;
  const data = generateMockData(trend, ma50, ma200);

  const getTrendColor = () => {
    if (trend.toLowerCase().includes('bull')) return '#10b981';
    if (trend.toLowerCase().includes('bear')) return '#ef4444';
    return '#6366f1';
  };

  return (
    <div style={{ width: '100%', height: '200px', marginTop: '16px' }}>
      <ResponsiveContainer width="100%" height="100%">
        <AreaChart data={data} margin={{ top: 5, right: 5, left: 0, bottom: 5 }}>
          <defs>
            <linearGradient id={`gradient-${stock}`} x1="0" y1="0" x2="0" y2="1">
              <stop offset="5%" stopColor={getTrendColor()} stopOpacity={0.3} />
              <stop offset="95%" stopColor={getTrendColor()} stopOpacity={0} />
            </linearGradient>
          </defs>
          <CartesianGrid strokeDasharray="3 3" stroke="var(--border-color)" opacity={0.5} />
          <XAxis 
            dataKey="date" 
            tick={{ fill: 'var(--text-secondary)', fontSize: 10 }}
            tickLine={false}
            axisLine={{ stroke: 'var(--border-color)' }}
            minTickGap={30}
          />
          <YAxis 
            tick={{ fill: 'var(--text-secondary)', fontSize: 10 }}
            tickLine={false}
            axisLine={{ stroke: 'var(--border-color)' }}
            domain={['auto', 'auto']}
            tickFormatter={(value) => `₹${value}`}
          />
          <Tooltip
            contentStyle={{
              background: 'var(--bg-surface)',
              border: '1px solid var(--border-color)',
              borderRadius: '8px',
              fontSize: '12px',
            }}
            labelStyle={{ color: 'var(--text-secondary)' }}
            itemStyle={{ color: 'var(--text-primary)' }}
            formatter={(value) => [`₹${value || 0}`, 'Price']}
          />
          {ma50 && (
            <ReferenceLine 
              y={ma50} 
              stroke="#f59e0b" 
              strokeDasharray="5 5" 
              label={{ value: 'MA50', fill: '#f59e0b', fontSize: 10, position: 'right' }}
            />
          )}
          {ma200 && (
            <ReferenceLine 
              y={ma200} 
              stroke="#8b5cf6" 
              strokeDasharray="5 5" 
              label={{ value: 'MA200', fill: '#8b5cf6', fontSize: 10, position: 'right' }}
            />
          )}
          <Area
            type="monotone"
            dataKey="price"
            stroke={getTrendColor()}
            strokeWidth={2}
            fill={`url(#gradient-${stock})`}
            animationDuration={1000}
          />
        </AreaChart>
      </ResponsiveContainer>
      <div style={{ display: 'flex', gap: '16px', marginTop: '8px', fontSize: '11px', color: 'var(--text-secondary)' }}>
        {ma50 && (
          <span style={{ display: 'flex', alignItems: 'center', gap: '4px' }}>
            <span style={{ width: '8px', height: '2px', background: '#f59e0b' }} /> MA50: ₹{ma50}
          </span>
        )}
        {ma200 && (
          <span style={{ display: 'flex', alignItems: 'center', gap: '4px' }}>
            <span style={{ width: '8px', height: '2px', background: '#8b5cf6' }} /> MA200: ₹{ma200}
          </span>
        )}
      </div>
    </div>
  );
};
