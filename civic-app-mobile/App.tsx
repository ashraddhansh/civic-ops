import React, { useState, useEffect } from 'react';
import { StatusBar } from 'expo-status-bar';
import { NavigationContainer } from '@react-navigation/native';
import { createStackNavigator } from '@react-navigation/stack';
import AsyncStorage from '@react-native-async-storage/async-storage';
import { View, Text, StyleSheet, ActivityIndicator } from 'react-native';

import AuthScreen from './screens/AuthScreen';
import OTPScreen from './screens/OTPScreen';

const Stack = createStackNavigator();

type AuthState = 'loading' | 'unauthenticated' | 'phone-entered' | 'authenticated';

export default function App() {
  const [authState, setAuthState] = useState<AuthState>('loading');
  const [phoneNumber, setPhoneNumber] = useState<string>('');

  useEffect(() => {
    checkAuthStatus();
  }, []);

  const checkAuthStatus = async () => {
    try {
      const token = await AsyncStorage.getItem('access_token');
      if (token) {
        setAuthState('authenticated');
      } else {
        setAuthState('unauthenticated');
      }
    } catch (error) {
      console.error('Error checking auth status:', error);
      setAuthState('unauthenticated');
    }
  };

  const handleOTPSent = (phone: string) => {
    setPhoneNumber(phone);
    setAuthState('phone-entered');
  };

  const handleVerificationSuccess = () => {
    setAuthState('authenticated');
  };

  const handleGoBack = () => {
    setAuthState('unauthenticated');
    setPhoneNumber('');
  };

  const handleLogout = async () => {
    try {
      await AsyncStorage.multiRemove(['access_token', 'user_data']);
      setAuthState('unauthenticated');
      setPhoneNumber('');
    } catch (error) {
      console.error('Error logging out:', error);
    }
  };

  if (authState === 'loading') {
    return (
      <View style={styles.loadingContainer}>
        <ActivityIndicator size="large" color="#2563EB" />
        <Text style={styles.loadingText}>Loading...</Text>
      </View>
    );
  }

  return (
    <NavigationContainer>
      <StatusBar style="auto" />
      <Stack.Navigator
        screenOptions={{
          headerShown: false,
        }}
      >
        {authState === 'unauthenticated' && (
          <Stack.Screen name="Auth">
            {() => <AuthScreen onOTPSent={handleOTPSent} />}
          </Stack.Screen>
        )}
        
        {authState === 'phone-entered' && (
          <Stack.Screen name="OTP">
            {() => (
              <OTPScreen
                phoneNumber={phoneNumber}
                onVerificationSuccess={handleVerificationSuccess}
                onGoBack={handleGoBack}
              />
            )}
          </Stack.Screen>
        )}
        
        {authState === 'authenticated' && (
          <Stack.Screen name="Main">
            {() => <MainApp onLogout={handleLogout} />}
          </Stack.Screen>
        )}
      </Stack.Navigator>
    </NavigationContainer>
  );
}

// Placeholder for the main app after authentication
const MainApp: React.FC<{ onLogout: () => void }> = ({ onLogout }) => {
  return (
    <View style={styles.mainContainer}>
      <Text style={styles.title}>🏛️ Civic App</Text>
      <Text style={styles.subtitle}>Welcome! You're successfully logged in.</Text>
      <Text style={styles.description}>
        Main app screens will be built here (issue reporting, maps, etc.)
      </Text>
      
      {/* Temporary logout button for testing */}
      <Text 
        style={styles.logoutButton}
        onPress={onLogout}
      >
        Logout (Test)
      </Text>
    </View>
  );
};

const styles = StyleSheet.create({
  loadingContainer: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    backgroundColor: '#F9FAFB',
  },
  loadingText: {
    marginTop: 16,
    fontSize: 16,
    color: '#6B7280',
  },
  mainContainer: {
    flex: 1,
    backgroundColor: '#f5f5f5',
    alignItems: 'center',
    justifyContent: 'center',
    padding: 20,
  },
  title: {
    fontSize: 32,
    fontWeight: 'bold',
    color: '#2563eb',
    marginBottom: 10,
    textAlign: 'center',
  },
  subtitle: {
    fontSize: 18,
    color: '#374151',
    marginBottom: 20,
    textAlign: 'center',
  },
  description: {
    fontSize: 14,
    color: '#6b7280',
    textAlign: 'center',
    marginTop: 30,
  },
  logoutButton: {
    marginTop: 40,
    padding: 12,
    backgroundColor: '#EF4444',
    color: 'white',
    borderRadius: 8,
    textAlign: 'center',
    fontWeight: '600',
  },
});
