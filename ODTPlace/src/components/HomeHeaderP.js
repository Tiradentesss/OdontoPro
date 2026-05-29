import React from 'react';
import { View, Text, TextInput, TouchableOpacity, StyleSheet, Platform, StatusBar, Image} from 'react-native';
import { LinearGradient } from 'expo-linear-gradient';
import NotificationButton from './NotificationButton';

const statusBarHeight = Platform.OS === 'android' ? StatusBar.currentHeight || 24 : 44;

export default function HomeHeader({ usuario, search, setSearch, onBellPress, onFilterPress}) {
    return (
        <LinearGradient 
            style={styles.topCard}
            start={{ x: 0, y: 0 }}
            end={{ x: 0.5, y: 1 }}
            colors={['#0a247c', '#1BC4EB']}>
            <View style={styles.topCardContent}>
                <View style={styles.topHeader}>
                    <View>
                        <Text style={styles.greeting}>
                            Oi <Text style={styles.userName}>{usuario}</Text>!
                        </Text>

                        <Text style={styles.subGreeting}>
                            Que você esteja sempre em boas condições.
                        </Text>
                    </View>

                    <NotificationButton
                        onPress={onBellPress}
                        style={styles.bell}
                    />
                </View>

                <View style={styles.searchBox}>
                    <Image
                            source={require('../../assets/IconLupa.png')}
                            style={styles.filterIcon}
                            resizeMode="contain"
                        />
                    <TextInput
                        value={search}
                        onChangeText={setSearch}
                        placeholder="  Pesquise por nomes"
                        placeholderTextColor="#737882"
                        style={styles.searchInput}
                    />
                    <TouchableOpacity style={styles.filterButton} onPress={onFilterPress} activeOpacity={0.8}>
                        <Image
                            source={require('../../assets/filtro.png')}
                            style={styles.filterIcon}
                            resizeMode="contain"
                        />
                    </TouchableOpacity>
                </View>
            </View>
        </LinearGradient>
    );
}

const styles = StyleSheet.create({
    topCard: {
        marginTop: -statusBarHeight,
        marginHorizontal: -20,
        overflow: 'hidden',
        shadowColor: '#000',
        shadowOffset: { width: 0, height: 10 },
        shadowOpacity: 0.12,
        shadowRadius: 18,
        elevation: 10,
    },
    topCardContent: {
        paddingHorizontal: 24,
        paddingTop: statusBarHeight + 30,
        paddingBottom: 28,
    },
    topHeader: {
        flexDirection: 'row',
        justifyContent: 'space-between',
        alignItems: 'center',
        marginBottom: 10,
    },
    greeting: {
        color: '#ffffff',
        fontSize: 32,
        fontWeight: '800',
        letterSpacing: -0.8,
    },
    userName: {
        color: '#ffffff',
        fontSize: 32,
        fontWeight: '800',
    },
    subGreeting: {
        color: 'rgba(255, 255, 255, 0.85)',
        fontSize: 15,
        fontWeight: '400',
        marginTop: 6,
        lineHeight: 22,
    },
    bell: {
        backgroundColor: '#ffffff',
        width: 42,
        height: 42,
        borderRadius: 16,
        justifyContent: 'center',
        alignItems: 'center',
    },
    welcomeText: {
        textAlign: 'center',
        color: '#fff',
        fontSize: 25,
        fontWeight: '800',
        marginTop: 20,
        lineHeight: 36,
    },
    welcomeName: {
        color: '#ffffff',
        fontSize: 25,
        fontWeight: '800',
    },
    searchBox: {
        width: '92%',
        alignSelf: 'center',
        flexDirection: 'row',
        alignItems: 'center',
        backgroundColor: '#ffffff',
        borderRadius: 16,
        marginTop: 30,
        paddingHorizontal: 14,
        paddingVertical: 10,
    },
    searchInput: {
        flex: 1,
        color: '#0f172a',
        fontSize: 16,
    },
    filterIcon: {
        width: 30,
        height: 30,
        tintColor: '#08acd1',
    },
    filterText: {
        fontSize: 18,
        color: '#0284c7',
    },
    sectionText: {
        color: '#ffffff',
        fontSize: 16,
        fontWeight: '700',
        marginTop: 16,
        marginLeft: 14,
    },
});
