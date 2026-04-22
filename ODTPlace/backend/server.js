require('dotenv').config();

const express = require('express');
const cors = require('cors');
const bcrypt = require('bcrypt');
const crypto = require('crypto');
const db = require('./config/database');

// Helper function: only accept Django PBKDF2 hash
function verifyPassword(inputPassword, storedHash) {
  if (!storedHash.startsWith('pbkdf2_sha256')) return Promise.resolve(false);
  const parts = storedHash.split('$');
  if (parts.length !== 4) return Promise.resolve(false);
  const iterations = parseInt(parts[1]);
  const salt = parts[2];
  const expectedHash = parts[3];
  const derived = crypto.pbkdf2Sync(inputPassword, salt, iterations, 32, 'sha256');
  const computedHash = derived.toString('base64');
  return Promise.resolve(computedHash === expectedHash);
}

// Debug: Check if .env is loaded
console.log('DB_HOST:', process.env.DB_HOST);
console.log('USE_MOCK_DATA:', process.env.USE_MOCK_DATA);

const app = express();
const PORT = process.env.PORT || 3001;

app.use(cors());
app.use(express.json());

// Mock data for development
const mockClinics = [
  { id: 1, nome: 'Clínica Sorriso Vivo', descricao: 'Clínica com equipamentos modernos', telefone: '(91) 98132-2686', preco: 'R$ 250,00', avaliacao: 5, num_avaliacoes: 83 },
  { id: 2, nome: 'Odonto Plus', descricao: 'Especializada em ortodontia', telefone: '(91) 3211-5000', preco: 'R$ 200,00', avaliacao: 4.8, num_avaliacoes: 45 },
];

const mockDoctors = [
  { id: 1, nome: 'Dr. Lucas Castro', especialidades: ['Ortodontia'], rating: 5, reviews: 120 },
  { id: 2, nome: 'Dra. Ana Borges', especialidades: ['Endodontia'], rating: 4.9, reviews: 95 },
];

const useMockData = () => process.env.USE_MOCK_DATA === 'true';

app.get('/api/test', (req, res) => {
  db.query('SELECT 1', (err, results) => {
    if (err) {
      return res.status(500).json({ error: 'Database connection failed' });
    }
    res.json({ message: 'Database connected successfully', data: results });
  });
});

app.get('/api/clinics', (req, res) => {
  if (useMockData()) {
    return res.json(mockClinics);
  }
  const query = `SELECT c.id, c.cnpj, c.nome, c.descricao, c.telefone, c.conta_bancaria_juridica, c.email, c.ativo, c.logo, c.imagem, c.preco_consulta as preco, c.avaliacao, c.num_avaliacoes, e.rua, e.numero, e.bairro, e.cidade, e.estado, e.cep FROM odontoPro_clinica c LEFT JOIN odontoPro_endereco e ON c.endereco_id = e.id WHERE c.ativo = 1`;
  db.query(query, (err, results) => {
    if (err) {
      console.error('Database error:', err);
      return res.status(500).json({ error: 'Database error. Using mock data.', data: mockClinics });
    }
    res.json(results);
  });
});

app.get('/api/clinics/:id', (req, res) => {
  const clinicId = req.params.id;
  const query = `SELECT c.id, c.cnpj, c.nome, c.descricao, c.telefone, c.conta_bancaria_juridica, c.email, c.ativo, c.logo, c.imagem, c.preco_consulta as preco, c.avaliacao, c.num_avaliacoes, e.rua, e.numero, e.bairro, e.cidade, e.estado, e.cep FROM odontoPro_clinica c LEFT JOIN odontoPro_endereco e ON c.endereco_id = e.id WHERE c.id = ? AND c.ativo = 1`;
  db.query(query, [clinicId], (err, results) => {
    if (err) {
      return res.status(500).json({ error: err.message });
    }
    if (results.length === 0) {
      return res.status(404).json({ error: 'Clinic not found' });
    }
    res.json(results[0]);
  });
});

app.get('/api/clinics/:clinicId/specialties', (req, res) => {
  const clinicId = req.params.clinicId;
  const query = 'SELECT id, nome, preco FROM odontoPro_especialidade WHERE clinica_id = ?';
  db.query(query, [clinicId], (err, results) => {
    if (err) {
      return res.status(500).json({ error: err.message });
    }
    res.json(results);
  });
});

app.get('/api/clinics/:clinicId/doctors', (req, res) => {
  if (useMockData()) {
    return res.json(mockDoctors);
  }
  const clinicId = req.params.clinicId;
  const query = `SELECT m.id, m.nome, m.crm_cro, m.telefone, m.ativo, m.avaliacao, m.num_avaliacoes, m.foto, GROUP_CONCAT(e.nome) as especialidades FROM odontoPro_medico m LEFT JOIN odontoPro_medico_especialidades me ON m.id = me.medico_id LEFT JOIN odontoPro_especialidade e ON me.especialidade_id = e.id WHERE m.clinica_id = ? AND m.ativo = 1 GROUP BY m.id`;
  db.query(query, [clinicId], (err, results) => {
    if (err) {
      console.error('Database error:', err);
      return res.status(500).json({ error: 'Database error. Using mock data.', data: mockDoctors });
    }
    res.json(results.map((row) => ({ ...row, especialidades: row.especialidades ? row.especialidades.split(',') : [] })));
  });
});

app.get('/api/appointments/:patientEmail', (req, res) => {
  const patientEmail = req.params.patientEmail;
  const query = `SELECT c.id, c.nome, c.email, c.telefone, c.data_hora, c.observacoes, c.status, c.criado_em, cl.nome as clinica_nome, m.nome as medico_nome, e.nome as especialidade_nome FROM odontoPro_consulta c LEFT JOIN odontoPro_clinica cl ON c.clinica_id = cl.id LEFT JOIN odontoPro_medico m ON c.medico_id = m.id LEFT JOIN odontoPro_especialidade e ON c.especialidade_id = e.id WHERE c.email = ? ORDER BY c.data_hora DESC`;
  db.query(query, [patientEmail], (err, results) => {
    if (err) {
      return res.status(500).json({ error: err.message });
    }
    res.json(results);
  });
});

app.post('/api/appointments', (req, res) => {
  const { nome, email, telefone, clinica_id, medico_id, especialidade_id, data_hora, observacoes } = req.body;
  const query = `INSERT INTO odontoPro_consulta (nome, email, telefone, clinica_id, medico_id, especialidade_id, data_hora, observacoes, status, criado_em) VALUES (?, ?, ?, ?, ?, ?, ?, ?, 'agendada', NOW())`;
  db.query(query, [nome, email, telefone, clinica_id, medico_id, especialidade_id, data_hora, observacoes], (err, result) => {
    if (err) {
      return res.status(500).json({ error: err.message });
    }
    res.json({ id: result.insertId, message: 'Appointment created successfully' });
  });
});

app.post('/api/login', (req, res) => {
  const { email, senha } = req.body;
  if (useMockData()) {
    if (email && senha) {
      return res.json({ id: 1, nome: 'Usuário Teste', email, telefone: '(91) 99999-9999' });
    }
    return res.status(401).json({ error: 'Invalid credentials' });
  }
  const query = 'SELECT id, nome, email, telefone, cpf, data_nascimento, sexo, foto, senha FROM odontoPro_paciente WHERE email = ? AND ativo = 1';
  db.query(query, [email], async (err, results) => {
    if (err) {
      console.error('Database error:', err);
      return res.status(500).json({ error: err.message });
    }
    if (results.length === 0) {
      return res.status(401).json({ error: 'Invalid credentials' });
    }
    const user = results[0];
    const passwordMatch = await verifyPassword(senha, user.senha);
    if (!passwordMatch) {
      return res.status(401).json({ error: 'Invalid credentials' });
    }
    const { senha: _, ...userWithoutPassword } = user;
    res.json(userWithoutPassword);
  });
});

app.post('/api/register', (req, res) => {
  const { nome, email, senha, telefone, cpf, data_nascimento, sexo } = req.body;
  if (useMockData()) {
    return res.json({ id: 1, nome, email, telefone, message: 'Patient registered successfully (mock)' });
  }
  // Hash the password before saving
  const hashedPassword = bcrypt.hashSync(senha, 10);
  const query = 'INSERT INTO odontoPro_paciente (nome, email, senha, telefone, cpf, data_nascimento, sexo, ativo) VALUES (?, ?, ?, ?, ?, ?, ?, 1)';
  db.query(query, [nome, email, hashedPassword, telefone, cpf, data_nascimento, sexo], (err, result) => {
    if (err) {
      console.error('Database error:', err);
      return res.status(500).json({ error: err.message });
    }
    res.json({ id: result.insertId, message: 'Patient registered successfully' });
  });
});

app.listen(PORT, () => {
  console.log(`Server running on port ${PORT}`);
  console.log(`Development mode: ${useMockData() ? 'Using mock data' : 'Connected to database'}`);
});