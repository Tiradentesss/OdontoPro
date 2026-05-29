import { TouchableOpacity, Text, StyleSheet } from 'react-native';

// Componente de botão reutilizável
export default function CustomButton({ title, onPress, style, textStyle }) {
  return (

    // TouchableOpacity = botão clicável com efeito de opacidade
    <TouchableOpacity style={[styles.button, style]} onPress={onPress}>

      {/* Texto do botão */}
      <Text style={[styles.text, textStyle]}>
        {title}
      </Text>

    </TouchableOpacity>
  );
}
// Estilos
const styles = StyleSheet.create({

  button: {
    marginTop: 25,
    backgroundColor: '#fff',
    padding: 15,
    borderRadius: 8,
    alignItems: 'center',
    width: 335,
    height: 50,
    alignSelf: 'stretch',
  },

  text: {
    color: '#08a4c4',
    fontSize: 16,
    fontWeight: 'bold',
  },

});