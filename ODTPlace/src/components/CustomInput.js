import { TextInput, StyleSheet } from 'react-native';

export default function CustomInput(props) {
  return (
    <TextInput
      style={styles.input}
      placeholderTextColor="#9ca3af"
      {...props}
    />
  );
}

const styles = StyleSheet.create({
  input: {
    borderWidth: 1,
    borderColor: '#d3e4fe',
    padding: 12,
    marginBottom: 15,
    borderRadius: 12,
    backgroundColor: '#f8fbff',
    color: '#0f172a',
  },
});