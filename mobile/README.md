# ALCC Mobile

Expo React Native app for iOS and Android — connected to all ALCC backend services with 3D animations.

## Quick Start

```bash
npm install
cp .env.example .env   # set your LAN IP for physical device testing
npx expo start
```

Scan QR code with **Expo Go** (Android/iOS) or press `a` / `i` for emulator.

## API Configuration

On a physical device, `localhost` won't work. Set your machine's LAN IP:

```
EXPO_PUBLIC_API_URL=http://192.168.1.XXX:8000
EXPO_PUBLIC_WS_URL=ws://192.168.1.XXX:8000
```

Ensure backend CORS includes your dev origin or use `--host 0.0.0.0` for uvicorn.

## Screens

| Tab | Backend Service |
|-----|----------------|
| Dashboard | Analytics + Tracking + WebSocket |
| Fleet | Fleet (3D vehicle previews) |
| Missions | Routing |
| Tracking | Tracking + WebSocket (3D globe) |
| Alertes | Notification |
| Analytics | Analytics |
| Tasks | Celery Worker |

## 3D Stack

- **expo-gl** + **@react-three/fiber/native** + **three.js**
- Procedural vehicle models (M-Series, X-Drive, i-Freight inspired)
- Rotating showroom on login, fleet globe on dashboard/tracking

## Demo Accounts

| Email | Password |
|-------|----------|
| admin@alcc.io | admin1234 |
| operator@alcc.io | operator123 |
