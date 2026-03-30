import { View, Text, FlatList, StyleSheet } from 'react-native';
import CustomButton from '../components/CustomButton';

export default function HomeScreen() {

  const dados = [
    { id: '1', nome: 'Notebook' },
    { id: '2', nome: 'Mouse' },
    { id: '3', nome: 'Teclado' },
    { id: '4', nome: 'Monitor' },
  ];

  return (
    <View style={styles.container}>

      {/* Cabeçalho */}
      <Text style={styles.titulo}>🛍️ Produtos</Text>

      <FlatList
        data={dados}
        keyExtractor={(item) => item.id}
        showsVerticalScrollIndicator={false}

        renderItem={({ item }) => (
        <View style={styles.card}>

          <Text style={styles.nome}>{item.nome}</Text>

          <Text style={styles.descricao}>
            Produto de alta qualidade
          </Text>

        {/* Botão reutilizável */}
        <CustomButton
          title="Ver mais"
          onPress={() => alert(`Você clicou em ${item.nome}`)}
        />

  </View>
)}
      />

    </View>
  );
}

const styles = StyleSheet.create({

  container: {
    flex: 1,
    backgroundColor: '#f5f5f5',
    paddingTop: 30,
    marginTop: 40,
  },

  titulo: {
    fontSize: 26,
    textAlign: 'center',
    fontWeight: 'bold',
    marginBottom: 20,
  },

  card: {
    backgroundColor: '#fff',
    padding: 16,
    borderRadius: 12,
    marginBottom: 15,

    // sombra (Android + iOS)
    elevation: 3, // Android
    shadowColor: '#000', // iOS
    shadowOpacity: 0.1,
    shadowRadius: 2,
    shadowOffset: { width: 0, height: 2 },
  },

  nome: {
    fontSize: 18,
    fontWeight: 'bold',
  },

  descricao: {
    fontSize: 14,
    color: '#666',
    marginTop: 5,
  },

});