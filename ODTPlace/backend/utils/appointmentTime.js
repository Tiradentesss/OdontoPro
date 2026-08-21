const formatDateTime = (value) => {
  const pad = (part) => String(part).padStart(2, '0');
  return `${value.getFullYear()}-${pad(value.getMonth() + 1)}-${pad(value.getDate())} ${pad(value.getHours())}:${pad(value.getMinutes())}:${pad(value.getSeconds())}`;
};

const normalizeAppointmentDateValue = (value) => {
  if (!value) return value;

  if (value instanceof Date) {
    return formatDateTime(value);
  }

  if (typeof value !== 'string') {
    return value;
  }

  const trimmedValue = value.trim();
  if (!trimmedValue) return trimmedValue;

  const sqlDateFormat = /^\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}(?:\.\d+)?$/;
  if (sqlDateFormat.test(trimmedValue)) {
    return trimmedValue.replace(/\.\d+$/, '');
  }

  const components = trimmedValue.match(/^(\d{4})-(\d{2})-(\d{2})[T ](\d{2}):(\d{2})(?::(\d{2}))?/);
  if (components) {
    const [, year, month, day, hour, minute, second = '0'] = components;
    return `${year}-${month}-${day} ${hour}:${minute}:${second}`;
  }

  const date = new Date(trimmedValue);
  if (Number.isNaN(date.getTime())) {
    return trimmedValue;
  }

  return formatDateTime(date);
};

const normalizeAppointmentRow = (row) => {
  if (!row || typeof row !== 'object') {
    return row;
  }

  const normalizedRow = { ...row };
  if (normalizedRow.data_hora !== undefined) {
    normalizedRow.data_hora = normalizeAppointmentDateValue(normalizedRow.data_hora);
  }

  return normalizedRow;
};

const normalizeAppointmentRows = (rows) => {
  if (!Array.isArray(rows)) {
    return rows;
  }

  return rows.map(normalizeAppointmentRow);
};

module.exports = {
  normalizeAppointmentDateValue,
  normalizeAppointmentRow,
  normalizeAppointmentRows,
};
