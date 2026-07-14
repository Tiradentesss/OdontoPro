import React, { useEffect, useRef, useState, useCallback } from 'react';
import { View, StyleSheet, Dimensions, ScrollView } from 'react-native'; 
import BottomNavBar from './BottomNavBar';
import HomeScreen from '../screens/HomeScreen';
import ScheduleScreen from '../screens/ScheduleScreen';
import HistoryScreen from '../screens/HistoryScreen';
import SettingsScreen from '../screens/SettingsScreen';

const tabs = [
    { key: 'home', component: HomeScreen },
    { key: 'schedule', component: ScheduleScreen },
    { key: 'history', component: HistoryScreen },
    { key: 'settings', component: SettingsScreen },
];

export default function MainTabs({ route, navigation }) {
    const scrollViewRef = useRef(null);
    const [activeTab, setActiveTab] = useState('home');
    const [screenWidth, setScreenWidth] = useState(Dimensions.get('window').width);

    useEffect(() => {
        const subscription = Dimensions.addEventListener('change', ({ window }) => {
            setScreenWidth(window.width);
        });
        return () => subscription?.remove?.();
    }, []);

    const handleTabPress = useCallback((tabKey) => {
        const index = tabs.findIndex((tab) => tab.key === tabKey);
        if (index > -1 && scrollViewRef.current) {
            setActiveTab(tabKey);
            scrollViewRef.current.scrollTo({ x: index * screenWidth, animated: true });
        }
    }, [screenWidth]);

    const handleMomentumScrollEnd = (event) => {
        const index = Math.round(event.nativeEvent.contentOffset.x / screenWidth);
        if (tabs[index]) {
            setActiveTab(tabs[index].key);
        }
    };

    return (
        <View style={styles.container}>
            <ScrollView
                horizontal
                pagingEnabled
                showsHorizontalScrollIndicator={false}
                ref={scrollViewRef}
                onMomentumScrollEnd={handleMomentumScrollEnd}
                scrollEventThrottle={16}
                removeClippedSubviews={true}
                contentContainerStyle={{ width: `${tabs.length * 100}%` }}
            >
                {tabs.map(({ key, component: ScreenComponent }) => (
                    <View key={key} style={[styles.page, { width: screenWidth }]}> 
                        <ScreenComponent
                            navigation={navigation}
                            route={route}
                            activeTab={activeTab}
                            showBottomNav={false} // Mantém desativado nas telas internas
                        />
                    </View>
                ))}
            </ScrollView>
            
            {/* Nav fixa, limpa e integrada */}
            <View style={styles.navWrapper}>
                <BottomNavBar activeTab={activeTab} onTabPress={handleTabPress} />
            </View>
        </View>
    );
}

const styles = StyleSheet.create({
    container: {
        flex: 1,
        backgroundColor: '#f8fafc',
    },
    page: {
        flex: 1,
    },
    navWrapper: {
        position: 'absolute',
        bottom: 0,
        left: 0,
        right: 0,
        backgroundColor: '#ffffff', // Mesma cor do fundo da BottomNavBar
        paddingBottom: 0,
        paddingTop: 0,
        borderTopWidth: 0,
        elevation: 0,
        shadowOpacity: 0,
    },
});