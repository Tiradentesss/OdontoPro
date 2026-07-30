const assert = require('assert');
const { normalizeAppointmentDateValue, normalizeAppointmentRows } = require('../utils/appointmentTime');

function run() {
  const normalized = normalizeAppointmentDateValue('2026-05-20T12:30:00.000Z');
  assert.strictEqual(normalized, '2026-05-20 09:30:00');

  const rows = normalizeAppointmentRows([{ data_hora: '2026-05-20T12:30:00.000Z' }, { data_hora: '2026-05-20 12:30:00' }]);
  assert.strictEqual(rows[0].data_hora, '2026-05-20 09:30:00');
  assert.strictEqual(rows[1].data_hora, '2026-05-20 12:30:00');

  console.log('appointmentTime tests passed');
}

run();
