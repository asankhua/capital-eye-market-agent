import jsPDF from 'jspdf';
import 'jspdf-autotable';
import * as XLSX from 'xlsx';
import type { AnalysisResponse } from './types';

declare module 'jspdf' {
  interface jsPDF {
    autoTable: (options: unknown) => jsPDF;
  }
}

export const exportToPDF = (data: AnalysisResponse, filename: string = 'analysis-report') => {
  const doc = new jsPDF();
  
  // Title
  doc.setFontSize(20);
  doc.text('AI Market Analyst Report', 14, 20);
  
  // Date
  doc.setFontSize(10);
  doc.text(`Generated: ${new Date().toLocaleString()}`, 14, 30);
  
  // Recommendation
  doc.setFontSize(14);
  doc.text(`Recommendation: ${data.recommendation}`, 14, 45);
  
  // Reasoning
  doc.setFontSize(11);
  const reasoningLines = doc.splitTextToSize(data.reasoning, 180);
  doc.text(reasoningLines, 14, 55);
  
  let yPos = 55 + (reasoningLines.length * 5) + 10;
  
  // Stock analysis for each stock
  data.stocks.forEach((stock) => {
    if (yPos > 250) {
      doc.addPage();
      yPos = 20;
    }
    
    doc.setFontSize(16);
    doc.text(`${stock.stock} Analysis`, 14, yPos);
    yPos += 10;
    
    // Fundamental
    doc.setFontSize(12);
    doc.text('Fundamental Analysis', 14, yPos);
    yPos += 6;
    doc.setFontSize(10);
    doc.text(`Score: ${stock.fundamental.score}/10`, 14, yPos);
    yPos += 5;
    const fundLines = doc.splitTextToSize(stock.fundamental.summary, 180);
    doc.text(fundLines, 14, yPos);
    yPos += fundLines.length * 4 + 8;
    
    // Technical
    doc.setFontSize(12);
    doc.text('Technical Analysis', 14, yPos);
    yPos += 6;
    doc.setFontSize(10);
    doc.text(`Score: ${stock.technical.score}/10 | Trend: ${stock.technical.trend}`, 14, yPos);
    yPos += 5;
    const techLines = doc.splitTextToSize(stock.technical.summary, 180);
    doc.text(techLines, 14, yPos);
    yPos += techLines.length * 4 + 8;
    
    // Sentiment
    doc.setFontSize(12);
    doc.text('Sentiment Analysis', 14, yPos);
    yPos += 6;
    doc.setFontSize(10);
    doc.text(`Score: ${stock.sentiment.score}/10`, 14, yPos);
    yPos += 5;
    const sentLines = doc.splitTextToSize(stock.sentiment.summary, 180);
    doc.text(sentLines, 14, yPos);
    yPos += sentLines.length * 4 + 15;
  });
  
  doc.save(`${filename}.pdf`);
};

export const exportToExcel = (data: AnalysisResponse, filename: string = 'analysis-report') => {
  const workbook = XLSX.utils.book_new();
  
  // Summary sheet
  const summaryData = [
    ['AI Market Analyst Report'],
    ['Generated', new Date().toLocaleString()],
    ['Analysis Type', data.analysis_type],
    ['Recommendation', data.recommendation],
    ['Reasoning', data.reasoning],
    [],
    ['Stocks Analyzed', data.stocks.map((s: { stock: string }) => s.stock).join(', ')],
  ];
  
  const summarySheet = XLSX.utils.aoa_to_sheet(summaryData);
  XLSX.utils.book_append_sheet(workbook, summarySheet, 'Summary');
  
  // Stock details sheet
  const stockDetails = data.stocks.map((stock: typeof data.stocks[0]) => ({
    'Stock': stock.stock,
    'Fundamental Score': stock.fundamental.score,
    'P/E Ratio': stock.fundamental.pe_ratio || 'N/A',
    'Profit Margin': stock.fundamental.profit_margin,
    'Earnings Growth': stock.fundamental.earnings_growth,
    'Debt': stock.fundamental.debt,
    'Technical Score': stock.technical.score,
    'RSI': stock.technical.rsi || 'N/A',
    'Trend': stock.technical.trend,
    'MACD': stock.technical.macd,
    'Sentiment Score': stock.sentiment.score,
    'Positive Signals': stock.sentiment.positive_signals.join(', ') || 'None',
    'Negative Signals': stock.sentiment.negative_signals.join(', ') || 'None',
  }));
  
  const stockSheet = XLSX.utils.json_to_sheet(stockDetails);
  XLSX.utils.book_append_sheet(workbook, stockSheet, 'Stock Details');
  
  // Save
  XLSX.writeFile(workbook, `${filename}.xlsx`);
};
