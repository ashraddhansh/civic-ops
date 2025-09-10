// Network Test Component
import React, { useState } from 'react';
import { View, Text, TouchableOpacity, StyleSheet, Alert } from 'react-native';
import axios from 'axios';

const NetworkTest: React.FC = () => {
  const [testing, setTesting] = useState(false);

  const testConnections = async () => {
    setTesting(true);
    const results: string[] = [];

    // Test different IPs and ports
    const testUrls = [
      'http://192.168.1.38:8000/',
      'http://192.168.1.38:8000/docs',
      'https://httpbin.org/get', // External test
    ];

    for (const url of testUrls) {
      try {
        console.log(`Testing: ${url}`);
        const response = await axios.get(url, { timeout: 5000 });
        results.push(`✅ ${url} - SUCCESS (${response.status})`);
        console.log(`✅ ${url} - SUCCESS`);
      } catch (error) {
        if (axios.isAxiosError(error)) {
          results.push(`❌ ${url} - FAILED: ${error.message}`);
          console.log(`❌ ${url} - FAILED:`, error.message);
        }
      }
    }

    Alert.alert('Network Test Results', results.join('\n\n'));
    setTesting(false);
  };

  return (
    <View style={styles.container}>
      <Text style={styles.title}>Network Connectivity Test</Text>
      <TouchableOpacity
        style={[styles.button, testing && styles.buttonDisabled]}
        onPress={testConnections}
        disabled={testing}
      >
        <Text style={styles.buttonText}>
          {testing ? 'Testing...' : 'Test Network Connection'}
        </Text>
      </TouchableOpacity>
    </View>
  );
};

const styles = StyleSheet.create({
  container: {
    padding: 20,
    backgroundColor: 'white',
    margin: 20,
    borderRadius: 10,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.1,
    shadowRadius: 4,
    elevation: 3,
  },
  title: {
    fontSize: 18,
    fontWeight: 'bold',
    marginBottom: 15,
    textAlign: 'center',
  },
  button: {
    backgroundColor: '#007AFF',
    padding: 15,
    borderRadius: 8,
    alignItems: 'center',
  },
  buttonDisabled: {
    backgroundColor: '#ccc',
  },
  buttonText: {
    color: 'white',
    fontWeight: 'bold',
  },
});

export default NetworkTest;
