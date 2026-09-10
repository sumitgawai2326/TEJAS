import React, { useState, useEffect } from 'react';
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
  AlertTriangle,
  Layers,
  FileText,
  CheckCircle2,
  WifiOff,
  Upload,
  RefreshCw,
  Clock,
  Zap,
  CheckCircle,
  XCircle,
  ArrowRight,
  PlusCircle,
  PlayCircle,
  Droplets,
  Check,
  RotateCcw
} from 'lucide-react';
import { 
  fetchDeviceStatus, 
  fetchFields, 
  createField,
  fetchFieldHistory,
  analyzeCropImage, 
  fetchVisionStatus,
  analyzeField,
  fetchFieldAdvisories,
  recordSoilReading,
  fetchDeviceSelfTest,
  fetchRegisteredModels,
  DeviceStatus, 
  FieldModel, 
  VisionAnalysisResponse, 
  VisionStatusResponse,
  FieldHistoryModel,
  FieldAnalysisResponse,
  FarmerAdvisoryItem,
  SoilReadingModel,
  SelfTestResponse,
  ModelRegistryResponse
} from './services/api';

import en from './i18n/locales/en.json';
import hi from './i18n/locales/hi.json';
import mr from './i18n/locales/mr.json';

const translations: Record<string, Record<string, string>> = { en, hi, mr };

export default function App() {
  const [lang, setLang] = useState<'en' | 'hi' | 'mr'>('en');
  const [activeTab, setActiveTab] = useState<'home' | 'wizard' | 'fields' | 'scanner' | 'soil' | 'risk' | 'advisory' | 'history' | 'diagnostics' | 'settings'>('home');
  const [deviceStatus, setDeviceStatus] = useState<DeviceStatus | null>(null);
  const [hasError, setHasError] = useState(false);

  // Field & Scanner State
  const [fields, setFields] = useState<FieldModel[]>([]);
  const [selectedFieldId, setSelectedFieldId] = useState<number | null>(null);
  const [visionStatus, setVisionStatus] = useState<VisionStatusResponse | null>(null);
  const [scanResult, setScanResult] = useState<VisionAnalysisResponse | null>(null);
  const [isScanning, setIsScanning] = useState(false);
  const [scanError, setScanError] = useState<string | null>(null);
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [previewUrl, setPreviewUrl] = useState<string | null>(null);

  // Guided Wizard State (Steps 1 to 7)
  const [wizardStep, setWizardStep] = useState<number>(1);
  const [liveSoilReading, setLiveSoilReading] = useState<SoilReadingModel | null>(null);
  const [isReadingSoil, setIsReadingSoil] = useState(false);

  // Fusion & Risk & Advisory State
  const [fusionResult, setFusionResult] = useState<FieldAnalysisResponse | null>(null);
  const [isFusing, setIsFusing] = useState(false);
  const [advisoryList, setAdvisoryList] = useState<FarmerAdvisoryItem[]>([]);
  const [isLoadingAdvisories, setIsLoadingAdvisories] = useState(false);

  // Add Field Modal State
  const [showAddFieldModal, setShowAddFieldModal] = useState(false);
  const [newFieldName, setNewFieldName] = useState('');
  const [newFieldSoilType, setNewFieldSoilType] = useState('Black Cotton');
  const [newFieldArea, setNewFieldArea] = useState('2.0');
  const [isCreatingField, setIsCreatingField] = useState(false);

  // History State
  const [historyData, setHistoryData] = useState<FieldHistoryModel | null>(null);
  const [isLoadingHistory, setIsLoadingHistory] = useState(false);
  const [historyFilter, setHistoryFilter] = useState<'ALL' | 'SCAN' | 'SOIL' | 'RISK' | 'ADVISORY'>('ALL');

  // Self-Test & Model Registry State
  const [selfTestResult, setSelfTestResult] = useState<SelfTestResponse | null>(null);
  const [isRunningSelfTest, setIsRunningSelfTest] = useState(false);
  const [modelRegistry, setModelRegistry] = useState<ModelRegistryResponse | null>(null);

  const t = (key: string) => translations[lang]?.[key] || key;

  // Polling device telemetry
  useEffect(() => {
    const loadStatus = async () => {
      try {
        const data = await fetchDeviceStatus();
        setDeviceStatus(data);
        setHasError(false);
      } catch {
        setHasError(true);
      }
    };

    loadStatus();
    const interval = setInterval(loadStatus, 3000);
    return () => clearInterval(interval);
  }, []);

  // Load fields and AI status on startup
  useEffect(() => {
    refreshFields();
  }, []);

  const refreshFields = async () => {
    try {
      const fieldList = await fetchFields();
      setFields(fieldList);
      if (fieldList.length > 0 && selectedFieldId === null) {
        setSelectedFieldId(fieldList[0].id);
      }
      const vStatus = await fetchVisionStatus();
      setVisionStatus(vStatus);
      const mRegistry = await fetchRegisteredModels();
      setModelRegistry(mRegistry);
    } catch (e) {
      console.error("Failed to load initial fields/vision/models data", e);
    }
  };

  // Load field history or advisories when tab changes
  useEffect(() => {
    if (activeTab === 'history' && selectedFieldId) {
      loadHistory(selectedFieldId);
    } else if (activeTab === 'advisory' && selectedFieldId) {
      loadAdvisories(selectedFieldId);
    }
  }, [activeTab, selectedFieldId]);

  const loadHistory = async (fieldId: number) => {
    setIsLoadingHistory(true);
    try {
      const hist = await fetchFieldHistory(fieldId);
      setHistoryData(hist);
    } catch (e) {
      console.error("Failed to fetch history", e);
    } finally {
      setIsLoadingHistory(false);
    }
  };

  const loadAdvisories = async (fieldId: number) => {
    setIsLoadingAdvisories(true);
    try {
      const advs = await fetchFieldAdvisories(fieldId);
      setAdvisoryList(advs);
    } catch (e) {
      console.error("Failed to fetch advisories", e);
    } finally {
      setIsLoadingAdvisories(false);
    }
  };

  const handleFileSelect = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      const file = e.target.files[0];
      setSelectedFile(file);
      setPreviewUrl(URL.createObjectURL(file));
      setScanResult(null);
      setScanError(null);
    }
  };

  const executeScan = async (useCamera = false) => {
    setIsScanning(true);
    setScanError(null);
    try {
      const formData = new FormData();
      if (useCamera) {
        formData.append('use_camera', 'true');
      } else if (selectedFile) {
        formData.append('file', selectedFile);
      } else {
        formData.append('use_camera', 'true');
      }

      if (selectedFieldId) {
        formData.append('field_id', selectedFieldId.toString());
      }

      const res = await analyzeCropImage(formData);
      setScanResult(res);
      return res;
    } catch (err: any) {
      const msg = err.response?.data?.detail || err.message || 'Vision analysis failed';
      setScanError(msg);
      return null;
    } finally {
      setIsScanning(false);
    }
  };

  const triggerLiveSoil = async (fieldId: number) => {
    setIsReadingSoil(true);
    try {
      const reading = await recordSoilReading(fieldId);
      setLiveSoilReading(reading);
      return reading;
    } catch (e) {
      console.error("Error reading live soil sensor", e);
      return null;
    } finally {
      setIsReadingSoil(false);
    }
  };

  const executeFusion = async () => {
    if (!selectedFieldId) return;
    setIsFusing(true);
    try {
      const formData = new FormData();
      if (selectedFile) {
        formData.append('file', selectedFile);
      }
      formData.append('trigger_soil_read', 'true');

      const res = await analyzeField(selectedFieldId, formData);
      setFusionResult(res);
      setAdvisoryList(res.advisories);
      return res;
    } catch (err: any) {
      console.error("Fusion analysis error", err);
      return null;
    } finally {
      setIsFusing(false);
    }
  };

  const handleCreateField = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!newFieldName.trim()) return;
    setIsCreatingField(true);
    try {
      const created = await createField({
        name: newFieldName.trim(),
        soil_type: newFieldSoilType,
        area: parseFloat(newFieldArea) || 1.0
      });
      setShowAddFieldModal(false);
      setNewFieldName('');
      await refreshFields();
      setSelectedFieldId(created.id);
    } catch (err) {
      console.error("Failed to create field", err);
    } finally {
      setIsCreatingField(false);
    }
  };

  const handleRunSelfTest = async () => {
    setIsRunningSelfTest(true);
    try {
      const res = await fetchDeviceSelfTest();
      setSelfTestResult(res);
    } catch (err) {
      console.error("Self-test error", err);
    } finally {
      setIsRunningSelfTest(false);
    }
  };

  const selectedField = fields.find(f => f.id === selectedFieldId);

  return (
    <div className="flex flex-col h-screen w-screen overflow-hidden bg-slate-950 text-slate-100 font-sans select-none">
      {/* ------------------------------------------------------------- */}
      {/* TOP EMBEDDED RUGGED HARDWARE STATUS BAR                       */}
      {/* ------------------------------------------------------------- */}
      <header className="bg-slate-900 border-b border-slate-800 px-4 py-3 flex items-center justify-between text-sm shrink-0">
        <div className="flex items-center space-x-3">
          <div className="flex items-center space-x-2 bg-emerald-950 text-emerald-400 border border-emerald-800/80 px-3 py-1.5 rounded-lg font-bold tracking-wide text-xs">
            <Sprout className="w-4 h-4 text-emerald-400 shrink-0" />
            <span>{t('app_name')}</span>
          </div>

          {/* Explicit DEMO vs REAL Badge */}
          {deviceStatus?.demo_mode ? (
            <div className="flex items-center space-x-1.5 bg-amber-500/20 text-amber-300 border border-amber-500/50 px-3 py-1 rounded-md text-xs font-bold tracking-wider animate-pulse">
              <AlertTriangle className="w-4 h-4 text-amber-400 shrink-0" />
              <span>{t('demo_badge')}</span>
            </div>
          ) : (
            <div className="flex items-center space-x-1.5 bg-emerald-950 text-emerald-300 border border-emerald-700 px-3 py-1 rounded-md text-xs font-bold tracking-wider">
              <CheckCircle2 className="w-4 h-4 text-emerald-400 shrink-0" />
              <span>{t('real_badge')}</span>
            </div>
          )}

          {/* Offline/Edge indicator */}
          <div className="flex items-center space-x-1.5 bg-cyan-950/80 text-cyan-300 border border-cyan-800/60 px-2.5 py-1 rounded-md text-xs font-semibold">
            <WifiOff className="w-3.5 h-3.5 text-cyan-400 shrink-0" />
            <span>{t('status_offline')}</span>
          </div>

          {hasError && (
            <div className="text-xs text-rose-300 bg-rose-950 border border-rose-800 px-2.5 py-1 rounded font-bold">
              Backend Offline
            </div>
          )}
        </div>

        {/* Right Hardware Telemetry Indicators */}
        <div className="flex items-center space-x-3">
          {/* AI Accelerator Indicator */}
          <div className="hidden sm:flex items-center space-x-1.5 text-xs text-slate-300 bg-slate-800 px-3 py-1 rounded-lg border border-slate-700">
            <Cpu className="w-4 h-4 text-purple-400 shrink-0" />
            <span className="font-mono">AI: <b className="text-purple-300">{deviceStatus?.ai_status_label || 'CPU'}</b></span>
          </div>

          {/* Battery Status */}
          <div className="flex items-center space-x-1.5 text-xs text-slate-300 bg-slate-800 px-3 py-1 rounded-lg border border-slate-700">
            {deviceStatus?.battery?.power_plugged ? (
              <BatteryCharging className="w-4 h-4 text-emerald-400 shrink-0" />
            ) : (
              <Battery className="w-4 h-4 text-emerald-400 shrink-0" />
            )}
            <span className="font-mono font-bold">{deviceStatus?.battery?.percent ?? '--'}%</span>
          </div>

          {/* One-Touch Multilingual Selector */}
          <div className="flex items-center bg-slate-800 rounded-lg border border-slate-700 p-1 text-xs font-bold space-x-1">
            <button
              onClick={() => setLang('en')}
              className={`px-2.5 py-1 rounded transition ${lang === 'en' ? 'bg-emerald-600 text-white shadow' : 'text-slate-400 hover:text-white'}`}
            >
              EN
            </button>
            <button
              onClick={() => setLang('hi')}
              className={`px-2.5 py-1 rounded transition ${lang === 'hi' ? 'bg-emerald-600 text-white shadow' : 'text-slate-400 hover:text-white'}`}
            >
              हिंदी
            </button>
            <button
              onClick={() => setLang('mr')}
              className={`px-2.5 py-1 rounded transition ${lang === 'mr' ? 'bg-emerald-600 text-white shadow' : 'text-slate-400 hover:text-white'}`}
            >
              मराठी
            </button>
          </div>
        </div>
      </header>

      {/* ------------------------------------------------------------- */}
      {/* MAIN TOUCH WORKSPACE & NAVIGATION                             */}
      {/* ------------------------------------------------------------- */}
      <main className="flex-1 flex overflow-hidden p-3 gap-3">
        {/* Rugged Touch Left Navigation Bar */}
        <nav className="w-52 bg-slate-900 border border-slate-800 rounded-2xl p-2.5 flex flex-col justify-between shrink-0 select-none shadow-xl">
          <div className="space-y-1.5">
            {/* 1. Home Dashboard */}
            <button
              onClick={() => setActiveTab('home')}
              className={`w-full flex items-center space-x-3 px-3.5 py-3 rounded-xl text-sm font-bold transition ${
                activeTab === 'home' ? 'bg-emerald-600 text-white shadow-lg shadow-emerald-900/40' : 'text-slate-300 hover:bg-slate-800'
              }`}
            >
              <Activity className="w-5 h-5 shrink-0" />
              <span>{t('nav_home')}</span>
            </button>

            {/* 2. Guided Field Check Wizard */}
            <button
              onClick={() => {
                setActiveTab('wizard');
                setWizardStep(1);
              }}
              className={`w-full flex items-center space-x-3 px-3.5 py-3 rounded-xl text-sm font-bold transition ${
                activeTab === 'wizard' ? 'bg-cyan-600 text-white shadow-lg shadow-cyan-900/40' : 'text-cyan-300 bg-cyan-950/40 border border-cyan-800/40 hover:bg-cyan-900/50'
              }`}
            >
              <PlayCircle className="w-5 h-5 shrink-0 text-cyan-400" />
              <span>{t('nav_wizard')}</span>
            </button>

            {/* 3. Fields / Plots */}
            <button
              onClick={() => setActiveTab('fields')}
              className={`w-full flex items-center space-x-3 px-3.5 py-2.5 rounded-xl text-sm font-semibold transition ${
                activeTab === 'fields' ? 'bg-emerald-600 text-white' : 'text-slate-300 hover:bg-slate-800'
              }`}
            >
              <Layers className="w-5 h-5 shrink-0" />
              <span>{t('nav_fields')}</span>
            </button>

            {/* 4. Standalone Crop Scanner */}
            <button
              onClick={() => setActiveTab('scanner')}
              className={`w-full flex items-center space-x-3 px-3.5 py-2.5 rounded-xl text-sm font-semibold transition ${
                activeTab === 'scanner' ? 'bg-emerald-600 text-white' : 'text-slate-300 hover:bg-slate-800'
              }`}
            >
              <Camera className="w-5 h-5 shrink-0" />
              <span>{t('nav_scanner')}</span>
            </button>

            {/* 5. 6-Parameter Soil Module */}
            <button
              onClick={() => setActiveTab('soil')}
              className={`w-full flex items-center space-x-3 px-3.5 py-2.5 rounded-xl text-sm font-semibold transition ${
                activeTab === 'soil' ? 'bg-emerald-600 text-white' : 'text-slate-300 hover:bg-slate-800'
              }`}
            >
              <Droplets className="w-5 h-5 shrink-0" />
              <span>{t('nav_soil')}</span>
            </button>

            {/* 6. Multi-Modal Risk */}
            <button
              onClick={() => setActiveTab('risk')}
              className={`w-full flex items-center space-x-3 px-3.5 py-2.5 rounded-xl text-sm font-semibold transition ${
                activeTab === 'risk' ? 'bg-emerald-600 text-white' : 'text-slate-300 hover:bg-slate-800'
              }`}
            >
              <ShieldAlert className="w-5 h-5 shrink-0" />
              <span>{t('nav_risk')}</span>
            </button>

            {/* 7. Actionable Advisories */}
            <button
              onClick={() => setActiveTab('advisory')}
              className={`w-full flex items-center space-x-3 px-3.5 py-2.5 rounded-xl text-sm font-semibold transition ${
                activeTab === 'advisory' ? 'bg-emerald-600 text-white' : 'text-slate-300 hover:bg-slate-800'
              }`}
            >
              <FileText className="w-5 h-5 shrink-0" />
              <span>{t('nav_advisory')}</span>
            </button>

            {/* 8. History & Timeline */}
            <button
              onClick={() => setActiveTab('history')}
              className={`w-full flex items-center space-x-3 px-3.5 py-2.5 rounded-xl text-sm font-semibold transition ${
                activeTab === 'history' ? 'bg-emerald-600 text-white' : 'text-slate-300 hover:bg-slate-800'
              }`}
            >
              <HistoryIcon className="w-5 h-5 shrink-0" />
              <span>{t('nav_history')}</span>
            </button>
          </div>

          {/* Bottom Settings & Diagnostics */}
          <div className="space-y-1.5 pt-2 border-t border-slate-800">
            <button
              onClick={() => setActiveTab('diagnostics')}
              className={`w-full flex items-center space-x-3 px-3.5 py-2 rounded-xl text-xs font-bold transition ${
                activeTab === 'diagnostics' ? 'bg-emerald-600 text-white' : 'text-slate-400 hover:bg-slate-800 hover:text-white'
              }`}
            >
              <CheckCircle2 className="w-4 h-4 shrink-0" />
              <span>{t('nav_diagnostics')}</span>
            </button>

            <button
              onClick={() => setActiveTab('settings')}
              className={`w-full flex items-center space-x-3 px-3.5 py-2 rounded-xl text-xs font-bold transition ${
                activeTab === 'settings' ? 'bg-emerald-600 text-white' : 'text-slate-400 hover:bg-slate-800 hover:text-white'
              }`}
            >
              <SettingsIcon className="w-4 h-4 shrink-0" />
              <span>{t('nav_settings')}</span>
            </button>
          </div>
        </nav>

        {/* ------------------------------------------------------------- */}
        {/* MAIN TOUCH CONTENT VIEWPORT                                   */}
        {/* ------------------------------------------------------------- */}
        <section className="flex-1 bg-slate-900/80 border border-slate-800 rounded-2xl p-5 overflow-y-auto flex flex-col justify-between shadow-2xl">
          <div>
            {/* Header Title & Host Telemetry */}
            <div className="flex items-center justify-between pb-3.5 border-b border-slate-800">
              <div>
                <h1 className="text-2xl font-black text-slate-100 flex items-center space-x-2 tracking-wide">
                  <span>{t(`nav_${activeTab}`)}</span>
                </h1>
                <p className="text-xs text-slate-400 mt-0.5">{t('tagline')}</p>
              </div>

              {/* Live Host Telemetry Pill */}
              {deviceStatus && (
                <div className="flex items-center space-x-3 text-xs font-mono bg-slate-800/90 px-3.5 py-1.5 rounded-xl border border-slate-700">
                  <span className="text-slate-400">CPU: <b className="text-slate-200">{deviceStatus.cpu_usage_percent}%</b></span>
                  <span className="text-slate-400">RAM: <b className="text-slate-200">{deviceStatus.ram_usage_percent}%</b></span>
                  {deviceStatus.cpu_temperature_celsius !== null && (
                    <span className="text-slate-400">TEMP: <b className="text-amber-400">{deviceStatus.cpu_temperature_celsius}°C</b></span>
                  )}
                </div>
              )}
            </div>

            {/* Viewport Dynamic Content */}
            <div className="mt-5">
              {/* ========================================================= */}
              {/* TAB 1: HOME (RUGGED FARMER DASHBOARD)                     */}
              {/* ========================================================= */}
              {activeTab === 'home' && (
                <div className="space-y-5">
                  {/* GIANT PRIMARY TOUCH ACTION: START FIELD CHECK */}
                  <div className="bg-gradient-to-r from-emerald-900/60 via-slate-900 to-slate-900 border-2 border-emerald-600/70 rounded-2xl p-6 shadow-2xl flex items-center justify-between">
                    <div className="space-y-1">
                      <div className="text-xs font-mono font-bold text-emerald-400 tracking-wider">GUIDED EDGE WORKFLOW</div>
                      <div className="text-2xl font-black text-slate-100">Ready for Field Diagnosis</div>
                      <p className="text-xs text-slate-400 max-w-lg">
                        Execute step-by-step leaf pathology scanning, 6-parameter soil telemetry, multi-modal risk scoring, and actionable advisory.
                      </p>
                    </div>

                    <button
                      onClick={() => {
                        setActiveTab('wizard');
                        setWizardStep(1);
                      }}
                      className="bg-emerald-600 hover:bg-emerald-500 text-white px-6 py-4 rounded-xl text-base font-black tracking-wide flex items-center space-x-3 shadow-xl shadow-emerald-950 transition active:scale-95"
                    >
                      <span>{t('btn_start_check')}</span>
                      <ArrowRight className="w-5 h-5" />
                    </button>
                  </div>

                  {/* Hardware Readiness Matrix (Truthful!) */}
                  <div>
                    <div className="text-xs font-bold text-slate-400 tracking-wider mb-2.5">LIVE HARDWARE DIAGNOSTIC MATRIX</div>
                    <div className="grid grid-cols-4 gap-3.5">
                      {/* Subsystem 1: Camera */}
                      <div className="bg-slate-800/80 border border-slate-700 rounded-xl p-4 space-y-1.5">
                        <div className="flex justify-between items-center text-xs text-slate-400">
                          <span>CAMERA SUBSYSTEM</span>
                          <Camera className="w-4 h-4 text-slate-400" />
                        </div>
                        <div className="text-lg font-bold text-slate-100">
                          {deviceStatus?.subsystems?.camera?.is_mock ? 'Mock (Demo)' : (deviceStatus?.subsystems?.camera?.status || 'Active')}
                        </div>
                        <div className="text-[11px] text-emerald-400 font-mono">
                          {deviceStatus?.camera_status_label === 'READY' || deviceStatus?.subsystems?.camera?.status === 'READY' ? '● Ready for scan' : '○ ' + (deviceStatus?.camera_status_label || 'Unavailable')}
                        </div>
                      </div>

                      {/* Subsystem 2: 6-Param Soil Module */}
                      <div className="bg-slate-800/80 border border-slate-700 rounded-xl p-4 space-y-1.5">
                        <div className="flex justify-between items-center text-xs text-slate-400">
                          <span>6-PARAM SOIL SENSOR</span>
                          <Droplets className="w-4 h-4 text-cyan-400" />
                        </div>
                        <div className="text-lg font-bold text-slate-100">
                          {deviceStatus?.demo_mode ? 'Simulated 6-in-1' : (deviceStatus?.soil_status_label || 'DISCONNECTED')}
                        </div>
                        <div className={`text-[11px] font-mono ${deviceStatus?.soil_status_label === 'CONNECTED' ? 'text-emerald-400' : (deviceStatus?.demo_mode ? 'text-amber-400' : 'text-rose-400')}`}>
                          {deviceStatus?.demo_mode ? '● Demo simulation' : (deviceStatus?.soil_status_label === 'CONNECTED' ? '● RS485 Link OK' : '○ Sensor Disconnected')}
                        </div>
                      </div>

                      {/* Subsystem 3: AI Accelerator */}
                      <div className="bg-slate-800/80 border border-slate-700 rounded-xl p-4 space-y-1.5">
                        <div className="flex justify-between items-center text-xs text-slate-400">
                          <span>AI ACCELERATOR</span>
                          <Cpu className="w-4 h-4 text-purple-400" />
                        </div>
                        <div className="text-lg font-bold text-slate-100">
                          {visionStatus?.accelerator || 'CPU FALLBACK'}
                        </div>
                        <div className="text-[11px] text-purple-300 font-mono">
                          {visionStatus?.ready ? '● Model Loaded' : '○ Missing weights'}
                        </div>
                      </div>

                      {/* Subsystem 4: SQLite Database */}
                      <div className="bg-slate-800/80 border border-slate-700 rounded-xl p-4 space-y-1.5">
                        <div className="flex justify-between items-center text-xs text-slate-400">
                          <span>LOCAL SQLITE DB</span>
                          <HistoryIcon className="w-4 h-4 text-emerald-400" />
                        </div>
                        <div className="text-lg font-bold text-slate-100">
                          Offline Storage
                        </div>
                        <div className="text-[11px] text-emerald-400 font-mono">
                          ● {fields.length} Fields registered
                        </div>
                      </div>
                    </div>
                  </div>

                  {/* Quick Navigation Cards */}
                  <div className="grid grid-cols-3 gap-4 pt-2">
                    <div 
                      onClick={() => setActiveTab('fields')}
                      className="bg-slate-800/50 hover:bg-slate-800 border border-slate-700 rounded-xl p-4 cursor-pointer transition flex items-center space-x-3.5"
                    >
                      <div className="w-10 h-10 rounded-xl bg-emerald-950 border border-emerald-800 flex items-center justify-center text-emerald-400">
                        <Layers className="w-5 h-5" />
                      </div>
                      <div>
                        <div className="font-bold text-sm text-slate-200">Manage Fields</div>
                        <div className="text-xs text-slate-400">Select or add agricultural plots</div>
                      </div>
                    </div>

                    <div 
                      onClick={() => setActiveTab('soil')}
                      className="bg-slate-800/50 hover:bg-slate-800 border border-slate-700 rounded-xl p-4 cursor-pointer transition flex items-center space-x-3.5"
                    >
                      <div className="w-10 h-10 rounded-xl bg-cyan-950 border border-cyan-800 flex items-center justify-center text-cyan-400">
                        <Droplets className="w-5 h-5" />
                      </div>
                      <div>
                        <div className="font-bold text-sm text-slate-200">6-Parameter Soil Probe</div>
                        <div className="text-xs text-slate-400">Inspect live N/P/K/pH/Moisture</div>
                      </div>
                    </div>

                    <div 
                      onClick={() => setActiveTab('history')}
                      className="bg-slate-800/50 hover:bg-slate-800 border border-slate-700 rounded-xl p-4 cursor-pointer transition flex items-center space-x-3.5"
                    >
                      <div className="w-10 h-10 rounded-xl bg-purple-950 border border-purple-800 flex items-center justify-center text-purple-400">
                        <HistoryIcon className="w-5 h-5" />
                      </div>
                      <div>
                        <div className="font-bold text-sm text-slate-200">Field History Timeline</div>
                        <div className="text-xs text-slate-400">View chronological field records</div>
                      </div>
                    </div>
                  </div>
                </div>
              )}

              {/* ========================================================= */}
              {/* TAB 2: GUIDED FIELD CHECK WIZARD (7-STAGE FLOW)           */}
              {/* ========================================================= */}
              {activeTab === 'wizard' && (
                <div className="space-y-4">
                  {/* Progress Indicator Bar */}
                  <div className="bg-slate-800/70 border border-slate-700 rounded-xl p-3.5 flex items-center justify-between">
                    <div className="flex items-center space-x-2">
                      {[1, 2, 3, 4, 5, 6, 7].map(step => (
                        <div 
                          key={step} 
                          className={`w-7 h-7 rounded-full flex items-center justify-center text-xs font-bold transition ${
                            wizardStep === step ? 'bg-cyan-500 text-slate-950 ring-2 ring-cyan-300' :
                            wizardStep > step ? 'bg-emerald-600 text-white' :
                            'bg-slate-800 text-slate-500 border border-slate-700'
                          }`}
                        >
                          {wizardStep > step ? <Check className="w-3.5 h-3.5" /> : step}
                        </div>
                      ))}
                    </div>

                    <div className="text-xs font-mono font-bold text-cyan-300">
                      STEP {wizardStep} OF 7: {t(`step_${wizardStep}_title`)}
                    </div>
                  </div>

                  {/* WIZARD STEP 1: SELECT FIELD */}
                  {wizardStep === 1 && (
                    <div className="bg-slate-800/60 border border-slate-700 rounded-2xl p-6 space-y-4">
                      <div className="space-y-1">
                        <h2 className="text-xl font-bold text-slate-100">{t('step_1_title')}</h2>
                        <p className="text-xs text-slate-400">{t('step_1_desc')}</p>
                      </div>

                      <div className="grid grid-cols-2 gap-3.5 max-h-72 overflow-y-auto pr-1">
                        {fields.map(field => (
                          <div 
                            key={field.id}
                            onClick={() => setSelectedFieldId(field.id)}
                            className={`p-4 rounded-xl border-2 cursor-pointer transition flex justify-between items-center ${
                              selectedFieldId === field.id ? 'bg-emerald-950/60 border-emerald-500 text-white shadow-lg' : 'bg-slate-800/40 border-slate-700 hover:bg-slate-800 text-slate-300'
                            }`}
                          >
                            <div>
                              <div className="font-bold text-base">{field.name}</div>
                              <div className="text-xs text-slate-400 mt-0.5">Soil: {field.soil_type || 'General'} &bull; Area: {field.area || 1.0} {field.area_unit}</div>
                            </div>
                            {selectedFieldId === field.id && (
                              <CheckCircle className="w-6 h-6 text-emerald-400 shrink-0" />
                            )}
                          </div>
                        ))}
                      </div>

                      <div className="flex justify-between items-center pt-3 border-t border-slate-700">
                        <button
                          onClick={() => setShowAddFieldModal(true)}
                          className="bg-slate-700 hover:bg-slate-600 text-slate-200 px-4 py-2 rounded-xl text-xs font-bold flex items-center space-x-1.5"
                        >
                          <PlusCircle className="w-4 h-4" />
                          <span>{t('btn_add_field')}</span>
                        </button>

                        <button
                          disabled={!selectedFieldId}
                          onClick={() => setWizardStep(2)}
                          className="bg-emerald-600 hover:bg-emerald-500 disabled:bg-slate-700 text-white px-6 py-2.5 rounded-xl text-sm font-bold flex items-center space-x-2"
                        >
                          <span>{t('btn_next')}</span>
                          <ArrowRight className="w-4 h-4" />
                        </button>
                      </div>
                    </div>
                  )}

                  {/* WIZARD STEP 2: CROP LEAF CAPTURE */}
                  {wizardStep === 2 && (
                    <div className="bg-slate-800/60 border border-slate-700 rounded-2xl p-6 space-y-4">
                      <div className="space-y-1">
                        <h2 className="text-xl font-bold text-slate-100">{t('step_2_title')}</h2>
                        <p className="text-xs text-slate-400">{t('step_2_desc')}</p>
                      </div>

                      <div className="grid grid-cols-2 gap-4">
                        {/* Viewfinder Preview */}
                        <div className="bg-slate-900 border-2 border-dashed border-slate-700 rounded-xl p-4 flex flex-col items-center justify-center min-h-[260px] text-center relative overflow-hidden">
                          {previewUrl ? (
                            <img src={previewUrl} alt="Leaf preview" className="max-h-56 object-contain rounded-lg shadow-md" />
                          ) : (
                            <div className="space-y-2 text-slate-400">
                              <Camera className="w-12 h-12 mx-auto text-slate-500" />
                              <div className="font-bold text-sm">Offline Hardware Viewfinder</div>
                              <p className="text-xs text-slate-500 max-w-xs">Take a photo using edge camera or upload a file.</p>
                            </div>
                          )}
                        </div>

                        {/* Capture Controls */}
                        <div className="flex flex-col justify-center space-y-3">
                          <button
                            onClick={async () => {
                              const res = await executeScan(true);
                              if (res) setWizardStep(3);
                            }}
                            disabled={isScanning}
                            className="w-full bg-emerald-600 hover:bg-emerald-500 disabled:bg-slate-700 text-white py-4 rounded-xl text-sm font-bold flex items-center justify-center space-x-2 shadow-lg"
                          >
                            {isScanning ? <RefreshCw className="w-4 h-4 animate-spin" /> : <Camera className="w-5 h-5" />}
                            <span>Capture from Hardware Camera</span>
                          </button>

                          <label className="w-full cursor-pointer bg-slate-800 hover:bg-slate-700 text-slate-200 py-3.5 rounded-xl text-xs font-bold flex items-center justify-center space-x-2 border border-slate-700">
                            <Upload className="w-4 h-4" />
                            <span>{t('btn_upload')}</span>
                            <input type="file" accept="image/*" className="hidden" onChange={handleFileSelect} />
                          </label>

                          {selectedFile && (
                            <button
                              onClick={async () => {
                                const res = await executeScan(false);
                                if (res) setWizardStep(3);
                              }}
                              disabled={isScanning}
                              className="w-full bg-cyan-600 hover:bg-cyan-500 text-white py-3 rounded-xl text-xs font-bold flex items-center justify-center space-x-1.5"
                            >
                              <span>Analyze Selected Upload</span>
                              <ArrowRight className="w-4 h-4" />
                            </button>
                          )}

                          {scanError && (
                            <div className="bg-rose-950/80 border border-rose-800 text-rose-300 p-2.5 rounded-lg text-xs flex items-center space-x-2">
                              <AlertTriangle className="w-4 h-4 flex-shrink-0" />
                              <span>{scanError}</span>
                            </div>
                          )}
                        </div>
                      </div>

                      <div className="flex justify-between items-center pt-3 border-t border-slate-700">
                        <button
                          onClick={() => setWizardStep(1)}
                          className="bg-slate-700 hover:bg-slate-600 text-slate-200 px-4 py-2 rounded-xl text-xs font-bold"
                        >
                          {t('btn_back')}
                        </button>
                      </div>
                    </div>
                  )}

                  {/* WIZARD STEP 3: IMAGE QUALITY CHECK */}
                  {wizardStep === 3 && scanResult && (
                    <div className="bg-slate-800/60 border border-slate-700 rounded-2xl p-6 space-y-4">
                      <div className="space-y-1">
                        <h2 className="text-xl font-bold text-slate-100">{t('step_3_title')}</h2>
                        <p className="text-xs text-slate-400">{t('step_3_desc')}</p>
                      </div>

                      <div className={`p-4 rounded-xl border-2 ${
                        scanResult.image_quality.passed ? 'bg-emerald-950/40 border-emerald-600/80 text-emerald-200' : 'bg-amber-950/40 border-amber-600/80 text-amber-200'
                      }`}>
                        <div className="flex justify-between items-center font-bold">
                          <span className="flex items-center space-x-2 text-base">
                            {scanResult.image_quality.passed ? <CheckCircle className="w-5 h-5 text-emerald-400" /> : <AlertTriangle className="w-5 h-5 text-amber-400" />}
                            <span>{scanResult.image_quality.passed ? 'Image Quality Passed' : 'Image Quality Warning'}</span>
                          </span>
                          <span className="font-mono text-sm font-bold">Sharpness: {scanResult.image_quality.blur_score}</span>
                        </div>
                        <p className="mt-2 text-xs font-medium">
                          {scanResult.image_quality.farmer_instruction || scanResult.image_quality.error_reason || 'Image meets diagnostic resolution and exposure requirements.'}
                        </p>
                      </div>

                      <div className="grid grid-cols-3 gap-3 text-xs font-mono bg-slate-900/80 p-3.5 rounded-xl border border-slate-800">
                        <div>Sharpness (Blur): <b className="text-slate-200">{scanResult.image_quality.blur_score}</b></div>
                        <div>Exposure (Luminance): <b className="text-slate-200">{scanResult.image_quality.brightness_score}</b></div>
                        <div>Resolution: <b className="text-slate-200">{scanResult.image_quality.resolution}</b></div>
                      </div>

                      <div className="flex justify-between items-center pt-3 border-t border-slate-700">
                        <button
                          onClick={() => setWizardStep(2)}
                          className="bg-slate-700 hover:bg-slate-600 text-slate-200 px-4 py-2 rounded-xl text-xs font-bold flex items-center space-x-1"
                        >
                          <RotateCcw className="w-4 h-4" />
                          <span>{t('btn_retake')}</span>
                        </button>

                        <button
                          onClick={() => setWizardStep(4)}
                          className="bg-emerald-600 hover:bg-emerald-500 text-white px-6 py-2.5 rounded-xl text-sm font-bold flex items-center space-x-2"
                        >
                          <span>{t('btn_next')}</span>
                          <ArrowRight className="w-4 h-4" />
                        </button>
                      </div>
                    </div>
                  )}

                  {/* WIZARD STEP 4: AI VISION ANALYSIS */}
                  {wizardStep === 4 && scanResult && (
                    <div className="bg-slate-800/60 border border-slate-700 rounded-2xl p-6 space-y-4">
                      <div className="space-y-1">
                        <h2 className="text-xl font-bold text-slate-100">{t('step_4_title')}</h2>
                        <p className="text-xs text-slate-400">{t('step_4_desc')}</p>
                      </div>

                      <div className="bg-slate-900 border border-slate-800 rounded-xl p-5 space-y-3">
                        <div className="flex justify-between items-center">
                          <span className="text-xs text-slate-400 font-bold">PATHOLOGY CLASSIFICATION</span>
                          <span className="text-xs font-mono text-purple-400 bg-purple-950 px-2 py-0.5 rounded border border-purple-800">
                            {scanResult.inference_device} ({scanResult.inference_time_ms}ms)
                          </span>
                        </div>

                        <div className="text-2xl font-black text-slate-100">{scanResult.prediction}</div>

                        {/* Confidence Gauge */}
                        <div>
                          <div className="flex justify-between text-xs font-mono text-slate-300 mb-1">
                            <span>Model Confidence</span>
                            <b>{(scanResult.confidence * 100).toFixed(1)}%</b>
                          </div>
                          <div className="w-full h-3 bg-slate-800 rounded-full overflow-hidden">
                            <div 
                              className={`h-full ${scanResult.confidence >= 0.70 ? 'bg-emerald-500' : 'bg-amber-500'}`} 
                              style={{ width: `${Math.min(scanResult.confidence * 100, 100)}%` }}
                            ></div>
                          </div>
                        </div>

                        {scanResult.status === 'low_confidence' && (
                          <div className="bg-amber-950/60 border border-amber-800 text-amber-300 p-2.5 rounded-lg text-xs">
                            AI result is uncertain (&lt; 70% threshold). Proceeding with caution.
                          </div>
                        )}
                      </div>

                      <div className="flex justify-between items-center pt-3 border-t border-slate-700">
                        <button
                          onClick={() => setWizardStep(3)}
                          className="bg-slate-700 hover:bg-slate-600 text-slate-200 px-4 py-2 rounded-xl text-xs font-bold"
                        >
                          {t('btn_back')}
                        </button>

                        <button
                          onClick={async () => {
                            if (selectedFieldId) await triggerLiveSoil(selectedFieldId);
                            setWizardStep(5);
                          }}
                          className="bg-emerald-600 hover:bg-emerald-500 text-white px-6 py-2.5 rounded-xl text-sm font-bold flex items-center space-x-2"
                        >
                          <span>{t('btn_next')}</span>
                          <ArrowRight className="w-4 h-4" />
                        </button>
                      </div>
                    </div>
                  )}

                  {/* WIZARD STEP 5: 6-PARAM SOIL TELEMETRY */}
                  {wizardStep === 5 && (
                    <div className="bg-slate-800/60 border border-slate-700 rounded-2xl p-6 space-y-4">
                      <div className="flex justify-between items-center">
                        <div>
                          <h2 className="text-xl font-bold text-slate-100">{t('step_5_title')}</h2>
                          <p className="text-xs text-slate-400">{t('step_5_desc')}</p>
                        </div>
                        <button
                          onClick={() => selectedFieldId && triggerLiveSoil(selectedFieldId)}
                          disabled={isReadingSoil}
                          className="bg-cyan-600 hover:bg-cyan-500 text-white px-3 py-1.5 rounded-lg text-xs font-bold flex items-center space-x-1"
                        >
                          <RefreshCw className={`w-3.5 h-3.5 ${isReadingSoil ? 'animate-spin' : ''}`} />
                          <span>Re-read Sensor</span>
                        </button>
                      </div>

                      <div className="grid grid-cols-3 gap-3">
                        <div className="bg-slate-900/90 border border-slate-800 rounded-xl p-3.5">
                          <div className="text-xs text-slate-400 font-semibold">{t('soil_n')}</div>
                          <div className="text-xl font-extrabold text-cyan-400 mt-1 font-mono">
                            {liveSoilReading?.nitrogen !== null && liveSoilReading?.nitrogen !== undefined ? `${liveSoilReading.nitrogen} mg/kg` : '--'}
                          </div>
                        </div>

                        <div className="bg-slate-900/90 border border-slate-800 rounded-xl p-3.5">
                          <div className="text-xs text-slate-400 font-semibold">{t('soil_p')}</div>
                          <div className="text-xl font-extrabold text-cyan-400 mt-1 font-mono">
                            {liveSoilReading?.phosphorus !== null && liveSoilReading?.phosphorus !== undefined ? `${liveSoilReading.phosphorus} mg/kg` : '--'}
                          </div>
                        </div>

                        <div className="bg-slate-900/90 border border-slate-800 rounded-xl p-3.5">
                          <div className="text-xs text-slate-400 font-semibold">{t('soil_k')}</div>
                          <div className="text-xl font-extrabold text-cyan-400 mt-1 font-mono">
                            {liveSoilReading?.potassium !== null && liveSoilReading?.potassium !== undefined ? `${liveSoilReading.potassium} mg/kg` : '--'}
                          </div>
                        </div>

                        <div className="bg-slate-900/90 border border-slate-800 rounded-xl p-3.5">
                          <div className="text-xs text-slate-400 font-semibold">{t('soil_ph')}</div>
                          <div className="text-xl font-extrabold text-cyan-400 mt-1 font-mono">
                            {liveSoilReading?.ph !== null && liveSoilReading?.ph !== undefined ? `${liveSoilReading.ph} pH` : '--'}
                          </div>
                        </div>

                        <div className="bg-slate-900/90 border border-slate-800 rounded-xl p-3.5">
                          <div className="text-xs text-slate-400 font-semibold">{t('soil_moisture')}</div>
                          <div className="text-xl font-extrabold text-cyan-400 mt-1 font-mono">
                            {liveSoilReading?.moisture !== null && liveSoilReading?.moisture !== undefined ? `${liveSoilReading.moisture}%` : '--'}
                          </div>
                        </div>

                        <div className="bg-slate-900/90 border border-slate-800 rounded-xl p-3.5">
                          <div className="text-xs text-slate-400 font-semibold">{t('soil_temp')}</div>
                          <div className="text-xl font-extrabold text-cyan-400 mt-1 font-mono">
                            {liveSoilReading?.temperature !== null && liveSoilReading?.temperature !== undefined ? `${liveSoilReading.temperature}°C` : '--'}
                          </div>
                        </div>
                      </div>

                      {liveSoilReading?.is_mock && (
                        <div className="text-[11px] font-mono text-amber-400 bg-amber-950/40 p-2 rounded border border-amber-800/40">
                          Note: Simulated soil telemetry active in DEMO_MODE.
                        </div>
                      )}

                      <div className="flex justify-between items-center pt-3 border-t border-slate-700">
                        <button
                          onClick={() => setWizardStep(4)}
                          className="bg-slate-700 hover:bg-slate-600 text-slate-200 px-4 py-2 rounded-xl text-xs font-bold"
                        >
                          {t('btn_back')}
                        </button>

                        <button
                          onClick={async () => {
                            await executeFusion();
                            setWizardStep(6);
                          }}
                          disabled={isFusing}
                          className="bg-emerald-600 hover:bg-emerald-500 text-white px-6 py-2.5 rounded-xl text-sm font-bold flex items-center space-x-2"
                        >
                          {isFusing ? <RefreshCw className="w-4 h-4 animate-spin" /> : null}
                          <span>Synthesize Multi-Modal Fusion</span>
                          <ArrowRight className="w-4 h-4" />
                        </button>
                      </div>
                    </div>
                  )}

                  {/* WIZARD STEP 6: CROP + SOIL FUSION & MULTIMODAL RISK */}
                  {wizardStep === 6 && fusionResult && (
                    <div className="bg-slate-800/60 border border-slate-700 rounded-2xl p-6 space-y-4">
                      <div className="space-y-1">
                        <h2 className="text-xl font-bold text-slate-100">{t('step_6_title')}</h2>
                        <p className="text-xs text-slate-400">{t('step_6_desc')}</p>
                      </div>

                      {/* Multimodal Risk Card */}
                      <div className="bg-slate-900 border border-slate-800 rounded-xl p-5 space-y-3">
                        <div className="flex justify-between items-center">
                          <span className="text-xs text-slate-400 font-bold">OVERALL FIELD RISK LEVEL</span>
                          <span className={`px-2.5 py-1 rounded text-xs font-extrabold ${
                            fusionResult.risk.risk_level === 'CRITICAL' ? 'bg-rose-950 text-rose-300 border border-rose-800' :
                            fusionResult.risk.risk_level === 'HIGH' ? 'bg-rose-900 text-rose-200 border border-rose-700' :
                            fusionResult.risk.risk_level === 'MODERATE' ? 'bg-amber-950 text-amber-300 border border-amber-800' :
                            fusionResult.risk.risk_level === 'LOW' ? 'bg-emerald-950 text-emerald-300 border border-emerald-800' :
                            'bg-slate-800 text-slate-400 border border-slate-700'
                          }`}>
                            {fusionResult.risk.risk_level}
                          </span>
                        </div>

                        <p className="text-sm text-slate-200 font-medium">{fusionResult.risk.explanation}</p>

                        <div className="grid grid-cols-3 gap-2 pt-2 border-t border-slate-800 text-xs font-mono">
                          <div>Disease: <b className="text-rose-400">{fusionResult.risk.disease_risk}</b></div>
                          <div>Soil Stress: <b className="text-amber-400">{fusionResult.risk.soil_stress}</b></div>
                          <div>Completeness: <b className="text-cyan-400">{(fusionResult.risk.data_completeness * 100).toFixed(0)}%</b></div>
                        </div>
                      </div>

                      <div className="flex justify-between items-center pt-3 border-t border-slate-700">
                        <button
                          onClick={() => setWizardStep(5)}
                          className="bg-slate-700 hover:bg-slate-600 text-slate-200 px-4 py-2 rounded-xl text-xs font-bold"
                        >
                          {t('btn_back')}
                        </button>

                        <button
                          onClick={() => setWizardStep(7)}
                          className="bg-emerald-600 hover:bg-emerald-500 text-white px-6 py-2.5 rounded-xl text-sm font-bold flex items-center space-x-2"
                        >
                          <span>View Farmer Advisories</span>
                          <ArrowRight className="w-4 h-4" />
                        </button>
                      </div>
                    </div>
                  )}

                  {/* WIZARD STEP 7: ACTIONABLE FARMER ADVISORY & PERSISTENCE */}
                  {wizardStep === 7 && fusionResult && (
                    <div className="bg-slate-800/60 border border-slate-700 rounded-2xl p-6 space-y-4">
                      <div className="space-y-1">
                        <h2 className="text-xl font-bold text-slate-100">{t('step_7_title')}</h2>
                        <p className="text-xs text-slate-400">{t('step_7_desc')}</p>
                      </div>

                      <div className="space-y-3 max-h-72 overflow-y-auto pr-1">
                        {fusionResult.advisories.map((adv, idx) => (
                          <div key={idx} className="bg-slate-900 border border-slate-800 rounded-xl p-4 space-y-2">
                            <div className="flex justify-between items-center">
                              <span className={`px-2 py-0.5 rounded text-[10px] font-bold ${
                                adv.priority === 'URGENT' ? 'bg-rose-950 text-rose-300 border border-rose-800' :
                                adv.priority === 'HIGH' ? 'bg-amber-950 text-amber-300 border border-amber-800' :
                                'bg-emerald-950 text-emerald-300 border border-emerald-800'
                              }`}>
                                {adv.priority} PRIORITY
                              </span>
                              <span className="text-xs font-bold text-slate-200">{adv.title}</span>
                            </div>
                            <div className="text-xs text-slate-300"><b>Observation:</b> {adv.message}</div>
                            <div className="bg-slate-950 p-2.5 rounded-lg border border-slate-800 text-xs text-emerald-300">
                              <b>Action:</b> {adv.recommended_action}
                            </div>
                          </div>
                        ))}
                      </div>

                      <div className="flex justify-between items-center pt-3 border-t border-slate-700">
                        <button
                          onClick={() => setWizardStep(1)}
                          className="bg-slate-700 hover:bg-slate-600 text-slate-200 px-4 py-2 rounded-xl text-xs font-bold flex items-center space-x-1"
                        >
                          <RotateCcw className="w-4 h-4" />
                          <span>Start New Scan</span>
                        </button>

                        <button
                          onClick={() => {
                            setActiveTab('history');
                            if (selectedFieldId) loadHistory(selectedFieldId);
                          }}
                          className="bg-emerald-600 hover:bg-emerald-500 text-white px-6 py-2.5 rounded-xl text-sm font-bold flex items-center space-x-2"
                        >
                          <Check className="w-4 h-4" />
                          <span>{t('btn_finish')}</span>
                        </button>
                      </div>
                    </div>
                  )}
                </div>
              )}

              {/* ========================================================= */}
              {/* TAB 3: FIELDS / PLOTS MANAGEMENT                          */}
              {/* ========================================================= */}
              {activeTab === 'fields' && (
                <div className="space-y-4">
                  <div className="flex justify-between items-center bg-slate-800/60 border border-slate-700 rounded-xl p-4">
                    <div>
                      <div className="font-bold text-sm text-slate-200">Registered Agricultural Fields</div>
                      <div className="text-xs text-slate-400">Total {fields.length} active plots in local SQLite</div>
                    </div>

                    <button
                      onClick={() => setShowAddFieldModal(true)}
                      className="bg-emerald-600 hover:bg-emerald-500 text-white px-4 py-2 rounded-xl text-xs font-bold flex items-center space-x-1.5"
                    >
                      <PlusCircle className="w-4 h-4" />
                      <span>{t('btn_add_field')}</span>
                    </button>
                  </div>

                  <div className="grid grid-cols-2 gap-4">
                    {fields.map(field => (
                      <div 
                        key={field.id}
                        className={`bg-slate-800/80 border rounded-xl p-4 space-y-3 transition ${
                          selectedFieldId === field.id ? 'border-emerald-500 ring-1 ring-emerald-500' : 'border-slate-700'
                        }`}
                      >
                        <div className="flex justify-between items-start">
                          <div>
                            <div className="text-lg font-extrabold text-slate-100">{field.name}</div>
                            <div className="text-xs text-slate-400 mt-0.5">Soil Type: <b className="text-slate-300">{field.soil_type || 'General'}</b></div>
                          </div>
                          <span className="text-xs font-mono text-cyan-400 bg-slate-900 px-2 py-0.5 rounded border border-slate-800">
                            {field.area || 1.0} {field.area_unit}
                          </span>
                        </div>

                        <div className="pt-2 border-t border-slate-700/60 flex justify-between items-center">
                          <button
                            onClick={() => {
                              setSelectedFieldId(field.id);
                              setActiveTab('wizard');
                              setWizardStep(1);
                            }}
                            className="bg-emerald-600 hover:bg-emerald-500 text-white px-3.5 py-1.5 rounded-lg text-xs font-bold flex items-center space-x-1"
                          >
                            <span>Start Field Check</span>
                            <ArrowRight className="w-3.5 h-3.5" />
                          </button>

                          <button
                            onClick={() => {
                              setSelectedFieldId(field.id);
                              setActiveTab('history');
                            }}
                            className="text-xs text-slate-400 hover:text-white"
                          >
                            View Timeline
                          </button>
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              )}

              {/* ========================================================= */}
              {/* TAB 4: STANDALONE CROP SCANNER                            */}
              {/* ========================================================= */}
              {activeTab === 'scanner' && (
                <div className="space-y-4">
                  <div className="bg-slate-800/60 border border-slate-700 rounded-xl p-4 flex items-center justify-between">
                    <div className="flex items-center space-x-3">
                      <label className="text-xs font-semibold text-slate-300">Target Field:</label>
                      <select 
                        value={selectedFieldId || ''} 
                        onChange={(e) => setSelectedFieldId(Number(e.target.value))}
                        className="bg-slate-900 border border-slate-700 rounded-lg px-3 py-1.5 text-xs text-slate-200 font-medium"
                      >
                        {fields.map(f => (
                          <option key={f.id} value={f.id}>{f.name} ({f.soil_type || 'General'})</option>
                        ))}
                      </select>
                    </div>

                    <div className="flex items-center space-x-2">
                      <label className="cursor-pointer bg-slate-700 hover:bg-slate-600 text-slate-200 px-3.5 py-1.5 rounded-lg text-xs font-semibold flex items-center space-x-1.5">
                        <Upload className="w-3.5 h-3.5" />
                        <span>Upload</span>
                        <input type="file" accept="image/*" className="hidden" onChange={handleFileSelect} />
                      </label>

                      <button
                        onClick={() => executeScan(true)}
                        disabled={isScanning}
                        className="bg-emerald-600 hover:bg-emerald-500 text-white px-4 py-1.5 rounded-lg text-xs font-bold flex items-center space-x-1.5"
                      >
                        {isScanning ? <RefreshCw className="w-3.5 h-3.5 animate-spin" /> : <Camera className="w-3.5 h-3.5" />}
                        <span>Capture</span>
                      </button>
                    </div>
                  </div>

                  <div className="grid grid-cols-2 gap-4">
                    <div className="bg-slate-900 border border-slate-800 rounded-xl p-4 flex flex-col items-center justify-center min-h-[280px]">
                      {previewUrl ? (
                        <img src={previewUrl} alt="Scan preview" className="max-h-60 object-contain rounded-lg" />
                      ) : (
                        <div className="text-center text-slate-500 space-y-2">
                          <Camera className="w-10 h-10 mx-auto" />
                          <div className="text-xs">Live Viewfinder Preview</div>
                        </div>
                      )}
                    </div>

                    {scanResult ? (
                      <div className="bg-slate-800/80 border border-slate-700 rounded-xl p-4 space-y-3">
                        <div className="flex justify-between items-center">
                          <div className="text-xs font-bold text-slate-400">DIAGNOSIS RESULT</div>
                          <div className="flex items-center space-x-1.5">
                            {scanResult.confidence_tier && (
                              <span className={`text-[10px] font-extrabold px-2 py-0.5 rounded ${
                                scanResult.confidence_tier === 'HIGH' ? 'bg-emerald-950 text-emerald-300 border border-emerald-800' :
                                scanResult.confidence_tier === 'MEDIUM' ? 'bg-amber-950 text-amber-300 border border-amber-800' :
                                'bg-rose-950 text-rose-300 border border-rose-800'
                              }`}>
                                {scanResult.confidence_tier} CONFIDENCE
                              </span>
                            )}
                            <span className="text-[10px] font-mono text-purple-300 bg-purple-950 px-2 py-0.5 rounded border border-purple-800">
                              {scanResult.inference_device} ({scanResult.inference_time_ms}ms)
                            </span>
                          </div>
                        </div>

                        <div className="text-2xl font-black text-slate-100">{scanResult.prediction}</div>

                        <div className="grid grid-cols-2 gap-2 text-xs font-mono bg-slate-900/80 p-2.5 rounded-lg border border-slate-800 text-slate-300">
                          <div>Model: <b className="text-slate-200">{scanResult.model_name} v{scanResult.model_version}</b></div>
                          <div>Hash: <b className="text-slate-200">{scanResult.model_hash ? scanResult.model_hash.substring(0, 8) : 'N/A'}</b></div>
                          <div>Validation: <b className="text-amber-400">{scanResult.is_validated ? 'VALIDATED' : 'NOT YET VALIDATED'}</b></div>
                          <div>Confidence: <b className="text-emerald-400">{(scanResult.confidence * 100).toFixed(1)}%</b></div>
                        </div>

                        <div className="bg-slate-900 p-2.5 rounded-lg border border-slate-800 text-xs text-slate-300 space-y-1">
                          <div className="font-semibold text-slate-200">{scanResult.message}</div>
                          {scanResult.farmer_guidance && (
                            <div className="text-[11px] text-emerald-400">{scanResult.farmer_guidance}</div>
                          )}
                        </div>
                      </div>
                    ) : (
                      <div className="bg-slate-800/40 border border-slate-700 rounded-xl p-6 text-center text-slate-500 flex items-center justify-center">
                        <div>Ready to capture or upload leaf photo.</div>
                      </div>
                    )}
                  </div>
                </div>
              )}

              {/* ========================================================= */}
              {/* TAB 5: 6-PARAM SOIL SENSOR (DEDICATED MODULE)             */}
              {/* ========================================================= */}
              {activeTab === 'soil' && (
                <div className="space-y-4">
                  <div className="flex justify-between items-center bg-slate-800/60 border border-slate-700 rounded-xl p-4">
                    <div>
                      <div className="font-bold text-sm text-slate-200">6-Parameter Soil Sensor Module</div>
                      <div className="text-xs text-slate-400">RS485 Modbus-RTU Telemetry (Zero Hardware Hallucination)</div>
                    </div>

                    <button
                      onClick={() => selectedFieldId && triggerLiveSoil(selectedFieldId)}
                      disabled={isReadingSoil}
                      className="bg-cyan-600 hover:bg-cyan-500 disabled:bg-slate-700 text-white px-4 py-2 rounded-xl text-xs font-bold flex items-center space-x-1.5"
                    >
                      <RefreshCw className={`w-3.5 h-3.5 ${isReadingSoil ? 'animate-spin' : ''}`} />
                      <span>Take Live Soil Reading</span>
                    </button>
                  </div>

                  <div className="grid grid-cols-3 gap-4">
                    <div className="bg-slate-800/80 border border-slate-700 rounded-xl p-4">
                      <div className="text-xs text-slate-400 font-semibold">{t('soil_n')}</div>
                      <div className="text-3xl font-extrabold text-cyan-400 mt-2 font-mono">
                        {liveSoilReading?.nitrogen !== null && liveSoilReading?.nitrogen !== undefined ? `${liveSoilReading.nitrogen} mg/kg` : (deviceStatus?.demo_mode ? '42 mg/kg' : '--')}
                      </div>
                      <div className="text-[11px] text-slate-400 mt-1">{deviceStatus?.demo_mode ? 'Simulated' : (liveSoilReading?.nitrogen !== null ? 'Live Probe' : 'Unavailable')}</div>
                    </div>

                    <div className="bg-slate-800/80 border border-slate-700 rounded-xl p-4">
                      <div className="text-xs text-slate-400 font-semibold">{t('soil_p')}</div>
                      <div className="text-3xl font-extrabold text-cyan-400 mt-2 font-mono">
                        {liveSoilReading?.phosphorus !== null && liveSoilReading?.phosphorus !== undefined ? `${liveSoilReading.phosphorus} mg/kg` : (deviceStatus?.demo_mode ? '18 mg/kg' : '--')}
                      </div>
                      <div className="text-[11px] text-slate-400 mt-1">{deviceStatus?.demo_mode ? 'Simulated' : (liveSoilReading?.phosphorus !== null ? 'Live Probe' : 'Unavailable')}</div>
                    </div>

                    <div className="bg-slate-800/80 border border-slate-700 rounded-xl p-4">
                      <div className="text-xs text-slate-400 font-semibold">{t('soil_k')}</div>
                      <div className="text-3xl font-extrabold text-cyan-400 mt-2 font-mono">
                        {liveSoilReading?.potassium !== null && liveSoilReading?.potassium !== undefined ? `${liveSoilReading.potassium} mg/kg` : (deviceStatus?.demo_mode ? '156 mg/kg' : '--')}
                      </div>
                      <div className="text-[11px] text-slate-400 mt-1">{deviceStatus?.demo_mode ? 'Simulated' : (liveSoilReading?.potassium !== null ? 'Live Probe' : 'Unavailable')}</div>
                    </div>

                    <div className="bg-slate-800/80 border border-slate-700 rounded-xl p-4">
                      <div className="text-xs text-slate-400 font-semibold">{t('soil_ph')}</div>
                      <div className="text-3xl font-extrabold text-cyan-400 mt-2 font-mono">
                        {liveSoilReading?.ph !== null && liveSoilReading?.ph !== undefined ? `${liveSoilReading.ph} pH` : (deviceStatus?.demo_mode ? '6.8 pH' : '--')}
                      </div>
                      <div className="text-[11px] text-slate-400 mt-1">{deviceStatus?.demo_mode ? 'Simulated' : (liveSoilReading?.ph !== null ? 'Live Probe' : 'Unavailable')}</div>
                    </div>

                    <div className="bg-slate-800/80 border border-slate-700 rounded-xl p-4">
                      <div className="text-xs text-slate-400 font-semibold">{t('soil_moisture')}</div>
                      <div className="text-3xl font-extrabold text-cyan-400 mt-2 font-mono">
                        {liveSoilReading?.moisture !== null && liveSoilReading?.moisture !== undefined ? `${liveSoilReading.moisture}%` : (deviceStatus?.demo_mode ? '24.2%' : '--')}
                      </div>
                      <div className="text-[11px] text-slate-400 mt-1">{deviceStatus?.demo_mode ? 'Simulated' : (liveSoilReading?.moisture !== null ? 'Live Probe' : 'Unavailable')}</div>
                    </div>

                    <div className="bg-slate-800/80 border border-slate-700 rounded-xl p-4">
                      <div className="text-xs text-slate-400 font-semibold">{t('soil_temp')}</div>
                      <div className="text-3xl font-extrabold text-cyan-400 mt-2 font-mono">
                        {liveSoilReading?.temperature !== null && liveSoilReading?.temperature !== undefined ? `${liveSoilReading.temperature}°C` : (deviceStatus?.demo_mode ? '26.4°C' : '--')}
                      </div>
                      <div className="text-[11px] text-slate-400 mt-1">{deviceStatus?.demo_mode ? 'Simulated' : (liveSoilReading?.temperature !== null ? 'Live Probe' : 'Unavailable')}</div>
                    </div>
                  </div>
                </div>
              )}

              {/* ========================================================= */}
              {/* TAB 6: MULTI-MODAL RISK INTELLIGENCE                      */}
              {/* ========================================================= */}
              {activeTab === 'risk' && (
                <div className="space-y-4">
                  <div className="bg-slate-800/60 border border-slate-700 rounded-xl p-4 flex items-center justify-between">
                    <div className="flex items-center space-x-3">
                      <label className="text-xs font-semibold text-slate-300">Target Field:</label>
                      <select 
                        value={selectedFieldId || ''} 
                        onChange={(e) => setSelectedFieldId(Number(e.target.value))}
                        className="bg-slate-900 border border-slate-700 rounded-lg px-3 py-1.5 text-xs text-slate-200 font-medium"
                      >
                        {fields.map(f => (
                          <option key={f.id} value={f.id}>{f.name} ({f.soil_type || 'General'})</option>
                        ))}
                      </select>
                    </div>

                    <button
                      onClick={executeFusion}
                      disabled={isFusing}
                      className="bg-emerald-600 hover:bg-emerald-500 text-white px-4 py-2 rounded-xl text-xs font-bold flex items-center space-x-1.5"
                    >
                      {isFusing ? <RefreshCw className="w-3.5 h-3.5 animate-spin" /> : <Zap className="w-3.5 h-3.5" />}
                      <span>Run Multi-Modal Fusion</span>
                    </button>
                  </div>

                  {fusionResult ? (
                    <div className="grid grid-cols-3 gap-4">
                      <div className="bg-slate-800/80 border border-slate-700 rounded-xl p-5 space-y-3">
                        <div className="text-xs font-bold text-slate-400">FIELD RISK LEVEL</div>
                        <div className="text-3xl font-black text-slate-100">{fusionResult.risk.risk_level}</div>
                        <p className="text-xs text-slate-300">{fusionResult.risk.explanation}</p>
                        <div className="pt-2 border-t border-slate-700 text-xs font-mono">
                          <div>Completeness: <b>{(fusionResult.risk.data_completeness * 100).toFixed(0)}%</b></div>
                        </div>
                      </div>

                      <div className="col-span-2 bg-slate-800/60 border border-slate-700 rounded-xl p-4 space-y-2 max-h-72 overflow-y-auto pr-1">
                        <div className="text-xs font-bold text-slate-300">EXPLAINABLE RISK EVIDENCE</div>
                        {fusionResult.evidence.map((ev, idx) => (
                          <div key={idx} className="bg-slate-900 p-2.5 rounded-lg text-xs space-y-0.5 border border-slate-800">
                            <div className="flex justify-between items-center">
                              <span className="font-bold text-slate-200">{ev.title}</span>
                              <span className="text-[10px] font-mono text-slate-400">{ev.source}</span>
                            </div>
                            <p className="text-slate-400 text-[11px]">{ev.description}</p>
                          </div>
                        ))}
                      </div>
                    </div>
                  ) : (
                    <div className="bg-slate-800/40 border border-slate-700 rounded-xl p-8 text-center text-slate-500">
                      Click <b>Run Multi-Modal Fusion</b> to assess multi-modal crop and soil risk.
                    </div>
                  )}
                </div>
              )}

              {/* ========================================================= */}
              {/* TAB 7: ACTIONABLE FARMER ADVISORIES                       */}
              {/* ========================================================= */}
              {activeTab === 'advisory' && (
                <div className="space-y-4">
                  <div className="flex justify-between items-center bg-slate-800/60 border border-slate-700 rounded-xl p-4">
                    <div>
                      <div className="font-bold text-sm text-slate-200">Personalized Agronomic Advisories</div>
                      <div className="text-xs text-slate-400">Actionable, non-toxic recommendations for {selectedField?.name || 'Selected Field'}</div>
                    </div>

                    <button
                      onClick={() => selectedFieldId && loadAdvisories(selectedFieldId)}
                      disabled={isLoadingAdvisories}
                      className="bg-slate-700 hover:bg-slate-600 text-slate-200 px-3.5 py-1.5 rounded-xl text-xs font-bold flex items-center space-x-1"
                    >
                      <RefreshCw className={`w-3.5 h-3.5 ${isLoadingAdvisories ? 'animate-spin' : ''}`} />
                      <span>{t('btn_refresh')}</span>
                    </button>
                  </div>

                  {advisoryList.length > 0 ? (
                    <div className="space-y-3 max-h-96 overflow-y-auto pr-1">
                      {advisoryList.map((adv, idx) => (
                        <div key={idx} className="bg-slate-800/80 border border-slate-700 rounded-xl p-4 space-y-2">
                          <div className="flex justify-between items-center">
                            <span className={`px-2.5 py-0.5 rounded text-[10px] font-extrabold ${
                              adv.priority === 'URGENT' ? 'bg-rose-950 text-rose-300 border border-rose-800' :
                              adv.priority === 'HIGH' ? 'bg-amber-950 text-amber-300 border border-amber-800' :
                              'bg-emerald-950 text-emerald-300 border border-emerald-800'
                            }`}>
                              {adv.priority} PRIORITY
                            </span>
                            <span className="text-xs font-bold text-slate-200">{adv.title}</span>
                          </div>
                          <div className="text-xs text-slate-300"><b>Observation:</b> {adv.message}</div>
                          <div className="bg-slate-900 p-2.5 rounded-lg border border-slate-800 text-xs text-emerald-300">
                            <b>Recommended Action:</b> {adv.recommended_action}
                          </div>
                        </div>
                      ))}
                    </div>
                  ) : (
                    <div className="bg-slate-800/40 border border-slate-700 rounded-xl p-8 text-center text-slate-500">
                      No active advisories found. Run Field Check to generate guidance.
                    </div>
                  )}
                </div>
              )}

              {/* ========================================================= */}
              {/* TAB 8: CHRONOLOGICAL FIELD HISTORY & TIMELINE             */}
              {/* ========================================================= */}
              {activeTab === 'history' && (
                <div className="space-y-4">
                  <div className="flex justify-between items-center bg-slate-800/60 border border-slate-700 rounded-xl p-3.5">
                    <div className="flex items-center space-x-3">
                      <label className="text-xs font-semibold text-slate-300">Target Field:</label>
                      <select 
                        value={selectedFieldId || ''} 
                        onChange={(e) => setSelectedFieldId(Number(e.target.value))}
                        className="bg-slate-900 border border-slate-700 rounded-lg px-3 py-1.5 text-xs text-slate-200 font-medium"
                      >
                        {fields.map(f => (
                          <option key={f.id} value={f.id}>{f.name}</option>
                        ))}
                      </select>
                    </div>

                    <div className="flex items-center space-x-2">
                      <div className="flex bg-slate-900 border border-slate-700 rounded-lg p-0.5 text-[11px] font-bold">
                        {(['ALL', 'SCAN', 'SOIL', 'RISK', 'ADVISORY'] as const).map(flt => (
                          <button
                            key={flt}
                            onClick={() => setHistoryFilter(flt)}
                            className={`px-2.5 py-1 rounded-md transition ${
                              historyFilter === flt ? 'bg-emerald-600 text-white shadow' : 'text-slate-400 hover:text-slate-200'
                            }`}
                          >
                            {flt}
                          </button>
                        ))}
                      </div>

                      <button
                        onClick={() => selectedFieldId && loadHistory(selectedFieldId)}
                        className="bg-slate-700 hover:bg-slate-600 text-slate-200 px-3.5 py-1.5 rounded-lg text-xs font-bold flex items-center space-x-1"
                      >
                        <RefreshCw className="w-3.5 h-3.5" />
                        <span>{t('btn_refresh')}</span>
                      </button>
                    </div>
                  </div>

                  {isLoadingHistory ? (
                    <div className="p-8 text-center text-slate-400 text-xs">Loading offline field timeline...</div>
                  ) : historyData && historyData.timeline.length > 0 ? (
                    <div className="space-y-2 max-h-[380px] overflow-y-auto pr-1">
                      {historyData.timeline
                        .filter(item => {
                          if (historyFilter === 'ALL') return true;
                          if (historyFilter === 'SCAN') return item.type === 'SCAN';
                          if (historyFilter === 'SOIL') return item.type === 'SOIL_READING';
                          if (historyFilter === 'RISK') return item.type === 'RISK_ASSESSMENT';
                          if (historyFilter === 'ADVISORY') return item.type === 'ADVISORY';
                          return true;
                        })
                        .map((item, idx) => (
                        <div key={idx} className="bg-slate-800/70 border border-slate-700 rounded-lg p-3 flex items-center justify-between text-xs">
                          <div className="flex items-center space-x-3">
                            {item.type === 'SCAN' ? (
                              <div className="w-8 h-8 rounded-full bg-emerald-950 border border-emerald-800 flex items-center justify-center text-emerald-400">
                                <Camera className="w-4 h-4" />
                              </div>
                            ) : item.type === 'SOIL_READING' ? (
                              <div className="w-8 h-8 rounded-full bg-cyan-950 border border-cyan-800 flex items-center justify-center text-cyan-400">
                                <Droplets className="w-4 h-4" />
                              </div>
                            ) : item.type === 'RISK_ASSESSMENT' ? (
                              <div className="w-8 h-8 rounded-full bg-purple-950 border border-purple-800 flex items-center justify-center text-purple-400">
                                <ShieldAlert className="w-4 h-4" />
                              </div>
                            ) : (
                              <div className="w-8 h-8 rounded-full bg-amber-950 border border-amber-800 flex items-center justify-center text-amber-400">
                                <FileText className="w-4 h-4" />
                              </div>
                            )}
                            <div>
                              <div className="font-bold text-slate-200">
                                {item.type === 'SCAN' ? `Crop Scan: ${item.prediction}` : 
                                 item.type === 'SOIL_READING' ? `Soil Reading (${item.sensor_status})` :
                                 item.type === 'RISK_ASSESSMENT' ? `Risk Assessment: ${item.disease_risk || 'CALCULATED'}` :
                                 `Advisory: ${item.title}`}
                              </div>
                              <div className="text-[11px] text-slate-400 flex items-center space-x-2 mt-0.5">
                                <Clock className="w-3 h-3" />
                                <span>{new Date(item.timestamp).toLocaleString()}</span>
                              </div>
                            </div>
                          </div>

                          <div className="text-right font-mono text-xs">
                            {item.type === 'SCAN' ? (
                              <span className="text-emerald-400 font-bold">{(item.confidence * 100).toFixed(0)}% Conf</span>
                            ) : item.type === 'SOIL_READING' ? (
                              <span className="text-cyan-400">{item.moisture !== null ? `${item.moisture}% Moist` : 'N/A'}</span>
                            ) : (
                              <span className="text-slate-400">{item.severity || item.status || 'RECORDED'}</span>
                            )}
                          </div>
                        </div>
                      ))}
                    </div>
                  ) : (
                    <div className="p-8 text-center text-slate-400 border border-dashed border-slate-800 rounded-xl text-xs">
                      No records saved yet for this field in local SQLite.
                    </div>
                  )}
                </div>
              )}

              {/* ========================================================= */}
              {/* TAB 9: HARDWARE DIAGNOSTICS MATRIX & SELF-TEST             */}
              {/* ========================================================= */}
              {activeTab === 'diagnostics' && (
                <div className="space-y-4">
                  {/* Host Platform & Board Architecture */}
                  <div className="bg-slate-800/60 border border-slate-700 rounded-xl p-4 space-y-2">
                    <div className="flex justify-between items-center">
                      <div className="text-sm font-bold text-slate-200">Host Platform & Architecture</div>
                      <span className="text-[11px] font-mono text-cyan-400 bg-slate-900 px-2.5 py-0.5 rounded border border-slate-800">
                        {deviceStatus?.platform?.board_model || 'Edge Host'}
                      </span>
                    </div>
                    <div className="grid grid-cols-4 gap-3 text-xs font-mono text-slate-300">
                      <div className="bg-slate-900/80 p-2.5 rounded-lg border border-slate-800">
                        <div className="text-[10px] text-slate-500 uppercase">OS & Kernel</div>
                        <div className="font-bold text-slate-200">{deviceStatus?.platform?.os_name} {deviceStatus?.platform?.architecture}</div>
                      </div>
                      <div className="bg-slate-900/80 p-2.5 rounded-lg border border-slate-800">
                        <div className="text-[10px] text-slate-500 uppercase">CPU Temperature</div>
                        <div className="font-bold text-amber-400">
                          {deviceStatus?.cpu_temperature_celsius !== null && deviceStatus?.cpu_temperature_celsius !== undefined ? `${deviceStatus.cpu_temperature_celsius}°C` : 'Telemetry N/A'}
                        </div>
                      </div>
                      <div className="bg-slate-900/80 p-2.5 rounded-lg border border-slate-800">
                        <div className="text-[10px] text-slate-500 uppercase">Local Storage</div>
                        <div className="font-bold text-emerald-400">{deviceStatus?.storage_free_gb || '--'} GB Free</div>
                      </div>
                      <div className="bg-slate-900/80 p-2.5 rounded-lg border border-slate-800">
                        <div className="text-[10px] text-slate-500 uppercase">Battery / PMIC</div>
                        <div className="font-bold text-slate-300">
                          {deviceStatus?.battery?.percent !== null && deviceStatus?.battery?.percent !== undefined ? `${deviceStatus.battery.percent}%` : (deviceStatus?.demo_mode ? '88.5% (Demo)' : 'Unavailable')}
                        </div>
                      </div>
                    </div>
                  </div>

                  {/* Subsystems Matrix */}
                  <div className="bg-slate-800/60 border border-slate-700 rounded-xl p-4">
                    <div className="text-sm font-bold text-slate-200 mb-3">Subsystems Diagnostic Matrix</div>
                    <div className="grid grid-cols-2 gap-3 text-xs">
                      <div className="p-3.5 bg-slate-900 rounded-xl border border-slate-800 space-y-1">
                        <div className="font-bold text-slate-200 flex justify-between">
                          <span>Camera Subsystem</span>
                          <Camera className="w-4 h-4 text-slate-400" />
                        </div>
                        <div className="text-slate-400">Driver: {deviceStatus?.subsystems.camera.is_mock ? 'MockCamera (Demo)' : 'OpenCV / V4L2'}</div>
                        <div className="text-slate-400">Status: <b className={deviceStatus?.camera_status_label === 'READY' ? 'text-emerald-400' : 'text-amber-400'}>{deviceStatus?.subsystems.camera.status}</b></div>
                      </div>

                      <div className="p-3.5 bg-slate-900 rounded-xl border border-slate-800 space-y-1">
                        <div className="font-bold text-slate-200 flex justify-between">
                          <span>6-Param RS485 Modbus</span>
                          <Droplets className="w-4 h-4 text-cyan-400" />
                        </div>
                        <div className="text-slate-400">Driver: {deviceStatus?.subsystems.soil_sensor.is_mock ? 'MockSoil (Demo)' : 'RS485 Serial'}</div>
                        <div className="text-slate-400">Status: <b className={deviceStatus?.soil_status_label === 'CONNECTED' ? 'text-emerald-400' : 'text-amber-400'}>{deviceStatus?.subsystems.soil_sensor.status}</b></div>
                      </div>

                      <div className="p-3.5 bg-slate-900 rounded-xl border border-slate-800 space-y-1">
                        <div className="font-bold text-slate-200 flex justify-between">
                          <span>AI Inference Engine</span>
                          <Cpu className="w-4 h-4 text-purple-400" />
                        </div>
                        <div className="text-slate-400">Accelerator: {visionStatus?.accelerator || 'CPU'}</div>
                        <div className="text-slate-400">Model: {visionStatus?.model_name || 'TEJAS-DemoVision'}</div>
                      </div>

                      <div className="p-3.5 bg-slate-900 rounded-xl border border-slate-800 space-y-1">
                        <div className="font-bold text-slate-200 flex justify-between">
                          <span>Offline SQLite Database</span>
                          <HistoryIcon className="w-4 h-4 text-emerald-400" />
                        </div>
                        <div className="text-slate-400">Engine: SQLAlchemy + SQLite PRAGMA FK</div>
                        <div className="text-slate-400">Status: <b className="text-emerald-400">{deviceStatus?.subsystems.database.status}</b></div>
                      </div>
                    </div>
                  </div>

                  {/* Detected Serial & RS485 Interfaces */}
                  <div className="bg-slate-800/60 border border-slate-700 rounded-xl p-4 space-y-2">
                    <div className="text-sm font-bold text-slate-200">Detected Serial & RS485 Interfaces</div>
                    {deviceStatus?.serial_ports && deviceStatus.serial_ports.length > 0 ? (
                      <div className="space-y-1.5 max-h-36 overflow-y-auto pr-1">
                        {deviceStatus.serial_ports.map((p, idx) => (
                          <div key={idx} className="bg-slate-900/90 border border-slate-800 p-2 rounded-lg flex justify-between items-center text-xs">
                            <div>
                              <span className="font-mono font-bold text-cyan-400">{p.device}</span>
                              <span className="text-slate-400 text-[11px] ml-2">{p.description}</span>
                            </div>
                            {p.is_usb_rs485_candidate && (
                              <span className="text-[10px] font-mono bg-cyan-950 text-cyan-300 px-2 py-0.5 rounded border border-cyan-800">
                                USB-RS485 Candidate
                              </span>
                            )}
                          </div>
                        ))}
                      </div>
                    ) : (
                      <div className="text-xs text-slate-500 p-2 bg-slate-900/50 rounded-lg">
                        No physical serial or USB-RS485 adapters currently attached.
                      </div>
                    )}
                  </div>

                  {/* Automated Startup Self-Test Panel */}
                  <div className="bg-slate-800/60 border border-slate-700 rounded-xl p-4 space-y-3">
                    <div className="flex justify-between items-center">
                      <div>
                        <div className="text-sm font-bold text-slate-200">Hardware & Subsystem Self-Test</div>
                        <div className="text-xs text-slate-400">Verifies local DB, storage, camera, soil probe, and AI engine</div>
                      </div>
                      <button
                        onClick={handleRunSelfTest}
                        disabled={isRunningSelfTest}
                        className="bg-purple-600 hover:bg-purple-500 disabled:bg-slate-700 text-white px-4 py-2 rounded-xl text-xs font-bold flex items-center space-x-1.5 shadow"
                      >
                        {isRunningSelfTest ? <RefreshCw className="w-3.5 h-3.5 animate-spin" /> : <Activity className="w-3.5 h-3.5" />}
                        <span>{isRunningSelfTest ? 'Running Self-Test...' : 'Run Hardware Self-Test'}</span>
                      </button>
                    </div>

                    {selfTestResult && (
                      <div className="space-y-3 pt-2 border-t border-slate-700">
                        <div className="flex justify-between items-center bg-slate-900 p-3 rounded-xl border border-slate-800">
                          <span className="text-xs font-bold text-slate-300">OVERALL DEVICE STATUS:</span>
                          <span className={`px-3 py-1 rounded-lg text-xs font-black ${
                            selfTestResult.overall_status === 'DEVICE READY' ? 'bg-emerald-950 text-emerald-300 border border-emerald-800' :
                            selfTestResult.overall_status === 'DEVICE READY WITH WARNINGS' ? 'bg-amber-950 text-amber-300 border border-amber-800' :
                            'bg-rose-950 text-rose-300 border border-rose-800'
                          }`}>
                            {selfTestResult.overall_status}
                          </span>
                        </div>

                        <div className="grid grid-cols-2 gap-2 text-xs">
                          {selfTestResult.items.map((item, idx) => (
                            <div key={idx} className="bg-slate-900/90 border border-slate-800 p-2.5 rounded-lg space-y-1">
                              <div className="flex justify-between items-center">
                                <span className="font-bold text-slate-200">{item.subsystem}</span>
                                <span className={`text-[10px] font-extrabold px-2 py-0.5 rounded ${
                                  item.status === 'PASSED' ? 'bg-emerald-950 text-emerald-300' :
                                  item.status === 'WARNING' ? 'bg-amber-950 text-amber-300' :
                                  'bg-rose-950 text-rose-300'
                                }`}>
                                  {item.status} {item.latency_ms !== null && item.latency_ms !== undefined ? `(${item.latency_ms}ms)` : ''}
                                </span>
                              </div>
                              <p className="text-[11px] text-slate-400">{item.message}</p>
                              {item.details && (
                                <p className="text-[10px] font-mono text-slate-500">{item.details}</p>
                              )}
                            </div>
                          ))}
                        </div>
                      </div>
                    )}
                  </div>

                  {/* Phase 8: Active AI Model Registry & Real Profiler */}
                  <div className="bg-slate-800/60 border border-slate-700 rounded-xl p-4 space-y-3">
                    <div className="flex justify-between items-center">
                      <div>
                        <div className="text-sm font-bold text-slate-200">AI Model Registry & Validation Status</div>
                        <div className="text-xs text-slate-400">Zero AI Hallucination: Model hashes verified via SHA-256</div>
                      </div>
                      <span className={`text-[10px] font-extrabold px-2.5 py-1 rounded border ${
                        modelRegistry?.active_model?.validation_status === 'VALIDATED' 
                          ? 'bg-emerald-950 text-emerald-300 border-emerald-800' 
                          : 'bg-amber-950 text-amber-300 border-amber-800'
                      }`}>
                        {modelRegistry?.active_model?.validation_status || 'NOT YET VALIDATED'}
                      </span>
                    </div>

                    <div className="grid grid-cols-2 gap-3 text-xs">
                      <div className="bg-slate-900/90 border border-slate-800 p-3 rounded-xl space-y-1.5 font-mono">
                        <div className="text-[10px] text-slate-500 uppercase font-sans font-bold">Active Model Details</div>
                        <div>Name: <b className="text-slate-200">{modelRegistry?.active_model?.model_name || visionStatus?.model_name || 'DemoVision'}</b></div>
                        <div>Version: <b className="text-slate-200">{modelRegistry?.active_model?.model_version || '0.1.0'}</b></div>
                        <div>Status: <b className="text-cyan-400">{modelRegistry?.active_model?.model_status || 'DEMO_MODEL'}</b></div>
                        <div className="truncate text-[11px]">SHA-256: <b className="text-purple-300">{modelRegistry?.active_model?.model_hash || 'demo_hash'}</b></div>
                      </div>

                      <div className="bg-slate-900/90 border border-slate-800 p-3 rounded-xl space-y-1.5 font-mono">
                        <div className="text-[10px] text-slate-500 uppercase font-sans font-bold">Latency Profiling (Monotonic)</div>
                        <div>Avg Inference: <b className="text-emerald-400">{visionStatus?.profiling_summary?.avg_inference_ms !== null && visionStatus?.profiling_summary?.avg_inference_ms !== undefined ? `${visionStatus.profiling_summary.avg_inference_ms} ms` : 'N/A'}</b></div>
                        <div>Avg Total Pipeline: <b className="text-cyan-400">{visionStatus?.profiling_summary?.avg_total_ms !== null && visionStatus?.profiling_summary?.avg_total_ms !== undefined ? `${visionStatus.profiling_summary.avg_total_ms} ms` : 'N/A'}</b></div>
                        <div>Measured Inferences: <b className="text-slate-200">{visionStatus?.profiling_summary?.total_inferences_measured || 0}</b></div>
                        <div>Accelerator: <b className="text-purple-300">{visionStatus?.accelerator || 'CPU'}</b></div>
                      </div>
                    </div>
                  </div>
                </div>
              )}

              {/* ========================================================= */}
              {/* TAB 10: SETTINGS                                          */}
              {/* ========================================================= */}
              {activeTab === 'settings' && (
                <div className="bg-slate-800/60 border border-slate-700 rounded-xl p-5 text-xs space-y-3">
                  <div className="font-bold text-slate-200 text-sm">System Runtime Settings</div>
                  <div className="space-y-2 text-slate-300 font-mono">
                    <div>Operation Mode: <b className="text-amber-400">{deviceStatus?.demo_mode ? 'DEMO_MODE=true' : 'REAL HARDWARE'}</b></div>
                    <div>Confidence Threshold: <b className="text-emerald-400">{((visionStatus?.confidence_threshold || 0.70) * 100).toFixed(0)}%</b></div>
                    <div>Zero Hardware Hallucination: <b className="text-emerald-400">ENFORCED (Strict Nullability)</b></div>
                    <div>Database: <b className="text-slate-400">data/krishidrishti.db</b></div>
                  </div>
                </div>
              )}
            </div>
          </div>

          {/* Touch-First Rugged Footer */}
          <div className="pt-3.5 border-t border-slate-800 flex justify-between items-center text-[11px] text-slate-500 shrink-0">
            <div>TEJAS &bull; Smart India Hackathon 2026 Prototype</div>
            <div>Offline Edge System &bull; Version 1.0.0</div>
          </div>
        </section>
      </main>

      {/* ------------------------------------------------------------- */}
      {/* ADD FIELD MODAL DIALOG                                        */}
      {/* ------------------------------------------------------------- */}
      {showAddFieldModal && (
        <div className="fixed inset-0 bg-slate-950/80 backdrop-blur-sm z-50 flex items-center justify-center p-4">
          <div className="bg-slate-900 border-2 border-slate-700 rounded-2xl p-6 w-full max-w-md shadow-2xl space-y-4">
            <div className="flex justify-between items-center">
              <h3 className="text-lg font-bold text-slate-100">{t('btn_add_field')}</h3>
              <button onClick={() => setShowAddFieldModal(false)} className="text-slate-400 hover:text-white">
                <XCircle className="w-5 h-5" />
              </button>
            </div>

            <form onSubmit={handleCreateField} className="space-y-3.5">
              <div>
                <label className="block text-xs font-semibold text-slate-300 mb-1">Field / Plot Name:</label>
                <input 
                  type="text" 
                  required
                  placeholder="e.g. North Tomato Sector"
                  value={newFieldName}
                  onChange={(e) => setNewFieldName(e.target.value)}
                  className="w-full bg-slate-950 border border-slate-700 rounded-xl px-3.5 py-2 text-xs text-slate-100 focus:outline-none focus:border-emerald-500"
                />
              </div>

              <div>
                <label className="block text-xs font-semibold text-slate-300 mb-1">Soil Type:</label>
                <select 
                  value={newFieldSoilType}
                  onChange={(e) => setNewFieldSoilType(e.target.value)}
                  className="w-full bg-slate-950 border border-slate-700 rounded-xl px-3.5 py-2 text-xs text-slate-100 focus:outline-none focus:border-emerald-500"
                >
                  <option value="Black Cotton">Black Cotton Soil (Regur)</option>
                  <option value="Loamy">Loamy Soil</option>
                  <option value="Red Soil">Red Soil</option>
                  <option value="Alluvial">Alluvial Soil</option>
                  <option value="Clay">Clay Soil</option>
                </select>
              </div>

              <div>
                <label className="block text-xs font-semibold text-slate-300 mb-1">Area (Acres):</label>
                <input 
                  type="number" 
                  step="0.1"
                  min="0.1"
                  value={newFieldArea}
                  onChange={(e) => setNewFieldArea(e.target.value)}
                  className="w-full bg-slate-950 border border-slate-700 rounded-xl px-3.5 py-2 text-xs text-slate-100 focus:outline-none focus:border-emerald-500"
                />
              </div>

              <div className="flex justify-end space-x-2.5 pt-2">
                <button 
                  type="button"
                  onClick={() => setShowAddFieldModal(false)}
                  className="px-4 py-2 rounded-xl text-xs font-bold text-slate-400 hover:bg-slate-800"
                >
                  Cancel
                </button>

                <button 
                  type="submit"
                  disabled={isCreatingField || !newFieldName.trim()}
                  className="bg-emerald-600 hover:bg-emerald-500 text-white px-5 py-2 rounded-xl text-xs font-bold flex items-center space-x-1.5"
                >
                  {isCreatingField ? <RefreshCw className="w-3.5 h-3.5 animate-spin" /> : null}
                  <span>Save Field</span>
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
}
