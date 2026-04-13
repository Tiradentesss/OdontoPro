import React, { useState } from 'react';
import {
    View,
    Text,
    StyleSheet,
    TouchableOpacity,
    SafeAreaView,
    ScrollView,
    Modal,
    ImageBackground,
} from 'react-native';
import ScheduleHeaderNoBack from '../components/ScheduleHeaderNoBack';
import BottomNavBar from '../components/BottomNavBar';

const monthNames = ['Jan', 'Fev', 'Mar', 'Abr', 'Mai', 'Jun', 'Jul', 'Ago', 'Set', 'Out', 'Nov', 'Dez'];
const weekdays = ['D', 'S', 'T', 'Q', 'Q', 'S', 'S'];

const appointmentDays = ['2025-12-22'];

const appointmentsByDate = {
    '2025-12-22': [
        {
            id: '1',
            time: '09:00',
            endTime: '09:30',
            clinic: 'Clínica Sorriso Vivo',
            specialty: 'Ortodontia',
            confirmed: true,
        },
        {
            id: '2',
            time: '12:00',
            endTime: '12:30',
            clinic: 'Clínica Sorriso Vivo',
            specialty: 'Odontopediatria',
            confirmed: false,
        },
        {
            id: '3',
            time: '14:00',
            endTime: '14:30',
            clinic: 'Clínica Sorriso Vivo',
            specialty: 'Periodontia',
            confirmed: false,
        },
    ],
};

const getMonthDays = (year, month) => {
    const days = new Date(year, month, 0).getDate();
    return Array.from({ length: days }, (_, index) => {
        const day = index + 1;
        const id = `${year}-${String(month).padStart(2, '0')}-${String(day).padStart(2, '0')}`;
        const date = new Date(year, month - 1, day);
        return {
            id,
            day: String(day),
            weekday: weekdays[date.getDay()],
            hasAppointments: appointmentDays.includes(id),
        };
    });
};

export default function ScheduleScreen({ navigation }) {
    const [search, setSearch] = useState('');
    const usuario = 'Paciente';
    const [currentMonth, setCurrentMonth] = useState({ year: 2025, month: 12 });
    const [selectedDate, setSelectedDate] = useState('2025-12-22');
    const [pickerVisible, setPickerVisible] = useState(false);
    const [actionModalVisible, setActionModalVisible] = useState(false);
    const [selectedAppointment, setSelectedAppointment] = useState(null);
    const monthDays = getMonthDays(currentMonth.year, currentMonth.month);
    const calendarStartOffset = new Date(currentMonth.year, currentMonth.month - 1, 1).getDay();
    const calendarCells = [...Array(calendarStartOffset).fill(null), ...monthDays];
    const appointments = appointmentsByDate[selectedDate] ?? [];

    const monthLabel = `${monthNames[currentMonth.month - 1]}, ${currentMonth.year}`;

    const setMonth = (year, month) => {
        setCurrentMonth({ year, month });
        setSelectedDate(`${year}-${String(month).padStart(2, '0')}-01`);
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
        const lastDayOfMonth = monthDays[monthDays.length - 1].id;
        if (dateId === lastDayOfMonth) {
            goNextMonth();
            return;
        }
        setSelectedDate(dateId);
    };

    const handleOpenAppointmentActions = (item) => {
        setSelectedAppointment(item);
        setActionModalVisible(true);
    };

    const closeActionModal = () => {
        setActionModalVisible(false);
        setSelectedAppointment(null);
    };

    return (
        <ImageBackground
            source={require('../../assets/imagem background.png')}
            style={styles.pageBackground}
            resizeMode="cover"
        >
            <SafeAreaView style={styles.container}>
                <ScheduleHeaderNoBack title="Agendamentos" onNotificationPress={() => {}} />

                <View style={styles.monthRow}> 
                    <TouchableOpacity style={styles.monthArrow} onPress={goPreviousMonth} activeOpacity={0.8}>
                        <Text style={styles.monthArrowText}>‹</Text>
                    </TouchableOpacity>
                    <TouchableOpacity style={styles.monthSelector} onPress={() => setPickerVisible(true)} activeOpacity={0.8}>
                        <View style={styles.monthTitleWrapper}>
                            <Text style={styles.monthLabel}>{monthLabel}</Text>
                            <Text style={styles.monthHelp}>Clique no mês para abrir o calendário</Text>
                        </View>
                    </TouchableOpacity>
                    <TouchableOpacity style={styles.monthArrow} onPress={goNextMonth} activeOpacity={0.8}>
                        <Text style={styles.monthArrowText}>›</Text>
                    </TouchableOpacity>
                </View>

                <ScrollView
                    horizontal
                    showsHorizontalScrollIndicator={false}
                    contentContainerStyle={styles.dateCarousel}
                >
                    {monthDays.map((date) => {
                        const isSelected = date.id === selectedDate;
                        return (
                            <TouchableOpacity
                                key={date.id}
                                style={[styles.dateItem, isSelected && styles.dateItemActive]}
                                activeOpacity={0.85}
                                onPress={() => handleSelectDate(date.id)}
                            >
                                <Text style={[styles.dateWeekday, isSelected && styles.dateWeekdayActive]}>{date.weekday}</Text>
                                <Text style={[styles.dateDay, isSelected && styles.dateDayActive]}>{date.day}</Text>
                                {date.hasAppointments && (
                                    <View style={[styles.appointmentDot, isSelected && styles.appointmentDotSelected]} />
                                )}
                            </TouchableOpacity>
                        );
                    })}
                </ScrollView>

                <View style={styles.scheduleHeader}>
                    <Text style={styles.scheduleColumn}>Hora</Text>
                    <Text style={styles.scheduleTitleHeader}>Consultas do Dia</Text>
                </View>

                <ScrollView contentContainerStyle={styles.listContent} showsVerticalScrollIndicator={false}>
                    {appointments.map((item) => (
                        <View key={item.id} style={styles.appointmentRow}>
                            <View style={styles.timeColumn}>
                                <Text style={styles.timeText}>{item.time}</Text>
                                <Text style={styles.timeSub}>{item.endTime}</Text>
                            </View>
                            <View style={styles.appointmentCard}>
                                <View style={styles.cardHeader}>
                                    <Text style={styles.cardLabel}>{item.clinic}</Text>
                                    <View style={styles.cardRightActions}>
                                        <View style={[styles.statusDot, item.confirmed && styles.statusDotActive]} />
                                        <TouchableOpacity
                                            style={styles.actionMenuButton}
                                            onPress={() => handleOpenAppointmentActions(item)}
                                            activeOpacity={0.8}
                                        >
                                            <Text style={styles.actionMenuText}>...</Text>
                                        </TouchableOpacity>
                                    </View>
                                </View>
                                <Text style={styles.patientName}>{item.specialty}</Text>
                            </View>
                        </View>
                    ))}
                    {appointments.length === 0 && (
                        <View style={styles.emptyState}>
                            <Text style={styles.emptyText}>Nenhuma consulta agendada para este dia.</Text>
                        </View>
                    )}
                </ScrollView>

                <Modal visible={actionModalVisible} transparent animationType="fade">
                    <View style={styles.modalOverlay}>
                        <View style={styles.actionModalContent}>
                            <Text style={styles.actionModalTitle}>Informações da consulta</Text>
                            <Text style={styles.actionModalLabel}>{selectedAppointment?.clinic}</Text>
                            <Text style={styles.actionModalSubtitle}>{selectedAppointment?.specialty}</Text>
                            <Text style={styles.actionModalTime}>{selectedAppointment?.time} - {selectedAppointment?.endTime}</Text>
                            <View style={styles.actionButtonsRow}>
                                <TouchableOpacity style={styles.cancelButton} activeOpacity={0.8} onPress={closeActionModal}>
                                    <Text style={styles.cancelButtonText}>Cancelar</Text>
                                </TouchableOpacity>
                                <TouchableOpacity style={styles.rescheduleButton} activeOpacity={0.8} onPress={closeActionModal}>
                                    <Text style={styles.rescheduleButtonText}>Reagendar</Text>
                                </TouchableOpacity>
                            </View>
                            <TouchableOpacity style={styles.closeButton} onPress={closeActionModal} activeOpacity={0.8}>
                                <Text style={styles.closeButtonText}>Fechar</Text>
                            </TouchableOpacity>
                        </View>
                    </View>
                </Modal>

                <Modal visible={pickerVisible} transparent animationType="fade">
                    <View style={styles.modalOverlay}>
                        <View style={styles.modalContent}>
                            <View style={styles.modalHeaderRow}>
                                <TouchableOpacity style={styles.modalArrowButton} onPress={goPreviousMonth} activeOpacity={0.8}>
                                    <Text style={styles.modalArrowText}>‹</Text>
                                </TouchableOpacity>
                                <Text style={styles.modalTitle}>{monthLabel}</Text>
                                <TouchableOpacity style={styles.modalArrowButton} onPress={goNextMonth} activeOpacity={0.8}>
                                    <Text style={styles.modalArrowText}>›</Text>
                                </TouchableOpacity>
                            </View>
                            <View style={styles.weekHeader}>
                                {weekdays.map((weekday) => (
                                    <Text key={weekday} style={styles.weekdayText}>{weekday}</Text>
                                ))}
                            </View>
                            <View style={styles.calendarGrid}>
                                {calendarCells.map((date, index) => {
                                    if (!date) {
                                        return <View key={`blank-${index}`} style={styles.dayCellEmpty} />;
                                    }
                                    const isSelected = date.id === selectedDate;
                                    return (
                                        <TouchableOpacity
                                            key={date.id}
                                            style={[styles.dayCell, isSelected && styles.dayCellActive]}
                                            activeOpacity={0.85}
                                            onPress={() => {
                                                handleSelectDate(date.id);
                                                setPickerVisible(false);
                                            }}
                                        >
                                            <Text style={[styles.dayNumber, isSelected && styles.dayNumberActive]}>{date.day}</Text>
                                            {date.hasAppointments && <View style={styles.dayDot} />}
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

                <BottomNavBar
                    activeTab="schedule"
                    onTabPress={(tab) => {
                        if (tab === 'home') {
                            navigation.navigate('Home');
                        }
                    }}
                />
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
        paddingTop: 120,
    },
    headerRow: {
        marginTop: 24,
        paddingHorizontal: 20,
        flexDirection: 'row',
        alignItems: 'center',
        justifyContent: 'space-between',
    },
    monthRow: {
        marginTop: 24,
        marginHorizontal: 20,
        flexDirection: 'row',
        justifyContent: 'space-between',
        alignItems: 'center',
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
        width: 32,
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
        width: 40,
        height: 44,
        marginBottom: 8,
    },
    dayCell: {
        width: 40,
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
        paddingTop: 6,
        paddingBottom: 4,
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
    },
    dateItemActive: {
        backgroundColor: '#0ea5e9',
    },
    dateWeekday: {
        color: '#94a3b8',
        fontSize: 11,
        marginBottom: 4,
    },
    dateWeekdayActive: {
        color: '#ffffff',
    },
    dateDay: {
        color: '#0f172a',
        fontSize: 16,
        fontWeight: '800',
    },
    dateDayActive: {
        color: '#ffffff',
    },
    appointmentDot: {
        width: 6,
        height: 6,
        borderRadius: 3,
        backgroundColor: '#0ea5e9',
        marginTop: 8,
    },
    appointmentDotSelected: {
        backgroundColor: '#ffffff',
    },
    scheduleHeader: {
        marginTop: 12,
        marginHorizontal: 20,
        flexDirection: 'row',
        justifyContent: 'space-between',
        alignItems: 'center',
        marginBottom: 8,
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
    },
    timeColumn: {
        width: 68,
        alignItems: 'flex-start',
    },
    timeText: {
        fontSize: 18,
        fontWeight: '700',
        color: '#0f172a',
    },
    timeSub: {
        color: '#94a3b8',
        marginTop: 6,
    },
    appointmentCard: {
        flex: 1,
        backgroundColor: '#ffffff',
        borderRadius: 24,
        padding: 16,
        marginLeft: 12,
        shadowColor: '#000',
        shadowOpacity: 0.05,
        shadowOffset: { width: 0, height: 6 },
        shadowRadius: 16,
        elevation: 6,
    },
    cardHeader: {
        flexDirection: 'row',
        justifyContent: 'space-between',
        alignItems: 'center',
        marginBottom: 10,
    },
    cardRightActions: {
        flexDirection: 'row',
        alignItems: 'center',
    },
    actionMenuButton: {
        marginLeft: 10,
        width: 34,
        height: 34,
        borderRadius: 12,
        backgroundColor: '#f1f5f9',
        alignItems: 'center',
        justifyContent: 'center',
    },
    actionMenuText: {
        fontSize: 18,
        color: '#0f172a',
        fontWeight: '700',
    },
    cardLabel: {
        fontSize: 14,
        fontWeight: '700',
        color: '#0f172a',
    },
    statusDot: {
        width: 10,
        height: 10,
        borderRadius: 5,
        backgroundColor: '#dcdcdc',
    },
    statusDotActive: {
        backgroundColor: '#34d399',
    },
    patientName: {
        fontSize: 15,
        fontWeight: '700',
        color: '#0f172a',
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
        padding: 20,
    },
    actionModalTitle: {
        fontSize: 18,
        fontWeight: '800',
        color: '#0f172a',
        marginBottom: 10,
    },
    actionModalLabel: {
        fontSize: 16,
        fontWeight: '700',
        color: '#0f172a',
        marginBottom: 4,
    },
    actionModalSubtitle: {
        fontSize: 14,
        color: '#64748b',
        marginBottom: 8,
    },
    actionModalTime: {
        fontSize: 14,
        color: '#64748b',
        marginBottom: 18,
    },
    actionButtonsRow: {
        flexDirection: 'row',
        justifyContent: 'space-between',
        marginBottom: 14,
    },
    cancelButton: {
        flex: 1,
        marginRight: 10,
        backgroundColor: '#f8fafc',
        borderRadius: 16,
        paddingVertical: 14,
        alignItems: 'center',
        borderWidth: 1,
        borderColor: '#cbd5e1',
    },
    cancelButtonText: {
        color: '#0f172a',
        fontWeight: '700',
    },
    rescheduleButton: {
        flex: 1,
        backgroundColor: '#0ea5e9',
        borderRadius: 16,
        paddingVertical: 14,
        alignItems: 'center',
    },
    rescheduleButtonText: {
        color: '#ffffff',
        fontWeight: '700',
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
        justifyContent: 'space-between',
        marginBottom: 8,
    },
    weekdayText: {
        width: 32,
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
    dayCell: {
        width: 40,
        height: 52,
        borderRadius: 16,
        alignItems: 'center',
        justifyContent: 'center',
        marginBottom: 10,
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
        marginTop: 4,
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
});
