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
    marginTop:10,
    backgroundColor: '#00bceb',
    paddingVertical: 14,
    paddingHorizontal: 16,
    borderRadius: 8,
    alignItems: 'center',
    justifyContent: 'center',
    alignSelf: 'center',
    width: '100%',
    maxWidth: 360,
    minHeight: 50,
  },

  text: {
    color: '#fff',
    fontSize: 16,
    fontWeight: 'bold',
  },

});