import React from 'react';
import { View, Text, Button, StyleSheet, Image } from 'react-native';

// Tela de perfil
export default function ProfileScreen({ navigation }) {

  return (
    <View style={styles.container}>
      <View style={styles.profileHeader}>
        <View style={styles.profileInfo}>
          <Image style={styles.imagem2} source={require('../../assets/profile.png')} />
          <Text style={styles.titulo}>AAA</Text>
        </View>

        <Image style={styles.imagem} source={require('../../assets/profile.png')} />
        <Text style={styles.titulo}>Nome: AAA</Text>
      </View>
      <View style={{ alignItems: 'right', marginBottom: 20}}>

        <Text style={styles.titulo}>Email: AAA@gmail.com</Text>

        <Text style={styles.titulo}>Senha: ********</Text>

        <Text style={styles.titulo}>Numero: 3914148128</Text>
      </View>

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

  profileHeader: {
    width: '100%',
    paddingHorizontal: 20,
    paddingVertical: 16,
    marginBottom: 20,
    backgroundColor: '#3b65c0',
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'space-between',
  },

  profileInfo: {
    flexDirection: 'row',
    alignItems: 'center',
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