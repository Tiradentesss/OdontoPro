import React from 'react';
import { View, Text, Button, StyleSheet, Image } from 'react-native';

// Tela de perfil
export default function TresScreen({ navigation }) {

  return (
    <View style={styles.container}>
      <View style={{ alignItems: 'center', marginBottom: 20, flexDirection: 'row', backgroundColor: '#3b65c0', height: 80, width: '100%' }}>
        <View style={{ alignItems: 'center', justifyContent: 'left', marginBottom: 20, flexDirection: 'row' }}>
          <Image style={styles.imagem2} source={require('../../assets/profile.png')} />
          <Text style={styles.titulo}>AAA</Text>
        </View>
      
      </View>

      <Text style={styles.titulo}>Tela de texto</Text>

      <Text style={styles.titulo}>Texto Texto Texto Texto Texto Texto Texto Texto Texto Texto Texto Texto Texto Texto Texto Texto Texto Texto Texto Texto Texto Texto Texto Texto Texto Texto Texto Texto Texto Texto Texto Texto Texto Texto Texto Texto Texto Texto Texto Texto Texto Texto Texto Texto Texto Texto Texto Texto Texto Texto Texto </Text>

      <Button
        title="Voltar"

        onPress={() => navigation.goBack()}
      />

      <View style={{ alignItems: 'top', justifyContent: 'space-between', flexDirection: 'row', backgroundColor: '#3b65c0', height: 100, width: '100%'}}>
              <Button style={styles.botoes}
                title="Home"
      
                onPress={() => navigation.navigate('Home')}
              />
      
               <Button style={styles.botoes}
                title="Profile"
      
                onPress={() => navigation.navigate('Perfil')}
              />
      
               <Button style={styles.botoes}
                title="Tela3"
      
                onPress={() => navigation.navigate('Info')}
              />
      </View>
    </View>
  );
}
// Estilos
const styles = StyleSheet.create({

  container: {
    flex: 1,
    alignItems: 'right',
    justifyContent: 'space-between',
  },

  titulo: {
    fontSize: 22,
    marginBottom: 20,
  },

  imagem: {
    width: 100,
    height: 100,
    marginBottom: 20,
    borderRadius: 50,
  },

    imagem2: {
    width: 50,
    height: 50,
    marginBottom: 20,
    borderRadius: 50,
  },

  botoes: {
    backgroundColor: '#00c3ff',
    borderRadius: 10,
    height: 80,
    width: 80,
  }

});