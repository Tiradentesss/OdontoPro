const mysql = require('mysql2');
require('dotenv').config();

const db = mysql.createConnection({
  host: process.env.DB_HOST,
  port: process.env.DB_PORT,
  user: process.env.DB_USER,
  password: process.env.DB_PASSWORD,
  database: process.env.DB_NAME,
  connectTimeout: 30000,
});

let connectionAttempts = 0;
const maxAttempts = 3;

const connect = () => {
  db.connect((err) => {
    if (err) {
      connectionAttempts++;
      console.error(`MySQL connection attempt ${connectionAttempts}/${maxAttempts} failed:`, err.code);
      if (connectionAttempts < maxAttempts) {
        setTimeout(connect, 5000);
      } else {
        console.error('Max connection attempts reached. Running in development mode with mock data.');
        process.env.USE_MOCK_DATA = 'true';
      }
      return;
    }
    console.log('Connected to MySQL database');
  });
};

db.on('error', (err) => {
  console.error('MySQL error:', err.code);
  if (err.code === 'PROTOCOL_CONNECTION_LOST') {
    connect();
  }
  if (err.code === 'ER_CON_COUNT_ERROR') {
    setTimeout(connect, 1000);
  }
});

connect();

module.exports = db;