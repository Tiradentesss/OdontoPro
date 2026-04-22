const db = require('./config/database');
const crypto = require('crypto');

const email = 'aaa@gmail.com';
const senha = '123';

const query = 'SELECT id, nome, email, telefone, cpf, data_nascimento, sexo, foto, senha FROM odontoPro_paciente WHERE email = ? AND ativo = 1';
db.query(query, [email], (err, results) => {
  if (err) {
    console.error('Database error:', err);
    process.exit();
  }
  if (results.length === 0) {
    console.log('No user found');
    process.exit();
  }
  
  const user = results[0];
  console.log('User found:', user.email);
  console.log('Stored hash:', user.senha);
  
  // Test password
  const storedHash = user.senha;
  const parts = storedHash.split('$');
  const iterations = parseInt(parts[1]);
  const salt = parts[2];
  const expectedHash = parts[3];
  
  const derived = crypto.pbkdf2Sync(senha, salt, iterations, 32, 'sha256');
  const computedHash = derived.toString('base64');
  
  console.log('Match:', computedHash === expectedHash);
  process.exit();
});