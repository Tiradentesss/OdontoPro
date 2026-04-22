const db = require('./config/database');

const correctHash = 'pbkdf2_sha256$1000000$4gazoTkeYLKIzfrLqSbMoR$2aArCCWphRsnnxzRe+YFZbGFAjD07EIgt+M6midszEk=';

db.query('UPDATE odontoPro_paciente SET senha = ? WHERE email = ?', [correctHash, 'aaa@gmail.com'], (err, result) => {
  if (err) {
    console.error('Error:', err);
  } else {
    console.log('Updated:', result.affectedRows);
  }
  // Verify
  db.query('SELECT email, senha FROM odontoPro_paciente WHERE email = ?', ['aaa@gmail.com'], (err2, results) => {
    console.log('Hash now:', results[0].senha);
    process.exit();
  });
});