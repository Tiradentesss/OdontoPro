import { useState } from 'react';
import { TextInput, StyleSheet } from 'react-native';

export default function CustomInput(props) {
  const [isFocused, setIsFocused] = useState(false);

  return (
    <TextInput
      style={styles.input}
      placeholderTextColor="#9ca3af"
      {...props}
      style={[
        styles.input,
        isFocused && styles.inputFocused,
      ]}
      onFocus={(e) => {
        setIsFocused(true);
        props.onFocus?.(e);
      }}
      onBlur={(e) => {
        setIsFocused(false);
        props.onBlur?.(e);
      }}
    />
  );
}

const styles = StyleSheet.create({
  input: {
    borderWidth: 1,
    padding: 12,
    marginBottom: 15,
    borderRadius: 12,
    borderColor: '#d3e4fe',
    backgroundColor: '#f8fbff',
    color: '#0f172a',
  },

  inputFocused: {
    borderColor: '#1BC3EA',

    // Android
    elevation: 3,

    // iOS
    shadowColor: '#1BC3EA',
    shadowOffset: {
      width: 0,
      height: 0,
    },
    shadowOpacity: 0.2,
    shadowRadius: 6,
  },
});