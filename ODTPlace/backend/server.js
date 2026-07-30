const path = require('path');
const envPath = path.resolve(__dirname, '../.env');
console.log('Loading env from:', envPath);
require('dotenv').config({ path: envPath });

const express = require('express');
const cors = require('cors');
const bcrypt = require('bcrypt');
const crypto = require('crypto');
const db = require('./config/database');
const { normalizeAppointmentDateValue, normalizeAppointmentRows } = require('./utils/appointmentTime');

// Support both Django PBKDF2 hashes and bcrypt hashes for backward compatibility.
async function verifyPassword(inputPassword, storedHash) {
  if (!storedHash) return false;

  if (storedHash.startsWith('pbkdf2_sha256')) {
    const parts = storedHash.split('$');
    if (parts.length !== 4) return false;
    const iterations = parseInt(parts[1], 10);
    const salt = parts[2];
    const expectedHash = parts[3];
    const derived = crypto.pbkdf2Sync(inputPassword, salt, iterations, 32, 'sha256');
    const computedHash = derived.toString('base64');
    return computedHash === expectedHash;
  }

  if (storedHash.startsWith('$2') && storedHash.length >= 60) {
    return bcrypt.compare(inputPassword, storedHash);
  }

  return false;
}

// Debug: Check if .env is loaded
console.log('DB_HOST:', process.env.DB_HOST);
console.log('USE_MOCK_DATA:', process.env.USE_MOCK_DATA);

const app = express();
const PORT = process.env.PORT || 3001;
const HOST = process.env.HOST || '0.0.0.0';

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

const mockAppointments = [
  { id: 1, nome: 'Gabriel Gomes', email: 'gabriel@example.com', telefone: '(91) 99999-1111', data_hora: '2026-05-22T09:00:00.000Z', observacoes: 'Extração de siso', status: 'agendada', clinica_nome: 'Clínica Sorriso Vivo', medico_nome: 'Dr. Lucas Castro', especialidade_nome: 'Ortodontia', paciente_id: 1 },
  { id: 2, nome: 'Mariana Costa', email: 'mariana@example.com', telefone: '(91) 98888-2222', data_hora: '2026-05-22T10:30:00.000Z', observacoes: 'Dor de dente aguda', status: 'pendente', clinica_nome: 'Clínica Sorriso Vivo', medico_nome: 'Dr. Lucas Castro', especialidade_nome: 'Ortodontia', paciente_id: 2 },
  { id: 3, nome: 'Hugo Pontes', email: 'hugo@example.com', telefone: '(91) 97777-3333', data_hora: '2026-05-23T12:00:00.000Z', observacoes: 'Ajuste de prótese', status: 'confirmada', clinica_nome: 'Clínica Sorriso Vivo', medico_nome: 'Dr. Lucas Castro', especialidade_nome: 'Ortodontia', paciente_id: 3 },
  { id: 4, nome: 'Natália Silva', email: 'natalia@example.com', telefone: '(91) 96666-4444', data_hora: '2026-05-24T14:00:00.000Z', observacoes: 'Clareamento dental', status: 'reagendada', clinica_nome: 'Clínica Sorriso Vivo', medico_nome: 'Dr. Lucas Castro', especialidade_nome: 'Ortodontia', paciente_id: 4 },
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
  const query = `SELECT m.id, m.nome, m.crm_cro, m.telefone, m.email, m.ativo, m.avaliacao, m.num_avaliacoes, m.foto, GROUP_CONCAT(e.nome) as especialidades FROM odontoPro_medico m LEFT JOIN odontoPro_medico_especialidades me ON m.id = me.medico_id LEFT JOIN odontoPro_especialidade e ON me.especialidade_id = e.id WHERE m.clinica_id = ? AND m.ativo = 1 GROUP BY m.id`;
  db.query(query, [clinicId], (err, results) => {
    if (err) {
      console.error('Database error:', err);
      return res.status(500).json({ error: 'Database error. Using mock data.', data: mockDoctors });
    }
    res.json(results.map((row) => ({ ...row, especialidades: row.especialidades ? row.especialidades.split(',') : [] })));
  });
});

app.get('/api/doctors/:id', (req, res) => {
  const doctorId = req.params.id;
  if (useMockData()) {
    const doctor = mockDoctors.find((item) => String(item.id) === String(doctorId));
    return doctor ? res.json(doctor) : res.status(404).json({ error: 'Doctor not found' });
  }

  const query = `SELECT m.id, m.nome, m.crm_cro, m.telefone, m.email, m.foto, m.avaliacao, m.num_avaliacoes, GROUP_CONCAT(e.nome) as especialidades FROM odontoPro_medico m LEFT JOIN odontoPro_medico_especialidades me ON m.id = me.medico_id LEFT JOIN odontoPro_especialidade e ON me.especialidade_id = e.id WHERE m.id = ? AND m.ativo = 1 GROUP BY m.id`;
  db.query(query, [doctorId], (err, results) => {
    if (err) {
      console.error('Database error:', err);
      return res.status(500).json({ error: err.message });
    }
    if (results.length === 0) {
      return res.status(404).json({ error: 'Doctor not found' });
    }
    const doctor = results[0];
    res.json({ ...doctor, especialidades: doctor.especialidades ? doctor.especialidades.split(',') : [] });
  });
});

app.put('/api/doctors/:id', (req, res) => {
  const doctorId = req.params.id;
  const { nome, email, telefone, crm_cro, foto } = req.body;

  if (useMockData()) {
    return res.json({ id: doctorId, nome, email, telefone, crm_cro, foto });
  }

  const updates = [];
  const params = [];

  if (nome !== undefined) {
    updates.push('nome = ?');
    params.push(nome);
  }
  if (email !== undefined) {
    updates.push('email = ?');
    params.push(email);
  }
  if (telefone !== undefined) {
    updates.push('telefone = ?');
    params.push(telefone);
  }
  if (crm_cro !== undefined) {
    updates.push('crm_cro = ?');
    params.push(crm_cro);
  }
  if (foto !== undefined) {
    updates.push('foto = ?');
    params.push(foto);
  }

  if (updates.length === 0) {
    return res.status(400).json({ error: 'No valid fields to update' });
  }

  params.push(doctorId);
  const query = `UPDATE odontoPro_medico SET ${updates.join(', ')} WHERE id = ?`;

  db.query(query, params, (err, result) => {
    if (err) {
      console.error('Database error:', err);
      return res.status(500).json({ error: err.message });
    }
    res.json({ id: doctorId, nome, email, telefone, crm_cro, foto, affectedRows: result.affectedRows });
  });
});

app.get('/api/patients/:id', (req, res) => {
  const patientId = req.params.id;
  if (useMockData()) {
    return res.json({
      id: patientId,
      nome: 'Paciente Mock',
      email: 'paciente.mock@exemplo.com',
      telefone: '(91) 99999-9999',
      cpf: '000.000.000-00',
      data_nascimento: '1990-01-01',
      sexo: 'Masculino',
      foto: null,
    });
  }

  const query = 'SELECT id, nome, email, telefone, cpf, data_nascimento, sexo, foto FROM odontoPro_paciente WHERE id = ? AND ativo = 1';
  db.query(query, [patientId], (err, results) => {
    if (err) {
      console.error('Database error:', err);
      return res.status(500).json({ error: err.message });
    }
    if (results.length === 0) {
      return res.status(404).json({ error: 'Patient not found' });
    }
    res.json(results[0]);
  });
});

app.put('/api/patients/:id', (req, res) => {
  const patientId = req.params.id;
  const { nome, email, telefone, cpf, data_nascimento, sexo } = req.body;
  if (useMockData()) {
    return res.json({ id: patientId, nome, email, telefone, cpf, data_nascimento, sexo, foto: null });
  }

  const query = 'UPDATE odontoPro_paciente SET nome = ?, email = ?, telefone = ?, cpf = ?, data_nascimento = ?, sexo = ? WHERE id = ?';
  db.query(query, [nome, email, telefone, cpf, data_nascimento, sexo, patientId], (err) => {
    if (err) {
      console.error('Database error:', err);
      return res.status(500).json({ error: err.message });
    }
    res.json({ id: patientId, nome, email, telefone, cpf, data_nascimento, sexo });
  });
});

app.get(['/api/appointments', '/appointments'], (req, res) => {
  if (useMockData()) {
    return res.json(mockAppointments);
  }

  const { medico_id, clinica_id } = req.query;
  let query = `SELECT c.id, c.nome, c.email, c.telefone, c.data_hora, c.observacoes, c.status, c.criado_em, c.paciente_id, cl.nome as clinica_nome, m.nome as medico_nome, e.nome as especialidade_nome FROM odontoPro_consulta c LEFT JOIN odontoPro_clinica cl ON c.clinica_id = cl.id LEFT JOIN odontoPro_medico m ON c.medico_id = m.id LEFT JOIN odontoPro_especialidade e ON c.especialidade_id = e.id WHERE 1=1`;
  const params = [];

  if (medico_id) {
    query += ' AND c.medico_id = ?';
    params.push(medico_id);
  }

  if (clinica_id) {
    query += ' AND c.clinica_id = ?';
    params.push(clinica_id);
  }

  query += ' ORDER BY c.data_hora ASC';

  db.query(query, params, (err, results) => {
    if (err) {
      console.error('Appointments query failed, returning mock data:', err.message);
      return res.json(mockAppointments);
    }
    res.json(normalizeAppointmentRows(results));
  });
});

app.get(['/api/appointments/:patientEmail', '/appointments/:patientEmail'], (req, res) => {
  if (useMockData()) {
    return res.json(mockAppointments);
  }

  const patientEmail = req.params.patientEmail;
  // Tentar buscar por paciente_id primeiro (número), depois por email
  const isNumericId = /^\d+$/.test(patientEmail);
  let query, params;
  
  if (isNumericId) {
    query = `SELECT c.id, c.nome, c.email, c.telefone, c.data_hora, c.observacoes, c.status, c.criado_em, c.paciente_id, cl.nome as clinica_nome, m.nome as medico_nome, e.nome as especialidade_nome FROM odontoPro_consulta c LEFT JOIN odontoPro_clinica cl ON c.clinica_id = cl.id LEFT JOIN odontoPro_medico m ON c.medico_id = m.id LEFT JOIN odontoPro_especialidade e ON c.especialidade_id = e.id WHERE c.paciente_id = ? ORDER BY c.data_hora DESC`;
    params = [parseInt(patientEmail)];
  } else {
    query = `SELECT c.id, c.nome, c.email, c.telefone, c.data_hora, c.observacoes, c.status, c.criado_em, c.paciente_id, cl.nome as clinica_nome, m.nome as medico_nome, e.nome as especialidade_nome FROM odontoPro_consulta c LEFT JOIN odontoPro_clinica cl ON c.clinica_id = cl.id LEFT JOIN odontoPro_medico m ON c.medico_id = m.id LEFT JOIN odontoPro_especialidade e ON c.especialidade_id = e.id WHERE c.email = ? ORDER BY c.data_hora DESC`;
    params = [patientEmail];
  }
  
  db.query(query, params, (err, results) => {
    if (err) {
      return res.status(500).json({ error: err.message });
    }
    res.json(normalizeAppointmentRows(results));
  });
});

app.put(['/api/appointments/:id', '/appointments/:id'], (req, res) => {
  if (useMockData()) {
    const appointmentId = Number(req.params.id);
    const appointment = mockAppointments.find((item) => item.id === appointmentId);
    if (!appointment) {
      return res.status(404).json({ error: 'Appointment not found' });
    }

    Object.assign(appointment, req.body);
    return res.json({ message: 'Appointment updated successfully', appointment });
  }

  const appointmentId = req.params.id;
  const { status, data_hora, observacoes } = req.body;
  const updates = [];
  const params = [];

  if (status !== undefined) {
    updates.push('status = ?');
    params.push(status);
  }

  if (data_hora !== undefined) {
    updates.push('data_hora = ?');
    params.push(normalizeAppointmentDateValue(data_hora));
  }

  if (observacoes !== undefined) {
    updates.push('observacoes = ?');
    params.push(observacoes);
  }

  if (updates.length === 0) {
    return res.status(400).json({ error: 'No valid fields to update' });
  }

  params.push(appointmentId);
  const query = `UPDATE odontoPro_consulta SET ${updates.join(', ')} WHERE id = ?`;

  db.query(query, params, (err, result) => {
    if (err) {
      return res.status(500).json({ error: err.message });
    }
    res.json({ message: 'Appointment updated successfully', affectedRows: result.affectedRows });
  });
});

app.post(['/api/appointments', '/appointments'], (req, res) => {
  const { nome, email, telefone, clinica_id, medico_id, especialidade_id, data_hora, observacoes, paciente_id } = req.body;
  const normalizedDataHora = normalizeAppointmentDateValue(data_hora);
  const query = `INSERT INTO odontoPro_consulta (nome, email, telefone, clinica_id, medico_id, especialidade_id, data_hora, observacoes, status, paciente_id, criado_em) VALUES (?, ?, ?, ?, ?, ?, ?, ?, 'agendada', ?, NOW())`;
  db.query(query, [nome, email, telefone, clinica_id, medico_id, especialidade_id, normalizedDataHora, observacoes, paciente_id], (err, result) => {
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

app.post('/api/login/profissional', (req, res) => {
  const { email, senha } = req.body;
  if (useMockData()) {
    if (email && senha) {
      return res.json({ id: 1, nome: 'Dr. Usuário Teste', email, telefone: '(91) 99999-0000', crm_cro: 'CRO-12345' });
    }
    return res.status(401).json({ error: 'Invalid credentials' });
  }
  const query = 'SELECT id, nome, email, telefone, crm_cro, foto, senha FROM odontoPro_medico WHERE (email = ? OR crm_cro = ?) AND ativo = 1';
  db.query(query, [email, email], async (err, results) => {
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

app.listen(PORT, HOST, () => {
  console.log(`Server running on http://${HOST}:${PORT}`);
  console.log(`Development mode: ${useMockData() ? 'Using mock data' : 'Connected to database'}`);
});

// Estatísticas rápidas do médico: consultas completadas e avaliação geral
app.get('/api/doctors/:id/stats', (req, res) => {
  const doctorId = req.params.id;
  if (useMockData()) {
    return res.json({ completed_consultations: 120, positive_reviews: 4.8 });
  }

  const completedQuery = `SELECT COUNT(*) as completed FROM odontoPro_consulta WHERE medico_id = ? AND status IN ('realizada', 'completa', 'confirmada')`;
  db.query(completedQuery, [doctorId], (err, completedResults) => {
    if (err) {
      console.error('Error fetching doctor completed count:', err.message);
      return res.status(500).json({ error: 'Database error' });
    }

    const completed = completedResults[0]?.completed ?? 0;
    const ratingQuery = `SELECT COALESCE(avaliacao, 0) as average_rating FROM odontoPro_medico WHERE id = ? AND ativo = 1`;

    db.query(ratingQuery, [doctorId], (err2, ratingResults) => {
      if (err2) {
        console.error('Error fetching doctor rating:', err2.message);
        return res.json({ completed_consultations: completed, positive_reviews: 0 });
      }

      const averageRating = ratingResults[0]?.average_rating ?? 0;
      return res.json({ completed_consultations: completed, positive_reviews: averageRating });
    });
  });
});