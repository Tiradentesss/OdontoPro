import { TextInput, StyleSheet } from 'react-native';

export default function CustomInput(props) {
  return (
    <TextInput
      style={styles.input}
      {...props}
    />
  );
}

const styles = StyleSheet.create({
  input: {
    borderWidth: 1,
    padding: 12,
    marginBottom: 15,
    borderRadius: 8,
  },
});