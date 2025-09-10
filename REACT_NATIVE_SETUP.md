# React Native & Expo Development Setup Guide (Arch Linux)

## 🚀 Quick Answer: Do I need Android Studio?
**NO!** For Expo managed workflow (recommended for your civic app):
- ✅ Test on your actual phone using Expo Go app
- ✅ No Android Studio installation required
- ✅ No complex Android SDK setup needed
- ✅ Just install Node.js (✅ done) and create Expo project

**Only install Android Studio if:** you specifically want Android emulator testing (optional).

## ✅ Already Installed
- Node.js v24.7.0
- npm v11.5.2
- Java OpenJDK 24.0.2

## 🛠️ Required Tools Installation (Arch Linux)

### 1. Expo CLI (via npx - recommended)
```bash
# No global installation needed - use npx
npx @expo/cli --version  # ✅ Already working (v0.24.20)
```

### 2. React Native CLI (optional - mainly for bare React Native projects)
```bash
# For bare React Native projects (not needed for Expo managed workflow)
npx react-native@latest
```

### 3. Development Tools

#### 🎯 For Expo Managed Workflow (Recommended for your civic app):
```bash
# You DON'T need Android Studio!
# Just install Expo Go app on your phone for testing

# Optional: Android emulator setup (if you want to test on emulator)
# Only install if you specifically want Android emulator testing
yay -S android-studio  # Optional - only for emulator
```

#### 📱 Testing Options with Expo:
1. **Physical Device (Recommended)**:
   - Install Expo Go app from Play Store/App Store
   - Scan QR code from `npx expo start`
   - No Android Studio needed!

2. **Android Emulator (Optional)**:
   - Requires Android Studio or Android SDK
   - Useful for testing different screen sizes
   - Not required for development

#### For Bare React Native Projects (Not recommended for beginners):
```bash
# Only needed if you're NOT using Expo managed workflow
yay -S android-studio
# Full Android development environment required
```

#### For iOS Development (macOS only):
```bash
# Install Xcode from App Store
# Install iOS Simulator
# Install CocoaPods
sudo gem install cocoapods
```

### 4. Expo Development Build Tools
```bash
# Expo Application Services CLI (for building apps)
npx eas-cli@latest

# Install Expo Go app on your mobile device
# Android: https://play.google.com/store/apps/details?id=host.exp.exponent
# iOS: https://apps.apple.com/app/expo-go/id982107779
```

### 5. Useful Development Tools (Arch Linux)
```bash
# Watchman (file watching - recommended for React Native)
sudo pacman -S watchman

# React Developer Tools (optional)
npm install -g react-devtools

# Flipper (debugging tool - optional)
yay -S flipper

# Git (if not already installed)
sudo pacman -S git

# USB debugging tools
sudo pacman -S android-udev

# Optional: Install ADB if not included with android-tools
sudo pacman -S android-tools
```

## 📱 Getting Started with Your Civic App (Expo Managed Workflow)

### 1. Create Expo Project (No Android Studio needed!)
```bash
cd /home/grayscaledev/Developer/github.com/civic-app
npx create-expo-app@latest civic-app-mobile --template blank-typescript
cd civic-app-mobile
```

### 2. Install Additional Dependencies
```bash
# Navigation
npm install @react-navigation/native @react-navigation/stack @react-navigation/bottom-tabs
npx expo install react-native-screens react-native-safe-area-context

# HTTP requests
npm install axios

# Forms and validation
npm install react-hook-form yup @hookform/resolvers

# Image handling
npx expo install expo-image-picker expo-media-library

# Location services
npx expo install expo-location

# Camera
npx expo install expo-camera

# Async storage
npx expo install @react-native-async-storage/async-storage

# Push notifications
npx expo install expo-notifications

# Maps (if needed)
npm install react-native-maps
npx expo install expo-location
```

### 3. Start Development (Test on Your Phone!)
```bash
cd civic-app-mobile
npx expo start

# Scan the QR code with:
# - Android: Expo Go app (scan directly)
# - iOS: Camera app (will open in Expo Go)
```

## 🔧 Development Workflow

### Testing on Device
1. **Expo Go App**: Install Expo Go on your phone and scan QR code
2. **Android Emulator**: Start Android Studio AVD
3. **iOS Simulator**: Available on macOS only

### Building for Production
```bash
# Configure EAS Build
npx eas build:configure

# Build for Android
npx eas build --platform android

# Build for iOS (requires Apple Developer account)
npx eas build --platform ios
```

## 🌐 Backend Integration

Your FastAPI backend is ready at: `http://localhost:8000`

### Key API Endpoints to Integrate:
- `POST /auth/request-otp` - Request OTP
- `POST /auth/verify-otp` - Verify OTP & get JWT
- `POST /users/report-issue` - Report civic issues
- `POST /users/upload-file` - Upload images/files
- `GET /users/profile` - Get user profile
- `GET /admin/issues` - Admin: View all issues

### Example API Configuration:
```typescript
// config/api.ts
const API_BASE_URL = __DEV__ 
  ? 'http://10.0.2.2:8000'  // Android emulator
  // ? 'http://localhost:8000'  // iOS simulator
  : 'https://your-production-api.com';

export default API_BASE_URL;
```

## 📝 Next Steps

1. Install Android Studio or set up Android SDK
2. Create the Expo project
3. Set up navigation structure
4. Implement authentication flow
5. Create issue reporting screens
6. Integrate with your FastAPI backend
7. Test on device using Expo Go

## 🚨 Troubleshooting

### Common Issues:
- **Metro bundler issues**: Clear cache with `npx expo start --clear`
- **Android emulator not found**: Ensure ANDROID_HOME is set correctly
- **Network issues**: Use your local IP instead of localhost for device testing
- **Permission issues**: Use npx instead of global npm installs

### Get Your Local IP:
```bash
ip addr show | grep inet
# Use the 192.168.x.x address for testing on real devices
```
