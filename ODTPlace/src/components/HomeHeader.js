import React from 'react';
import {
    View,
    Text,
    TextInput,
    TouchableOpacity,
    StyleSheet,
    Platform,
    StatusBar,
    Image,
} from 'react-native';

import NotificationButton from './NotificationButton';

const statusBarHeight =
    Platform.OS === 'android'
        ? StatusBar.currentHeight || 24
        : 44;

export default function HomeHeader({
    usuario,
    search,
    setSearch,
    onBellPress,
    onFilterPress,
}) {
    return (
        <View style={styles.topCard}>
            <View style={styles.topCardContent}>

                {/* Logo + Notificação */}
                <View style={styles.headerTop}>

                    <Image
                        source={require('../../assets/logobrancahorizontal.png')}
                        style={styles.logo}
                    />

                    <NotificationButton onPress={onBellPress} />

                </View>

                {/* Boas-vindas */}
                <Text style={styles.welcomeText}>
                    Bem-vindo,
                </Text>

                <Text style={styles.userName}>
                    {usuario}
                </Text>

                {/* Pesquisa */}
                <View style={styles.searchBox}>

                    <Image
                        source={require('../../assets/IconLupa.png')}
                        style={styles.searchIcon}
                    />

                    <TextInput
                        value={search}
                        onChangeText={setSearch}
                        placeholder="Pesquise por clínicas..."
                        placeholderTextColor="#94a3b8"
                        style={styles.searchInput}
                    />
                </View>

            </View>
        </View>
    );
}

const styles = StyleSheet.create({

    topCard: {
        marginTop: -statusBarHeight,
        marginHorizontal: -20,

        backgroundColor: '#00BCEB',

        borderBottomLeftRadius: 30,
        borderBottomRightRadius: 30,

        shadowColor: '#000',
        shadowOffset: {
            width: 0,
            height: 8,
        },
        shadowOpacity: 0.12,
        shadowRadius: 18,
        elevation: 10,
    },

    topCardContent: {
        paddingTop: statusBarHeight + 30,
        paddingBottom: 16,
        paddingHorizontal: 32,
    },

    headerTop: {
        flexDirection: 'row',
        justifyContent: 'space-between',
        alignItems: 'center',
        marginBottom: 18,
    },

    logo: {
        width: 150,
        height: 42,
        resizeMode: 'contain',
    },

    welcomeText: {
        color: '#E8F8FD',
        textAlign: 'center',
        fontSize: 18,
        fontWeight: '500',
    },

    userName: {
        color: '#FFF',
        textAlign: 'center',
        fontSize: 24,
        fontWeight: '800',
        marginTop: 4,
        marginBottom: 20,
    },

    searchBox: {
        width: '92%',
        flexDirection: 'row',
        alignItems: 'center',
        alignSelf: 'center',

        backgroundColor: '#FFF',

        borderRadius: 28,

        height: 56,

        paddingHorizontal: 10,

        shadowColor: '#000',
        shadowOpacity: 0.08,
        shadowRadius: 10,
        elevation: 4,
    },

    searchIcon: {
        width: 20,
        height: 20,
        resizeMode: 'contain',
        marginRight: 10,
    },

    searchInput: {
        flex: 1,
        color: '#0F172A',
        fontSize: 16,
    },
});