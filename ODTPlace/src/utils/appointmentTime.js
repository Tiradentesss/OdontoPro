const APPOINTMENT_DATE_PATTERN = /^(\d{4})-(\d{2})-(\d{2})[T ](\d{2}):(\d{2})(?::(\d{2}))?/;

export const parseAppointmentDate = (value) => {
    if (!value) return null;

    if (value instanceof Date) {
        return Number.isNaN(value.getTime()) ? null : new Date(value.getTime());
    }

    if (typeof value !== 'string') return null;

    const match = value.trim().match(APPOINTMENT_DATE_PATTERN);
    if (match) {
        const [, year, month, day, hours, minutes, seconds = '0'] = match;
        return new Date(Number(year), Number(month) - 1, Number(day), Number(hours), Number(minutes), Number(seconds));
    }

    const parsed = new Date(value);
    return Number.isNaN(parsed.getTime()) ? null : parsed;
};

export const formatAppointmentDateKey = (value) => {
    const date = value instanceof Date ? value : parseAppointmentDate(value);
    if (!date) return null;

    return `${date.getFullYear()}-${String(date.getMonth() + 1).padStart(2, '0')}-${String(date.getDate()).padStart(2, '0')}`;
};

export const formatAppointmentTime = (value) => {
    const date = value instanceof Date ? value : parseAppointmentDate(value);
    return date ? `${String(date.getHours()).padStart(2, '0')}:${String(date.getMinutes()).padStart(2, '0')}` : null;
};

export const formatAppointmentDateTime = (dateKey, time) => {
    if (!dateKey || !time) return null;
    const [year, month, day] = dateKey.split('-');
    const [hours, minutes] = time.split(':');
    return `${year}-${month}-${day} ${String(Number(hours)).padStart(2, '0')}:${String(Number(minutes)).padStart(2, '0')}:00`;
};

export const addAppointmentMinutes = (value, minutes) => {
    const date = value instanceof Date ? new Date(value.getTime()) : parseAppointmentDate(value);
    if (!date) return null;
    date.setMinutes(date.getMinutes() + minutes);
    return date;
};
