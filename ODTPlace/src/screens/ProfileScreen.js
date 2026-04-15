import React, { useState } from 'react';
import { View, Text, Button, StyleSheet, Image, TextInput, TouchableOpacity, ScrollView } from 'react-native';

// Tela de perfil
export default function ProfileScreen({ navigation }) {
  const [searchQuery, setSearchQuery] = useState('');
  const [showAllSpecialties, setShowAllSpecialties] = useState(false);

  const specialties = [
    'Ortodontia',
    'Endodontia',
    'Periodontia',
    'Odontopediatria',
    'Prótese',
    'Implantodontia',
    'Cirurgia Bucomaxilofacial',
  ];

  const filteredSpecialties = specialties.filter((item) =>
    item.toLowerCase().startsWith(searchQuery.toLowerCase())
  );

  const visibleSpecialties = showAllSpecialties ? filteredSpecialties : filteredSpecialties.slice(0, 5);

  const hasMoreSpecialties = filteredSpecialties.length > 5;

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

      <View style={styles.section}>
        <Text style={styles.sectionTitle}>Especialidades</Text>
        <TextInput
          style={styles.searchInput}
          placeholder="Pesquisar especialidades"
          placeholderTextColor="#94a3b8"
          value={searchQuery}
          onChangeText={setSearchQuery}
        />
        <ScrollView style={styles.specialtyList} nestedScrollEnabled>
          {visibleSpecialties.map((item) => (
            <View key={item} style={styles.specialtyItem}>
              <Text style={styles.specialtyText}>{item}</Text>
            </View>
          ))}
          {visibleSpecialties.length === 0 && (
            <Text style={styles.noResultsText}>Nenhuma especialidade encontrada.</Text>
          )}
        </ScrollView>
        {hasMoreSpecialties && (
          <TouchableOpacity
            style={styles.showMoreButton}
            onPress={() => setShowAllSpecialties((prev) => !prev)}
            activeOpacity={0.8}
          >
            <Text style={styles.showMoreText}>
              {showAllSpecialties ? 'Ver menos' : 'Ver mais'}
            </Text>
          </TouchableOpacity>
        )}
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
  },
  section: {
    width: '100%',
    paddingHorizontal: 20,
    marginBottom: 20,
  },
  sectionTitle: {
    fontSize: 20,
    fontWeight: '800',
    color: '#0f172a',
    marginBottom: 12,
  },
  searchInput: {
    width: '100%',
    height: 48,
    backgroundColor: '#f1f5f9',
    borderRadius: 14,
    paddingHorizontal: 16,
    marginBottom: 12,
    color: '#0f172a',
  },
  specialtyList: {
    maxHeight: 220,
    marginBottom: 12,
  },
  specialtyItem: {
    paddingVertical: 12,
    paddingHorizontal: 14,
    backgroundColor: '#ffffff',
    borderRadius: 16,
    marginBottom: 10,
    borderWidth: 1,
    borderColor: '#e2e8f0',
  },
  specialtyText: {
    color: '#0f172a',
    fontSize: 15,
  },
  noResultsText: {
    color: '#64748b',
    fontSize: 14,
    textAlign: 'center',
    paddingVertical: 14,
  },
  showMoreButton: {
    alignSelf: 'flex-start',
    paddingVertical: 12,
    paddingHorizontal: 20,
    backgroundColor: '#0ea5e9',
    borderRadius: 16,
  },
  showMoreText: {
    color: '#ffffff',
    fontWeight: '700',
  },

});