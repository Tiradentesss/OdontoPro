const path = require('path');
const mysql = require('mysql2');
require('dotenv').config({
  path: path.resolve(__dirname, '../../.env'),
});

const useSsl = process.env.DB_SSL === 'true';

const db = mysql.createPool({
  host: process.env.DB_HOST?.trim(),
  port: Number(process.env.DB_PORT),
  user: process.env.DB_USER?.trim(),
  password: process.env.DB_PASSWORD,
  database: process.env.DB_NAME?.trim(),
  ...(useSsl && {
    ssl: {
      rejectUnauthorized: process.env.DB_SSL_REJECT_UNAUTHORIZED !== 'false',
    },
  }),
  waitForConnections: true,
  connectionLimit: 10,
  queueLimit: 0,
  connectTimeout: 10000,
});

db.getConnection((err, connection) => {
  if (err) {
    console.error('Initial MySQL connection check failed:', err.code, err.message);
    return;
  }

  console.log('Connected to MySQL database');
  connection.release();
});

module.exports = db;