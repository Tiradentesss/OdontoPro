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
    marginTop:10,
    backgroundColor: '#00bceb',
    padding: 15,
    borderRadius: 8,
    alignItems: 'center',
    width: 335,
    height: 50,
  },

  text: {
    color: '#fff',
    fontSize: 16,
    fontWeight: 'bold',
  },

});