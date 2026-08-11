import React, { useEffect, useState } from 'react';
import {
  View,
  Text,
  StyleSheet,
  TouchableOpacity,
  SafeAreaView,
  Platform,
  StatusBar,
  Alert,
} from 'react-native';

import { Feather } from '@expo/vector-icons';

import { useTheme } from '../components/ThemeContext';
import {
  getProfessionalAppointments,
  updateAppointment,
} from '../services/api';

import { useAuth } from '../context/AuthContext';

export default function AppointmentDetailsScreen({
  route,
  navigation,
}) {
  const {
    patientName,
    allowReschedule = true,
    appointment: routeAppointment,
    isPatientView = false,
  } = route.params || {
    patientName: 'Victor Araújo',
  };

  const [appointment, setAppointment] = useState(
    routeAppointment || null
  );

  const [status, setStatus] = useState(
    routeAppointment?.status || 'pendente'
  );

  const { user } = useAuth();

  const { isDarkMode, colors } = useTheme();

  // =========================================================
  // CARREGAR CONSULTA
  // =========================================================

  useEffect(() => {
    const loadAppointment = async () => {
      // Se a consulta veio diretamente pela navegação,
      // utiliza os dados recebidos.
      if (routeAppointment?.id) {
        setAppointment(routeAppointment);
        setStatus(
          (routeAppointment.status || 'pendente')
            .toString()
            .toLowerCase()
        );
      }

      // Se for visualização do paciente, não precisa
      // buscar novamente as consultas do profissional.
      if (isPatientView) {
        return;
      }

      if (!route.params?.id || !user?.id) {
        return;
      }

      try {
        const data = await getProfessionalAppointments({
          medico_id: user.id,
        });

        const found = Array.isArray(data)
          ? data.find(
              (item) =>
                String(item.id) === String(route.params.id)
            )
          : null;

        setAppointment(found || null);

        setStatus(
          (found?.status || 'pendente')
            .toString()
            .toLowerCase()
        );
      } catch (error) {
        console.log(
          'Error loading appointment details:',
          error
        );
      }
    };

    loadAppointment();
  }, [
    routeAppointment?.id,
    route.params?.id,
    user?.id,
    isPatientView,
  ]);

  // =========================================================
  // INFORMAÇÕES VISUAIS DO STATUS
  // =========================================================

  const getStatusInfo = (statusValue) => {
    const normalized = (statusValue || '')
      .toString()
      .toLowerCase();

    // CANCELADA
    if (normalized === 'cancelada') {
      return {
        label: 'CANCELADA',
        bg: isDarkMode ? '#581c1c' : '#fee2e2',
        text: isDarkMode ? '#fca5a5' : '#b91c1c',
        icon: 'x-circle',
        iconColor: isDarkMode ? '#fecaca' : '#b91c1c',
      };
    }

    // REALIZADA
    if (
      normalized === 'realizada' ||
      normalized === 'completa'
    ) {
      return {
        label: 'REALIZADA',
        bg: isDarkMode ? '#064e3b' : '#dcfce7',
        text: isDarkMode ? '#86efac' : '#047857',
        icon: 'check-circle',
        iconColor: isDarkMode ? '#86efac' : '#047857',
      };
    }

    // CONFIRMADA
    if (normalized === 'confirmada') {
      return {
        label: 'CONFIRMADA',
        bg: isDarkMode ? '#78350f' : '#fef3c7',
        text: isDarkMode ? '#fde68a' : '#b45309',
        icon: 'check-circle',
        iconColor: isDarkMode ? '#fde68a' : '#b45309',
      };
    }

    // PERDIDA
    if (normalized === 'perdida') {
      return {
        label: 'PERDIDA',
        bg: isDarkMode ? '#111827' : '#e5e7eb',
        text: isDarkMode ? '#f8fafc' : '#111827',
        icon: 'x-circle',
        iconColor: isDarkMode ? '#f8fafc' : '#111827',
      };
    }

    // AGENDADA / PADRÃO
    return {
      label: 'AGENDADA',
      bg: isDarkMode ? '#78350f' : '#fef3c7',
      text: isDarkMode ? '#fde68a' : '#b45309',
      icon: 'alert-circle',
      iconColor: isDarkMode ? '#fde68a' : '#b45309',
    };
  };

  // =========================================================
  // STATUS NORMALIZADO
  // =========================================================

  const normalizedStatus = (status || '')
    .toString()
    .toLowerCase();

  const statusInfo = getStatusInfo(status);

  // =========================================================
  // REGRAS DOS BOTÕES
  // =========================================================

  // Só pode confirmar se estiver AGENDADA.
  const canConfirm =
    normalizedStatus === 'agendada';

  // Só pode marcar como realizada se estiver CONFIRMADA.
  const canMarkAsCompleted =
    normalizedStatus === 'confirmada';

  // Só pode reagendar enquanto estiver AGENDADA.
  const canReschedule =
    normalizedStatus === 'agendada';

  // Só pode cancelar enquanto estiver AGENDADA.
  const canCancel =
    normalizedStatus === 'agendada';

  // =========================================================
  // DATA E HORÁRIO
  // =========================================================

  const appointmentDate = appointment?.data_hora
    ? new Date(appointment.data_hora)
    : null;

  const appointmentDateLabel =
    appointmentDate?.toLocaleDateString('pt-BR', {
      day: '2-digit',
      month: 'long',
      year: 'numeric',
    });

  const appointmentTimeLabel =
    appointmentDate?.toLocaleTimeString('pt-BR', {
      hour: '2-digit',
      minute: '2-digit',
    });

  const appointmentEndTimeLabel = appointmentDate
    ? new Date(
        appointmentDate.getTime() + 30 * 60000
      ).toLocaleTimeString('pt-BR', {
        hour: '2-digit',
        minute: '2-digit',
      })
    : null;

  const appointmentReason =
    appointment?.observacoes ||
    route.params?.motivo ||
    'Consulta';

  // =========================================================
  // CONFIRMAR CONSULTA
  // =========================================================

  const handleConfirm = async () => {
    try {
      if (!appointment?.id) {
        Alert.alert(
          'Erro',
          'Consulta não encontrada.'
        );
        return;
      }

      // IMPORTANTE:
      // Confirmar NÃO significa que a consulta foi realizada.
      // Aqui o status passa de AGENDADA -> CONFIRMADA.
      await updateAppointment(appointment.id, {
        status: 'confirmada',
      });

      // Atualiza imediatamente a tela.
      setAppointment((prev) =>
        prev
          ? {
              ...prev,
              status: 'confirmada',
            }
          : prev
      );

      setStatus('confirmada');

      // Mantém sua navegação atual.
      navigation.navigate('SuccessScreen');
    } catch (error) {
      console.log(
        'Erro ao confirmar consulta:',
        error
      );

      Alert.alert(
        'Erro',
        'Não foi possível confirmar a consulta.'
      );
    }
  };

  // =========================================================
  // MARCAR CONSULTA COMO REALIZADA
  // =========================================================

  const handleMarkAsCompleted = async () => {
    try {
      if (!appointment?.id) {
        Alert.alert(
          'Erro',
          'Consulta não encontrada.'
        );
        return;
      }

      // Aqui sim a consulta passa de
      // CONFIRMADA -> REALIZADA.
      await updateAppointment(appointment.id, {
        status: 'realizada',
      });

      // Atualiza imediatamente a tela.
      setAppointment((prev) =>
        prev
          ? {
              ...prev,
              status: 'realizada',
            }
          : prev
      );

      setStatus('realizada');

      // Mantém sua navegação atual.
      navigation.navigate('SuccessScreen');
    } catch (error) {
      console.log(
        'Erro ao marcar consulta como realizada:',
        error
      );

      Alert.alert(
        'Erro',
        'Não foi possível marcar a consulta como realizada.'
      );
    }
  };

  // =========================================================
  // REAGENDAR
  // =========================================================

  const handleReschedule = () => {
    navigation.navigate('RescheduleScreen', {
      patientName:
        appointment?.nome || patientName,
      appointment,
    });
  };

  // =========================================================
  // CANCELAR
  // =========================================================

  const handleCancelAppointment = async () => {
    try {
      if (!appointment?.id) {
        Alert.alert(
          'Erro',
          'Consulta não encontrada.'
        );
        return;
      }

      await updateAppointment(appointment.id, {
        status: 'cancelada',
      });

      setAppointment((prev) =>
        prev
          ? {
              ...prev,
              status: 'cancelada',
            }
          : prev
      );

      setStatus('cancelada');
    } catch (error) {
      console.log(
        'Erro ao cancelar consulta:',
        error
      );

      Alert.alert(
        'Erro',
        'Não foi possível cancelar a consulta.'
      );
    }
  };

  // =========================================================
  // TELA
  // =========================================================

  return (
    <SafeAreaView
      style={[
        styles.container,
        {
          backgroundColor: colors.container,
        },
      ]}
    >
      <StatusBar
        barStyle={
          isDarkMode
            ? 'light-content'
            : 'dark-content'
        }
        backgroundColor={colors.card}
        translucent={false}
      />

      {/* =====================================================
          CABEÇALHO
      ====================================================== */}

      <View
        style={[
          styles.header,
          {
            backgroundColor: colors.card,
            borderColor: colors.border,
          },
        ]}
      >
        <TouchableOpacity
          style={[
            styles.backButton,
            {
              backgroundColor:
                colors.backButtonBg,
            },
          ]}
          onPress={() => navigation.goBack()}
          activeOpacity={0.6}
        >
          <Feather
            name="arrow-left"
            size={22}
            color={colors.text}
          />
        </TouchableOpacity>

        <Text
          style={[
            styles.headerTitle,
            {
              color: colors.text,
            },
          ]}
        >
          Detalhes da Consulta
        </Text>

        <View style={styles.headerSpacer} />
      </View>

      {/* =====================================================
          CONTEÚDO
      ====================================================== */}

      <View style={styles.content}>
        {/* PACIENTE */}

        <View style={styles.patientMetaContainer}>
          <Text style={styles.patientLabel}>
            Paciente
          </Text>

          <Text
            style={[
              styles.patientName,
              {
                color: colors.text,
              },
            ]}
          >
            {patientName}
          </Text>
        </View>

        {/* INFORMAÇÕES GERAIS */}

        <Text style={styles.sectionTitle}>
          Informações Gerais
        </Text>

        <View
          style={[
            styles.appointmentCard,
            {
              backgroundColor: colors.card,
              borderColor: colors.border,
            },
          ]}
        >
          {/* DATA */}

          <View style={styles.infoRow}>
            <View
              style={[
                styles.iconBox,
                {
                  backgroundColor: isDarkMode
                    ? '#1E3A8A'
                    : '#EFF6FF',
                },
              ]}
            >
              <Feather
                name="calendar"
                size={18}
                color={
                  isDarkMode
                    ? '#60A5FA'
                    : '#163783'
                }
              />
            </View>

            <View style={styles.infoTextContainer}>
              <Text style={styles.infoLabel}>
                Data do Atendimento
              </Text>

              <Text
                style={[
                  styles.infoValue,
                  {
                    color: colors.text,
                  },
                ]}
              >
                {appointmentDateLabel ||
                  'Data a definir'}
              </Text>
            </View>
          </View>

          <View
            style={[
              styles.divider,
              {
                backgroundColor: colors.border,
              },
            ]}
          />

          {/* HORÁRIO */}

          <View style={styles.infoRow}>
            <View
              style={[
                styles.iconBox,
                {
                  backgroundColor: isDarkMode
                    ? '#334155'
                    : '#F1F5F9',
                },
              ]}
            >
              <Feather
                name="clock"
                size={18}
                color={
                  isDarkMode
                    ? '#94A3B8'
                    : '#475569'
                }
              />
            </View>

            <View style={styles.infoTextContainer}>
              <Text style={styles.infoLabel}>
                Horário Marcado
              </Text>

              <Text
                style={[
                  styles.infoValue,
                  {
                    color: colors.text,
                  },
                ]}
              >
                {appointmentTimeLabel &&
                appointmentEndTimeLabel
                  ? `${appointmentTimeLabel} — ${appointmentEndTimeLabel}`
                  : 'Horário a definir'}
              </Text>
            </View>
          </View>

          <View
            style={[
              styles.divider,
              {
                backgroundColor: colors.border,
              },
            ]}
          />

          {/* STATUS */}

          <View style={styles.infoRow}>
            <View
              style={[
                styles.iconBox,
                {
                  backgroundColor:
                    statusInfo.bg,
                },
              ]}
            >
              <Feather
                name={statusInfo.icon}
                size={18}
                color={statusInfo.iconColor}
              />
            </View>

            <View style={styles.infoTextContainer}>
              <Text style={styles.infoLabel}>
                Status da Confirmação
              </Text>

              <Text
                style={[
                  styles.infoValue,
                  {
                    color: statusInfo.text,
                  },
                ]}
              >
                {statusInfo.label}
              </Text>
            </View>
          </View>
        </View>

        {/* MOTIVO */}

        <Text style={styles.sectionTitle}>
          Motivo / Sintomas
        </Text>

        <View
          style={[
            styles.reasonCard,
            {
              backgroundColor: colors.card,
              borderColor: colors.border,
              borderLeftColor:
                colors.brandBlue,
            },
          ]}
        >
          <Text
            style={[
              styles.reasonText,
              {
                color: isDarkMode
                  ? '#94A3B8'
                  : '#334155',
              },
            ]}
          >
            {appointmentReason}
          </Text>
        </View>

        {/* ESPAÇADOR */}

        <View style={styles.spacer} />

        {/* =================================================
            BOTÕES
        ================================================== */}

        <View style={styles.footerActions}>
          {/* -------------------------------------------------
              AGENDADA:
              CONFIRMAR
          -------------------------------------------------- */}

          {canConfirm && !isPatientView && (
            <TouchableOpacity
              style={[
                styles.confirmButton,
                isDarkMode && {
                  shadowColor: '#000000',
                  backgroundColor: '#059669',
                },
              ]}
              activeOpacity={0.8}
              onPress={handleConfirm}
            >
              <Feather
                name="check"
                size={16}
                color="#FFFFFF"
                style={{
                  marginRight: 8,
                }}
              />

              <Text
                style={styles.confirmButtonText}
              >
                Confirmar Consulta
              </Text>
            </TouchableOpacity>
          )}

          {/* -------------------------------------------------
              CONFIRMADA:
              MARCAR COMO REALIZADA

              Quando o status for confirmada,
              TODOS os outros botões desaparecem.
          -------------------------------------------------- */}

          {canMarkAsCompleted &&
            !isPatientView && (
              <TouchableOpacity
                style={[
                  styles.completedButton,
                  isDarkMode && {
                    shadowColor: '#000000',
                    backgroundColor: '#059669',
                  },
                ]}
                activeOpacity={0.8}
                onPress={
                  handleMarkAsCompleted
                }
              >
                <Feather
                  name="check-circle"
                  size={17}
                  color="#FFFFFF"
                  style={{
                    marginRight: 8,
                  }}
                />

                <Text
                  style={
                    styles.confirmButtonText
                  }
                >
                  Finalizar Consulta
                </Text>
              </TouchableOpacity>
            )}

          {/* -------------------------------------------------
              AGENDADA:
              REAGENDAR
          -------------------------------------------------- */}

          {allowReschedule &&
            canReschedule && (
              <TouchableOpacity
                style={[
                  styles.rescheduleButton,
                  {
                    backgroundColor:
                      colors.card,
                    borderColor:
                      colors.border,
                  },
                ]}
                activeOpacity={0.7}
                onPress={handleReschedule}
              >
                <Feather
                  name="calendar"
                  size={16}
                  color={
                    colors.mutedText
                  }
                  style={{
                    marginRight: 8,
                  }}
                />

                <Text
                  style={[
                    styles.rescheduleButtonText,
                    {
                      color: colors.text,
                    },
                  ]}
                >
                  Reagendar Consulta
                </Text>
              </TouchableOpacity>
            )}

          {/* -------------------------------------------------
              AGENDADA:
              CANCELAR
          -------------------------------------------------- */}

          {canCancel && (
            <TouchableOpacity
              style={styles.cancelButton}
              activeOpacity={0.8}
              onPress={
                handleCancelAppointment
              }
            >
              <Feather
                name="x-circle"
                size={16}
                color="#FFFFFF"
                style={{
                  marginRight: 8,
                }}
              />

              <Text
                style={
                  styles.cancelButtonText
                }
              >
                Cancelar Consulta
              </Text>
            </TouchableOpacity>
          )}
        </View>
      </View>
    </SafeAreaView>
  );
}

// =============================================================
// DESIGN SYSTEM & ESTILOS
// =============================================================

const styles = StyleSheet.create({
  container: {
    flex: 1,
  },

  // ===========================================================
  // HEADER
  // ===========================================================

  header: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'space-between',
    paddingHorizontal: 24,
    paddingTop:
      Platform.OS === 'android'
        ? StatusBar.currentHeight + 12
        : 12,
    paddingBottom: 16,
    borderBottomWidth: 1,
  },

  backButton: {
    padding: 8,
    borderRadius: 12,
  },

  headerTitle: {
    fontSize: 16,
    fontWeight: '700',
  },

  headerSpacer: {
    width: 38,
  },

  // ===========================================================
  // CONTENT
  // ===========================================================

  content: {
    flex: 1,
    paddingHorizontal: 24,
    paddingTop: 20,
  },

  patientMetaContainer: {
    marginBottom: 24,
  },

  patientLabel: {
    fontSize: 11,
    fontWeight: '600',
    color: '#64748B',
    textTransform: 'uppercase',
    letterSpacing: 0.5,
    marginBottom: 4,
  },

  patientName: {
    fontSize: 24,
    fontWeight: '800',
  },

  // ===========================================================
  // SECTION
  // ===========================================================

  sectionTitle: {
    fontSize: 13,
    fontWeight: '700',
    color: '#475569',
    textTransform: 'uppercase',
    letterSpacing: 0.8,
    marginBottom: 12,
  },

  // ===========================================================
  // APPOINTMENT CARD
  // ===========================================================

  appointmentCard: {
    borderRadius: 16,
    padding: 16,
    borderWidth: 1,
    marginBottom: 24,
  },

  infoRow: {
    flexDirection: 'row',
    alignItems: 'center',
  },

  iconBox: {
    width: 38,
    height: 38,
    borderRadius: 10,
    justifyContent: 'center',
    alignItems: 'center',
    marginRight: 14,
  },

  infoTextContainer: {
    flex: 1,
  },

  infoLabel: {
    fontSize: 11,
    color: '#64748B',
    fontWeight: '600',
    textTransform: 'uppercase',
    marginBottom: 1,
  },

  infoValue: {
    fontSize: 15,
    fontWeight: '700',
  },

  divider: {
    height: 1,
    marginVertical: 12,
  },

  // ===========================================================
  // REASON
  // ===========================================================

  reasonCard: {
    borderRadius: 16,
    padding: 16,
    borderWidth: 1,
    borderLeftWidth: 4,
  },

  reasonText: {
    fontSize: 14,
    fontWeight: '500',
    lineHeight: 22,
  },

  // ===========================================================
  // SPACER
  // ===========================================================

  spacer: {
    flex: 1,
  },

  // ===========================================================
  // FOOTER
  // ===========================================================

  footerActions: {
    paddingBottom:
      Platform.OS === 'ios' ? 20 : 30,
    marginTop: 20,
  },

  // ===========================================================
  // CONFIRMAR
  // ===========================================================

  confirmButton: {
    flexDirection: 'row',
    backgroundColor: '#10B981',
    borderRadius: 14,
    height: 54,
    justifyContent: 'center',
    alignItems: 'center',
    marginBottom: 12,

    shadowColor: '#10B981',
    shadowOffset: {
      width: 0,
      height: 4,
    },
    shadowOpacity: 0.12,
    shadowRadius: 8,
    elevation: 2,
  },

  // ===========================================================
  // CONSULTA REALIZADA
  // ===========================================================

  completedButton: {
    flexDirection: 'row',
    backgroundColor: '#10B981',
    borderRadius: 14,
    height: 54,
    justifyContent: 'center',
    alignItems: 'center',
    marginBottom: 12,

    shadowColor: '#10B981',
    shadowOffset: {
      width: 0,
      height: 4,
    },
    shadowOpacity: 0.12,
    shadowRadius: 8,
    elevation: 2,
  },

  confirmButtonText: {
    fontSize: 15,
    fontWeight: '700',
    color: '#FFFFFF',
  },

  // ===========================================================
  // REAGENDAR
  // ===========================================================

  rescheduleButton: {
    flexDirection: 'row',
    borderRadius: 14,
    height: 50,
    justifyContent: 'center',
    alignItems: 'center',
    borderWidth: 1,
  },

  rescheduleButtonText: {
    fontSize: 14,
    fontWeight: '700',
  },

  // ===========================================================
  // CANCELAR
  // ===========================================================

  cancelButton: {
    flexDirection: 'row',
    backgroundColor: '#DC2626',
    borderRadius: 14,
    height: 50,
    justifyContent: 'center',
    alignItems: 'center',
    marginTop: 12,
  },

  cancelButtonText: {
    fontSize: 14,
    fontWeight: '700',
    color: '#FFFFFF',
  },
});