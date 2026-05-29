import { TextInput, StyleSheet } from 'react-native';

export default function CustomInput(props) {
  return (
    <TextInput
      style={styles.input}
      placeholderTextColor="#fff"
      {...props}
    />
  );
}

const styles = StyleSheet.create({
  input: {
    padding: 12,
    marginBottom: 15,
    borderRadius: 8,

    // fundo translúcido
    backgroundColor: 'rgba(230,230,230,0.5)',

    // borda branca
    borderWidth: 1,
    borderColor: '#fff',

    // texto branco
    color: '#fff',
  },
});