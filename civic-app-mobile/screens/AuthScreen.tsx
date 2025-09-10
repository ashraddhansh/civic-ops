// Authentication Screen - Login/Signup with Phone Number
import React, { useState } from 'react';
import {
  View,
  Text,
  TextInput,
  TouchableOpacity,
  StyleSheet,
  Alert,
  KeyboardAvoidingView,
  Platform,
  ScrollView,
} from 'react-native';
import { useForm, Controller } from 'react-hook-form';
import { yupResolver } from '@hookform/resolvers/yup';
import * as yup from 'yup';
import axios from 'axios';
import API_BASE_URL, { API_ENDPOINTS, API_CONFIG } from '../config/api';
import NetworkTest from '../components/NetworkTest';

// Validation schema
const phoneSchema = yup.object().shape({
  phoneNumber: yup
    .string()
    .required('Phone number is required')
    .matches(/^[0-9]{10}$/, 'Please enter a valid 10-digit phone number'),
});

interface PhoneFormData {
  phoneNumber: string;
}

interface AuthScreenProps {
  onOTPSent: (phoneNumber: string) => void;
}

const AuthScreen: React.FC<AuthScreenProps> = ({ onOTPSent }) => {
  const [loading, setLoading] = useState(false);
  
  const {
    control,
    handleSubmit,
    formState: { errors },
  } = useForm<PhoneFormData>({
    resolver: yupResolver(phoneSchema),
    defaultValues: {
      phoneNumber: '',
    },
  });

  const onSubmit = async (data: PhoneFormData) => {
    setLoading(true);
    
    try {
      const fullPhoneNumber = `+91${data.phoneNumber}`;
      
      console.log('Making API request to:', `${API_BASE_URL}${API_ENDPOINTS.REQUEST_OTP}`);
      console.log('Request data:', { phone_number: fullPhoneNumber });
      
      // Call the FastAPI backend to request OTP
      const response = await axios.post(
        `${API_BASE_URL}${API_ENDPOINTS.REQUEST_OTP}`,
        { phone_number: fullPhoneNumber },
        {
          timeout: API_CONFIG.timeout,
          headers: API_CONFIG.headers,
        }
      );

      console.log('API Response:', response.data);

      if (response.status === 200) {
        Alert.alert(
          'OTP Sent!',
          `Verification code has been sent to ${fullPhoneNumber}`,
          [
            {
              text: 'OK',
              onPress: () => onOTPSent(fullPhoneNumber),
            },
          ]
        );
      }
    } catch (error) {
      console.error('Error requesting OTP:', error);
      
      if (axios.isAxiosError(error)) {
        if (error.code === 'NETWORK_ERROR' || error.message === 'Network Error') {
          Alert.alert(
            'Connection Error',
            `Cannot connect to backend server.\n\nMake sure:\n1. Your phone and computer are on the same WiFi\n2. FastAPI server is running\n3. Try the IP: ${API_BASE_URL}\n\nError: ${error.message}`
          );
        } else {
          const errorMessage = error.response?.data?.detail || 'Failed to send OTP. Please try again.';
          Alert.alert('Error', errorMessage);
        }
      } else {
        Alert.alert('Error', 'Network error. Please check your connection and try again.');
      }
    } finally {
      setLoading(false);
    }
  };

  return (
    <KeyboardAvoidingView 
      style={styles.container}
      behavior={Platform.OS === 'ios' ? 'padding' : 'height'}
    >
      <ScrollView contentContainerStyle={styles.scrollContainer}>
        <View style={styles.header}>
          <Text style={styles.appTitle}>🏛️ Civic App</Text>
          <Text style={styles.subtitle}>Report Civic Issues in Your Community</Text>
        </View>

        <View style={styles.formContainer}>
          <Text style={styles.formTitle}>Sign In / Sign Up</Text>
          <Text style={styles.description}>
            Enter your phone number to continue. We'll send you a verification code.
          </Text>

          <View style={styles.inputContainer}>
            <Text style={styles.label}>Phone Number</Text>
            <View style={styles.phoneInputWrapper}>
              <View style={styles.countryCode}>
                <Text style={styles.countryCodeText}>+91</Text>
              </View>
              <Controller
                control={control}
                name="phoneNumber"
                render={({ field: { onChange, onBlur, value } }) => (
                  <TextInput
                    style={[
                      styles.phoneInput,
                      errors.phoneNumber && styles.inputError,
                    ]}
                    placeholder="9876543210"
                    placeholderTextColor="#9CA3AF"
                    value={value}
                    onBlur={onBlur}
                    onChangeText={onChange}
                    keyboardType="phone-pad"
                    maxLength={10}
                    autoComplete="tel"
                    textContentType="telephoneNumber"
                  />
                )}
              />
            </View>
            {errors.phoneNumber && (
              <Text style={styles.errorText}>{errors.phoneNumber.message}</Text>
            )}
          </View>

          <TouchableOpacity
            style={[styles.submitButton, loading && styles.submitButtonDisabled]}
            onPress={handleSubmit(onSubmit)}
            disabled={loading}
          >
            <Text style={styles.submitButtonText}>
              {loading ? 'Sending OTP...' : 'Send OTP'}
            </Text>
          </TouchableOpacity>

          <Text style={styles.termsText}>
            By continuing, you agree to our Terms of Service and Privacy Policy
          </Text>
        </View>

        {/* Temporary Network Test Component */}
        <NetworkTest />
      </ScrollView>
    </KeyboardAvoidingView>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#F9FAFB',
  },
  scrollContainer: {
    flexGrow: 1,
    justifyContent: 'center',
    padding: 24,
  },
  header: {
    alignItems: 'center',
    marginBottom: 48,
  },
  appTitle: {
    fontSize: 36,
    fontWeight: 'bold',
    color: '#1F2937',
    marginBottom: 8,
  },
  subtitle: {
    fontSize: 16,
    color: '#6B7280',
    textAlign: 'center',
  },
  formContainer: {
    backgroundColor: 'white',
    borderRadius: 16,
    padding: 24,
    shadowColor: '#000',
    shadowOffset: {
      width: 0,
      height: 2,
    },
    shadowOpacity: 0.1,
    shadowRadius: 8,
    elevation: 4,
  },
  formTitle: {
    fontSize: 24,
    fontWeight: 'bold',
    color: '#1F2937',
    textAlign: 'center',
    marginBottom: 8,
  },
  description: {
    fontSize: 14,
    color: '#6B7280',
    textAlign: 'center',
    marginBottom: 32,
    lineHeight: 20,
  },
  inputContainer: {
    marginBottom: 24,
  },
  label: {
    fontSize: 16,
    fontWeight: '600',
    color: '#374151',
    marginBottom: 8,
  },
  phoneInputWrapper: {
    flexDirection: 'row',
    borderWidth: 2,
    borderColor: '#E5E7EB',
    borderRadius: 12,
    overflow: 'hidden',
  },
  countryCode: {
    backgroundColor: '#F3F4F6',
    paddingHorizontal: 16,
    paddingVertical: 16,
    justifyContent: 'center',
    borderRightWidth: 1,
    borderRightColor: '#E5E7EB',
  },
  countryCodeText: {
    fontSize: 16,
    fontWeight: '600',
    color: '#374151',
  },
  phoneInput: {
    flex: 1,
    paddingHorizontal: 16,
    paddingVertical: 16,
    fontSize: 16,
    color: '#1F2937',
  },
  inputError: {
    borderColor: '#EF4444',
  },
  errorText: {
    color: '#EF4444',
    fontSize: 14,
    marginTop: 4,
  },
  submitButton: {
    backgroundColor: '#2563EB',
    borderRadius: 12,
    paddingVertical: 16,
    alignItems: 'center',
    marginBottom: 16,
  },
  submitButtonDisabled: {
    backgroundColor: '#9CA3AF',
  },
  submitButtonText: {
    color: 'white',
    fontSize: 16,
    fontWeight: '600',
  },
  termsText: {
    fontSize: 12,
    color: '#6B7280',
    textAlign: 'center',
    lineHeight: 16,
  },
});

export default AuthScreen;
