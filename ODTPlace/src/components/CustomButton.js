import { TouchableOpacity, Text, StyleSheet } from 'react-native';

// Componente de botão reutilizável
export default function CustomButton({ title, onPress }) {
  return (

    // TouchableOpacity = botão clicável com efeito de opacidade
    <TouchableOpacity style={styles.button} onPress={onPress}>

      {/* Texto do botão */}
      <Text style={styles.text}>
        {title}
      </Text>

    </TouchableOpacity>
  );
}
// Estilos
const styles = StyleSheet.create({

  button: {
    backgroundColor: '#1BC3EA',
    padding: 15,
    borderRadius: 8,
    alignItems: 'center',
  },

  text: {
    color: '#fff',
    fontSize: 16,
    fontWeight: 'bold',
  },

});