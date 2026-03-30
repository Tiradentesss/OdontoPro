import React from 'react';
import { View, Text, Button, StyleSheet, Image } from 'react-native';
import CustomInput from '../components/CustomInput';
import CustomButton from '../components/CustomButton';

export default function LoginScreen({ navigation }) {

    const [username, setUsername] = React.useState('');
    const handleLogin = () => {
