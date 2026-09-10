import os
import json

base_fe = r"C:\Users\Admin\.gemini\antigravity\scratch\krishidrishti-edge\frontend"

# 1. package.json
package_json = {
  "name": "krishidrishti-edge-frontend",
  "private": True,
  "version": "1.0.0",
  "type": "module",
  "scripts": {
    "dev": "vite",
    "build": "tsc && vite build",
    "preview": "vite preview"
  },
  "dependencies": {
    "react": "^18.2.0",
    "react-dom": "^18.2.0",
    "lucide-react": "^0.344.0",
    "axios": "^1.6.7"
  },
  "devDependencies": {
    "@types/react": "^18.2.56",
    "@types/react-dom": "^18.2.19",
    "@vitejs/plugin-react": "^4.2.1",
    "autoprefixer": "^10.4.18",
    "postcss": "^8.4.35",
    "tailwindcss": "^3.4.1",
    "typescript": "^5.2.2",
    "vite": "^5.1.4"
  }
}

with open(os.path.join(base_fe, "package.json"), "w", encoding="utf-8") as f:
    json.dump(package_json, f, indent=2)

# 2. vite.config.ts
vite_config = """import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// https://vitejs.dev/config/
export default defineConfig({
  plugins: [react()],
  server: {
    host: '0.0.0.0',
    port: 5173,
    proxy: {
      '/api': {
        target: 'http://127.0.0.1:8000',
        changeOrigin: true,
      }
    }
  }
})
"""

with open(os.path.join(base_fe, "vite.config.ts"), "w", encoding="utf-8") as f:
    f.write(vite_config)

# 3. tsconfig.json
tsconfig = """{
  "compilerOptions": {
    "target": "ES2020",
    "useDefineForClassFields": true,
    "lib": ["ES2020", "DOM", "DOM.Iterable"],
    "module": "ESNext",
    "skipLibCheck": true,
    "moduleResolution": "bundler",
    "allowImportingTsExtensions": true,
    "resolveJsonModule": true,
    "isolatedModules": true,
    "noEmit": true,
    "jsx": "react-jsx",
    "strict": true,
    "noUnusedLocals": true,
    "noUnusedParameters": true,
    "noFallthroughCasesInSwitch": true
  },
  "include": ["src"],
  "references": [{ "path": "./tsconfig.node.json" }]
}
"""

with open(os.path.join(base_fe, "tsconfig.json"), "w", encoding="utf-8") as f:
    f.write(tsconfig)

# 4. tsconfig.node.json
tsconfig_node = """{
  "compilerOptions": {
    "composite": true,
    "skipLibCheck": true,
    "module": "ESNext",
    "moduleResolution": "bundler",
    "allowSyntheticDefaultImports": true
  },
  "include": ["vite.config.ts"]
}
"""

with open(os.path.join(base_fe, "tsconfig.node.json"), "w", encoding="utf-8") as f:
    f.write(tsconfig_node)

# 5. tailwind.config.js
tailwind_config = """/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        krishi: {
          dark: '#0f291e',
          forest: '#1b4d3e',
          leaf: '#2d6a4f',
          accent: '#52b788',
          light: '#d8f3dc',
          sand: '#f4f1de',
          clay: '#e07a5f',
          gold: '#e9c46a'
        }
      }
    },
  },
  plugins: [],
}
"""

with open(os.path.join(base_fe, "tailwind.config.js"), "w", encoding="utf-8") as f:
    f.write(tailwind_config)

# 6. postcss.config.js
postcss_config = """export default {
  plugins: {
    tailwindcss: {},
    autoprefixer: {},
  },
}
"""

with open(os.path.join(base_fe, "postcss.config.js"), "w", encoding="utf-8") as f:
    f.write(postcss_config)

# 7. index.html
index_html = """<!doctype html>
<html lang="en">
  <head>
    <meta charset="UTF-8" />
    <link rel="icon" type="image/svg+xml" href="/leaf.svg" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no" />
    <title>KrishiDrishti Edge | See. Sense. Predict. Act.</title>
  </head>
  <body class="bg-slate-900 text-slate-100 antialiased select-none">
    <div id="root"></div>
    <script type="module" src="/src/main.tsx"></script>
  </body>
</html>
"""

with open(os.path.join(base_fe, "index.html"), "w", encoding="utf-8") as f:
    f.write(index_html)

# 8. src/index.css
index_css = """@tailwind base;
@tailwind components;
@tailwind utilities;

:root {
  font-family: Inter, system-ui, Avenir, Helvetica, Arial, sans-serif;
  color-scheme: dark;
}

body {
  margin: 0;
  display: flex;
  min-width: 320px;
  min-height: 100vh;
  background-color: #0f172a;
}

/* Touchscreen UI Enhancements */
button {
  touch-action: manipulation;
}

/* Custom scrollbars for 7-inch touch screens */
::-webkit-scrollbar {
  width: 6px;
  height: 6px;
}
::-webkit-scrollbar-track {
  background: #1e293b;
}
::-webkit-scrollbar-thumb {
  background: #334155;
  border-radius: 3px;
}
"""

with open(os.path.join(base_fe, "src", "index.css"), "w", encoding="utf-8") as f:
    f.write(index_css)

# 9. i18n translation files
en_json = {
  "app_name": "KrishiDrishti Edge",
  "tagline": "See. Sense. Predict. Act.",
  "status_online": "Connected",
  "status_offline": "Offline Edge Mode",
  "demo_badge": "DEMO / SIMULATION MODE",
  "nav_dashboard": "Dashboard",
  "nav_scanner": "Crop Scan",
  "nav_soil": "Soil Probe",
  "nav_risk": "Field Risk",
  "nav_advisory": "Advisory",
  "nav_history": "History",
  "nav_diagnostics": "Diagnostics",
  "nav_settings": "Settings",
  "battery": "Battery",
  "ai_mode": "AI Mode",
  "soil_status": "Soil Sensor",
  "camera_status": "Camera"
}

hi_json = {
  "app_name": "कृषिदृष्टि एज",
  "tagline": "देखें. मापें. समझें. कार्य करें.",
  "status_online": "कनेक्टेड",
  "status_offline": "ऑफलाइन एज मोड",
  "demo_badge": "डेमो / सिमुलेशन मोड",
  "nav_dashboard": "डैशबोर्ड",
  "nav_scanner": "फसल स्कैन",
  "nav_soil": "मृदा जांच",
  "nav_risk": "खेत जोखिम",
  "nav_advisory": "कृषि सलाह",
  "nav_history": "इतिहास",
  "nav_diagnostics": "जांच व स्थिति",
  "nav_settings": "सेटिंग्स",
  "battery": "बैटरी",
  "ai_mode": "एआई मोड",
  "soil_status": "मृदा सेंसर",
  "camera_status": "कैमरा"
}

mr_json = {
  "app_name": "कृषिदृष्टी एज",
  "tagline": "पाहा. मोजा. ओळखा. कृती करा.",
  "status_online": "कनेक्टेड",
  "status_offline": "ऑफलाइन एज मोड",
  "demo_badge": "डेमो / सिम्युलेशन मोड",
  "nav_dashboard": "डॅशबोर्ड",
  "nav_scanner": "पीक स्कॅन",
  "nav_soil": "माती तपासणी",
  "nav_risk": "शेत जोखीम",
  "nav_advisory": "सल्लागार",
  "nav_history": "इतिहास",
  "nav_diagnostics": "निदान व स्थिती",
  "nav_settings": "सेटिंग्ज",
  "battery": "बॅटरी",
  "ai_mode": "एआय मोड",
  "soil_status": "माती सेन्सर",
  "camera_status": "कॅमेरा"
}

locales_dir = os.path.join(base_fe, "src", "i18n", "locales")
with open(os.path.join(locales_dir, "en.json"), "w", encoding="utf-8") as f:
    json.dump(en_json, f, ensure_ascii=False, indent=2)

with open(os.path.join(locales_dir, "hi.json"), "w", encoding="utf-8") as f:
    json.dump(hi_json, f, ensure_ascii=False, indent=2)

with open(os.path.join(locales_dir, "mr.json"), "w", encoding="utf-8") as f:
    json.dump(mr_json, f, ensure_ascii=False, indent=2)

# 10. src/services/api.ts
api_ts = """import axios from 'axios';

const api = axios.create({
  baseURL: '/api',
  timeout: 10000,
});

export interface DeviceStatus {
  status: string;
  app_version: string;
  app_name: string;
  demo_mode: bool;
  mode_label: string;
  uptime_seconds: number;
  cpu_temperature_celsius: number | null;
  cpu_usage_percent: number;
  ram_usage_percent: number;
  storage_usage_percent: number;
  battery: {
    percent: number;
    power_plugged: boolean;
    status: string;
    is_mock: boolean;
  };
  subsystems: {
    camera: { status: string; details: string; is_mock: boolean };
    soil_sensor: { status: string; details: string; is_mock: boolean };
    ai_engine: { status: string; details: string; is_mock: boolean };
    database: { status: string; details: string; is_mock: boolean };
  };
}

export const fetchHealth = async () => {
  const res = await api.get('/health');
  return res.data;
};

export const fetchDeviceStatus = async (): Promise<DeviceStatus> => {
  const res = await api.get('/device/status');
  return res.data;
};

export default api;
"""

with open(os.path.join(base_fe, "src", "services", "api.ts"), "w", encoding="utf-8") as f:
    f.write(api_ts)

# 11. src/main.tsx
main_tsx = """import React from 'react'
import ReactDOM from 'react-dom/client'
import App from './App'
import './index.css'

ReactDOM.createRoot(document.getElementById('root')!).render(
  <React.StrictMode>
    <App />
  </React.StrictMode>,
)
"""

with open(os.path.join(base_fe, "src", "main.tsx"), "w", encoding="utf-8") as f:
    f.write(main_tsx)

# 12. src/App.tsx
app_tsx = """import React, { useState, useEffect } from 'react';
import { 
  Sprout, 
  Camera, 
  Cpu, 
  Activity, 
  History as HistoryIcon, 
  Settings as SettingsIcon, 
  Battery, 
  BatteryCharging, 
  ShieldAlert, 
  CheckCircle2, 
  AlertTriangle,
  Layers,
  FileText,
  Languages
} from 'lucide-react';
import { fetchDeviceStatus, DeviceStatus } from './services/api';
import en from './i18n/locales/en.json';
import hi from './i18n/locales/hi.json';
import mr from './i18n/locales/mr.json';

const translations: Record<string, Record<string, string>> = { en, hi, mr };

export default function App() {
  const [lang, setLang] = useState<'en' | 'hi' | 'mr'>('en');
  const [activeTab, setActiveTab] = useState<'dashboard' | 'scanner' | 'soil' | 'risk' | 'advisory' | 'history' | 'diagnostics' | 'settings'>('dashboard');
  const [deviceStatus, setDeviceStatus] = useState<DeviceStatus | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const t = (key: string) => translations[lang][key] || key;

  useEffect(() => {
    const loadStatus = async () => {
      try {
        const data = await fetchDeviceStatus();
        setDeviceStatus(data);
        setError(null);
      } catch (err: any) {
        setError('Device backend offline or initializing...');
      } finally {
        setLoading(false);
      }
    };

    loadStatus();
    const interval = setInterval(loadStatus, 4000);
    return () => clearInterval(interval);
  }, []);

  return (
    <div className="flex flex-col h-screen w-screen overflow-hidden bg-slate-950 text-slate-100">
      {/* Top Embedded Hardware Status Bar */}
      <header className="bg-slate-900 border-b border-slate-800 px-4 py-2.5 flex items-center justify-between text-sm select-none">
        <div className="flex items-center space-x-3">
          <div className="flex items-center space-x-2 bg-emerald-950 text-emerald-400 border border-emerald-800/60 px-2.5 py-1 rounded-md font-semibold tracking-wide text-xs">
            <Sprout className="w-4 h-4 text-emerald-400" />
            <span>{t('app_name')}</span>
          </div>

          {/* DEMO / MOCK Badge */}
          {deviceStatus?.demo_mode && (
            <div className="flex items-center space-x-1.5 bg-amber-500/20 text-amber-300 border border-amber-500/40 px-2.5 py-1 rounded-md text-xs font-bold animate-pulse">
              <AlertTriangle className="w-3.5 h-3.5 text-amber-400" />
              <span>{t('demo_badge')}</span>
            </div>
          )}

          {/* Offline/Edge indicator */}
          <div className="flex items-center space-x-1.5 bg-cyan-950/80 text-cyan-300 border border-cyan-800/50 px-2.5 py-1 rounded-md text-xs font-medium">
            <span className="w-2 h-2 rounded-full bg-cyan-400 animate-ping"></span>
            <span>{t('status_offline')}</span>
          </div>
        </div>

        {/* Right Status Indicators */}
        <div className="flex items-center space-x-4">
          {/* AI Mode */}
          <div className="flex items-center space-x-1.5 text-xs text-slate-300 bg-slate-800/80 px-2.5 py-1 rounded border border-slate-700">
            <Cpu className="w-3.5 h-3.5 text-purple-400" />
            <span className="font-mono">AI: {deviceStatus?.subsystems?.ai_engine?.status || 'STANDBY'}</span>
          </div>

          {/* Soil Status */}
          <div className="flex items-center space-x-1.5 text-xs text-slate-300 bg-slate-800/80 px-2.5 py-1 rounded border border-slate-700">
            <Layers className="w-3.5 h-3.5 text-emerald-400" />
            <span className="font-mono">SOIL: {deviceStatus?.subsystems?.soil_sensor?.status || 'CHECKING'}</span>
          </div>

          {/* Battery Status */}
          <div className="flex items-center space-x-1.5 text-xs text-slate-300 bg-slate-800/80 px-2.5 py-1 rounded border border-slate-700">
            {deviceStatus?.battery?.power_plugged ? (
              <BatteryCharging className="w-4 h-4 text-emerald-400" />
            ) : (
              <Battery className="w-4 h-4 text-emerald-400" />
            )}
            <span className="font-mono">{deviceStatus?.battery?.percent ?? 88}%</span>
          </div>

          {/* Language Selector */}
          <div className="flex items-center bg-slate-800 rounded border border-slate-700 p-0.5 text-xs">
            <button
              onClick={() => setLang('en')}
              className={`px-2 py-0.5 rounded font-medium transition ${lang === 'en' ? 'bg-emerald-600 text-white font-bold' : 'text-slate-400 hover:text-white'}`}
            >
              EN
            </button>
            <button
              onClick={() => setLang('hi')}
              className={`px-2 py-0.5 rounded font-medium transition ${lang === 'hi' ? 'bg-emerald-600 text-white font-bold' : 'text-slate-400 hover:text-white'}`}
            >
              हिंदी
            </button>
            <button
              onClick={() => setLang('mr')}
              className={`px-2 py-0.5 rounded font-medium transition ${lang === 'mr' ? 'bg-emerald-600 text-white font-bold' : 'text-slate-400 hover:text-white'}`}
            >
              मराठी
            </button>
          </div>
        </div>
      </header>

      {/* Main Touch Workspace */}
      <main className="flex-1 flex overflow-hidden p-3 gap-3">
        {/* Left Touch Navigation Bar */}
        <nav className="w-48 bg-slate-900 border border-slate-800 rounded-xl p-2 flex flex-col justify-between shrink-0 select-none">
          <div className="space-y-1.5">
            <button
              onClick={() => setActiveTab('dashboard')}
              className={`w-full flex items-center space-x-3 px-3.5 py-3 rounded-lg text-sm font-semibold transition ${
                activeTab === 'dashboard' ? 'bg-emerald-600 text-white shadow-lg shadow-emerald-900/40' : 'text-slate-300 hover:bg-slate-800'
              }`}
            >
              <Activity className="w-5 h-5 shrink-0" />
              <span>{t('nav_dashboard')}</span>
            </button>

            <button
              onClick={() => setActiveTab('scanner')}
              className={`w-full flex items-center space-x-3 px-3.5 py-3 rounded-lg text-sm font-semibold transition ${
                activeTab === 'scanner' ? 'bg-emerald-600 text-white shadow-lg shadow-emerald-900/40' : 'text-slate-300 hover:bg-slate-800'
              }`}
            >
              <Camera className="w-5 h-5 shrink-0" />
              <span>{t('nav_scanner')}</span>
            </button>

            <button
              onClick={() => setActiveTab('soil')}
              className={`w-full flex items-center space-x-3 px-3.5 py-3 rounded-lg text-sm font-semibold transition ${
                activeTab === 'soil' ? 'bg-emerald-600 text-white shadow-lg shadow-emerald-900/40' : 'text-slate-300 hover:bg-slate-800'
              }`}
            >
              <Layers className="w-5 h-5 shrink-0" />
              <span>{t('nav_soil')}</span>
            </button>

            <button
              onClick={() => setActiveTab('risk')}
              className={`w-full flex items-center space-x-3 px-3.5 py-3 rounded-lg text-sm font-semibold transition ${
                activeTab === 'risk' ? 'bg-emerald-600 text-white shadow-lg shadow-emerald-900/40' : 'text-slate-300 hover:bg-slate-800'
              }`}
            >
              <ShieldAlert className="w-5 h-5 shrink-0" />
              <span>{t('nav_risk')}</span>
            </button>

            <button
              onClick={() => setActiveTab('advisory')}
              className={`w-full flex items-center space-x-3 px-3.5 py-3 rounded-lg text-sm font-semibold transition ${
                activeTab === 'advisory' ? 'bg-emerald-600 text-white shadow-lg shadow-emerald-900/40' : 'text-slate-300 hover:bg-slate-800'
              }`}
            >
              <FileText className="w-5 h-5 shrink-0" />
              <span>{t('nav_advisory')}</span>
            </button>

            <button
              onClick={() => setActiveTab('history')}
              className={`w-full flex items-center space-x-3 px-3.5 py-3 rounded-lg text-sm font-semibold transition ${
                activeTab === 'history' ? 'bg-emerald-600 text-white shadow-lg shadow-emerald-900/40' : 'text-slate-300 hover:bg-slate-800'
              }`}
            >
              <HistoryIcon className="w-5 h-5 shrink-0" />
              <span>{t('nav_history')}</span>
            </button>
          </div>

          <div className="space-y-1.5 pt-2 border-t border-slate-800">
            <button
              onClick={() => setActiveTab('diagnostics')}
              className={`w-full flex items-center space-x-3 px-3.5 py-2.5 rounded-lg text-xs font-semibold transition ${
                activeTab === 'diagnostics' ? 'bg-emerald-600 text-white' : 'text-slate-400 hover:bg-slate-800 hover:text-white'
              }`}
            >
              <CheckCircle2 className="w-4 h-4 shrink-0" />
              <span>{t('nav_diagnostics')}</span>
            </button>

            <button
              onClick={() => setActiveTab('settings')}
              className={`w-full flex items-center space-x-3 px-3.5 py-2.5 rounded-lg text-xs font-semibold transition ${
                activeTab === 'settings' ? 'bg-emerald-600 text-white' : 'text-slate-400 hover:bg-slate-800 hover:text-white'
              }`}
            >
              <SettingsIcon className="w-4 h-4 shrink-0" />
              <span>{t('nav_settings')}</span>
            </button>
          </div>
        </nav>

        {/* Main Content Area */}
        <section className="flex-1 bg-slate-900/70 border border-slate-800 rounded-xl p-5 overflow-y-auto flex flex-col justify-between">
          <div>
            <div className="flex items-center justify-between pb-4 border-b border-slate-800">
              <div>
                <h1 className="text-2xl font-bold text-slate-100 flex items-center space-x-2">
                  <span>{t(`nav_${activeTab}`)}</span>
                </h1>
                <p className="text-xs text-slate-400 mt-0.5">{t('tagline')}</p>
              </div>

              {/* Hardware Host Quick Telemetry */}
              {deviceStatus && (
                <div className="flex items-center space-x-3 text-xs font-mono bg-slate-800/80 px-3 py-1.5 rounded-lg border border-slate-700">
                  <span className="text-slate-400">CPU: <b className="text-slate-200">{deviceStatus.cpu_usage_percent}%</b></span>
                  <span className="text-slate-400">RAM: <b className="text-slate-200">{deviceStatus.ram_usage_percent}%</b></span>
                  {deviceStatus.cpu_temperature_celsius && (
                    <span className="text-slate-400">TEMP: <b className="text-amber-400">{deviceStatus.cpu_temperature_celsius}°C</b></span>
                  )}
                </div>
              )}
            </div>

            {/* Viewport content */}
            <div className="mt-6">
              {activeTab === 'dashboard' && (
                <div className="grid grid-cols-3 gap-4">
                  {/* Crop Health Card */}
                  <div className="bg-slate-800/60 border border-slate-700 rounded-xl p-4 shadow-sm">
                    <div className="flex justify-between items-center text-slate-400 text-xs font-medium">
                      <span>Crop Health</span>
                      <Sprout className="w-4 h-4 text-emerald-400" />
                    </div>
                    <div className="mt-2 text-3xl font-extrabold text-emerald-400">78%</div>
                    <div className="mt-1 text-xs text-emerald-300/80 font-medium">Healthy (Vegetative stage)</div>
                  </div>

                  {/* Disease Risk Card */}
                  <div className="bg-slate-800/60 border border-slate-700 rounded-xl p-4 shadow-sm">
                    <div className="flex justify-between items-center text-slate-400 text-xs font-medium">
                      <span>Disease Risk</span>
                      <ShieldAlert className="w-4 h-4 text-amber-400" />
                    </div>
                    <div className="mt-2 text-3xl font-extrabold text-amber-400">Medium</div>
                    <div className="mt-1 text-xs text-slate-400">Early Blight symptoms scanned</div>
                  </div>

                  {/* Soil Moisture Card */}
                  <div className="bg-slate-800/60 border border-slate-700 rounded-xl p-4 shadow-sm">
                    <div className="flex justify-between items-center text-slate-400 text-xs font-medium">
                      <span>Soil Moisture</span>
                      <Layers className="w-4 h-4 text-cyan-400" />
                    </div>
                    <div className="mt-2 text-3xl font-extrabold text-cyan-400">24.2%</div>
                    <div className="mt-1 text-xs text-cyan-300/80 font-medium">Optimal Rhizosphere Zone</div>
                  </div>
                </div>
              )}

              {activeTab !== 'dashboard' && (
                <div className="p-8 text-center text-slate-400 border border-dashed border-slate-800 rounded-xl">
                  <div className="text-lg font-semibold text-slate-200">
                    Phase Scaffolding: {t(`nav_${activeTab}`)} module
                  </div>
                  <p className="text-xs text-slate-500 mt-2 max-w-md mx-auto">
                    This module is connected to the centralized architecture and ready for Phase 2-15 progressive feature integration.
                  </p>
                </div>
              )}
            </div>
          </div>

          {/* Footer note */}
          <div className="pt-4 border-t border-slate-800/80 flex justify-between items-center text-[11px] text-slate-500">
            <div>KrishiDrishti Edge &bull; Smart India Hackathon 2026 Prototype</div>
            <div>Offline Edge System &bull; Version 1.0.0</div>
          </div>
        </section>
      </main>
    </div>
  );
}
"""

with open(os.path.join(base_fe, "src", "App.tsx"), "w", encoding="utf-8") as f:
    f.write(app_tsx)

print("Frontend foundation files created successfully.")
