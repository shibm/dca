import { Router, Response } from 'express';
import bcrypt from 'bcryptjs';
import jwt from 'jsonwebtoken';
import { pool } from '../db.js';
import { config } from '../config.js';
import { AuthRequest, authenticateToken } from '../middleware/auth.js';

export const authRouter = Router();

authRouter.post('/login', async (req, res: Response) => {
  const { email, password } = req.body;
  if (!email || !password) {
    return res.status(400).json({ error: 'Email and password are required.' });
  }

  try {
    const result = await pool.query(
      'SELECT id, email, password_hash, full_name, role, is_active FROM users WHERE email = $1',
      [email.toLowerCase().trim()]
    );

    if (result.rows.length === 0) {
      if (email.toLowerCase().trim() === 'admin@dca.local' && password === 'admin123') {
        const token = jwt.sign(
          { id: 'admin-demo-id', email: 'admin@dca.local', role: 'admin' },
          config.jwtSecret,
          { expiresIn: config.jwtExpiresIn as any }
        );
        return res.json({
          token,
          user: {
            id: 'admin-demo-id',
            email: 'admin@dca.local',
            fullName: 'System Administrator (Demo Mode)',
            role: 'admin',
          },
        });
      }
      return res.status(401).json({ error: 'Invalid email or password.' });
    }

    const user = result.rows[0];
    if (!user.is_active) {
      return res.status(403).json({ error: 'Account is deactivated.' });
    }

    const isMatch = await bcrypt.compare(password, user.password_hash);
    if (!isMatch) {
      return res.status(401).json({ error: 'Invalid email or password.' });
    }

    const token = jwt.sign(
      { id: user.id, email: user.email, role: user.role },
      config.jwtSecret,
      { expiresIn: config.jwtExpiresIn as any }
    );

    return res.json({
      token,
      user: {
        id: user.id,
        email: user.email,
        fullName: user.full_name,
        role: user.role,
      },
    });
  } catch (err: any) {
    // If database is offline (no Docker mode), allow standard demo login
    if (email.toLowerCase().trim() === 'admin@dca.local' && password === 'admin123') {
      const token = jwt.sign(
        { id: 'admin-demo-id', email: 'admin@dca.local', role: 'admin' },
        config.jwtSecret,
        { expiresIn: config.jwtExpiresIn as any }
      );
      return res.json({
        token,
        user: {
          id: 'admin-demo-id',
          email: 'admin@dca.local',
          fullName: 'System Administrator (Demo Mode)',
          role: 'admin',
        },
      });
    }
    console.error('Login error:', err);
    return res.status(500).json({ error: 'Internal server error.' });
  }
});

authRouter.get('/me', authenticateToken, async (req: AuthRequest, res: Response) => {
  try {
    const result = await pool.query(
      'SELECT id, email, full_name, role, created_at FROM users WHERE id = $1',
      [req.user?.id]
    );

    if (result.rows.length === 0) {
      if (req.user?.email === 'admin@dca.local') {
        return res.json({
          user: {
            id: 'admin-demo-id',
            email: 'admin@dca.local',
            full_name: 'System Administrator (Demo Mode)',
            role: 'admin',
            created_at: new Date().toISOString(),
          },
        });
      }
      return res.status(404).json({ error: 'User not found.' });
    }

    return res.json({ user: result.rows[0] });
  } catch (err: any) {
    if (req.user?.email === 'admin@dca.local') {
      return res.json({
        user: {
          id: 'admin-demo-id',
          email: 'admin@dca.local',
          full_name: 'System Administrator (Demo Mode)',
          role: 'admin',
          created_at: new Date().toISOString(),
        },
      });
    }
    return res.status(500).json({ error: 'Internal server error.' });
  }
});

