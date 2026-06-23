import React, { useLayoutEffect } from 'react';
import { 
  View, 
  Text, 
  StyleSheet, 
  ScrollView, 
  TouchableOpacity, 
  SafeAreaView, 
  StatusBar, 
  Dimensions,
  Platform 
} from 'react-native';
import { Feather } from '@expo/vector-icons';
import { useTheme } from '../ThemeContext'; 

const { width } = Dimensions.get('window');

// Cores semânticas fixas para manter a identidade de dados analíticos
const SUCCESS_GREEN = "#15803D"; 
const NO_SHOW_RED = "#DC2626";

export default function ReportsScreen({ navigation }) {
  
  const { isDarkMode, colors } = useTheme();

  // Oculta a TabBar padrão ao montar a tela
  useLayoutEffect(() => {
    if (navigation) {
      navigation.getParent()?.setOptions({
        tabBarStyle: { display: 'none' }
      });
    }
    return () => {
      navigation.getParent()?.setOptions({
        tabBarStyle: undefined
      });
    };
  }, [navigation]);

  return (
    <SafeAreaView style={[styles.container, { backgroundColor: colors.container }]}>
      <StatusBar 
        barStyle={isDarkMode ? 'light-content' : 'dark-content'} 
        backgroundColor={colors.container} 
        translucent={false} 
      />
      
      {/* Cabeçalho Premium Dinâmico */}
      <View style={styles.header}>
        <TouchableOpacity 
          style={[styles.backButton, { backgroundColor: colors.backButtonBg }]} 
          onPress={() => navigation?.goBack()}
          activeOpacity={0.6}
        >
          <Feather name="arrow-left" size={24} color={colors.brandBlue} />
        </TouchableOpacity>
        <Text style={[styles.title, { color: colors.text }]}>Relatórios Gerais</Text>
        <View style={styles.headerSpacer} />
      </View>

      <ScrollView 
        showsVerticalScrollIndicator={false} 
        contentContainerStyle={styles.scrollContent}
      >
        
        {/* Resumo de Métricas (Cards de Performance) */}
        <View style={styles.statsRow}>
          <View style={[styles.miniCard, { backgroundColor: colors.card, borderColor: colors.border }]}>
            <View style={styles.miniCardHeader}>
              <Text style={[styles.miniLabel, { color: colors.mutedText }]}>Consultas</Text>
              <View style={[styles.iconWrapper, { backgroundColor: isDarkMode ? '#1E293B' : '#EFF6FF' }]}>
                <Feather name="activity" size={14} color={colors.brandBlue} />
              </View>
            </View>
            <Text style={[styles.miniValue, { color: colors.text }]}>142</Text>
            <View style={styles.trendingRow}>
              <Feather name="trending-up" size={12} color={SUCCESS_GREEN} />
              <Text style={styles.miniSubGreen}>+12% este mês</Text>
            </View>
            <Text style={[styles.descriptionText, { color: colors.mutedText }]}>Total de procedimentos executados na clínica.</Text>
          </View>

          <View style={[styles.miniCard, { backgroundColor: colors.card, borderColor: colors.border }]}>
            <View style={styles.miniCardHeader}>
              <Text style={[styles.miniLabel, { color: colors.mutedText }]}>Novos Pacientes</Text>
              <View style={[styles.iconWrapper, { backgroundColor: isDarkMode ? '#14532D30' : '#F0FDF4' }]}>
                <Feather name="users" size={14} color={SUCCESS_GREEN} />
              </View>
            </View>
            <Text style={[styles.miniValue, { color: colors.text }]}>28</Text>
            <View style={styles.trendingRow}>
              <Feather name="trending-up" size={12} color={SUCCESS_GREEN} />
              <Text style={styles.miniSubGreen}>+8% de alcance</Text>
            </View>
            <Text style={[styles.descriptionText, { color: colors.mutedText }]}>Primeiras consultas registradas no sistema.</Text>
          </View>
        </View>

        {/* Gráfico Analítico de Frequência Semanal */}
        <View style={[styles.chartCard, { backgroundColor: colors.card, borderColor: colors.border }]}>
          <View style={styles.chartHeaderRow}>
            <View>
              <Text style={[styles.cardHeaderTitle, { color: colors.text }]}>Frequência Semanal</Text>
              <Text style={[styles.cardHeaderSub, { color: colors.mutedText }]}>Média de comparecimento por dia útil</Text>
            </View>
          </View>
          
          <View style={styles.chartContainer}>
            <View style={styles.chartGridLines}>
              <View style={[styles.gridLine, { borderColor: colors.border }]} />
              <View style={[styles.gridLine, { borderColor: colors.border }]} />
              <View style={[styles.gridLine, { borderColor: colors.border }]} />
            </View>

            <View style={styles.barWrapper}>
              <View style={[styles.barActive, { height: '60%', backgroundColor: isDarkMode ? '#334155' : '#E2E8F0' }]} />
              <Text style={[styles.barLabel, { color: colors.mutedText }]}>Seg</Text>
            </View>
            <View style={styles.barWrapper}>
              <View style={[styles.barActive, { height: '45%', backgroundColor: isDarkMode ? '#334155' : '#E2E8F0' }]} />
              <Text style={[styles.barLabel, { color: colors.mutedText }]}>Ter</Text>
            </View>
            <View style={styles.barWrapper}>
              <View style={[styles.barActive, { height: '85%', backgroundColor: isDarkMode ? '#334155' : '#E2E8F0' }]} />
              <Text style={[styles.barLabel, { color: colors.mutedText }]}>Qua</Text>
            </View>
            <View style={styles.barWrapper}>
              <View style={[styles.barActive, { height: '70%', backgroundColor: isDarkMode ? '#334155' : '#E2E8F0' }]} />
              <Text style={[styles.barLabel, { color: colors.mutedText }]}>Qui</Text>
            </View>
            <View style={styles.barWrapper}>
              <View style={[styles.barActive, { height: '98%', backgroundColor: colors.brandBlue }]} />
              <Text style={[styles.barLabel, { fontWeight: '700', color: colors.text }]}>Sex</Text>
            </View>
          </View>
          <Text style={[styles.sectionFooterDescription, { color: colors.mutedText, borderColor: colors.border }]}>
            Identifica os dias com maior fluxo de cadeiras ocupadas para otimização de estoque e equipe técnica.
          </Text>
        </View>

        {/* Eficiência da Agenda (No-Show / Absenteísmo) */}
        <View style={[styles.detailsCard, { marginBottom: 24, backgroundColor: colors.card, borderColor: colors.border }]}>
          <Text style={[styles.cardHeaderTitle, { color: colors.text }]}>Eficiência da Agenda</Text>
          <Text style={[styles.cardHeaderSub, { color: colors.mutedText }]}>Taxa de presença e cancelamentos</Text>
          
          <View style={styles.listRow}>
            <View style={styles.rowTopLine}>
              <View style={styles.labelGroup}>
                <View style={[styles.indicatorCircle, { backgroundColor: SUCCESS_GREEN }]} />
                <Text style={[styles.rowText, { color: colors.text }]}>Comparecimento</Text>
              </View>
              <Text style={[styles.rowValue, { color: colors.text }]}>92%</Text>
            </View>
            <View style={[styles.progressBarBg, { backgroundColor: isDarkMode ? '#334155' : '#F1F5F9' }]}>
              {/* AJUSTADO: Fechamento correto da tag com colchetes */}
              <View style={[styles.progressBarFill, { width: '92%', backgroundColor: SUCCESS_GREEN }]} />
            </View>
          </View>

          <View style={styles.listRow}>
            <View style={styles.rowTopLine}>
              <View style={styles.labelGroup}>
                <View style={[styles.indicatorCircle, { backgroundColor: NO_SHOW_RED }]} />
                <Text style={[styles.rowText, { color: colors.text }]}>Faltas não justificadas (No-Show)</Text>
              </View>
              <Text style={[styles.rowValue, { color: colors.text }]}>8%</Text>
            </View>
            <View style={[styles.progressBarBg, { backgroundColor: isDarkMode ? '#334155' : '#F1F5F9' }]}>
              <View style={[styles.progressBarFill, { width: '8%', backgroundColor: NO_SHOW_RED }]} />
            </View>
          </View>
          <Text style={[styles.sectionFooterDescription, { color: colors.mutedText, borderColor: colors.border }]}>
            Mede o impacto de faltas na receita. Taxas abaixo de 10% indicam excelente engajamento das confirmações automatizadas.
          </Text>
        </View>

        {/* Segmentação / Distribuição por Convênios */}
        <View style={[styles.detailsCard, { backgroundColor: colors.card, borderColor: colors.border }]}>
          <Text style={[styles.cardHeaderTitle, { color: colors.text }]}>Origem dos Recebimentos</Text>
          <Text style={[styles.cardHeaderSub, { color: colors.mutedText }]}>Proporção de faturamento por categoria</Text>
          
          <View style={styles.listRow}>
            <View style={styles.rowTopLine}>
              <View style={styles.labelGroup}>
                <View style={[styles.indicatorCircle, { backgroundColor: colors.brandBlue }]} />
                <Text style={[styles.rowText, { color: colors.text }]}>Particular</Text>
              </View>
              <Text style={[styles.rowValue, { color: colors.text }]}>54%</Text>
            </View>
            <View style={[styles.progressBarBg, { backgroundColor: isDarkMode ? '#334155' : '#F1F5F9' }]}>
              <View style={[styles.progressBarFill, { width: '54%', backgroundColor: colors.brandBlue }]} />
            </View>
          </View>

          <View style={styles.listRow}>
            <View style={styles.rowTopLine}>
              <View style={styles.labelGroup}>
                <View style={[styles.indicatorCircle, { backgroundColor: '#1E40AF' }]} />
                <Text style={[styles.rowText, { color: colors.text }]}>Convênio Unimed</Text>
              </View>
              <Text style={[styles.rowValue, { color: colors.text }]}>30%</Text>
            </View>
            <View style={[styles.progressBarBg, { backgroundColor: isDarkMode ? '#334155' : '#F1F5F9' }]}>
              <View style={[styles.progressBarFill, { width: '30%', backgroundColor: '#1E40AF' }]} />
            </View>
          </View>

          <View style={styles.listRow}>
            <View style={styles.rowTopLine}>
              <View style={styles.labelGroup}>
                <View style={[styles.indicatorCircle, { backgroundColor: '#60A5FA' }]} />
                <Text style={[styles.rowText, { color: colors.text }]}>Convênio Amil</Text>
              </View>
              <Text style={[styles.rowValue, { color: colors.text }]}>16%</Text>
            </View>
            <View style={[styles.progressBarBg, { backgroundColor: isDarkMode ? '#334155' : '#F1F5F9' }]}>
              <View style={[styles.progressBarFill, { width: '16%', backgroundColor: '#60A5FA' }]} />
            </View>
          </View>
          <Text style={[styles.sectionFooterDescription, { color: colors.mutedText, borderColor: colors.border }]}>
            Divisão analítica da receita bruta para monitorar a dependência de planos de saúde vs. tratamentos diretos.
          </Text>
        </View>

      </ScrollView>
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  container: { 
    flex: 1, 
  },
  header: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'space-between',
    paddingHorizontal: 24,
    paddingTop: Platform.OS === 'android' ? StatusBar.currentHeight + 16 : 16,
    paddingBottom: 8,
  },
  backButton: {
    padding: 10,
    borderRadius: 14,
  },
  title: { 
    fontSize: 22, 
    fontWeight: '700', 
    letterSpacing: -0.5,
  },
  headerSpacer: {
    width: 44,
  },
  scrollContent: {
    paddingHorizontal: 24,
    paddingTop: 20,
    paddingBottom: 120,
  },
  statsRow: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    marginBottom: 24,
  },
  miniCard: {
    width: (width - 62) / 2,
    padding: 16,
    borderRadius: 16,
    borderWidth: 1,
  },
  miniCardHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
  },
  miniLabel: {
    fontSize: 12,
    fontWeight: '600',
  },
  iconWrapper: {
    width: 26,
    height: 26,
    borderRadius: 8,
    justifyContent: 'center',
    alignItems: 'center',
  },
  miniValue: {
    fontSize: 26,
    fontWeight: '800',
    marginTop: 8,
  },
  trendingRow: {
    flexDirection: 'row',
    alignItems: 'center',
    marginTop: 4,
    marginBottom: 10,
  },
  miniSubGreen: {
    fontSize: 11,
    color: SUCCESS_GREEN,
    fontWeight: '600',
    marginLeft: 4,
  },
  descriptionText: {
    fontSize: 11,
    lineHeight: 14,
    fontWeight: '400',
  },
  chartCard: {
    padding: 20,
    borderRadius: 20,
    marginBottom: 24,
    borderWidth: 1,
  },
  chartHeaderRow: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'flex-start',
    marginBottom: 24,
  },
  cardHeaderTitle: {
    fontSize: 14,
    fontWeight: '700',
  },
  cardHeaderSub: {
    fontSize: 12,
    marginTop: 2,
  },
  chartContainer: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'flex-end',
    height: 120,
    position: 'relative',
    marginBottom: 16,
  },
  chartGridLines: {
    position: 'absolute',
    width: '100%',
    height: '100%',
    justifyContent: 'space-between',
    zIndex: 0,
    paddingBottom: 20, 
  },
  gridLine: {
    width: '100%',
    borderBottomWidth: 1,
    borderStyle: 'dashed',
  },
  barWrapper: {
    alignItems: 'center',
    height: '100%',
    justifyContent: 'flex-end',
    width: (width - 110) / 5,
    zIndex: 1,
  },
  barActive: {
    width: 14,
    borderRadius: 4,
  },
  barLabel: {
    fontSize: 11,
    fontWeight: '600',
    marginTop: 8,
  },
  detailsCard: {
    padding: 20,
    borderRadius: 20,
    borderWidth: 1,
  },
  listRow: {
    marginBottom: 16,
  },
  rowTopLine: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'space-between',
    marginBottom: 6,
  },
  labelGroup: {
    flexDirection: 'row',
    alignItems: 'center',
  },
  indicatorCircle: {
    width: 8,
    height: 8,
    borderRadius: 4,
  },
  rowText: {
    fontSize: 13,
    fontWeight: '600',
    marginLeft: 10,
  },
  rowValue: {
    fontSize: 13,
    fontWeight: '700',
  },
  progressBarBg: {
    width: '100%',
    height: 6,
    borderRadius: 3,
    overflow: 'hidden',
  },
  progressBarFill: {
    height: '100%',
    borderRadius: 3,
  },
  sectionFooterDescription: {
    fontSize: 12,
    lineHeight: 16,
    borderTopWidth: 1,
    paddingTop: 12,
    marginTop: 4,
  },
});