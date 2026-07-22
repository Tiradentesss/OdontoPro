import { Pressable, Text, StyleSheet } from 'react-native';

export default function CustomButton({
  title,
  onPress,
  style,
  textStyle,
}) {
  return (
    <Pressable
      onPress={onPress}
      style={({ pressed }) => [
        styles.button,
        style,
        pressed && styles.buttonPressed,
      ]}
    >
      {({ pressed }) => (
        <Text
          style={[
            styles.text,
            textStyle,
            pressed && styles.textPressed,
          ]}
        >
          {title}
        </Text>
      )}
    </Pressable>
  );
}

const styles = StyleSheet.create({
  button: {
    marginTop: 10,
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

    borderWidth: 1,
    borderColor: '#00bceb',
  },

  buttonPressed: {
    backgroundColor: '#fff',
    borderColor: '#00bceb',

    // Efeito de "flutuação"
    transform: [{ scale: 0.98 }],

    // iOS
    shadowColor: '#00bceb',
    shadowOffset: {
      width: 0,
      height: 4,
    },
    shadowOpacity: 0.25,
    shadowRadius: 8,

    // Android
    elevation: 6,
  },

  text: {
    color: '#fff',
    fontSize: 16,
    fontWeight: 'bold',
  },

  textPressed: {
    color: '#00bceb',
  },
});