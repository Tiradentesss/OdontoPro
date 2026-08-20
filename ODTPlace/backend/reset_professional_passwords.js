const bcrypt = require('bcrypt');
const db = require('./config/database');

const email = process.argv[2];
const password = process.argv[3];

if (!email || !password) {
  console.log('Uso: node reset_professional_passwords.js <email> <nova_senha>');
  console.log('Exemplo: node reset_professional_passwords.js ana@gmail.com "Odonto@2026"');
  process.exit(1);
}

const hash = bcrypt.hashSync(password, 10);
const query = 'UPDATE odontoPro_medico SET senha = ? WHERE email = ? AND ativo = 1';

db.query(query, [hash, email], (err, result) => {
  if (err) {
    console.error('Erro ao atualizar senha do profissional:', err.message);
    process.exit(1);
  }

  if (result.affectedRows === 0) {
    console.log(`Nenhum profissional encontrado para o email: ${email}`);
    process.exit(1);
  }

  console.log(`Senha atualizada com sucesso para ${email}.`);
  console.log('Nova senha temporária: ' + password);
  db.end();
});
