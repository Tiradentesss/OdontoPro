const BRAZIL_TIMEZONE = 'America/Sao_Paulo';

const formatBrazilDateTime = (value) => {
  const parts = new Intl.DateTimeFormat('sv-SE', {
    timeZone: BRAZIL_TIMEZONE,
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit',
    second: '2-digit',
    hour12: false,
  }).formatToParts(value);

  const formatted = {};
  parts.forEach((part) => {
    if (part.type !== 'literal') {
      formatted[part.type] = part.value;
    }
  });

  return `${formatted.year}-${formatted.month}-${formatted.day} ${formatted.hour}:${formatted.minute}:${formatted.second}`;
};

const normalizeAppointmentDateValue = (value) => {
  if (!value) return value;

  if (value instanceof Date) {
    return formatBrazilDateTime(value);
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

  const date = new Date(trimmedValue);
  if (Number.isNaN(date.getTime())) {
    return trimmedValue;
  }

  return formatBrazilDateTime(date);
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
