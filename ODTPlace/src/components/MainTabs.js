import React, { useEffect, useRef, useState } from 'react';
import { View, StyleSheet, ScrollView, Dimensions } from 'react-native';
import BottomNavBar from './BottomNavBar';
import HomeScreen from '../screens/HomeScreen';
import ScheduleScreen from '../screens/ScheduleScreen';
import NotificationsScreen from '../screens/NotificationsScreen';
import SettingsScreen from '../screens/SettingsScreen';

const tabs = [
    { key: 'home', component: HomeScreen },
    { key: 'schedule', component: ScheduleScreen },
    { key: 'notifications', component: NotificationsScreen },
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

    const handleTabPress = (tabKey) => {
        const index = tabs.findIndex((tab) => tab.key === tabKey);
        if (index < 0 || !scrollViewRef.current) {
            return;
        }
        setActiveTab(tabKey);
        scrollViewRef.current.scrollTo({ x: index * screenWidth, animated: true });
    };

    const handleMomentumScrollEnd = (event) => {
        const index = Math.round(event.nativeEvent.contentOffset.x / screenWidth);
        const nextTab = tabs[index]?.key ?? 'home';
        setActiveTab(nextTab);
    };

    return (
        <View style={styles.container}>
            <ScrollView
                horizontal
                pagingEnabled
                showsHorizontalScrollIndicator={false}
                ref={scrollViewRef}
                onMomentumScrollEnd={handleMomentumScrollEnd}
                contentContainerStyle={styles.scrollContent}
            >
                {tabs.map(({ key, component: ScreenComponent }) => (
                    <View key={key} style={[styles.page, { width: screenWidth }]}> 
                        <ScreenComponent
                            navigation={navigation}
                            route={route}
                            showBottomNav={false}
                            activeTab={activeTab}
                        />
                    </View>
                ))}
            </ScrollView>
            <BottomNavBar activeTab={activeTab} onTabPress={handleTabPress} />
        </View>
    );
}

const styles = StyleSheet.create({
    container: {
        flex: 1,
        backgroundColor: 'transparent',
    },
    scrollContent: {
        flexGrow: 1,
    },
    page: {
        flex: 1,
    },
});
