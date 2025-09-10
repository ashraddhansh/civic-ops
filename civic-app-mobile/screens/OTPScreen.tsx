// OTP Verification Screen
import React, { useState, useRef, useEffect } from 'react';
import {
  View,
  Text,
  TextInput,
  TouchableOpacity,
  StyleSheet,
  Alert,
  KeyboardAvoidingView,
  Platform,
} from 'react-native';
import axios from 'axios';
import AsyncStorage from '@react-native-async-storage/async-storage';
import API_BASE_URL, { API_ENDPOINTS, API_CONFIG } from '../config/api';

interface OTPScreenProps {
  phoneNumber: string;
  onVerificationSuccess: () => void;
  onGoBack: () => void;
}

const OTPScreen: React.FC<OTPScreenProps> = ({ 
  phoneNumber, 
  onVerificationSuccess, 
  onGoBack 
}) => {
  const [otp, setOtp] = useState(['', '', '', '', '', '']);
  const [loading, setLoading] = useState(false);
  const [resendLoading, setResendLoading] = useState(false);
  const [timer, setTimer] = useState(60);
  
  const otpRefs = useRef<(TextInput | null)[]>([]);

  // Countdown timer for resend OTP
  useEffect(() => {
    if (timer > 0) {
      const interval = setInterval(() => {
        setTimer(timer - 1);
      }, 1000);
      return () => clearInterval(interval);
    }
  }, [timer]);

  const handleOtpChange = (value: string, index: number) => {
    const newOtp = [...otp];
    newOtp[index] = value;
    setOtp(newOtp);

    // Auto-focus next input
    if (value && index < 5) {
      otpRefs.current[index + 1]?.focus();
    }
    
    // Auto-submit when all 6 digits are entered
    if (newOtp.every(digit => digit !== '') && index === 5) {
      handleVerifyOtp(newOtp.join(''));
    }
  };

  const handleKeyPress = (e: any, index: number) => {
    if (e.nativeEvent.key === 'Backspace' && !otp[index] && index > 0) {
      otpRefs.current[index - 1]?.focus();
    }
  };

  const handleVerifyOtp = async (otpCode?: string) => {
    const otpToVerify = otpCode || otp.join('');
    
    if (otpToVerify.length !== 6) {
      Alert.alert('Error', 'Please enter the complete 6-digit OTP');
      return;
    }

    setLoading(true);

    try {
      const response = await axios.post(
        `${API_BASE_URL}${API_ENDPOINTS.VERIFY_OTP}`,
        {
          phone_number: phoneNumber,
          otp: otpToVerify,
        },
        {
          timeout: API_CONFIG.timeout,
          headers: API_CONFIG.headers,
        }
      );

      if (response.status === 200) {
        const { access_token, user } = response.data;
        
        // Store the JWT token and user data
        await AsyncStorage.setItem('access_token', access_token);
        await AsyncStorage.setItem('user_data', JSON.stringify(user));
        
        Alert.alert(
          'Success!',
          'Phone number verified successfully',
          [
            {
              text: 'Continue',
              onPress: onVerificationSuccess,
            },
          ]
        );
      }
    } catch (error) {
      console.error('Error verifying OTP:', error);
      
      if (axios.isAxiosError(error)) {
        const errorMessage = error.response?.data?.detail || 'Invalid OTP. Please try again.';
        Alert.alert('Verification Failed', errorMessage);
        
        // Clear OTP inputs on error
        setOtp(['', '', '', '', '', '']);
        otpRefs.current[0]?.focus();
      } else {
        Alert.alert('Error', 'Network error. Please check your connection and try again.');
      }
    } finally {
      setLoading(false);
    }
  };

  const handleResendOtp = async () => {
    setResendLoading(true);
    
    try {
      const response = await axios.post(
        `${API_BASE_URL}${API_ENDPOINTS.REQUEST_OTP}`,
        { phone_number: phoneNumber },
        {
          timeout: API_CONFIG.timeout,
          headers: API_CONFIG.headers,
        }
      );

      if (response.status === 200) {
        Alert.alert('OTP Resent', 'A new verification code has been sent to your phone');
        setTimer(60);
        setOtp(['', '', '', '', '', '']);
        otpRefs.current[0]?.focus();
      }
    } catch (error) {
      console.error('Error resending OTP:', error);
      Alert.alert('Error', 'Failed to resend OTP. Please try again.');
    } finally {
      setResendLoading(false);
    }
  };

  return (
    <KeyboardAvoidingView 
      style={styles.container}
      behavior={Platform.OS === 'ios' ? 'padding' : 'height'}
    >
      <View style={styles.header}>
        <Text style={styles.title}>Verify Phone Number</Text>
        <Text style={styles.subtitle}>
          Enter the 6-digit code sent to{'\n'}
          <Text style={styles.phoneNumber}>{phoneNumber}</Text>
        </Text>
      </View>

      <View style={styles.otpContainer}>
        {otp.map((digit, index) => (
          <TextInput
            key={index}
            ref={(ref) => {
              otpRefs.current[index] = ref;
            }}
            style={[
              styles.otpInput,
              digit && styles.otpInputFilled,
            ]}
            value={digit}
            onChangeText={(value) => handleOtpChange(value, index)}
            onKeyPress={(e) => handleKeyPress(e, index)}
            keyboardType="numeric"
            maxLength={1}
            selectTextOnFocus
            autoFocus={index === 0}
          />
        ))}
      </View>

      <TouchableOpacity
        style={[styles.verifyButton, loading && styles.verifyButtonDisabled]}
        onPress={() => handleVerifyOtp()}
        disabled={loading}
      >
        <Text style={styles.verifyButtonText}>
          {loading ? 'Verifying...' : 'Verify OTP'}
        </Text>
      </TouchableOpacity>

      <View style={styles.resendContainer}>
        {timer > 0 ? (
          <Text style={styles.timerText}>
            Resend OTP in {timer} seconds
          </Text>
        ) : (
          <TouchableOpacity
            onPress={handleResendOtp}
            disabled={resendLoading}
          >
            <Text style={styles.resendText}>
              {resendLoading ? 'Sending...' : 'Resend OTP'}
            </Text>
          </TouchableOpacity>
        )}
      </View>

      <TouchableOpacity onPress={onGoBack} style={styles.backButton}>
        <Text style={styles.backButtonText}>← Change Phone Number</Text>
      </TouchableOpacity>
    </KeyboardAvoidingView>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#F9FAFB',
    padding: 24,
    justifyContent: 'center',
  },
  header: {
    alignItems: 'center',
    marginBottom: 48,
  },
  title: {
    fontSize: 28,
    fontWeight: 'bold',
    color: '#1F2937',
    marginBottom: 12,
  },
  subtitle: {
    fontSize: 16,
    color: '#6B7280',
    textAlign: 'center',
    lineHeight: 24,
  },
  phoneNumber: {
    fontWeight: '600',
    color: '#2563EB',
  },
  otpContainer: {
    flexDirection: 'row',
    justifyContent: 'center',
    marginBottom: 32,
    gap: 12,
  },
  otpInput: {
    width: 48,
    height: 56,
    borderWidth: 2,
    borderColor: '#E5E7EB',
    borderRadius: 12,
    textAlign: 'center',
    fontSize: 24,
    fontWeight: '600',
    color: '#1F2937',
    backgroundColor: 'white',
  },
  otpInputFilled: {
    borderColor: '#2563EB',
    backgroundColor: '#EFF6FF',
  },
  verifyButton: {
    backgroundColor: '#2563EB',
    borderRadius: 12,
    paddingVertical: 16,
    alignItems: 'center',
    marginBottom: 24,
  },
  verifyButtonDisabled: {
    backgroundColor: '#9CA3AF',
  },
  verifyButtonText: {
    color: 'white',
    fontSize: 16,
    fontWeight: '600',
  },
  resendContainer: {
    alignItems: 'center',
    marginBottom: 32,
  },
  timerText: {
    color: '#6B7280',
    fontSize: 14,
  },
  resendText: {
    color: '#2563EB',
    fontSize: 14,
    fontWeight: '600',
  },
  backButton: {
    alignItems: 'center',
  },
  backButtonText: {
    color: '#6B7280',
    fontSize: 14,
  },
});

export default OTPScreen;
