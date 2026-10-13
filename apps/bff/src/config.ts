import dotenv from 'dotenv';
import path from 'path';

dotenv.config({ path: path.resolve(__dirname, '../../../.env') });

export const config = {
  port: parseInt(process.env.BFF_PORT || '4000', 10),
  jwtSecret: process.env.JWT_SECRET || 'dev-secret-key-change-in-production',
  jwtExpiresIn: process.env.JWT_EXPIRES_IN || '1d',
  corsOrigin: process.env.CORS_ORIGIN || 'http://localhost:3000',
  databaseUrl: process.env.DATABASE_URL || 'postgresql://dca_user:dca_secure_password@localhost:5432/dca_db',
  processorUrl: `http://${process.env.PROCESSOR_HOST || 'localhost'}:${process.env.PROCESSOR_PORT || '8000'}`,
  uploadDir: path.resolve(__dirname, '../../uploads'),
};

