import express from 'express';
import cors from 'cors';
import { config } from './config.js';
import { authRouter } from './routes/auth.js';
import { documentsRouter } from './routes/documents.js';
import { extractionsRouter } from './routes/extractions.js';
import { reportsRouter } from './routes/reports.js';
import { financialsRouter } from './routes/financials.js';

const app = express();

// Global Middlewares
app.use(cors({ origin: config.corsOrigin, credentials: true }));
app.use(express.json());
app.use(express.urlencoded({ extended: true }));

// Health Check
app.get('/health', (_req, res) => {
  res.json({
    status: 'healthy',
    service: 'dca-bff',
    timestamp: new Date().toISOString(),
  });
});

// API Routes
app.use('/api/auth', authRouter);
app.use('/api/documents', documentsRouter);
app.use('/api/extractions', extractionsRouter);
app.use('/api/reports', reportsRouter);
app.use('/api/financials', financialsRouter);

// Start server
app.listen(config.port, () => {
  console.log(`🚀 DCA BFF service running on http://localhost:${config.port}`);
});

export default app;

