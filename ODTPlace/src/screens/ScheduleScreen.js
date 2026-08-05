import React, { useState, useRef, useEffect } from 'react';
import {
    View,
    Text,
    StyleSheet,
    TouchableOpacity,
    SafeAreaView,
    ScrollView,
    Modal,
    ImageBackground,
    ActivityIndicator,
    Alert,
} from 'react-native';
import ScheduleHeaderNoBack from '../components/ScheduleHeaderNoBack';
import BottomNavBar from '../components/BottomNavBar';
import { getPatientAppointments, updateAppointment } from '../services/api';
import { useAuth } from '../context/AuthContext';
import { useTheme } from '../components/ThemeContext';

const monthNames = ['Jan', 'Fev', 'Mar', 'Abr', 'Mai', 'Jun', 'Jul', 'Ago', 'Set', 'Out', 'Nov', 'Dez'];
const weekdays = ['D', 'S', 'T', 'Q', 'Q', 'S', 'S'];
const FILTER_OPTIONS = ['Todos', 'Pendente', 'Realizada', 'Cancelada'];

// Dados mockados como fallback
const appointmentDays = [];

const appointmentsByDate = {
    '2026-04-11': [
        {
            id: '1',
            time: '10:00',
            endTime: '10:30',
            date: '11/04/2026',
            clinic: 'Clínica Sorriso Vivo',
            specialty: 'Odontopediatria',
            doctor: 'Maria Silva',
            status: 'confirmada',
            confirmed: true,
            observations: 'Consulta de rotina para avaliação dentária infantil',
            patientNotes: 'Lembrar de trazer a carteirinha de vacinação',
        },
    ],
    '2026-04-16': [
        {
            id: '2',
            time: '09:00',
            endTime: '09:30',
            date: '16/04/2026',
            clinic: 'Clínica Sorriso Vivo',
            specialty: 'Ortodontia',
            doctor: 'João Santos',
            status: 'agendada',
            confirmed: true,
            observations: 'Avaliação para aparelho ortodôntico',
            patientNotes: '',
        },
        {
            id: '3',
            time: '12:00',
            endTime: '12:30',
            date: '16/04/2026',
            clinic: 'Clínica Sorriso Vivo',
            specialty: 'Periodontia',
            doctor: 'Ana Costa',
            status: 'realizada',
            confirmed: false,
            observations: 'Tratamento de gengivite - limpeza profunda realizada',
            patientNotes: 'Retorno em 6 meses',
        },
    ],
};

const toDateOnly = (dateId) => {
    const [year, month, day] = dateId.split('-').map(Number);
    return new Date(year, month - 1, day);
};

const today = new Date();
const todayStart = new Date(today.getFullYear(), today.getMonth(), today.getDate());

const formatDateTime = (dateString, timeString) => {
    if (!dateString || !timeString) return null;
    const [year, month, day] = dateString.split('-').map(Number);
    const [hours, minutes] = timeString.split(':').map(Number);
    const date = new Date(year, month - 1, day, hours, minutes);
    return date.toISOString();
};

const getUpcomingAppointmentDate = (appointmentsData = []) => {
    // Se tiver dados reais, usa eles
    if (appointmentsData.length > 0) {
        const futureDates = appointmentsData
            .map(apt => ({ id: new Date(apt.data_hora).toISOString().split('T')[0], date: new Date(apt.data_hora) }))
            .filter(({ date }) => date >= todayStart)
            .sort((a, b) => a.date - b.date)
            .map(({ id }) => id);
        if (futureDates.length > 0) return futureDates[0];
    }
    // Fallback para dados mockados
    const futureDates = appointmentDays
        .map((id) => ({ id, date: toDateOnly(id) }))
        .filter(({ date }) => date >= todayStart)
        .sort((a, b) => a.date - b.date)
        .map(({ id }) => id);
    return futureDates[0] ?? appointmentDays.slice().sort()[0] ?? `${todayStart.getFullYear()}-${String(todayStart.getMonth() + 1).padStart(2, '0')}-${String(todayStart.getDate()).padStart(2, '0')}`;
};

const getMonthDays = (year, month, appointmentDatesSet = new Set()) => {
    const days = new Date(year, month, 0).getDate();
    return Array.from({ length: days }, (_, index) => {
        const day = index + 1;
        const id = `${year}-${String(month).padStart(2, '0')}-${String(day).padStart(2, '0')}`;
        const date = new Date(year, month - 1, day);
        return {
            id,
            day: String(day),
            weekday: weekdays[date.getDay()],
            hasAppointments: appointmentDatesSet.has(id) || appointmentDays.includes(id),
            isPast: toDateOnly(id) < todayStart,
        };
    });
};

export default function ScheduleScreen({ navigation, activeTab, showBottomNav = true, route }) {
    const { user } = useAuth();
    const { isDarkMode, colors } = useTheme();
    const [search, setSearch] = useState('');
    const [shouldResetPosition, setShouldResetPosition] = useState(true);
    const lastActiveTab = useRef(activeTab);
    const usuario = user?.nome ?? 'Paciente';
    const [currentMonth, setCurrentMonth] = useState({
        year: today.getFullYear(),
        month: today.getMonth() + 1,
    });
    const [selectedDate, setSelectedDate] = useState(`${today.getFullYear()}-${String(today.getMonth() + 1).padStart(2, '0')}-${String(today.getDate()).padStart(2, '0')}`);
    const [pickerVisible, setPickerVisible] = useState(false);
    const [swipeStartX, setSwipeStartX] = useState(null);
    const [carouselWidth, setCarouselWidth] = useState(0);
    const [appointmentsData, setAppointmentsData] = useState([]);
    const [loadingAppointments, setLoadingAppointments] = useState(true);
    const scrollViewRef = useRef(null);
    const dayButtonWidth = 58;
    const dayButtonSpacing = 8;

    // Datas que têm consultas (para marcar no calendário) - deve vir antes do monthDays
    const appointmentDatesSet = new Set(
        appointmentsData.map(apt => new Date(apt.data_hora).toISOString().split('T')[0])
    );

    const monthDays = getMonthDays(currentMonth.year, currentMonth.month, appointmentDatesSet);
    const calendarStartOffset = new Date(currentMonth.year, currentMonth.month - 1, 1).getDay();
    const calendarCells = [...Array(calendarStartOffset).fill(null), ...monthDays];

    // Carregar consultas do backend
    useEffect(() => {
        const loadAppointments = async () => {
            // Usar paciente_id (número) primeiro, depois email como fallback
            const patientId = user.id;
            if (patientId) {
                try {
                    const data = await getPatientAppointments(String(patientId));
                    setAppointmentsData(data || []);
                } catch (error) {
                    console.log('Error loading appointments:', error);
                } finally {
                    setLoadingAppointments(false);
                }
            } else if (user.email) {
                try {
                    const data = await getPatientAppointments(user.email);
                    setAppointmentsData(data || []);
                } catch (error) {
                    console.log('Error loading appointments:', error);
                } finally {
                    setLoadingAppointments(false);
                }
            } else {
                setLoadingAppointments(false);
            }
        };
        loadAppointments();
    }, [user.id, user.email]);

    // Converter dados da API para formato do calendário
    const getAppointmentsForDate = (dateId) => {
        if (appointmentsData.length > 0) {
            return appointmentsData
                .filter(apt => {
                    const aptDate = new Date(apt.data_hora).toISOString().split('T')[0];
                    return aptDate === dateId;
                })
                .map(apt => ({
                    id: String(apt.id),
                    data_hora: apt.data_hora,
                    nome: usuario,
                    time: new Date(apt.data_hora).toLocaleTimeString('pt-BR', { hour: '2-digit', minute: '2-digit' }),
                    endTime: new Date(apt.data_hora).toLocaleTimeString('pt-BR', { hour: '2-digit', minute: '2-digit' }),
                    date: new Date(apt.data_hora).toLocaleDateString('pt-BR'),
                    clinic: apt.clinica_nome || 'Clínica',
                    specialty: apt.especialidade_nome || 'Especialidade',
                    doctor: apt.medico_nome || 'Dr. Médico',
                    status: apt.status || 'agendada',
                    confirmed: apt.status === 'confirmada' || apt.status === 'agendada',
                    observacoes: apt.observacoes || apt.observations || 'Nenhuma observação',
                    patientNotes: apt.notas_paciente || '',
                }));
        }
        return appointmentsByDate[dateId] ?? [];
    };

    const getStatusBorderColor = (status) => {
        switch (status?.toLowerCase()) {
            case 'agendada':
            case 'confirmada':
                return '#FCD34D'; // Amarelo
            case 'realizada':
            case 'completa':
                return '#10B981'; // Verde
            case 'cancelada':
                return '#EF4444'; // Vermelho
            case 'perdida':
                return '#1F2937'; // Preto/Cinza escuro
            default:
                return '#FCD34D'; // Amarelo padrão
        }
    };

    const getStatusInfo = (status) => {
        const normalized = status?.toLowerCase();
        if (normalized === 'cancelada') {
            return { label: 'CANCELADA', color: '#B91C1C', bg: '#FEE2E2', border: '#FECACA' };
        }
        if (normalized === 'realizada' || normalized === 'completa') {
            return { label: 'REALIZADA', color: '#047857', bg: '#DCFCE7', border: '#BBF7D0' };
        }
        if (normalized === 'perdida') {
            return { label: 'PERDIDA', color: '#111827', bg: '#E5E7EB', border: '#D1D5DB' };
        }
        if (normalized === 'confirmada') {
            return { label: 'CONFIRMADA', color: '#B45309', bg: '#FEF3C7', border: '#FDE68A' };
        }
        return { label: 'AGENDADA', color: '#B45309', bg: '#FEF3C7', border: '#FDE68A' };
    };

    const appointments = getAppointmentsForDate(selectedDate);
    const [statusFilter, setStatusFilter] = useState('Todos');

    const filteredAppointments = appointments.filter((item) => {
        const normalized = item?.status?.toLowerCase();
        if (statusFilter === 'Todos') return true;
        if (statusFilter === 'Realizada') return ['realizada', 'completa'].includes(normalized);
        if (statusFilter === 'Pendente') return ['agendada', 'confirmada', 'pendente'].includes(normalized);
        if (statusFilter === 'Cancelada') return normalized === 'cancelada';
        return true;
    });

    const monthLabel = `${monthNames[currentMonth.month - 1]}, ${currentMonth.year}`;

    const setMonth = (year, month) => {
        setShouldResetPosition(false);
        setCurrentMonth({ year, month });
        const [currentYear, currentMonthNum, currentDay] = selectedDate.split('-').map(Number);
        const daysInNewMonth = new Date(year, month, 0).getDate();
        const nextDay = Math.min(currentDay, daysInNewMonth);
        setSelectedDate(`${year}-${String(month).padStart(2, '0')}-${String(nextDay).padStart(2, '0')}`);
    };

    const handleSwipeEnd = (endX) => {
        if (swipeStartX === null) {
            return;
        }
        const deltaX = endX - swipeStartX;
        setSwipeStartX(null);
        if (Math.abs(deltaX) < 40) {
            return;
        }
        if (deltaX > 0) {
            goPreviousMonth();
        } else {
            goNextMonth();
        }
    };

    const goPreviousMonth = () => {
        if (currentMonth.month === 1) {
            setMonth(currentMonth.year - 1, 12);
        } else {
            setMonth(currentMonth.year, currentMonth.month - 1);
        }
    };

    const goNextMonth = () => {
        if (currentMonth.month === 12) {
            setMonth(currentMonth.year + 1, 1);
        } else {
            setMonth(currentMonth.year, currentMonth.month + 1);
        }
    };

    const handleSelectDate = (dateId) => {
        setSelectedDate(dateId);
        setShouldResetPosition(false);
    };

    const handleCalendarSelect = (dateId) => {
        setSelectedDate(dateId);
        setPickerVisible(false);
        setShouldResetPosition(true);
    };

    useEffect(() => {
        if (lastActiveTab.current !== activeTab) {
            if (activeTab === 'schedule') {
                setShouldResetPosition(true);
            }
            lastActiveTab.current = activeTab;
        }
    }, [activeTab]);

    useEffect(() => {
        if (!scrollViewRef.current || carouselWidth === 0 || !shouldResetPosition) {
            return;
        }

        const selectedIndex = monthDays.findIndex((day) => day.id === selectedDate);
        if (selectedIndex < 0) {
            return;
        }

        const itemTotalWidth = dayButtonWidth + dayButtonSpacing;
        const targetX = Math.max(selectedIndex * itemTotalWidth + dayButtonWidth / 2 - carouselWidth / 2, 0);
        scrollViewRef.current.scrollTo({ x: targetX, animated: true });
        setShouldResetPosition(false);
    }, [selectedDate, monthDays, carouselWidth, shouldResetPosition]);


    return (
        <ImageBackground
            source={require('../../assets/imagem background.png')}
            style={styles.pageBackground}
            imageStyle={!isDarkMode ? { transform: [{ scale: 1.2 }] } : undefined}
            resizeMode="cover"
        >
            <SafeAreaView style={[styles.container, { backgroundColor: isDarkMode ? colors.container : '#f8fafc' }]}> 
                <ScheduleHeaderNoBack title="Agendamentos" iconName="calendar" />

                <View
                    style={styles.monthRow}
                    onTouchStart={(e) => setSwipeStartX(e.nativeEvent.pageX)}
                    onTouchEnd={(e) => handleSwipeEnd(e.nativeEvent.pageX)}
                >
                    <TouchableOpacity style={[styles.monthArrow, isDarkMode && { backgroundColor: '#1E293B' }]} onPress={goPreviousMonth} activeOpacity={0.8}>
                        <Text style={[styles.monthArrowText, { color: isDarkMode ? '#F8FAFC' : '#0f172a' }]}>‹</Text>
                    </TouchableOpacity>
                    <TouchableOpacity style={[styles.monthSelector, isDarkMode && { backgroundColor: '#0F172A', borderWidth: 1, borderColor: '#334155' }]} onPress={() => setPickerVisible(true)} activeOpacity={0.8}>
                        <View style={styles.monthTitleWrapper}>
                            <Text style={[styles.monthLabel, { color: isDarkMode ? '#F8FAFC' : '#0ea5e9' }]}>{monthLabel}</Text>
                            <Text style={[styles.monthHelp, { color: isDarkMode ? '#94A3B8' : '#64748b' }]}>Clique no mês para abrir o calendário</Text>
                        </View>
                    </TouchableOpacity>
                    <TouchableOpacity style={[styles.monthArrow, isDarkMode && { backgroundColor: '#1E293B' }]} onPress={goNextMonth} activeOpacity={0.8}>
                        <Text style={[styles.monthArrowText, { color: isDarkMode ? '#F8FAFC' : '#0f172a' }]}>›</Text>
                    </TouchableOpacity>
                </View>

                <ScrollView
                    horizontal
                    showsHorizontalScrollIndicator={false}
                    contentContainerStyle={styles.dateCarousel}
                    ref={scrollViewRef}
                    nestedScrollEnabled={true}
                    scrollEnabled={true}
                    onScrollBeginDrag={() => setShouldResetPosition(false)}
                    onLayout={(event) => setCarouselWidth(event.nativeEvent.layout.width)}
                >
                    {monthDays.map((date) => {
                        const isSelected = date.id === selectedDate;
                        return (
                            <TouchableOpacity
                                key={date.id}
                                style={[
                                    styles.dateItem,
                                    isSelected && styles.dateItemActive,
                                    date.isPast && styles.dateItemPast,
                                    isDarkMode && { backgroundColor: isSelected ? '#0F172A' : '#1E293B', borderColor: isSelected ? '#38BDF8' : 'transparent' }
                                ]}
                                activeOpacity={date.isPast ? 1 : 0.85}
                                onPress={() => handleSelectDate(date.id)}
                            >
                                <Text style={[
                                    styles.dateWeekday,
                                    isSelected && styles.dateWeekdayActive,
                                    date.isPast && styles.dateWeekdayPast,
                                    isDarkMode && { color: isSelected ? '#F8FAFC' : '#94A3B8' }
                                ]}>{date.weekday}</Text>
                                <Text style={[
                                    styles.dateDay,
                                    isSelected && styles.dateDayActive,
                                    date.isPast && styles.dateDayPast,
                                    isDarkMode && { color: isSelected ? '#F8FAFC' : '#E2E8F0' }
                                ]}>{date.day}</Text>
                                {date.hasAppointments && (
                                    <View
                                        style={[
                                            styles.appointmentDot,
                                            date.isPast && styles.appointmentDotPast,
                                            isDarkMode && { backgroundColor: isSelected ? '#38BDF8' : '#38BDF8' }
                                        ]}
                                    />
                                )}
                            </TouchableOpacity>
                        );
                    })}
                </ScrollView>

                <View style={styles.filterRow}>
                    {FILTER_OPTIONS.map((option) => {
                        const isActive = statusFilter === option;
                        return (
                            <TouchableOpacity
                                key={option}
                                style={[
                                    styles.filterChip,
                                    isActive && styles.filterChipActive,
                                    isDarkMode && { borderColor: isActive ? '#38BDF8' : '#334155', backgroundColor: isActive ? '#0F172A' : '#1E293B' }
                                ]}
                                activeOpacity={0.85}
                                onPress={() => setStatusFilter(option)}
                            >
                                <Text style={[
                                    styles.filterChipText,
                                    isActive && styles.filterChipTextActive,
                                    isDarkMode && !isActive && { color: '#CBD5E1' },
                                    isDarkMode && isActive && { color: '#F8FAFC' }
                                ]}>{option}</Text>
                            </TouchableOpacity>
                        );
                    })}
                </View>

                <View style={styles.scheduleHeader}>
                    <Text style={[styles.scheduleColumn, { color: isDarkMode ? '#94A3B8' : '#64748b' }]}>Hora</Text>
                    <Text style={[styles.scheduleTitleHeader, { color: isDarkMode ? '#94A3B8' : '#64748b' }]}>Consultas do Dia</Text>
                </View>

                <ScrollView contentContainerStyle={styles.listContent} showsVerticalScrollIndicator={false}>
                    {filteredAppointments.map((item) => {
                        const statusInfo = getStatusInfo(item.status);
                        return (
                            <View key={item.id} style={styles.appointmentRow}>
                                <View style={styles.timeColumn}>
                                    <Text style={[styles.timeText, { color: isDarkMode ? '#F8FAFC' : '#0f172a' }]}>{item.time}</Text>
                                    <Text style={[styles.timeSub, { color: isDarkMode ? '#94A3B8' : '#64748b' }]}>{item.date}</Text>
                                </View>
                                <TouchableOpacity
                                    style={[
                                        styles.appointmentCard,
                                        {
                                            borderLeftColor: getStatusBorderColor(item.status),
                                            backgroundColor: isDarkMode ? '#1E293B' : '#FFFFFF',
                                            borderColor: isDarkMode ? '#334155' : '#E2E8F0',
                                        }
                                    ]}
                                    activeOpacity={0.85}
                                    onPress={() => navigation.navigate('PatientAppointmentDetailsScreen', {
                                        patientName: usuario,
                                        appointment: item,
                                        allowReschedule: item.status?.toLowerCase() === 'agendada',
                                    })}
                                >
                                    <View style={styles.cardHeader}>
                                        <View style={styles.cardTitleSection}>
                                            <Text style={[styles.cardLabel, { color: isDarkMode ? '#F8FAFC' : '#0F172A' }]}>{item.clinic}</Text>
                                            <Text style={[styles.doctorName, { color: isDarkMode ? '#38BDF8' : '#0EA5E9' }]}>Dr. {item.doctor}</Text>
                                        </View>
                                        <View style={[styles.statusPill, { backgroundColor: statusInfo.bg, borderColor: statusInfo.border }]}>
                                            <Text style={[styles.statusPillText, { color: statusInfo.color }]}>{statusInfo.label}</Text>
                                        </View>
                                    </View>
                                    <Text style={[styles.specialtyText, { color: isDarkMode ? '#CBD5E1' : '#475569' }]}>{item.specialty}</Text>
                                    <View style={styles.cardDetails}>
                                        <Text style={[styles.detailLabel, { color: isDarkMode ? '#94A3B8' : '#64748B' }]}>Observações:</Text>
                                        <Text style={[styles.detailText, { color: isDarkMode ? '#E2E8F0' : '#374151' }]} numberOfLines={2}>
                                            {item.observations}
                                        </Text>
                                    </View>
                                    {item.patientNotes && (
                                        <View style={styles.cardDetails}>
                                            <Text style={[styles.detailLabel, { color: isDarkMode ? '#94A3B8' : '#64748B' }]}>Suas notas:</Text>
                                            <Text style={[styles.detailText, { color: isDarkMode ? '#E2E8F0' : '#374151' }]} numberOfLines={2}>
                                                {item.patientNotes}
                                            </Text>
                                        </View>
                                    )}
                                </TouchableOpacity>
                            </View>
                        );
                    })}
                    {filteredAppointments.length === 0 && (
                        <View style={styles.emptyState}>
                            <Text style={[styles.emptyText, { color: isDarkMode ? '#94A3B8' : '#64748b' }]}>Nenhuma consulta agendada para este dia.</Text>
                        </View>
                    )}
                </ScrollView>
                <Modal visible={pickerVisible} transparent animationType="fade">
                    <View style={styles.modalOverlay}>
                        <View style={[styles.modalContent, isDarkMode && { backgroundColor: '#0F172A', borderWidth: 1, borderColor: '#334155' }]}> 
                            <View
                                style={styles.modalHeaderRow}
                                onTouchStart={(e) => setSwipeStartX(e.nativeEvent.pageX)}
                                onTouchEnd={(e) => handleSwipeEnd(e.nativeEvent.pageX)}
                            >
                                <TouchableOpacity style={[styles.modalArrowButton, isDarkMode && { backgroundColor: '#1E293B' }]} onPress={goPreviousMonth} activeOpacity={0.8}>
                                    <Text style={[styles.modalArrowText, { color: isDarkMode ? '#F8FAFC' : '#0f172a' }]}>‹</Text>
                                </TouchableOpacity>
                                <Text style={[styles.modalTitle, { color: isDarkMode ? '#F8FAFC' : '#0f172a' }]}>{monthLabel}</Text>
                                <TouchableOpacity style={[styles.modalArrowButton, isDarkMode && { backgroundColor: '#1E293B' }]} onPress={goNextMonth} activeOpacity={0.8}>
                                    <Text style={[styles.modalArrowText, { color: isDarkMode ? '#F8FAFC' : '#0f172a' }]}>›</Text>
                                </TouchableOpacity>
                            </View>
                            <View style={styles.weekHeader}>
                                {weekdays.map((weekday, index) => (
                                    <Text key={`${weekday}-${index}`} style={[styles.weekdayText, { color: isDarkMode ? '#94A3B8' : '#64748b' }]}>{weekday}</Text>
                                ))}
                            </View>
                            <View
                                style={styles.calendarGrid}
                                onTouchStart={(e) => setSwipeStartX(e.nativeEvent.pageX)}
                                onTouchEnd={(e) => handleSwipeEnd(e.nativeEvent.pageX)}
                            >
                                {calendarCells.map((date, index) => {
                                    if (!date) {
                                        return <View key={`blank-${index}`} style={styles.dayCellEmpty} />;
                                    }
                                    const isSelected = date.id === selectedDate;
                                    return (
                                        <TouchableOpacity
                                            key={date.id}
                                            style={[
                                                styles.dayCell,
                                                isSelected && styles.dayCellActive,
                                                date.isPast && !isSelected && styles.dayCellPast,
                                                isDarkMode && !isSelected && !date.isPast && { backgroundColor: '#1E293B', borderWidth: 1, borderColor: '#334155' },
                                                isDarkMode && isSelected && { backgroundColor: '#38BDF8', borderWidth: 1, borderColor: '#38BDF8' },
                                                isDarkMode && date.isPast && !isSelected && { backgroundColor: '#334155', borderWidth: 1, borderColor: '#475569' },
                                            ]}
                                            activeOpacity={0.85}
                                            onPress={() => handleCalendarSelect(date.id)}
                                        >
                                            <Text
                                                style={[
                                                    styles.dayNumber,
                                                    isSelected && styles.dayNumberActive,
                                                    date.isPast && !isSelected && styles.dayNumberPast,
                                                    isDarkMode && !isSelected && { color: '#F8FAFC' },
                                                    isDarkMode && isSelected && { color: '#0F172A' },
                                                    isDarkMode && date.isPast && !isSelected && { color: '#CBD5E1' },
                                                ]}
                                            >
                                                {date.day}
                                            </Text>
                                            {date.hasAppointments && (
                                                <View
                                                    style={[
                                                        styles.dayDot,
                                                        isSelected && styles.dayDotSelected,
                                                        date.isPast && !isSelected && styles.dayDotPast,
                                                        isDarkMode && !isSelected && { backgroundColor: '#38BDF8' },
                                                        isDarkMode && isSelected && { backgroundColor: '#0F172A' },
                                                        isDarkMode && date.isPast && !isSelected && { backgroundColor: '#94A3B8' },
                                                    ]}
                                                />
                                            )}
                                        </TouchableOpacity>
                                    );
                                })}
                            </View>
                            <TouchableOpacity style={styles.closeButton} onPress={() => setPickerVisible(false)} activeOpacity={0.8}>
                                <Text style={styles.closeButtonText}>Fechar</Text>
                            </TouchableOpacity>
                        </View>
                    </View>
                </Modal>

                {showBottomNav && (
                    <BottomNavBar
                        activeTab="schedule"
                        onTabPress={(tab) => {
                            if (tab === 'home') {
                                navigation.navigate('Home');
                            } else if (tab === 'settings') {
                                navigation.navigate('Settings');
                            } else if (tab === 'notifications') {
                                navigation.navigate('Notifications');
                            }
                        }}
                    />
                )}
            </SafeAreaView>
        </ImageBackground>
    );
}

const styles = StyleSheet.create({
    pageBackground: {
        flex: 1,
    },
    container: {
        flex: 1,
        backgroundColor: 'transparent',
        paddingTop: 104,
    },
    headerRow: {
        marginTop: 24,
        paddingHorizontal: 20,
        flexDirection: 'row',
        alignItems: 'center',
        justifyContent: 'space-between',
    },
    monthRow: {
        marginTop: 16,
        marginHorizontal: 20,
        flexDirection: 'row',
        justifyContent: 'space-between',
        alignItems: 'center',
        marginBottom: 10,
    },
    monthLabel: {
        color: '#0ea5e9',
        fontSize: 18,
        fontWeight: '800',
    },
    monthHelp: {
        color: '#64748b',
        marginTop: 2,
        fontSize: 11,
    },
    selectButton: {
        backgroundColor: '#ffffff',
        borderRadius: 18,
        paddingHorizontal: 16,
        paddingVertical: 10,
        shadowColor: '#000',
        shadowOpacity: 0.05,
        shadowOffset: { width: 0, height: 4 },
        shadowRadius: 12,
        elevation: 6,
    },
    selectText: {
        color: '#0f172a',
        fontWeight: '700',
    },
    monthSelector: {
        flex: 1,
        flexDirection: 'row',
        alignItems: 'center',
        justifyContent: 'center',
        backgroundColor: '#ffffff',
        borderRadius: 20,
        paddingVertical: 6,
        paddingHorizontal: 10,
        marginHorizontal: 10,
        shadowColor: '#000',
        shadowOpacity: 0.04,
        shadowOffset: { width: 0, height: 4 },
        shadowRadius: 8,
        elevation: 4,
    },
    monthSelectIcon: {
        fontSize: 18,
        color: '#94a3b8',
        marginLeft: 8,
    },
    monthArrow: {
        width: 38,
        height: 38,
        borderRadius: 14,
        backgroundColor: '#ffffff',
        alignItems: 'center',
        justifyContent: 'center',
    },
    monthArrowText: {
        color: '#0f172a',
        fontSize: 22,
        fontWeight: '700',
    },
    monthTitleWrapper: {
        alignItems: 'center',
    },
    weekdayText: {
        flexBasis: '13.5%',
        maxWidth: '13.5%',
        textAlign: 'center',
        color: '#64748b',
        fontSize: 12,
        fontWeight: '700',
    },
    calendarGrid: {
        flexDirection: 'row',
        flexWrap: 'wrap',
        justifyContent: 'space-between',
    },
    dayCellEmpty: {
        flexBasis: '13.5%',
        maxWidth: '13.5%',
        height: 44,
        marginBottom: 8,
    },
    dayCell: {
        flexBasis: '13.5%',
        maxWidth: '13.5%',
        height: 44,
        borderRadius: 16,
        alignItems: 'center',
        justifyContent: 'center',
        marginBottom: 8,
        backgroundColor: '#f8fafc',
    },
    dayCellActive: {
        backgroundColor: '#0ea5e9',
    },
    dayNumber: {
        fontSize: 15,
        fontWeight: '700',
        color: '#0f172a',
    },
    dayNumberActive: {
        color: '#ffffff',
    },
    dayDot: {
        width: 6,
        height: 6,
        borderRadius: 3,
        backgroundColor: '#ffffff',
        marginTop: 6,
    },
    dateCarousel: {
        paddingHorizontal: 18,
        paddingTop: 2,
        paddingBottom: 16,
    },
    dateItem: {
        width: 58,
        height: 62,
        borderRadius: 18,
        backgroundColor: '#ffffff',
        marginRight: 8,
        alignItems: 'center',
        justifyContent: 'center',
        paddingVertical: 4,
        shadowColor: '#000',
        shadowOpacity: 0.04,
        shadowOffset: { width: 0, height: 4 },
        shadowRadius: 8,
        elevation: 4,
        borderWidth: 1,
        borderColor: 'transparent',
    },
    dateItemActive: {
        backgroundColor: '#ffffff',
        borderColor: '#0ea5e9',
        borderWidth: 2,
    },
    dateItemPast: {
        backgroundColor: '#f1f5f9',
    },
    dateWeekday: {
        color: '#94a3b8',
        fontSize: 11,
        marginBottom: 4,
    },
    dateWeekdayActive: {
        color: '#0ea5e9',
    },
    dateWeekdayPast: {
        color: '#94a3b8',
        opacity: 0.5,
    },
    dateDay: {
        color: '#0f172a',
        fontSize: 16,
        fontWeight: '800',
    },
    dateDayActive: {
        color: '#0ea5e9',
    },
    dateDayPast: {
        color: '#0f172a',
        opacity: 0.5,
    },
    appointmentDot: {
        width: 6,
        height: 6,
        borderRadius: 3,
        backgroundColor: '#0ea5e9',
        marginTop: 8,
    },
    appointmentDotSelected: {
        backgroundColor: '#0ea5e9',
    },
    appointmentDotPast: {
        backgroundColor: '#0b4a88',
    },
    filterRow: {
        marginTop: 8,
        marginHorizontal: 20,
        marginBottom: 16,
        flexDirection: 'row',
        flexWrap: 'wrap',
    },
    filterChip: {
        paddingVertical: 8,
        paddingHorizontal: 12,
        borderRadius: 999,
        backgroundColor: '#ffffff',
        borderWidth: 1,
        borderColor: '#E2E8F0',
        marginRight: 8,
        marginBottom: 8,
    },
    filterChipActive: {
        backgroundColor: '#0EA5E9',
        borderColor: '#0EA5E9',
    },
    filterChipText: {
        fontSize: 12,
        fontWeight: '700',
        color: '#475569',
    },
    filterChipTextActive: {
        color: '#FFFFFF',
    },
    scheduleHeader: {
        marginTop: 8,
        marginHorizontal: 20,
        flexDirection: 'row',
        justifyContent: 'space-between',
        alignItems: 'center',
        marginBottom: 10,
    },
    scheduleColumn: {
        fontSize: 12,
        color: '#64748b',
        fontWeight: '700',
    },
    scheduleTitleHeader: {
        fontSize: 12,
        color: '#64748b',
        fontWeight: '700',
    },
    listContent: {
        paddingHorizontal: 20,
        paddingBottom: 140,
    },
    appointmentRow: {
        flexDirection: 'row',
        marginBottom: 16,
        alignItems: 'center',
    },
    timeColumn: {
        width: 50,
        alignItems: 'flex-start',
        justifyContent: 'center',
    },
    timeText: {
        fontSize: 14,
        fontWeight: '700',
        color: '#0f172a',
        textAlign: 'left',
    },
    timeSub: {
        color: '#94a3b8',
        fontSize: 12,
        marginTop: 2,
    },
    appointmentCard: {
        flex: 1,
        backgroundColor: '#ffffff',
        borderRadius: 26,
        paddingVertical: 22,
        paddingHorizontal: 18,
        marginLeft: 14,
        shadowColor: '#000',
        shadowOpacity: 0.08,
        shadowOffset: { width: 0, height: 10 },
        shadowRadius: 22,
        elevation: 10,
        borderLeftWidth: 6,
        borderLeftColor: '#FCD34D',
        borderWidth: 1,
        borderColor: '#E2E8F0',
        minHeight: 160,
    },
    cardHeader: {
        flexDirection: 'row',
        justifyContent: 'space-between',
        alignItems: 'flex-start',
        marginBottom: 12,
    },
    cardTitleSection: {
        flex: 1,
        marginRight: 12,
    },
    cardLabel: {
        fontSize: 18,
        fontWeight: '800',
        color: '#0f172a',
        marginBottom: 4,
    },
    doctorName: {
        fontSize: 14,
        fontWeight: '600',
        color: '#0ea5e9',
    },
    specialtyText: {
        fontSize: 15,
        fontWeight: '700',
        color: '#475569',
        marginBottom: 12,
    },
    cardDetails: {
        marginBottom: 8,
    },
    detailLabel: {
        fontSize: 13,
        fontWeight: '700',
        color: '#64748b',
        marginBottom: 2,
    },
    detailText: {
        fontSize: 14,
        color: '#374151',
        lineHeight: 18,
    },
    statusPill: {
        paddingVertical: 6,
        paddingHorizontal: 12,
        borderRadius: 14,
        borderWidth: 1,
        alignSelf: 'flex-start',
    },
    statusPillText: {
        fontSize: 12,
        fontWeight: '800',
        textTransform: 'uppercase',
    },
    patientName: {
        fontSize: 15,
        fontWeight: '700',
        color: '#475569',
        marginTop: 12,
    },
    emptyState: {
        paddingVertical: 40,
        alignItems: 'center',
    },
    emptyText: {
        color: '#94a3b8',
        fontSize: 14,
    },
    modalOverlay: {
        flex: 1,
        backgroundColor: 'rgba(15, 23, 42, 0.45)',
        justifyContent: 'center',
        alignItems: 'center',
        paddingHorizontal: 24,
    },
    actionModalContent: {
        width: '100%',
        backgroundColor: '#ffffff',
        borderRadius: 24,
        padding: 24,
        maxHeight: '80%',
    },
    actionModalTitle: {
        fontSize: 20,
        fontWeight: '800',
        color: '#0f172a',
        marginBottom: 20,
        textAlign: 'center',
    },
    modalInfoSection: {
        marginBottom: 16,
        paddingBottom: 12,
        borderBottomWidth: 1,
        borderBottomColor: '#f1f5f9',
    },
    modalInfoLabel: {
        fontSize: 12,
        fontWeight: '700',
        color: '#64748b',
        textTransform: 'uppercase',
        letterSpacing: 0.5,
        marginBottom: 4,
    },
    modalInfoValue: {
        fontSize: 16,
        fontWeight: '600',
        color: '#0f172a',
        lineHeight: 22,
    },
    actionButtonsRow: {
        flexDirection: 'row',
        justifyContent: 'space-between',
        marginTop: 24,
    },
    cancelButton: {
        flex: 1,
        marginRight: 10,
        backgroundColor: '#f8fafc',
        borderRadius: 16,
        paddingVertical: 16,
        alignItems: 'center',
        borderWidth: 1,
        borderColor: '#cbd5e1',
    },
    cancelButtonText: {
        color: '#0f172a',
        fontWeight: '700',
        fontSize: 16,
    },
    rescheduleButton: {
        flex: 1,
        backgroundColor: '#0ea5e9',
        borderRadius: 16,
        paddingVertical: 16,
        alignItems: 'center',
    },
    evaluateButton: {
        backgroundColor: '#10B981', // Green for evaluate
    },
    rescheduleButtonText: {
        color: '#ffffff',
        fontWeight: '700',
        fontSize: 16,
    },
    modalContent: {
        width: '100%',
        backgroundColor: '#ffffff',
        borderRadius: 24,
        padding: 16,
    },
    modalTitle: {
        fontSize: 18,
        fontWeight: '800',
        color: '#0f172a',
        marginBottom: 12,
    },
    modalHeaderRow: {
        flexDirection: 'row',
        alignItems: 'center',
        justifyContent: 'space-between',
        marginBottom: 10,
    },
    modalArrowButton: {
        width: 34,
        height: 34,
        borderRadius: 12,
        backgroundColor: '#f1f5f9',
        alignItems: 'center',
        justifyContent: 'center',
    },
    modalArrowText: {
        color: '#0f172a',
        fontSize: 18,
        fontWeight: '700',
    },
    weekHeader: {
        flexDirection: 'row',
        justifyContent: 'flex-start',
        marginBottom: 8,
    },
    weekdayText: {
        flexBasis: '13.5%',
        maxWidth: '13.5%',
        textAlign: 'center',
        color: '#64748b',
        fontSize: 12,
        fontWeight: '700',
    },
    calendarGrid: {
        flexDirection: 'row',
        flexWrap: 'wrap',
        justifyContent: 'flex-start',
    },
    dayCellEmpty: {
        flexBasis: '13.5%',
        maxWidth: '13.5%',
        height: 52,
        marginBottom: 10,
        marginRight: '0.7%',
    },
    dayCell: {
        flexBasis: '13.5%',
        maxWidth: '13.5%',
        height: 52,
        borderRadius: 16,
        alignItems: 'center',
        justifyContent: 'center',
        marginBottom: 10,
        marginRight: '0.7%',
        backgroundColor: '#f8fafc',
    },
    dayCellPast: {
        backgroundColor: '#d1d5db',
    },
    dayCellActive: {
        backgroundColor: '#0ea5e9',
    },
    dayNumber: {
        fontSize: 15,
        fontWeight: '700',
        color: '#0f172a',
    },
    dayNumberPast: {
        color: '#475569',
    },
    dayNumberActive: {
        color: '#ffffff',
    },
    dayDot: {
        width: 6,
        height: 6,
        borderRadius: 3,
        backgroundColor: '#0ea5e9',
        marginTop: 4,
    },
    dayDotSelected: {
        backgroundColor: '#ffffff',
    },
    dayDotPast: {
        backgroundColor: '#0b4a88',
    },
    closeButton: {
        marginTop: 16,
        backgroundColor: '#0ea5e9',
        borderRadius: 16,
        paddingVertical: 12,
        alignItems: 'center',
    },
    closeButtonText: {
        color: '#ffffff',
        fontSize: 15,
        fontWeight: '700',
    },
    cancelAppointmentButton: {
        flex: 1,
        marginHorizontal: 6,
        backgroundColor: '#dc2626',
        borderRadius: 16,
        paddingVertical: 14,
        alignItems: 'center',
        borderWidth: 1,
        borderColor: '#b91c1c',
    },
    cancelAppointmentButtonText: {
        color: '#ffffff',
        fontWeight: '700',
        fontSize: 14,
    },
    cancelModalContent: {
        width: '90%',
        backgroundColor: '#ffffff',
        borderRadius: 24,
        padding: 24,
        alignItems: 'center',
    },
    cancelModalIcon: {
        width: 60,
        height: 60,
        borderRadius: 30,
        backgroundColor: '#fef3c7',
        alignItems: 'center',
        justifyContent: 'center',
        marginBottom: 16,
    },
    cancelModalIconText: {
        fontSize: 24,
    },
    cancelModalTitle: {
        fontSize: 20,
        fontWeight: '800',
        color: '#0f172a',
        marginBottom: 12,
        textAlign: 'center',
    },
    cancelModalMessage: {
        fontSize: 16,
        color: '#374151',
        textAlign: 'center',
        lineHeight: 22,
        marginBottom: 20,
    },
    cancelModalDetails: {
        backgroundColor: '#f8fafc',
        borderRadius: 12,
        padding: 16,
        width: '100%',
        marginBottom: 24,
    },
    cancelModalDetailText: {
        fontSize: 14,
        color: '#64748b',
        textAlign: 'center',
        marginBottom: 4,
    },
    cancelModalButtonsRow: {
        flexDirection: 'row',
        justifyContent: 'space-between',
        width: '100%',
    },
    cancelModalCancelButton: {
        flex: 1,
        marginRight: 8,
        backgroundColor: '#f1f5f9',
        borderRadius: 16,
        paddingVertical: 14,
        alignItems: 'center',
        borderWidth: 1,
        borderColor: '#cbd5e1',
    },
    cancelModalCancelText: {
        color: '#0f172a',
        fontWeight: '700',
        fontSize: 14,
    },
    cancelModalConfirmButton: {
        flex: 1,
        marginLeft: 8,
        backgroundColor: '#dc2626',
        borderRadius: 16,
        paddingVertical: 14,
        alignItems: 'center',
    },
    cancelModalConfirmText: {
        color: '#ffffff',
        fontWeight: '700',
        fontSize: 14,
    },
    rescheduleInfo: {
        fontSize: 14,
        color: '#64748b',
        textAlign: 'center',
        marginBottom: 4,
    },
    dateTimeSelector: {
        marginBottom: 20,
    },
    dateTimeButton: {
        backgroundColor: '#ffffff',
        borderRadius: 12,
        paddingVertical: 16,
        paddingHorizontal: 20,
        flexDirection: 'row',
        justifyContent: 'space-between',
        alignItems: 'center',
        shadowColor: '#000',
        shadowOpacity: 0.04,
        shadowOffset: { width: 0, height: 4 },
        shadowRadius: 10,
        elevation: 4,
    },
    dateTimeButtonText: {
        fontSize: 16,
        color: '#0f172a',
        fontWeight: '600',
    },
    dateTimeButtonIcon: {
        fontSize: 18,
    },
});
