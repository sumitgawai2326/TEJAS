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
  predictDisease,
  fetchSampleImages,
  fetchSampleImageBlob,
  SampleImageItem,
  DeviceStatus, 
  FieldModel, 
  VisionAnalysisResponse, 
  VisionStatusResponse,
  FieldHistoryModel,
  FieldAnalysisResponse,
  FarmerAdvisoryItem,
  SoilReadingModel,
  SelfTestResponse,
  ModelRegistryResponse,
  DiseasePredictResponse
} from './services/api';

import en from './i18n/locales/en.json';
import hi from './i18n/locales/hi.json';
import mr from './i18n/locales/mr.json';

const translations: Record<string, Record<string, string>> = { en, hi, mr };

const DEFAULT_SAMPLES: SampleImageItem[] = [
  { id: 'bacterial_spot', label: 'Bacterial Spot', class_name: 'Tomato_Bacterial_Spot', filename: 'sample_bacterial_spot.jpg', url: '/samples/sample_bacterial_spot.jpg' },
  { id: 'early_blight', label: 'Early Blight', class_name: 'Tomato_Early_Blight', filename: 'sample_early_blight.jpg', url: '/samples/sample_early_blight.jpg' },
  { id: 'healthy', label: 'Healthy', class_name: 'Tomato_Healthy', filename: 'sample_healthy.jpg', url: '/samples/sample_healthy.jpg' },
  { id: 'late_blight', label: 'Late Blight', class_name: 'Tomato_Late_Blight', filename: 'sample_late_blight.jpg', url: '/samples/sample_late_blight.jpg' },
  { id: 'yellow_leaf_curl', label: 'Yellow Leaf Curl', class_name: 'Tomato_Yellow_Leaf_Curl_Virus', filename: 'sample_yellow_leaf_curl.jpg', url: '/samples/sample_yellow_leaf_curl.jpg' },
  { id: 'leaf_mold', label: 'Leaf Mold', class_name: 'Tomato_Leaf_Mold', filename: 'sample_leaf_mold.jpg', url: '/samples/sample_leaf_mold.jpg' },
  { id: 'mosaic_virus', label: 'Mosaic Virus', class_name: 'Tomato_Mosaic_Virus', filename: 'sample_mosaic_virus.jpg', url: '/samples/sample_mosaic_virus.jpg' },
  { id: 'septoria_leaf_spot', label: 'Septoria Leaf Spot', class_name: 'Tomato_Septoria_Leaf_Spot', filename: 'sample_septoria_leaf_spot.jpg', url: '/samples/sample_septoria_leaf_spot.jpg' },
  { id: 'target_spot', label: 'Target Spot', class_name: 'Tomato_Target_Spot', filename: 'sample_target_spot.jpg', url: '/samples/sample_target_spot.jpg' },
  { id: 'two_spotted_spider_mite', label: 'Spider Mite', class_name: 'Tomato_Two-Spotted_Spider_Mite', filename: 'sample_two_spotted_spider_mite.jpg', url: '/samples/sample_two_spotted_spider_mite.jpg' },
];

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
  const [diseasePrediction, setDiseasePrediction] = useState<DiseasePredictResponse | null>(null);
  const [isPredictingDisease, setIsPredictingDisease] = useState(false);
  const [diseasePredictError, setDiseasePredictError] = useState<string | null>(null);

  // Curated Sample Images for Demo
  const [samplesList, setSamplesList] = useState<SampleImageItem[]>(DEFAULT_SAMPLES);
  const [selectedSampleId, setSelectedSampleId] = useState<string | null>(null);
  const [isLoadingSample, setIsLoadingSample] = useState(false);

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

  // Load fields, AI status, and sample catalog on startup
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
      try {
        const samples = await fetchSampleImages();
        if (samples && samples.length > 0) {
          setSamplesList(samples);
        }
      } catch (e) {
        console.warn("Could not fetch remote samples catalog, using default list", e);
      }
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
      setSelectedSampleId(null);
      setPreviewUrl(URL.createObjectURL(file));
      setScanResult(null);
      setScanError(null);
      setDiseasePrediction(null);
      setDiseasePredictError(null);
      handlePredictDisease(file);
    }
  };

  const handleSelectSample = async (sample: SampleImageItem, autoRunInference = false) => {
    setIsLoadingSample(true);
    setSelectedSampleId(sample.id);
    setScanError(null);
    setDiseasePredictError(null);
    try {
      let blob: Blob;
      try {
        blob = await fetchSampleImageBlob(sample.id);
      } catch {
        const resp = await fetch(sample.url);
        blob = await resp.blob();
      }
      const file = new File([blob], sample.filename, { type: 'image/jpeg' });
      setSelectedFile(file);
      setPreviewUrl(URL.createObjectURL(blob));
      setScanResult(null);
      setDiseasePrediction(null);
      if (autoRunInference) {
        await handlePredictDisease(file);
      }
      return file;
    } catch (err: any) {
      console.error("Error loading sample image", err);
      setScanError("Failed to load sample image: " + (err.message || "Unknown error"));
      return null;
    } finally {
      setIsLoadingSample(false);
    }
  };

  const handlePredictDisease = async (fileToScan?: File) => {
    const targetFile = fileToScan || selectedFile;
    if (!targetFile) return;
    setIsPredictingDisease(true);
    setDiseasePredictError(null);
    try {
      const formData = new FormData();
      formData.append('file', targetFile);
      const res = await predictDisease(formData);
      setDiseasePrediction(res);
      return res;
    } catch (err: any) {
      const msg = err.response?.data?.detail || err.message || 'Disease prediction failed';
      setDiseasePredictError(msg);
      return null;
    } finally {
      setIsPredictingDisease(false);
    }
  };

  const executeScan = async (useCamera = false, fileOverride?: File) => {
    setIsScanning(true);
    setScanError(null);
    try {
      const formData = new FormData();
      const targetFile = fileOverride || selectedFile;
      if (useCamera) {
        formData.append('use_camera', 'true');
      } else if (targetFile) {
        formData.append('file', targetFile);
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
    <div className="flex flex-col h-screen w-screen overflow-hidden bg-[#0a1f14] text-slate-100 font-sans select-none">
      {/* ------------------------------------------------------------- */}
      {/* TOP EMBEDDED RUGGED HARDWARE STATUS BAR                       */}
      {/* ------------------------------------------------------------- */}
      <header className="bg-[#0a1f14] border-b border-[#18452e] px-4 py-3 flex items-center justify-between text-sm shrink-0 shadow-sm">
        <div className="flex items-center space-x-3">
          <div className="flex items-center space-x-2 bg-emerald-950 text-emerald-300 border border-emerald-700/70 px-3.5 py-1.5 rounded-xl font-black tracking-wider text-xs shadow-inner">
            <Sprout className="w-4 h-4 text-emerald-400 shrink-0" />
            <span>{t('app_name')}</span>
          </div>

          {/* Explicit DEMO vs REAL Badge */}
          {deviceStatus?.demo_mode ? (
            <div className="flex items-center space-x-1.5 bg-amber-500/20 text-amber-300 border border-amber-500/50 px-3 py-1 rounded-lg text-xs font-bold tracking-wider animate-pulse">
              <AlertTriangle className="w-3.5 h-3.5 text-amber-400 shrink-0" />
              <span>{t('demo_badge')}</span>
            </div>
          ) : (
            <div className="flex items-center space-x-1.5 bg-emerald-500/20 text-emerald-300 border border-emerald-500/50 px-3 py-1 rounded-lg text-xs font-bold tracking-wider">
              <CheckCircle2 className="w-3.5 h-3.5 text-emerald-400 shrink-0" />
              <span>{t('real_badge')}</span>
            </div>
          )}

          {/* Offline/Edge indicator */}
          <div className="flex items-center space-x-1.5 bg-teal-950/80 text-teal-300 border border-teal-800/60 px-2.5 py-1 rounded-lg text-xs font-semibold">
            <WifiOff className="w-3.5 h-3.5 text-teal-400 shrink-0" />
            <span>{t('status_offline')}</span>
          </div>

          {hasError && (
            <div className="text-xs text-rose-300 bg-rose-950 border border-rose-800 px-2.5 py-1 rounded-lg font-bold">
              Backend Offline
            </div>
          )}
        </div>

        {/* Right Hardware Telemetry Indicators */}
        <div className="flex items-center space-x-3">
          {/* AI Accelerator Indicator */}
          <div className="hidden sm:flex items-center space-x-1.5 text-xs text-slate-300 bg-[#0f2d21] px-3 py-1 rounded-lg border border-[#1b4d3a]">
            <Cpu className="w-4 h-4 text-purple-400 shrink-0" />
            <span className="font-mono">AI: <b className="text-purple-300">{deviceStatus?.ai_status_label || 'CPU'}</b></span>
          </div>

          {/* Battery Status */}
          <div className="flex items-center space-x-1.5 text-xs text-slate-300 bg-[#0f2d21] px-3 py-1 rounded-lg border border-[#1b4d3a]">
            {deviceStatus?.battery?.power_plugged ? (
              <BatteryCharging className="w-4 h-4 text-emerald-400 shrink-0" />
            ) : (
              <Battery className="w-4 h-4 text-emerald-400 shrink-0" />
            )}
            <span className="font-mono font-bold">{deviceStatus?.battery?.percent ?? '--'}%</span>
          </div>

          {/* One-Touch Multilingual Selector */}
          <div className="flex items-center bg-[#0f2d21] rounded-lg border border-[#1b4d3a] p-1 text-xs font-bold space-x-1">
            <button
              onClick={() => setLang('en')}
              className={`px-2.5 py-1 rounded transition ${lang === 'en' ? 'bg-emerald-600 text-white shadow' : 'text-emerald-200/70 hover:text-white'}`}
            >
              EN
            </button>
            <button
              onClick={() => setLang('hi')}
              className={`px-2.5 py-1 rounded transition ${lang === 'hi' ? 'bg-emerald-600 text-white shadow' : 'text-emerald-200/70 hover:text-white'}`}
            >
              हिंदी
            </button>
            <button
              onClick={() => setLang('mr')}
              className={`px-2.5 py-1 rounded transition ${lang === 'mr' ? 'bg-emerald-600 text-white shadow' : 'text-emerald-200/70 hover:text-white'}`}
            >
              मराठी
            </button>
          </div>
        </div>
      </header>

      {/* ------------------------------------------------------------- */}
      {/* MAIN TOUCH WORKSPACE & NAVIGATION                             */}
      {/* ------------------------------------------------------------- */}
      <main className="flex-1 flex overflow-hidden p-3 gap-3 bg-[#0a1f14]">
        {/* Rugged Touch Left Navigation Bar */}
        <nav className="w-52 bg-[#0f2d21] border border-[#1a4733] rounded-2xl p-2.5 flex flex-col justify-between shrink-0 select-none shadow-2xl">
          <div className="space-y-1.5">
            {/* 1. Home Dashboard */}
            <button
              onClick={() => setActiveTab('home')}
              className={`w-full flex items-center space-x-3 px-3.5 py-3 rounded-xl text-sm font-bold transition ${
                activeTab === 'home' ? 'bg-emerald-600 text-white shadow-lg shadow-emerald-950/50' : 'text-emerald-100/80 hover:bg-[#153e2e] hover:text-white'
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
                activeTab === 'wizard' ? 'bg-emerald-600 text-white shadow-lg shadow-emerald-950/60 ring-1 ring-emerald-400' : 'text-emerald-200 bg-emerald-950/60 border border-emerald-700/50 hover:bg-emerald-900/60 hover:text-white'
              }`}
            >
              <PlayCircle className="w-5 h-5 shrink-0 text-emerald-300" />
              <span>{t('nav_wizard')}</span>
            </button>

            {/* 3. Fields / Plots */}
            <button
              onClick={() => setActiveTab('fields')}
              className={`w-full flex items-center space-x-3 px-3.5 py-2.5 rounded-xl text-sm font-semibold transition ${
                activeTab === 'fields' ? 'bg-emerald-600 text-white shadow-md' : 'text-emerald-100/80 hover:bg-[#153e2e] hover:text-white'
              }`}
            >
              <Layers className="w-5 h-5 shrink-0" />
              <span>{t('nav_fields')}</span>
            </button>

            {/* 4. Standalone Crop Scanner */}
            <button
              onClick={() => setActiveTab('scanner')}
              className={`w-full flex items-center space-x-3 px-3.5 py-2.5 rounded-xl text-sm font-semibold transition ${
                activeTab === 'scanner' ? 'bg-emerald-600 text-white shadow-md' : 'text-emerald-100/80 hover:bg-[#153e2e] hover:text-white'
              }`}
            >
              <Camera className="w-5 h-5 shrink-0" />
              <span>{t('nav_scanner')}</span>
            </button>

            {/* 5. 6-Parameter Soil Module */}
            <button
              onClick={() => setActiveTab('soil')}
              className={`w-full flex items-center space-x-3 px-3.5 py-2.5 rounded-xl text-sm font-semibold transition ${
                activeTab === 'soil' ? 'bg-emerald-600 text-white shadow-md' : 'text-emerald-100/80 hover:bg-[#153e2e] hover:text-white'
              }`}
            >
              <Droplets className="w-5 h-5 shrink-0" />
              <span>{t('nav_soil')}</span>
            </button>

            {/* 6. Multi-Modal Risk */}
            <button
              onClick={() => setActiveTab('risk')}
              className={`w-full flex items-center space-x-3 px-3.5 py-2.5 rounded-xl text-sm font-semibold transition ${
                activeTab === 'risk' ? 'bg-emerald-600 text-white shadow-md' : 'text-emerald-100/80 hover:bg-[#153e2e] hover:text-white'
              }`}
            >
              <ShieldAlert className="w-5 h-5 shrink-0" />
              <span>{t('nav_risk')}</span>
            </button>

            {/* 7. Actionable Advisories */}
            <button
              onClick={() => setActiveTab('advisory')}
              className={`w-full flex items-center space-x-3 px-3.5 py-2.5 rounded-xl text-sm font-semibold transition ${
                activeTab === 'advisory' ? 'bg-emerald-600 text-white shadow-md' : 'text-emerald-100/80 hover:bg-[#153e2e] hover:text-white'
              }`}
            >
              <FileText className="w-5 h-5 shrink-0" />
              <span>{t('nav_advisory')}</span>
            </button>

            {/* 8. History & Timeline */}
            <button
              onClick={() => setActiveTab('history')}
              className={`w-full flex items-center space-x-3 px-3.5 py-2.5 rounded-xl text-sm font-semibold transition ${
                activeTab === 'history' ? 'bg-emerald-600 text-white shadow-md' : 'text-emerald-100/80 hover:bg-[#153e2e] hover:text-white'
              }`}
            >
              <HistoryIcon className="w-5 h-5 shrink-0" />
              <span>{t('nav_history')}</span>
            </button>
          </div>

          {/* Bottom Settings & Diagnostics */}
          <div className="space-y-1.5 pt-2 border-t border-[#1a4733]">
            <button
              onClick={() => setActiveTab('diagnostics')}
              className={`w-full flex items-center space-x-3 px-3.5 py-2 rounded-xl text-xs font-bold transition ${
                activeTab === 'diagnostics' ? 'bg-emerald-600 text-white shadow' : 'text-emerald-200/70 hover:bg-[#153e2e] hover:text-white'
              }`}
            >
              <CheckCircle2 className="w-4 h-4 shrink-0" />
              <span>{t('nav_diagnostics')}</span>
            </button>

            <button
              onClick={() => setActiveTab('settings')}
              className={`w-full flex items-center space-x-3 px-3.5 py-2 rounded-xl text-xs font-bold transition ${
                activeTab === 'settings' ? 'bg-emerald-600 text-white shadow' : 'text-emerald-200/70 hover:bg-[#153e2e] hover:text-white'
              }`}
            >
              <SettingsIcon className="w-4 h-4 shrink-0" />
              <span>{t('nav_settings')}</span>
            </button>
          </div>
        </nav>

        {/* ------------------------------------------------------------- */}
        {/* MAIN TOUCH CONTENT VIEWPORT (LIGHT MODERN THEME)             */}
        {/* ------------------------------------------------------------- */}
        <section className="flex-1 bg-[#f6f8f6] text-slate-800 border border-slate-200/90 rounded-2xl p-5 overflow-y-auto flex flex-col justify-between shadow-2xl">
          <div>
            {/* Header Title & Host Telemetry */}
            <div className="flex items-center justify-between pb-3.5 border-b border-slate-200">
              <div>
                <h1 className="text-2xl font-black text-slate-900 flex items-center space-x-2 tracking-tight">
                  <span>{t(`nav_${activeTab}`)}</span>
                </h1>
                <p className="text-xs text-slate-500 font-medium mt-0.5">{t('tagline')}</p>
              </div>

              {/* Live Host Telemetry Pill */}
              {deviceStatus && (
                <div className="flex items-center space-x-3 text-xs font-mono bg-white px-3.5 py-1.5 rounded-xl border border-slate-200 shadow-sm">
                  <span className="text-slate-600">CPU: <b className="text-slate-900">{deviceStatus.cpu_usage_percent}%</b></span>
                  <span className="text-slate-600">RAM: <b className="text-slate-900">{deviceStatus.ram_usage_percent}%</b></span>
                  {deviceStatus.cpu_temperature_celsius !== null && (
                    <span className="text-slate-600">TEMP: <b className="text-amber-600 font-bold">{deviceStatus.cpu_temperature_celsius}°C</b></span>
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
                  <div className="bg-gradient-to-r from-emerald-800 via-emerald-700 to-teal-800 border border-emerald-600/40 rounded-2xl p-6 shadow-lg flex items-center justify-between text-white">
                    <div className="space-y-1.5">
                      <div className="text-xs font-mono font-bold text-emerald-200 tracking-wider uppercase">GUIDED EDGE WORKFLOW</div>
                      <div className="text-2xl font-black text-white">Ready for Field Diagnosis</div>
                      <p className="text-xs text-emerald-100/90 max-w-lg leading-relaxed">
                        Execute step-by-step leaf pathology scanning, 6-parameter soil telemetry, multi-modal risk scoring, and actionable advisory.
                      </p>
                    </div>

                    <button
                      onClick={() => {
                        setActiveTab('wizard');
                        setWizardStep(1);
                      }}
                      className="bg-white hover:bg-emerald-50 text-emerald-900 px-6 py-4 rounded-xl text-base font-black tracking-wide flex items-center space-x-3 shadow-xl transition active:scale-95 shrink-0"
                    >
                      <span>{t('btn_start_check')}</span>
                      <ArrowRight className="w-5 h-5 text-emerald-800" />
                    </button>
                  </div>

                  {/* Hardware Readiness Matrix (Truthful!) */}
                  <div>
                    <div className="text-xs font-bold text-slate-500 tracking-wider mb-2.5 uppercase">LIVE HARDWARE DIAGNOSTIC MATRIX</div>
                    <div className="grid grid-cols-4 gap-3.5">
                      {/* Subsystem 1: Camera */}
                      <div className="bg-white border border-slate-200 rounded-2xl p-4 space-y-1.5 shadow-sm hover:shadow transition">
                        <div className="flex justify-between items-center text-xs font-bold text-slate-400 uppercase tracking-wider">
                          <span>CAMERA SUBSYSTEM</span>
                          <Camera className="w-4 h-4 text-slate-400" />
                        </div>
                        <div className="text-lg font-black text-slate-900">
                          {deviceStatus?.subsystems?.camera?.is_mock ? 'Mock (Demo)' : (deviceStatus?.subsystems?.camera?.status || 'Active')}
                        </div>
                        <div className="text-[11px] text-emerald-600 font-mono font-medium">
                          {deviceStatus?.camera_status_label === 'READY' || deviceStatus?.subsystems?.camera?.status === 'READY' ? '● Ready for scan' : '○ ' + (deviceStatus?.camera_status_label || 'Unavailable')}
                        </div>
                      </div>

                      {/* Subsystem 2: 6-Param Soil Module */}
                      <div className="bg-white border border-slate-200 rounded-2xl p-4 space-y-1.5 shadow-sm hover:shadow transition">
                        <div className="flex justify-between items-center text-xs font-bold text-slate-400 uppercase tracking-wider">
                          <span>6-PARAM SOIL SENSOR</span>
                          <Droplets className="w-4 h-4 text-emerald-600" />
                        </div>
                        <div className="text-lg font-black text-slate-900">
                          {deviceStatus?.demo_mode ? 'Simulated 6-in-1' : (deviceStatus?.soil_status_label || 'DISCONNECTED')}
                        </div>
                        <div className={`text-[11px] font-mono font-medium ${deviceStatus?.soil_status_label === 'CONNECTED' ? 'text-emerald-600' : (deviceStatus?.demo_mode ? 'text-amber-600' : 'text-rose-600')}`}>
                          {deviceStatus?.demo_mode ? '● Demo simulation' : (deviceStatus?.soil_status_label === 'CONNECTED' ? '● RS485 Link OK' : '○ Sensor Disconnected')}
                        </div>
                      </div>

                      {/* Subsystem 3: AI Accelerator */}
                      <div className="bg-white border border-slate-200 rounded-2xl p-4 space-y-1.5 shadow-sm hover:shadow transition">
                        <div className="flex justify-between items-center text-xs font-bold text-slate-400 uppercase tracking-wider">
                          <span>AI ACCELERATOR</span>
                          <Cpu className="w-4 h-4 text-purple-600" />
                        </div>
                        <div className="text-lg font-black text-slate-900">
                          {visionStatus?.accelerator || 'CPU FALLBACK'}
                        </div>
                        <div className="text-[11px] text-purple-600 font-mono font-medium">
                          {visionStatus?.ready ? '● Model Loaded' : '○ Missing weights'}
                        </div>
                      </div>

                      {/* Subsystem 4: SQLite Database */}
                      <div className="bg-white border border-slate-200 rounded-2xl p-4 space-y-1.5 shadow-sm hover:shadow transition">
                        <div className="flex justify-between items-center text-xs font-bold text-slate-400 uppercase tracking-wider">
                          <span>LOCAL SQLITE DB</span>
                          <HistoryIcon className="w-4 h-4 text-emerald-600" />
                        </div>
                        <div className="text-lg font-black text-slate-900">
                          Offline Storage
                        </div>
                        <div className="text-[11px] text-emerald-600 font-mono font-medium">
                          ● {fields.length} Fields registered
                        </div>
                      </div>
                    </div>
                  </div>

                  {/* Quick Navigation Cards */}
                  <div className="grid grid-cols-3 gap-4 pt-2">
                    <div 
                      onClick={() => setActiveTab('fields')}
                      className="bg-white hover:bg-slate-50 border border-slate-200 rounded-2xl p-4 cursor-pointer transition shadow-sm flex items-center space-x-3.5"
                    >
                      <div className="w-10 h-10 rounded-xl bg-emerald-50 border border-emerald-200 flex items-center justify-center text-emerald-700">
                        <Layers className="w-5 h-5" />
                      </div>
                      <div>
                        <div className="font-bold text-sm text-slate-900">Manage Fields</div>
                        <div className="text-xs text-slate-500">Select or add agricultural plots</div>
                      </div>
                    </div>

                    <div 
                      onClick={() => setActiveTab('soil')}
                      className="bg-white hover:bg-slate-50 border border-slate-200 rounded-2xl p-4 cursor-pointer transition shadow-sm flex items-center space-x-3.5"
                    >
                      <div className="w-10 h-10 rounded-xl bg-teal-50 border border-teal-200 flex items-center justify-center text-teal-700">
                        <Droplets className="w-5 h-5" />
                      </div>
                      <div>
                        <div className="font-bold text-sm text-slate-900">6-Parameter Soil Probe</div>
                        <div className="text-xs text-slate-500">Inspect live N/P/K/pH/Moisture</div>
                      </div>
                    </div>

                    <div 
                      onClick={() => setActiveTab('history')}
                      className="bg-white hover:bg-slate-50 border border-slate-200 rounded-2xl p-4 cursor-pointer transition shadow-sm flex items-center space-x-3.5"
                    >
                      <div className="w-10 h-10 rounded-xl bg-purple-50 border border-purple-200 flex items-center justify-center text-purple-700">
                        <HistoryIcon className="w-5 h-5" />
                      </div>
                      <div>
                        <div className="font-bold text-sm text-slate-900">Field History Timeline</div>
                        <div className="text-xs text-slate-500">View chronological field records</div>
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
                  <div className="bg-white border border-slate-200 rounded-2xl p-3.5 shadow-sm flex items-center justify-between">
                    <div className="flex items-center space-x-2">
                      {[1, 2, 3, 4, 5, 6, 7].map(step => (
                        <div 
                          key={step} 
                          className={`w-7 h-7 rounded-full flex items-center justify-center text-xs font-bold transition ${
                            wizardStep === step ? 'bg-emerald-600 text-white ring-2 ring-emerald-300 ring-offset-1' :
                            wizardStep > step ? 'bg-emerald-100 text-emerald-800 font-bold' :
                            'bg-slate-100 text-slate-400 border border-slate-200'
                          }`}
                        >
                          {wizardStep > step ? <Check className="w-3.5 h-3.5" /> : step}
                        </div>
                      ))}
                    </div>

                    <div className="text-xs font-mono font-bold text-emerald-800 uppercase">
                      STEP {wizardStep} OF 7: {t(`step_${wizardStep}_title`)}
                    </div>
                  </div>

                  {/* WIZARD STEP 1: SELECT FIELD */}
                  {wizardStep === 1 && (
                    <div className="bg-white border border-slate-200 rounded-2xl p-6 space-y-4 shadow-sm">
                      <div className="space-y-1">
                        <h2 className="text-xl font-bold text-slate-900">{t('step_1_title')}</h2>
                        <p className="text-xs text-slate-500">{t('step_1_desc')}</p>
                      </div>

                      <div className="grid grid-cols-2 gap-3.5 max-h-72 overflow-y-auto pr-1">
                        {fields.map(field => (
                          <div 
                            key={field.id}
                            onClick={() => setSelectedFieldId(field.id)}
                            className={`p-4 rounded-xl border-2 cursor-pointer transition flex justify-between items-center ${
                              selectedFieldId === field.id 
                                ? 'bg-emerald-50/80 border-emerald-600 text-emerald-950 shadow-sm' 
                                : 'bg-slate-50 border-slate-200 hover:bg-slate-100 text-slate-800'
                            }`}
                          >
                            <div>
                              <div className="font-bold text-base">{field.name}</div>
                              <div className="text-xs text-slate-500 mt-0.5">Soil: {field.soil_type || 'General'} &bull; Area: {field.area || 1.0} {field.area_unit}</div>
                            </div>
                            {selectedFieldId === field.id && (
                              <CheckCircle className="w-6 h-6 text-emerald-600 shrink-0" />
                            )}
                          </div>
                        ))}
                      </div>

                      <div className="flex justify-between items-center pt-3 border-t border-slate-200">
                        <button
                          onClick={() => setShowAddFieldModal(true)}
                          className="bg-slate-100 hover:bg-slate-200 text-slate-700 px-4 py-2 rounded-xl text-xs font-bold flex items-center space-x-1.5 border border-slate-300"
                        >
                          <PlusCircle className="w-4 h-4" />
                          <span>{t('btn_add_field')}</span>
                        </button>

                        <button
                          disabled={!selectedFieldId}
                          onClick={() => setWizardStep(2)}
                          className="bg-emerald-600 hover:bg-emerald-500 disabled:bg-slate-300 disabled:text-slate-500 text-white px-6 py-2.5 rounded-xl text-sm font-bold flex items-center space-x-2 shadow"
                        >
                          <span>{t('btn_next')}</span>
                          <ArrowRight className="w-4 h-4" />
                        </button>
                      </div>
                    </div>
                  )}

                  {/* WIZARD STEP 2: CROP LEAF CAPTURE */}
                  {wizardStep === 2 && (
                    <div className="bg-white border border-slate-200 rounded-2xl p-6 space-y-4 shadow-sm">
                      <div className="space-y-1">
                        <h2 className="text-xl font-bold text-slate-900">{t('step_2_title')}</h2>
                        <p className="text-xs text-slate-500">{t('step_2_desc')}</p>
                      </div>

                      {/* Quick Demo Sample Leaf Selector */}
                      <div className="bg-slate-50 border border-slate-200 rounded-2xl p-4 space-y-3">
                        <div className="flex items-center justify-between">
                          <div className="text-xs font-bold text-slate-800 flex items-center space-x-1.5">
                            <Zap className="w-4 h-4 text-amber-500 shrink-0" />
                            <span>Choose Sample Leaf (Verified Test Dataset):</span>
                          </div>
                          <span className="text-[10px] font-mono font-bold text-emerald-800 bg-emerald-100 border border-emerald-300 px-2 py-0.5 rounded-md">
                            Real YOLO11n AI
                          </span>
                        </div>

                        <div className="flex flex-wrap items-center gap-2">
                          {samplesList.slice(0, 5).map(s => (
                            <button
                              key={s.id}
                              type="button"
                              onClick={() => handleSelectSample(s, false)}
                              disabled={isLoadingSample || isScanning}
                              className={`px-3 py-1.5 rounded-lg text-xs font-bold transition border flex items-center space-x-1.5 ${
                                selectedSampleId === s.id
                                  ? 'bg-emerald-600 text-white border-emerald-600 shadow-sm ring-2 ring-emerald-300'
                                  : 'bg-white text-slate-700 border-slate-300 hover:bg-slate-100'
                              }`}
                            >
                              <span>{s.label}</span>
                            </button>
                          ))}

                          <select
                            value={selectedSampleId || ''}
                            onChange={(e) => {
                              const found = samplesList.find(x => x.id === e.target.value);
                              if (found) handleSelectSample(found, false);
                            }}
                            className="bg-white border border-slate-300 rounded-lg px-2.5 py-1.5 text-xs text-slate-700 font-medium ml-auto"
                          >
                            <option value="" disabled>More Disease Classes (10)...</option>
                            {samplesList.map(s => (
                              <option key={s.id} value={s.id}>{s.label}</option>
                            ))}
                          </select>
                        </div>
                      </div>

                      <div className="grid grid-cols-2 gap-4">
                        {/* Viewfinder Preview */}
                        <div className="bg-slate-900 border-2 border-dashed border-slate-700 rounded-2xl p-4 flex flex-col items-center justify-center min-h-[260px] text-center relative overflow-hidden text-slate-100">
                          {previewUrl ? (
                            <div className="space-y-2 flex flex-col items-center">
                              <img src={previewUrl} alt="Leaf preview" className="max-h-52 object-contain rounded-lg shadow-md" />
                              {selectedSampleId && (
                                <span className="text-[11px] font-mono text-emerald-300 bg-emerald-950/90 border border-emerald-700 px-2.5 py-0.5 rounded">
                                  Sample Selected: {samplesList.find(s => s.id === selectedSampleId)?.label}
                                </span>
                              )}
                            </div>
                          ) : (
                            <div className="space-y-2 text-slate-400">
                              <Camera className="w-12 h-12 mx-auto text-slate-500" />
                              <div className="font-bold text-sm text-slate-300">Offline Hardware Viewfinder</div>
                              <p className="text-xs text-slate-500 max-w-xs">Select a verified sample leaf above, upload a file, or capture from camera.</p>
                            </div>
                          )}
                        </div>

                        {/* Capture Controls */}
                        <div className="flex flex-col justify-center space-y-3">
                          <button
                            onClick={async () => {
                              const res = await executeScan(true);
                              if (res && res.image_quality.passed) setWizardStep(3);
                            }}
                            disabled={isScanning || isLoadingSample}
                            className="w-full bg-emerald-600 hover:bg-emerald-500 disabled:bg-slate-300 disabled:text-slate-500 text-white py-3.5 rounded-xl text-sm font-bold flex items-center justify-center space-x-2 shadow-md"
                          >
                            {isScanning ? <RefreshCw className="w-4 h-4 animate-spin" /> : <Camera className="w-5 h-5" />}
                            <span>Capture from Hardware Camera</span>
                          </button>

                          <label className="w-full cursor-pointer bg-slate-100 hover:bg-slate-200 text-slate-700 py-3 rounded-xl text-xs font-bold flex items-center justify-center space-x-2 border border-slate-300">
                            <Upload className="w-4 h-4 text-slate-600" />
                            <span>{t('btn_upload')}</span>
                            <input type="file" accept="image/*" className="hidden" onChange={handleFileSelect} />
                          </label>

                          {selectedFile && (
                            <button
                              onClick={async () => {
                                const res = await executeScan(false);
                                if (res) setWizardStep(3);
                              }}
                              disabled={isScanning || isLoadingSample}
                              className="w-full bg-teal-600 hover:bg-teal-500 text-white py-3 rounded-xl text-xs font-bold flex items-center justify-center space-x-1.5 shadow-md"
                            >
                              <span>Analyze Selected Leaf (YOLO11n)</span>
                              <ArrowRight className="w-4 h-4" />
                            </button>
                          )}

                          {scanError && (
                            <div className="bg-rose-50 border border-rose-200 text-rose-800 p-3 rounded-xl text-xs flex items-start space-x-2">
                              <AlertTriangle className="w-4 h-4 flex-shrink-0 mt-0.5 text-rose-600" />
                              <div>
                                <div className="font-bold text-rose-900">Hardware Notice</div>
                                <div>{scanError}</div>
                                <div className="text-slate-600 mt-1">If no physical camera is plugged in, click any sample leaf above to test real YOLO11n inference.</div>
                              </div>
                            </div>
                          )}
                        </div>
                      </div>

                      <div className="flex justify-between items-center pt-3 border-t border-slate-200">
                        <button
                          onClick={() => setWizardStep(1)}
                          className="bg-slate-100 hover:bg-slate-200 text-slate-700 px-4 py-2 rounded-xl text-xs font-bold border border-slate-300"
                        >
                          {t('btn_back')}
                        </button>
                      </div>
                    </div>
                  )}

                  {/* WIZARD STEP 3: IMAGE QUALITY CHECK */}
                  {wizardStep === 3 && scanResult && (
                    <div className="bg-white border border-slate-200 rounded-2xl p-6 space-y-4 shadow-sm">
                      <div className="space-y-1">
                        <h2 className="text-xl font-bold text-slate-900">{t('step_3_title')}</h2>
                        <p className="text-xs text-slate-500">{t('step_3_desc')}</p>
                      </div>

                      <div className={`p-4 rounded-2xl border-2 ${
                        scanResult.image_quality.passed ? 'bg-emerald-50 border-emerald-500 text-emerald-950' : 'bg-amber-50 border-amber-500 text-amber-950'
                      }`}>
                        <div className="flex justify-between items-center font-bold">
                          <span className="flex items-center space-x-2 text-base">
                            {scanResult.image_quality.passed ? <CheckCircle className="w-5 h-5 text-emerald-600" /> : <AlertTriangle className="w-5 h-5 text-amber-600" />}
                            <span>{scanResult.image_quality.passed ? 'Image Quality Passed' : 'Image Quality Warning'}</span>
                          </span>
                          <span className="font-mono text-sm font-bold text-slate-800">Sharpness: {scanResult.image_quality.blur_score}</span>
                        </div>
                        <p className="mt-2 text-xs font-medium text-slate-700">
                          {scanResult.image_quality.farmer_instruction || scanResult.image_quality.error_reason || 'Image meets diagnostic resolution and exposure requirements.'}
                        </p>
                      </div>

                      <div className="grid grid-cols-3 gap-3 text-xs font-mono bg-slate-50 p-3.5 rounded-xl border border-slate-200 text-slate-700">
                        <div>Sharpness (Blur): <b className="text-slate-900">{scanResult.image_quality.blur_score}</b></div>
                        <div>Exposure (Luminance): <b className="text-slate-900">{scanResult.image_quality.brightness_score}</b></div>
                        <div>Resolution: <b className="text-slate-900">{scanResult.image_quality.resolution}</b></div>
                      </div>

                      <div className="flex justify-between items-center pt-3 border-t border-slate-200">
                        <button
                          onClick={() => setWizardStep(2)}
                          className="bg-slate-100 hover:bg-slate-200 text-slate-700 px-4 py-2 rounded-xl text-xs font-bold flex items-center space-x-1 border border-slate-300"
                        >
                          <RotateCcw className="w-4 h-4" />
                          <span>{t('btn_retake')}</span>
                        </button>

                        <button
                          onClick={() => setWizardStep(4)}
                          className="bg-emerald-600 hover:bg-emerald-500 text-white px-6 py-2.5 rounded-xl text-sm font-bold flex items-center space-x-2 shadow"
                        >
                          <span>{t('btn_next')}</span>
                          <ArrowRight className="w-4 h-4" />
                        </button>
                      </div>
                    </div>
                  )}

                  {/* WIZARD STEP 4: AI VISION ANALYSIS */}
                  {wizardStep === 4 && scanResult && (
                    <div className="bg-white border border-slate-200 rounded-2xl p-6 space-y-4 shadow-sm">
                      <div className="space-y-1">
                        <h2 className="text-xl font-bold text-slate-900">{t('step_4_title')}</h2>
                        <p className="text-xs text-slate-500">{t('step_4_desc')}</p>
                      </div>

                      <div className="bg-slate-50 border border-slate-200 rounded-2xl p-5 space-y-3.5">
                        <div className="flex justify-between items-center">
                          <span className="text-xs text-slate-500 font-bold uppercase tracking-wider">TEJAS AI PATHOLOGY DIAGNOSIS</span>
                          <div className="flex items-center space-x-1.5">
                            <span className="text-[10px] font-mono font-bold text-emerald-800 bg-emerald-100 px-2 py-0.5 rounded border border-emerald-300">
                              {scanResult.model_name}
                            </span>
                            <span className="text-xs font-mono text-purple-700 bg-purple-50 px-2 py-0.5 rounded border border-purple-200 font-semibold">
                              {scanResult.inference_device} ({scanResult.inference_time_ms}ms)
                            </span>
                          </div>
                        </div>

                        <div className="text-2xl font-black text-slate-900">{scanResult.prediction}</div>

                        {/* Confidence Gauge */}
                        <div>
                          <div className="flex justify-between text-xs font-mono text-slate-600 mb-1">
                            <span>Model Confidence</span>
                            <b className="text-slate-900">{(scanResult.confidence * 100).toFixed(1)}%</b>
                          </div>
                          <div className="w-full h-3 bg-slate-200 rounded-full overflow-hidden">
                            <div 
                              className={`h-full ${scanResult.confidence >= 0.70 ? 'bg-emerald-600' : 'bg-amber-500'}`} 
                              style={{ width: `${Math.min(scanResult.confidence * 100, 100)}%` }}
                            ></div>
                          </div>
                        </div>

                        {/* Top-3 Ranked Predictions */}
                        {scanResult.top_predictions && scanResult.top_predictions.length > 0 && (
                          <div className="space-y-2 bg-white p-3.5 rounded-xl border border-slate-200 shadow-sm">
                            <div className="text-[11px] font-mono text-slate-500 font-bold uppercase">TOP RANKED CLASSES</div>
                            <div className="space-y-2">
                              {scanResult.top_predictions.slice(0, 3).map((item, idx) => (
                                <div key={idx} className="space-y-0.5">
                                  <div className="flex justify-between text-xs text-slate-700">
                                    <span className="font-semibold">#{idx + 1} {item.class_name.replace(/_/g, ' ')}</span>
                                    <b className="font-mono text-slate-900">{(item.confidence * 100).toFixed(1)}%</b>
                                  </div>
                                  <div className="w-full h-1.5 bg-slate-200 rounded-full overflow-hidden">
                                    <div 
                                      className={`h-full rounded-full transition-all duration-300 ${
                                        idx === 0 ? 'bg-emerald-600' : idx === 1 ? 'bg-teal-600' : 'bg-slate-400'
                                      }`} 
                                      style={{ width: `${Math.max(item.confidence * 100, 1)}%` }}
                                    ></div>
                                  </div>
                                </div>
                              ))}
                            </div>
                          </div>
                        )}

                        {scanResult.status === 'low_confidence' && (
                          <div className="bg-amber-50 border border-amber-200 text-amber-800 p-3 rounded-xl text-xs font-medium">
                            AI result is uncertain (&lt; 70% threshold). Proceeding with caution.
                          </div>
                        )}
                      </div>

                      <div className="flex justify-between items-center pt-3 border-t border-slate-200">
                        <button
                          onClick={() => setWizardStep(3)}
                          className="bg-slate-100 hover:bg-slate-200 text-slate-700 px-4 py-2 rounded-xl text-xs font-bold border border-slate-300"
                        >
                          {t('btn_back')}
                        </button>

                        <button
                          onClick={async () => {
                            if (selectedFieldId) await triggerLiveSoil(selectedFieldId);
                            setWizardStep(5);
                          }}
                          className="bg-emerald-600 hover:bg-emerald-500 text-white px-6 py-2.5 rounded-xl text-sm font-bold flex items-center space-x-2 shadow"
                        >
                          <span>{t('btn_next')}</span>
                          <ArrowRight className="w-4 h-4" />
                        </button>
                      </div>
                    </div>
                  )}

                  {/* WIZARD STEP 5: 6-PARAM SOIL TELEMETRY */}
                  {wizardStep === 5 && (
                    <div className="bg-white border border-slate-200 rounded-2xl p-6 space-y-4 shadow-sm">
                      <div className="flex justify-between items-center">
                        <div>
                          <h2 className="text-xl font-bold text-slate-900">{t('step_5_title')}</h2>
                          <p className="text-xs text-slate-500">{t('step_5_desc')}</p>
                        </div>
                        <button
                          onClick={() => selectedFieldId && triggerLiveSoil(selectedFieldId)}
                          disabled={isReadingSoil}
                          className="bg-teal-600 hover:bg-teal-500 text-white px-3.5 py-1.5 rounded-xl text-xs font-bold flex items-center space-x-1 shadow-sm"
                        >
                          <RefreshCw className={`w-3.5 h-3.5 ${isReadingSoil ? 'animate-spin' : ''}`} />
                          <span>Re-read Sensor</span>
                        </button>
                      </div>

                      <div className="grid grid-cols-3 gap-3">
                        <div className="bg-slate-50 border border-slate-200 rounded-xl p-4 text-center">
                          <div className="text-xs text-slate-500 font-bold uppercase">{t('soil_n')}</div>
                          <div className="text-2xl font-black text-emerald-700 mt-1 font-mono">
                            {liveSoilReading?.nitrogen !== null && liveSoilReading?.nitrogen !== undefined ? `${liveSoilReading.nitrogen} mg/kg` : '--'}
                          </div>
                        </div>

                        <div className="bg-slate-50 border border-slate-200 rounded-xl p-4 text-center">
                          <div className="text-xs text-slate-500 font-bold uppercase">{t('soil_p')}</div>
                          <div className="text-2xl font-black text-emerald-700 mt-1 font-mono">
                            {liveSoilReading?.phosphorus !== null && liveSoilReading?.phosphorus !== undefined ? `${liveSoilReading.phosphorus} mg/kg` : '--'}
                          </div>
                        </div>

                        <div className="bg-slate-50 border border-slate-200 rounded-xl p-4 text-center">
                          <div className="text-xs text-slate-500 font-bold uppercase">{t('soil_k')}</div>
                          <div className="text-2xl font-black text-emerald-700 mt-1 font-mono">
                            {liveSoilReading?.potassium !== null && liveSoilReading?.potassium !== undefined ? `${liveSoilReading.potassium} mg/kg` : '--'}
                          </div>
                        </div>

                        <div className="bg-slate-50 border border-slate-200 rounded-xl p-4 text-center">
                          <div className="text-xs text-slate-500 font-bold uppercase">{t('soil_ph')}</div>
                          <div className="text-2xl font-black text-emerald-700 mt-1 font-mono">
                            {liveSoilReading?.ph !== null && liveSoilReading?.ph !== undefined ? `${liveSoilReading.ph} pH` : '--'}
                          </div>
                        </div>

                        <div className="bg-slate-50 border border-slate-200 rounded-xl p-4 text-center">
                          <div className="text-xs text-slate-500 font-bold uppercase">{t('soil_moisture')}</div>
                          <div className="text-2xl font-black text-emerald-700 mt-1 font-mono">
                            {liveSoilReading?.moisture !== null && liveSoilReading?.moisture !== undefined ? `${liveSoilReading.moisture}%` : '--'}
                          </div>
                        </div>

                        <div className="bg-slate-50 border border-slate-200 rounded-xl p-4 text-center">
                          <div className="text-xs text-slate-500 font-bold uppercase">{t('soil_temp')}</div>
                          <div className="text-2xl font-black text-emerald-700 mt-1 font-mono">
                            {liveSoilReading?.temperature !== null && liveSoilReading?.temperature !== undefined ? `${liveSoilReading.temperature}°C` : '--'}
                          </div>
                        </div>
                      </div>

                      {liveSoilReading?.is_mock && (
                        <div className="text-[11px] font-mono text-amber-800 bg-amber-50 p-2.5 rounded-lg border border-amber-200 font-medium">
                          Note: Simulated soil telemetry active in DEMO_MODE.
                        </div>
                      )}

                      <div className="flex justify-between items-center pt-3 border-t border-slate-200">
                        <button
                          onClick={() => setWizardStep(4)}
                          className="bg-slate-100 hover:bg-slate-200 text-slate-700 px-4 py-2 rounded-xl text-xs font-bold border border-slate-300"
                        >
                          {t('btn_back')}
                        </button>

                        <button
                          onClick={async () => {
                            await executeFusion();
                            setWizardStep(6);
                          }}
                          disabled={isFusing}
                          className="bg-emerald-600 hover:bg-emerald-500 text-white px-6 py-2.5 rounded-xl text-sm font-bold flex items-center space-x-2 shadow"
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
                    <div className="bg-white border border-slate-200 rounded-2xl p-6 space-y-4 shadow-sm">
                      <div className="space-y-1">
                        <h2 className="text-xl font-bold text-slate-900">{t('step_6_title')}</h2>
                        <p className="text-xs text-slate-500">{t('step_6_desc')}</p>
                      </div>

                      {/* Multimodal Risk Card */}
                      <div className="bg-slate-50 border border-slate-200 rounded-2xl p-5 space-y-3.5">
                        <div className="flex justify-between items-center">
                          <span className="text-xs text-slate-500 font-bold uppercase tracking-wider">OVERALL FIELD RISK LEVEL</span>
                          <span className={`px-3 py-1 rounded-lg text-xs font-black tracking-wider ${
                            fusionResult.risk.risk_level === 'CRITICAL' ? 'bg-rose-100 text-rose-800 border border-rose-300' :
                            fusionResult.risk.risk_level === 'HIGH' ? 'bg-rose-50 text-rose-700 border border-rose-200' :
                            fusionResult.risk.risk_level === 'MODERATE' ? 'bg-amber-100 text-amber-800 border border-amber-300' :
                            fusionResult.risk.risk_level === 'LOW' ? 'bg-emerald-100 text-emerald-800 border border-emerald-300' :
                            'bg-slate-100 text-slate-600 border border-slate-200'
                          }`}>
                            {fusionResult.risk.risk_level}
                          </span>
                        </div>

                        <p className="text-sm text-slate-800 font-medium leading-relaxed">{fusionResult.risk.explanation}</p>

                        <div className="grid grid-cols-3 gap-2 pt-3 border-t border-slate-200 text-xs font-mono">
                          <div>Disease: <b className="text-rose-600">{fusionResult.risk.disease_risk}</b></div>
                          <div>Soil Stress: <b className="text-amber-600">{fusionResult.risk.soil_stress}</b></div>
                          <div>Completeness: <b className="text-teal-700">{(fusionResult.risk.data_completeness * 100).toFixed(0)}%</b></div>
                        </div>
                      </div>

                      <div className="flex justify-between items-center pt-3 border-t border-slate-200">
                        <button
                          onClick={() => setWizardStep(5)}
                          className="bg-slate-100 hover:bg-slate-200 text-slate-700 px-4 py-2 rounded-xl text-xs font-bold border border-slate-300"
                        >
                          {t('btn_back')}
                        </button>

                        <button
                          onClick={() => setWizardStep(7)}
                          className="bg-emerald-600 hover:bg-emerald-500 text-white px-6 py-2.5 rounded-xl text-sm font-bold flex items-center space-x-2 shadow"
                        >
                          <span>View Farmer Advisories</span>
                          <ArrowRight className="w-4 h-4" />
                        </button>
                      </div>
                    </div>
                  )}

                  {/* WIZARD STEP 7: ACTIONABLE FARMER ADVISORY & PERSISTENCE */}
                  {wizardStep === 7 && fusionResult && (
                    <div className="bg-white border border-slate-200 rounded-2xl p-6 space-y-4 shadow-sm">
                      <div className="space-y-1">
                        <h2 className="text-xl font-bold text-slate-900">{t('step_7_title')}</h2>
                        <p className="text-xs text-slate-500">{t('step_7_desc')}</p>
                      </div>

                      <div className="space-y-3 max-h-72 overflow-y-auto pr-1">
                        {fusionResult.advisories.map((adv, idx) => (
                          <div key={idx} className="bg-slate-50 border border-slate-200 rounded-2xl p-4 space-y-2.5 shadow-sm">
                            <div className="flex justify-between items-center">
                              <span className={`px-2.5 py-0.5 rounded text-[10px] font-black tracking-wider ${
                                adv.priority === 'URGENT' ? 'bg-rose-100 text-rose-800 border border-rose-300' :
                                adv.priority === 'HIGH' ? 'bg-amber-100 text-amber-800 border border-amber-300' :
                                'bg-emerald-100 text-emerald-800 border border-emerald-300'
                              }`}>
                                {adv.priority} PRIORITY
                              </span>
                              <span className="text-xs font-bold text-slate-900">{adv.title}</span>
                            </div>
                            <div className="text-xs text-slate-700"><b>Observation:</b> {adv.message}</div>
                            <div className="bg-emerald-50 p-3 rounded-xl border border-emerald-200 text-xs text-emerald-950 font-medium">
                              <b>Action:</b> {adv.recommended_action}
                            </div>
                          </div>
                        ))}
                      </div>

                      <div className="flex justify-between items-center pt-3 border-t border-slate-200">
                        <button
                          onClick={() => setWizardStep(1)}
                          className="bg-slate-100 hover:bg-slate-200 text-slate-700 px-4 py-2 rounded-xl text-xs font-bold flex items-center space-x-1 border border-slate-300"
                        >
                          <RotateCcw className="w-4 h-4" />
                          <span>Start New Scan</span>
                        </button>

                        <button
                          onClick={() => {
                            setActiveTab('history');
                            if (selectedFieldId) loadHistory(selectedFieldId);
                          }}
                          className="bg-emerald-600 hover:bg-emerald-500 text-white px-6 py-2.5 rounded-xl text-sm font-bold flex items-center space-x-2 shadow"
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
                  <div className="flex justify-between items-center bg-white border border-slate-200 rounded-2xl p-4 shadow-sm">
                    <div>
                      <div className="font-bold text-sm text-slate-900">Registered Agricultural Fields</div>
                      <div className="text-xs text-slate-500">Total {fields.length} active plots in local SQLite</div>
                    </div>

                    <button
                      onClick={() => setShowAddFieldModal(true)}
                      className="bg-emerald-600 hover:bg-emerald-500 text-white px-4 py-2 rounded-xl text-xs font-bold flex items-center space-x-1.5 shadow"
                    >
                      <PlusCircle className="w-4 h-4" />
                      <span>{t('btn_add_field')}</span>
                    </button>
                  </div>

                  <div className="grid grid-cols-2 gap-4">
                    {fields.map(field => (
                      <div 
                        key={field.id}
                        className={`bg-white border rounded-2xl p-5 space-y-3 transition shadow-sm ${
                          selectedFieldId === field.id ? 'border-emerald-600 ring-2 ring-emerald-300' : 'border-slate-200'
                        }`}
                      >
                        <div className="flex justify-between items-start">
                          <div>
                            <div className="text-lg font-black text-slate-900">{field.name}</div>
                            <div className="text-xs text-slate-500 mt-0.5">Soil Type: <b className="text-slate-800">{field.soil_type || 'General'}</b></div>
                          </div>
                          <span className="text-xs font-mono text-emerald-800 bg-emerald-50 px-2.5 py-0.5 rounded-md border border-emerald-200 font-bold">
                            {field.area || 1.0} {field.area_unit}
                          </span>
                        </div>

                        <div className="pt-2 border-t border-slate-100 flex justify-between items-center">
                          <button
                            onClick={() => {
                              setSelectedFieldId(field.id);
                              setActiveTab('wizard');
                              setWizardStep(1);
                            }}
                            className="bg-emerald-600 hover:bg-emerald-500 text-white px-3.5 py-1.5 rounded-lg text-xs font-bold flex items-center space-x-1 shadow-sm"
                          >
                            <span>Start Field Check</span>
                            <ArrowRight className="w-3.5 h-3.5" />
                          </button>

                          <button
                            onClick={() => {
                              setSelectedFieldId(field.id);
                              setActiveTab('history');
                            }}
                            className="text-xs text-slate-500 hover:text-slate-900 font-medium"
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
                  <div className="bg-white border border-slate-200 rounded-2xl p-4 shadow-sm flex items-center justify-between">
                    <div className="flex items-center space-x-3">
                      <label className="text-xs font-bold text-slate-700">Target Field:</label>
                      <select 
                        value={selectedFieldId || ''} 
                        onChange={(e) => setSelectedFieldId(Number(e.target.value))}
                        className="bg-slate-50 border border-slate-300 rounded-lg px-3 py-1.5 text-xs text-slate-800 font-medium"
                      >
                        {fields.map(f => (
                          <option key={f.id} value={f.id}>{f.name} ({f.soil_type || 'General'})</option>
                        ))}
                      </select>
                    </div>

                    <div className="flex items-center space-x-2">
                      <label className="cursor-pointer bg-slate-100 hover:bg-slate-200 text-slate-700 px-3.5 py-1.5 rounded-lg text-xs font-bold flex items-center space-x-1.5 border border-slate-300">
                        <Upload className="w-3.5 h-3.5 text-slate-600" />
                        <span>Upload</span>
                        <input type="file" accept="image/*" className="hidden" onChange={handleFileSelect} />
                      </label>

                      <button
                        onClick={() => executeScan(true)}
                        disabled={isScanning || isPredictingDisease || isLoadingSample}
                        className="bg-emerald-600 hover:bg-emerald-500 text-white px-4 py-1.5 rounded-lg text-xs font-bold flex items-center space-x-1.5 shadow"
                      >
                        {isScanning ? <RefreshCw className="w-3.5 h-3.5 animate-spin" /> : <Camera className="w-3.5 h-3.5" />}
                        <span>Capture</span>
                      </button>

                      {selectedFile && (
                        <button
                          onClick={() => handlePredictDisease()}
                          disabled={isPredictingDisease || isLoadingSample}
                          className="bg-teal-600 hover:bg-teal-500 text-white px-3.5 py-1.5 rounded-lg text-xs font-bold flex items-center space-x-1.5 shadow"
                        >
                          {isPredictingDisease ? <RefreshCw className="w-3.5 h-3.5 animate-spin" /> : <Zap className="w-3.5 h-3.5" />}
                          <span>Classify (YOLO11n)</span>
                        </button>
                      )}
                    </div>
                  </div>

                  {/* One-Touch Sample Leaf Classifier Bar */}
                  <div className="bg-slate-50 border border-slate-200 rounded-2xl p-4 space-y-2.5">
                    <div className="flex items-center justify-between">
                      <div className="text-xs font-bold text-slate-800 flex items-center space-x-1.5">
                        <Zap className="w-4 h-4 text-amber-500 shrink-0" />
                        <span>One-Touch Sample Image Classification (Held-Out Test Set):</span>
                      </div>
                      <span className="text-[10px] font-mono font-bold text-emerald-800 bg-emerald-100 border border-emerald-300 px-2 py-0.5 rounded-md">
                        Offline YOLO11n ONNX
                      </span>
                    </div>

                    <div className="flex flex-wrap items-center gap-2">
                      {samplesList.slice(0, 5).map(s => (
                        <button
                          key={s.id}
                          type="button"
                          onClick={() => handleSelectSample(s, true)}
                          disabled={isLoadingSample || isPredictingDisease}
                          className={`px-3 py-1.5 rounded-lg text-xs font-bold transition border flex items-center space-x-1.5 ${
                            selectedSampleId === s.id
                              ? 'bg-emerald-600 text-white border-emerald-600 shadow-sm ring-2 ring-emerald-300'
                              : 'bg-white text-slate-700 border-slate-300 hover:bg-slate-100'
                          }`}
                        >
                          <span>{s.label}</span>
                        </button>
                      ))}

                      <select
                        value={selectedSampleId || ''}
                        onChange={(e) => {
                          const found = samplesList.find(x => x.id === e.target.value);
                          if (found) handleSelectSample(found, true);
                        }}
                        className="bg-white border border-slate-300 rounded-lg px-2.5 py-1.5 text-xs text-slate-700 font-medium ml-auto"
                      >
                        <option value="" disabled>More Disease Classes (10)...</option>
                        {samplesList.map(s => (
                          <option key={s.id} value={s.id}>{s.label}</option>
                        ))}
                      </select>
                    </div>
                  </div>

                  {diseasePredictError && (
                    <div className="bg-rose-50 border border-rose-200 text-rose-800 p-3 rounded-xl text-xs flex items-center space-x-2">
                      <AlertTriangle className="w-4 h-4 shrink-0 text-rose-600" />
                      <span>{diseasePredictError}</span>
                    </div>
                  )}

                  <div className="grid grid-cols-2 gap-4">
                    {/* Left: Viewfinder / Image Preview */}
                    <div className="bg-slate-900 border border-slate-800 rounded-2xl p-4 flex flex-col items-center justify-center min-h-[280px] text-slate-100">
                      {previewUrl ? (
                        <div className="relative w-full flex flex-col items-center">
                          <img src={previewUrl} alt="Scan preview" className="max-h-60 object-contain rounded-lg shadow-lg border border-slate-700/60" />
                          {diseasePrediction?.image && (
                            <div className="mt-2 text-[11px] font-mono text-slate-400 bg-slate-950 px-2.5 py-0.5 rounded border border-slate-800">
                              Input: {diseasePrediction.image.width} &times; {diseasePrediction.image.height} px
                            </div>
                          )}
                        </div>
                      ) : (
                        <div className="text-center text-slate-400 space-y-2">
                          <Camera className="w-10 h-10 mx-auto text-slate-500" />
                          <div className="text-xs font-bold text-slate-300">Live Viewfinder Preview</div>
                          <div className="text-[11px] text-slate-500">Upload or capture an image to classify</div>
                        </div>
                      )}
                    </div>

                    {/* Right: Disease Inference Output */}
                    {isPredictingDisease ? (
                      <div className="bg-white border border-slate-200 rounded-2xl p-6 flex flex-col items-center justify-center space-y-3 min-h-[280px] shadow-sm">
                        <RefreshCw className="w-8 h-8 text-emerald-600 animate-spin" />
                        <div className="text-sm font-bold text-slate-900">Running YOLO11n ONNX Inference...</div>
                        <div className="text-xs text-slate-500">Normalizing RGB (224&times;224) &bull; OpenCV DNN Engine</div>
                      </div>
                    ) : diseasePrediction ? (
                      <div className="bg-white border border-slate-200 rounded-2xl p-5 space-y-3.5 shadow-sm">
                        {/* Top Banner */}
                        <div className="flex justify-between items-center">
                          <div className="text-xs font-bold text-slate-500 uppercase tracking-wider">TEJAS AI PATHOLOGY DIAGNOSIS</div>
                          <div className="flex items-center space-x-1.5">
                            <span className="text-[10px] font-mono font-bold text-emerald-800 bg-emerald-100 px-2 py-0.5 rounded border border-emerald-300">
                              {diseasePrediction.model}
                            </span>
                            <span className="text-[10px] font-bold text-emerald-900 bg-emerald-50 px-2 py-0.5 rounded border border-emerald-200">
                              {(diseasePrediction.prediction.confidence * 100).toFixed(1)}% CONFIDENCE
                            </span>
                          </div>
                        </div>

                        {/* Top-1 Diagnosis */}
                        <div className="bg-slate-50 border border-slate-200 p-3.5 rounded-xl space-y-1">
                          <div className="text-[11px] font-mono text-slate-500 font-bold">PRIMARY PREDICTION (TOP-1)</div>
                          <div className="text-xl font-black text-emerald-800">
                            {diseasePrediction.prediction.class_name.replace(/_/g, ' ')}
                          </div>
                        </div>

                        {/* Top-3 Ranked Predictions */}
                        <div className="space-y-2 bg-slate-50 p-3.5 rounded-xl border border-slate-200">
                          <div className="text-[11px] font-mono text-slate-500 font-bold uppercase">TOP-3 RANKED CLASSES</div>
                          <div className="space-y-1.5">
                            {diseasePrediction.top_predictions.map((item, idx) => (
                              <div key={idx} className="space-y-0.5">
                                <div className="flex justify-between text-xs text-slate-700">
                                  <span className="font-semibold">#{idx + 1} {item.class_name.replace(/_/g, ' ')}</span>
                                  <b className="font-mono text-slate-900">{(item.confidence * 100).toFixed(1)}%</b>
                                </div>
                                <div className="w-full h-1.5 bg-slate-200 rounded-full overflow-hidden">
                                  <div 
                                    className={`h-full rounded-full transition-all duration-300 ${
                                      idx === 0 ? 'bg-emerald-600' : idx === 1 ? 'bg-teal-600' : 'bg-slate-400'
                                    }`} 
                                    style={{ width: `${Math.max(item.confidence * 100, 1)}%` }}
                                  ></div>
                                </div>
                              </div>
                            ))}
                          </div>
                        </div>

                        {/* Responsible AI Disclaimer */}
                        <div className="bg-amber-50 p-3 rounded-xl border border-amber-200 text-[11px] text-amber-900 space-y-1">
                          <div className="text-amber-800 font-bold flex items-center space-x-1">
                            <ShieldAlert className="w-3.5 h-3.5 shrink-0" />
                            <span>PlantVillage held-out test: 99.63% Top-1</span>
                          </div>
                          <div>
                            Prototype model trained on laboratory-style PlantVillage images; real field conditions may introduce domain shift. Decision-support only.
                          </div>
                        </div>
                      </div>
                    ) : scanResult ? (
                      <div className="bg-white border border-slate-200 rounded-2xl p-5 space-y-3.5 shadow-sm">
                        <div className="flex justify-between items-center">
                          <div className="text-xs font-bold text-slate-500 uppercase tracking-wider">DIAGNOSIS RESULT</div>
                          <div className="flex items-center space-x-1.5">
                            {scanResult.confidence_tier && (
                              <span className={`text-[10px] font-extrabold px-2 py-0.5 rounded ${
                                scanResult.confidence_tier === 'HIGH' ? 'bg-emerald-100 text-emerald-800 border border-emerald-300' :
                                scanResult.confidence_tier === 'MEDIUM' ? 'bg-amber-100 text-amber-800 border border-amber-300' :
                                'bg-rose-100 text-rose-800 border border-rose-300'
                              }`}>
                                {scanResult.confidence_tier} CONFIDENCE
                              </span>
                            )}
                            <span className="text-[10px] font-mono text-purple-700 bg-purple-50 px-2 py-0.5 rounded border border-purple-200">
                              {scanResult.inference_device} ({scanResult.inference_time_ms}ms)
                            </span>
                          </div>
                        </div>

                        <div className="text-2xl font-black text-slate-900">{scanResult.prediction}</div>

                        <div className="grid grid-cols-2 gap-2 text-xs font-mono bg-slate-50 p-3 rounded-xl border border-slate-200 text-slate-700">
                          <div>Model: <b className="text-slate-900">{scanResult.model_name} v{scanResult.model_version}</b></div>
                          <div>Hash: <b className="text-slate-900">{scanResult.model_hash ? scanResult.model_hash.substring(0, 8) : 'N/A'}</b></div>
                          <div>Validation: <b className="text-amber-700">{scanResult.is_validated ? 'VALIDATED' : 'NOT YET VALIDATED'}</b></div>
                          <div>Confidence: <b className="text-emerald-700">{(scanResult.confidence * 100).toFixed(1)}%</b></div>
                        </div>

                        <div className="bg-slate-50 p-3 rounded-xl border border-slate-200 text-xs text-slate-700 space-y-1">
                          <div className="font-bold text-slate-900">{scanResult.message}</div>
                          {scanResult.farmer_guidance && (
                            <div className="text-[11px] text-emerald-800">{scanResult.farmer_guidance}</div>
                          )}
                        </div>
                      </div>
                    ) : (
                      <div className="bg-white border border-slate-200 rounded-2xl p-6 text-center text-slate-400 flex items-center justify-center min-h-[280px] shadow-sm">
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
                  <div className="flex justify-between items-center bg-white border border-slate-200 rounded-2xl p-4 shadow-sm">
                    <div>
                      <div className="font-bold text-sm text-slate-900">6-Parameter Soil Sensor Module</div>
                      <div className="text-xs text-slate-500">RS485 Modbus-RTU Telemetry (Zero Hardware Hallucination)</div>
                    </div>

                    <button
                      onClick={() => selectedFieldId && triggerLiveSoil(selectedFieldId)}
                      disabled={isReadingSoil}
                      className="bg-teal-600 hover:bg-teal-500 disabled:bg-slate-300 disabled:text-slate-500 text-white px-4 py-2 rounded-xl text-xs font-bold flex items-center space-x-1.5 shadow"
                    >
                      <RefreshCw className={`w-3.5 h-3.5 ${isReadingSoil ? 'animate-spin' : ''}`} />
                      <span>Take Live Soil Reading</span>
                    </button>
                  </div>

                  <div className="grid grid-cols-3 gap-4">
                    <div className="bg-white border border-slate-200 rounded-2xl p-5 shadow-sm text-center">
                      <div className="text-xs text-slate-500 font-bold uppercase">{t('soil_n')}</div>
                      <div className="text-3xl font-black text-emerald-700 mt-2 font-mono">
                        {liveSoilReading?.nitrogen !== null && liveSoilReading?.nitrogen !== undefined ? `${liveSoilReading.nitrogen} mg/kg` : '--'}
                      </div>
                      <div className="text-[11px] text-slate-400 mt-1">
                        {liveSoilReading?.nitrogen !== null && liveSoilReading?.nitrogen !== undefined ? (deviceStatus?.demo_mode ? 'Simulated' : 'Live RS485') : 'Click "Take Live Soil Reading"'}
                      </div>
                    </div>

                    <div className="bg-white border border-slate-200 rounded-2xl p-5 shadow-sm text-center">
                      <div className="text-xs text-slate-500 font-bold uppercase">{t('soil_p')}</div>
                      <div className="text-3xl font-black text-emerald-700 mt-2 font-mono">
                        {liveSoilReading?.phosphorus !== null && liveSoilReading?.phosphorus !== undefined ? `${liveSoilReading.phosphorus} mg/kg` : '--'}
                      </div>
                      <div className="text-[11px] text-slate-400 mt-1">
                        {liveSoilReading?.phosphorus !== null && liveSoilReading?.phosphorus !== undefined ? (deviceStatus?.demo_mode ? 'Simulated' : 'Live RS485') : 'Click "Take Live Soil Reading"'}
                      </div>
                    </div>

                    <div className="bg-white border border-slate-200 rounded-2xl p-5 shadow-sm text-center">
                      <div className="text-xs text-slate-500 font-bold uppercase">{t('soil_k')}</div>
                      <div className="text-3xl font-black text-emerald-700 mt-2 font-mono">
                        {liveSoilReading?.potassium !== null && liveSoilReading?.potassium !== undefined ? `${liveSoilReading.potassium} mg/kg` : '--'}
                      </div>
                      <div className="text-[11px] text-slate-400 mt-1">
                        {liveSoilReading?.potassium !== null && liveSoilReading?.potassium !== undefined ? (deviceStatus?.demo_mode ? 'Simulated' : 'Live RS485') : 'Click "Take Live Soil Reading"'}
                      </div>
                    </div>

                    <div className="bg-white border border-slate-200 rounded-2xl p-5 shadow-sm text-center">
                      <div className="text-xs text-slate-500 font-bold uppercase">{t('soil_ph')}</div>
                      <div className="text-3xl font-black text-emerald-700 mt-2 font-mono">
                        {liveSoilReading?.ph !== null && liveSoilReading?.ph !== undefined ? `${liveSoilReading.ph} pH` : '--'}
                      </div>
                      <div className="text-[11px] text-slate-400 mt-1">
                        {liveSoilReading?.ph !== null && liveSoilReading?.ph !== undefined ? (deviceStatus?.demo_mode ? 'Simulated' : 'Live RS485') : 'Click "Take Live Soil Reading"'}
                      </div>
                    </div>

                    <div className="bg-white border border-slate-200 rounded-2xl p-5 shadow-sm text-center">
                      <div className="text-xs text-slate-500 font-bold uppercase">{t('soil_moisture')}</div>
                      <div className="text-3xl font-black text-emerald-700 mt-2 font-mono">
                        {liveSoilReading?.moisture !== null && liveSoilReading?.moisture !== undefined ? `${liveSoilReading.moisture}%` : '--'}
                      </div>
                      <div className="text-[11px] text-slate-400 mt-1">
                        {liveSoilReading?.moisture !== null && liveSoilReading?.moisture !== undefined ? (deviceStatus?.demo_mode ? 'Simulated' : 'Live RS485') : 'Click "Take Live Soil Reading"'}
                      </div>
                    </div>

                    <div className="bg-white border border-slate-200 rounded-2xl p-5 shadow-sm text-center">
                      <div className="text-xs text-slate-500 font-bold uppercase">{t('soil_temp')}</div>
                      <div className="text-3xl font-black text-emerald-700 mt-2 font-mono">
                        {liveSoilReading?.temperature !== null && liveSoilReading?.temperature !== undefined ? `${liveSoilReading.temperature}°C` : '--'}
                      </div>
                      <div className="text-[11px] text-slate-400 mt-1">
                        {liveSoilReading?.temperature !== null && liveSoilReading?.temperature !== undefined ? (deviceStatus?.demo_mode ? 'Simulated' : 'Live RS485') : 'Click "Take Live Soil Reading"'}
                      </div>
                    </div>
                  </div>
                </div>
              )}

              {/* ========================================================= */}
              {/* TAB 6: MULTI-MODAL RISK INTELLIGENCE                      */}
              {/* ========================================================= */}
              {activeTab === 'risk' && (
                <div className="space-y-4">
                  <div className="bg-white border border-slate-200 rounded-2xl p-4 shadow-sm flex items-center justify-between">
                    <div className="flex items-center space-x-3">
                      <label className="text-xs font-bold text-slate-700">Target Field:</label>
                      <select 
                        value={selectedFieldId || ''} 
                        onChange={(e) => setSelectedFieldId(Number(e.target.value))}
                        className="bg-slate-50 border border-slate-300 rounded-lg px-3 py-1.5 text-xs text-slate-800 font-medium"
                      >
                        {fields.map(f => (
                          <option key={f.id} value={f.id}>{f.name} ({f.soil_type || 'General'})</option>
                        ))}
                      </select>
                    </div>

                    <button
                      onClick={executeFusion}
                      disabled={isFusing}
                      className="bg-emerald-600 hover:bg-emerald-500 text-white px-4 py-2 rounded-xl text-xs font-bold flex items-center space-x-1.5 shadow"
                    >
                      {isFusing ? <RefreshCw className="w-3.5 h-3.5 animate-spin" /> : <Zap className="w-3.5 h-3.5" />}
                      <span>Run Multi-Modal Fusion</span>
                    </button>
                  </div>

                  {fusionResult ? (
                    <div className="grid grid-cols-3 gap-4">
                      <div className="bg-white border border-slate-200 rounded-2xl p-5 space-y-3.5 shadow-sm">
                        <div className="text-xs font-bold text-slate-500 uppercase tracking-wider">FIELD RISK LEVEL</div>
                        <div className="text-3xl font-black text-slate-900">{fusionResult.risk.risk_level}</div>
                        <p className="text-xs text-slate-600 leading-relaxed">{fusionResult.risk.explanation}</p>
                        <div className="pt-2 border-t border-slate-200 text-xs font-mono text-slate-700">
                          <div>Completeness: <b>{(fusionResult.risk.data_completeness * 100).toFixed(0)}%</b></div>
                        </div>
                      </div>

                      <div className="col-span-2 bg-white border border-slate-200 rounded-2xl p-4 space-y-2.5 max-h-72 overflow-y-auto pr-1 shadow-sm">
                        <div className="text-xs font-bold text-slate-700 uppercase tracking-wider">EXPLAINABLE RISK EVIDENCE</div>
                        {fusionResult.evidence.map((ev, idx) => (
                          <div key={idx} className="bg-slate-50 p-3 rounded-xl text-xs space-y-0.5 border border-slate-200">
                            <div className="flex justify-between items-center">
                              <span className="font-bold text-slate-900">{ev.title}</span>
                              <span className="text-[10px] font-mono text-slate-500 bg-white px-2 py-0.5 rounded border border-slate-200">{ev.source}</span>
                            </div>
                            <p className="text-slate-600 text-[11px] leading-relaxed">{ev.description}</p>
                          </div>
                        ))}
                      </div>
                    </div>
                  ) : (
                    <div className="bg-white border border-slate-200 rounded-2xl p-8 text-center text-slate-400 shadow-sm">
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
                  <div className="flex justify-between items-center bg-white border border-slate-200 rounded-2xl p-4 shadow-sm">
                    <div>
                      <div className="font-bold text-sm text-slate-900">Personalized Agronomic Advisories</div>
                      <div className="text-xs text-slate-500">Actionable, non-toxic recommendations for {selectedField?.name || 'Selected Field'}</div>
                    </div>

                    <button
                      onClick={() => selectedFieldId && loadAdvisories(selectedFieldId)}
                      disabled={isLoadingAdvisories}
                      className="bg-slate-100 hover:bg-slate-200 text-slate-700 px-3.5 py-1.5 rounded-xl text-xs font-bold flex items-center space-x-1 border border-slate-300"
                    >
                      <RefreshCw className={`w-3.5 h-3.5 ${isLoadingAdvisories ? 'animate-spin' : ''}`} />
                      <span>{t('btn_refresh')}</span>
                    </button>
                  </div>

                  {advisoryList.length > 0 ? (
                    <div className="space-y-3 max-h-96 overflow-y-auto pr-1">
                      {advisoryList.map((adv, idx) => (
                        <div key={idx} className="bg-white border border-slate-200 rounded-2xl p-4 space-y-2.5 shadow-sm">
                          <div className="flex justify-between items-center">
                            <span className={`px-2.5 py-0.5 rounded text-[10px] font-black tracking-wider ${
                              adv.priority === 'URGENT' ? 'bg-rose-100 text-rose-800 border border-rose-300' :
                              adv.priority === 'HIGH' ? 'bg-amber-100 text-amber-800 border border-amber-300' :
                              'bg-emerald-100 text-emerald-800 border border-emerald-300'
                            }`}>
                              {adv.priority} PRIORITY
                            </span>
                            <span className="text-xs font-bold text-slate-900">{adv.title}</span>
                          </div>
                          <div className="text-xs text-slate-700"><b>Observation:</b> {adv.message}</div>
                          <div className="bg-emerald-50 p-3 rounded-xl border border-emerald-200 text-xs text-emerald-950 font-medium">
                            <b>Recommended Action:</b> {adv.recommended_action}
                          </div>
                        </div>
                      ))}
                    </div>
                  ) : (
                    <div className="bg-white border border-slate-200 rounded-2xl p-8 text-center text-slate-400 shadow-sm">
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
                  <div className="flex justify-between items-center bg-white border border-slate-200 rounded-2xl p-3.5 shadow-sm">
                    <div className="flex items-center space-x-3">
                      <label className="text-xs font-bold text-slate-700">Target Field:</label>
                      <select 
                        value={selectedFieldId || ''} 
                        onChange={(e) => setSelectedFieldId(Number(e.target.value))}
                        className="bg-slate-50 border border-slate-300 rounded-lg px-3 py-1.5 text-xs text-slate-800 font-medium"
                      >
                        {fields.map(f => (
                          <option key={f.id} value={f.id}>{f.name}</option>
                        ))}
                      </select>
                    </div>

                    <div className="flex items-center space-x-2">
                      <div className="flex bg-slate-100 border border-slate-200 rounded-xl p-0.5 text-[11px] font-bold">
                        {(['ALL', 'SCAN', 'SOIL', 'RISK', 'ADVISORY'] as const).map(flt => (
                          <button
                            key={flt}
                            onClick={() => setHistoryFilter(flt)}
                            className={`px-2.5 py-1 rounded-lg transition ${
                              historyFilter === flt ? 'bg-emerald-600 text-white shadow-sm' : 'text-slate-600 hover:text-slate-900'
                            }`}
                          >
                            {flt}
                          </button>
                        ))}
                      </div>

                      <button
                        onClick={() => selectedFieldId && loadHistory(selectedFieldId)}
                        className="bg-slate-100 hover:bg-slate-200 text-slate-700 px-3.5 py-1.5 rounded-lg text-xs font-bold flex items-center space-x-1 border border-slate-300"
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
                        <div key={idx} className="bg-white border border-slate-200 rounded-xl p-3.5 flex items-center justify-between text-xs shadow-sm">
                          <div className="flex items-center space-x-3">
                            {item.type === 'SCAN' ? (
                              <div className="w-8 h-8 rounded-full bg-emerald-100 border border-emerald-300 flex items-center justify-center text-emerald-700">
                                <Camera className="w-4 h-4" />
                              </div>
                            ) : item.type === 'SOIL_READING' ? (
                              <div className="w-8 h-8 rounded-full bg-teal-100 border border-teal-300 flex items-center justify-center text-teal-700">
                                <Droplets className="w-4 h-4" />
                              </div>
                            ) : item.type === 'RISK_ASSESSMENT' ? (
                              <div className="w-8 h-8 rounded-full bg-purple-100 border border-purple-300 flex items-center justify-center text-purple-700">
                                <ShieldAlert className="w-4 h-4" />
                              </div>
                            ) : (
                              <div className="w-8 h-8 rounded-full bg-amber-100 border border-amber-300 flex items-center justify-center text-amber-700">
                                <FileText className="w-4 h-4" />
                              </div>
                            )}
                            <div>
                              <div className="font-bold text-slate-900">
                                {item.type === 'SCAN' ? `Crop Scan: ${item.prediction}` : 
                                 item.type === 'SOIL_READING' ? `Soil Reading (${item.sensor_status})` :
                                 item.type === 'RISK_ASSESSMENT' ? `Risk Assessment: ${item.disease_risk || 'CALCULATED'}` :
                                 `Advisory: ${item.title}`}
                              </div>
                              <div className="text-[11px] text-slate-500 flex items-center space-x-2 mt-0.5">
                                <Clock className="w-3 h-3" />
                                <span>{new Date(item.timestamp).toLocaleString()}</span>
                              </div>
                            </div>
                          </div>

                          <div className="text-right font-mono text-xs">
                            {item.type === 'SCAN' ? (
                              <span className="text-emerald-700 font-bold">{(item.confidence * 100).toFixed(0)}% Conf</span>
                            ) : item.type === 'SOIL_READING' ? (
                              <span className="text-teal-700 font-bold">{item.moisture !== null ? `${item.moisture}% Moist` : 'N/A'}</span>
                            ) : (
                              <span className="text-slate-600 font-medium">{item.severity || item.status || 'RECORDED'}</span>
                            )}
                          </div>
                        </div>
                      ))}
                    </div>
                  ) : (
                    <div className="p-8 text-center text-slate-400 border border-dashed border-slate-300 rounded-2xl text-xs bg-white">
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
                  <div className="bg-white border border-slate-200 rounded-2xl p-5 space-y-3 shadow-sm">
                    <div className="flex justify-between items-center">
                      <div className="text-sm font-bold text-slate-900">Host Platform & Architecture</div>
                      <span className="text-[11px] font-mono text-emerald-800 bg-emerald-50 px-2.5 py-0.5 rounded border border-emerald-200 font-bold">
                        {deviceStatus?.platform?.board_model || 'Edge Host'}
                      </span>
                    </div>
                    <div className="grid grid-cols-4 gap-3 text-xs font-mono text-slate-800">
                      <div className="bg-slate-50 p-3 rounded-xl border border-slate-200">
                        <div className="text-[10px] text-slate-500 uppercase font-sans font-bold">OS & Kernel</div>
                        <div className="font-bold text-slate-900 mt-0.5">{deviceStatus?.platform?.os_name} {deviceStatus?.platform?.architecture}</div>
                      </div>
                      <div className="bg-slate-50 p-3 rounded-xl border border-slate-200">
                        <div className="text-[10px] text-slate-500 uppercase font-sans font-bold">CPU Temperature</div>
                        <div className="font-bold text-amber-700 mt-0.5">
                          {deviceStatus?.cpu_temperature_celsius !== null && deviceStatus?.cpu_temperature_celsius !== undefined ? `${deviceStatus.cpu_temperature_celsius}°C` : 'Telemetry N/A'}
                        </div>
                      </div>
                      <div className="bg-slate-50 p-3 rounded-xl border border-slate-200">
                        <div className="text-[10px] text-slate-500 uppercase font-sans font-bold">Local Storage</div>
                        <div className="font-bold text-emerald-700 mt-0.5">{deviceStatus?.storage_free_gb || '--'} GB Free</div>
                      </div>
                      <div className="bg-slate-50 p-3 rounded-xl border border-slate-200">
                        <div className="text-[10px] text-slate-500 uppercase font-sans font-bold">Battery / PMIC</div>
                        <div className="font-bold text-slate-900 mt-0.5">
                          {deviceStatus?.battery?.percent !== null && deviceStatus?.battery?.percent !== undefined ? `${deviceStatus.battery.percent}%` : (deviceStatus?.demo_mode ? '88.5% (Demo)' : 'Unavailable')}
                        </div>
                      </div>
                    </div>
                  </div>

                  {/* Subsystems Matrix */}
                  <div className="bg-white border border-slate-200 rounded-2xl p-5 shadow-sm">
                    <div className="text-sm font-bold text-slate-900 mb-3">Subsystems Diagnostic Matrix</div>
                    <div className="grid grid-cols-2 gap-3 text-xs">
                      <div className="p-3.5 bg-slate-50 rounded-xl border border-slate-200 space-y-1">
                        <div className="font-bold text-slate-900 flex justify-between">
                          <span>Camera Subsystem</span>
                          <Camera className="w-4 h-4 text-slate-500" />
                        </div>
                        <div className="text-slate-600">Driver: {deviceStatus?.subsystems.camera.is_mock ? 'MockCamera (Demo)' : 'OpenCV / V4L2'}</div>
                        <div className="text-slate-600">Status: <b className={deviceStatus?.camera_status_label === 'READY' ? 'text-emerald-700' : 'text-amber-700'}>{deviceStatus?.subsystems.camera.status}</b></div>
                      </div>

                      <div className="p-3.5 bg-slate-50 rounded-xl border border-slate-200 space-y-1">
                        <div className="font-bold text-slate-900 flex justify-between">
                          <span>6-Param RS485 Modbus</span>
                          <Droplets className="w-4 h-4 text-teal-600" />
                        </div>
                        <div className="text-slate-600">Driver: {deviceStatus?.subsystems.soil_sensor.is_mock ? 'MockSoil (Demo)' : 'RS485 Serial'}</div>
                        <div className="text-slate-600">Status: <b className={deviceStatus?.soil_status_label === 'CONNECTED' ? 'text-emerald-700' : 'text-amber-700'}>{deviceStatus?.subsystems.soil_sensor.status}</b></div>
                      </div>

                      <div className="p-3.5 bg-slate-50 rounded-xl border border-slate-200 space-y-1">
                        <div className="font-bold text-slate-900 flex justify-between">
                          <span>AI Inference Engine</span>
                          <Cpu className="w-4 h-4 text-purple-600" />
                        </div>
                        <div className="text-slate-600">Accelerator: {visionStatus?.accelerator || 'CPU'}</div>
                        <div className="text-slate-600">Model: {visionStatus?.model_name || 'TEJAS-DemoVision'}</div>
                      </div>

                      <div className="p-3.5 bg-slate-50 rounded-xl border border-slate-200 space-y-1">
                        <div className="font-bold text-slate-900 flex justify-between">
                          <span>Offline SQLite Database</span>
                          <HistoryIcon className="w-4 h-4 text-emerald-600" />
                        </div>
                        <div className="text-slate-600">Engine: SQLAlchemy + SQLite PRAGMA FK</div>
                        <div className="text-slate-600">Status: <b className="text-emerald-700">{deviceStatus?.subsystems.database.status}</b></div>
                      </div>
                    </div>
                  </div>

                  {/* Detected Serial & RS485 Interfaces */}
                  <div className="bg-white border border-slate-200 rounded-2xl p-5 space-y-2.5 shadow-sm">
                    <div className="text-sm font-bold text-slate-900">Detected Serial & RS485 Interfaces</div>
                    {deviceStatus?.serial_ports && deviceStatus.serial_ports.length > 0 ? (
                      <div className="space-y-1.5 max-h-36 overflow-y-auto pr-1">
                        {deviceStatus.serial_ports.map((p, idx) => (
                          <div key={idx} className="bg-slate-50 border border-slate-200 p-2.5 rounded-xl flex justify-between items-center text-xs">
                            <div>
                              <span className="font-mono font-bold text-emerald-800">{p.device}</span>
                              <span className="text-slate-600 text-[11px] ml-2">{p.description}</span>
                            </div>
                            {p.is_usb_rs485_candidate && (
                              <span className="text-[10px] font-mono bg-teal-50 text-teal-800 px-2 py-0.5 rounded border border-teal-200 font-bold">
                                USB-RS485 Candidate
                              </span>
                            )}
                          </div>
                        ))}
                      </div>
                    ) : (
                      <div className="text-xs text-slate-500 p-3 bg-slate-50 border border-slate-200 rounded-xl">
                        No physical serial or USB-RS485 adapters currently attached.
                      </div>
                    )}
                  </div>

                  {/* Automated Startup Self-Test Panel */}
                  <div className="bg-white border border-slate-200 rounded-2xl p-5 space-y-3.5 shadow-sm">
                    <div className="flex justify-between items-center">
                      <div>
                        <div className="text-sm font-bold text-slate-900">Hardware & Subsystem Self-Test</div>
                        <div className="text-xs text-slate-500">Verifies local DB, storage, camera, soil probe, and AI engine</div>
                      </div>
                      <button
                        onClick={handleRunSelfTest}
                        disabled={isRunningSelfTest}
                        className="bg-purple-600 hover:bg-purple-500 disabled:bg-slate-300 disabled:text-slate-500 text-white px-4 py-2 rounded-xl text-xs font-bold flex items-center space-x-1.5 shadow"
                      >
                        {isRunningSelfTest ? <RefreshCw className="w-3.5 h-3.5 animate-spin" /> : <Activity className="w-3.5 h-3.5" />}
                        <span>{isRunningSelfTest ? 'Running Self-Test...' : 'Run Hardware Self-Test'}</span>
                      </button>
                    </div>

                    {selfTestResult && (
                      <div className="space-y-3 pt-3 border-t border-slate-200">
                        <div className="flex justify-between items-center bg-slate-50 p-3.5 rounded-xl border border-slate-200">
                          <span className="text-xs font-bold text-slate-700">OVERALL DEVICE STATUS:</span>
                          <span className={`px-3 py-1 rounded-lg text-xs font-black ${
                            selfTestResult.overall_status === 'DEVICE READY' ? 'bg-emerald-100 text-emerald-800 border border-emerald-300' :
                            selfTestResult.overall_status === 'DEVICE READY WITH WARNINGS' ? 'bg-amber-100 text-amber-800 border border-amber-300' :
                            'bg-rose-100 text-rose-800 border border-rose-300'
                          }`}>
                            {selfTestResult.overall_status}
                          </span>
                        </div>

                        <div className="grid grid-cols-2 gap-2 text-xs">
                          {selfTestResult.items.map((item, idx) => (
                            <div key={idx} className="bg-slate-50 border border-slate-200 p-3 rounded-xl space-y-1">
                              <div className="flex justify-between items-center">
                                <span className="font-bold text-slate-900">{item.subsystem}</span>
                                <span className={`text-[10px] font-black px-2 py-0.5 rounded ${
                                  item.status === 'PASSED' ? 'bg-emerald-100 text-emerald-800' :
                                  item.status === 'WARNING' ? 'bg-amber-100 text-amber-800' :
                                  'bg-rose-100 text-rose-800'
                                }`}>
                                  {item.status} {item.latency_ms !== null && item.latency_ms !== undefined ? `(${item.latency_ms}ms)` : ''}
                                </span>
                              </div>
                              <p className="text-[11px] text-slate-600">{item.message}</p>
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
                  <div className="bg-white border border-slate-200 rounded-2xl p-5 space-y-3.5 shadow-sm">
                    <div className="flex justify-between items-center">
                      <div>
                        <div className="text-sm font-bold text-slate-900">AI Model Registry & Validation Status</div>
                        <div className="text-xs text-slate-500">Zero AI Hallucination: Model hashes verified via SHA-256</div>
                      </div>
                      <span className={`text-[10px] font-black px-2.5 py-1 rounded border ${
                        modelRegistry?.active_model?.validation_status === 'VALIDATED' 
                          ? 'bg-emerald-100 text-emerald-800 border-emerald-300' 
                          : 'bg-amber-100 text-amber-800 border-amber-300'
                      }`}>
                        {modelRegistry?.active_model?.validation_status || 'NOT YET VALIDATED'}
                      </span>
                    </div>

                    <div className="grid grid-cols-2 gap-3 text-xs">
                      <div className="bg-slate-50 border border-slate-200 p-3.5 rounded-xl space-y-1.5 font-mono text-slate-800">
                        <div className="text-[10px] text-slate-500 uppercase font-sans font-bold">Active Model Details</div>
                        <div>Name: <b className="text-slate-900">{modelRegistry?.active_model?.model_name || visionStatus?.model_name || 'DemoVision'}</b></div>
                        <div>Version: <b className="text-slate-900">{modelRegistry?.active_model?.model_version || '0.1.0'}</b></div>
                        <div>Status: <b className="text-teal-700">{modelRegistry?.active_model?.model_status || 'DEMO_MODEL'}</b></div>
                        <div className="truncate text-[11px]">SHA-256: <b className="text-purple-700">{modelRegistry?.active_model?.model_hash || 'demo_hash'}</b></div>
                      </div>

                      <div className="bg-slate-50 border border-slate-200 p-3.5 rounded-xl space-y-1.5 font-mono text-slate-800">
                        <div className="text-[10px] text-slate-500 uppercase font-sans font-bold">Latency Profiling (Monotonic)</div>
                        <div>Avg Inference: <b className="text-emerald-700">{visionStatus?.profiling_summary?.avg_inference_ms !== null && visionStatus?.profiling_summary?.avg_inference_ms !== undefined ? `${visionStatus.profiling_summary.avg_inference_ms} ms` : 'N/A'}</b></div>
                        <div>Avg Total Pipeline: <b className="text-teal-700">{visionStatus?.profiling_summary?.avg_total_ms !== null && visionStatus?.profiling_summary?.avg_total_ms !== undefined ? `${visionStatus.profiling_summary.avg_total_ms} ms` : 'N/A'}</b></div>
                        <div>Measured Inferences: <b className="text-slate-900">{visionStatus?.profiling_summary?.total_inferences_measured || 0}</b></div>
                        <div>Accelerator: <b className="text-purple-700">{visionStatus?.accelerator || 'CPU'}</b></div>
                      </div>
                    </div>
                  </div>
                </div>
              )}

              {/* ========================================================= */}
              {/* TAB 10: SETTINGS                                          */}
              {/* ========================================================= */}
              {activeTab === 'settings' && (
                <div className="bg-white border border-slate-200 rounded-2xl p-6 text-xs space-y-3.5 shadow-sm">
                  <div className="font-bold text-slate-900 text-sm">System Runtime Settings</div>
                  <div className="space-y-2 text-slate-700 font-mono">
                    <div>Operation Mode: <b className="text-amber-700">{deviceStatus?.demo_mode ? 'DEMO_MODE=true' : 'REAL HARDWARE'}</b></div>
                    <div>Confidence Threshold: <b className="text-emerald-700">{((visionStatus?.confidence_threshold || 0.70) * 100).toFixed(0)}%</b></div>
                    <div>Zero Hardware Hallucination: <b className="text-emerald-700">ENFORCED (Strict Nullability)</b></div>
                    <div>Database: <b className="text-slate-500">SQLite Local Storage (Offline)</b></div>
                  </div>
                </div>
              )}
            </div>
          </div>

          {/* Touch-First Rugged Footer */}
          <div className="pt-3.5 border-t border-slate-200 flex justify-between items-center text-[11px] text-slate-500 shrink-0">
            <div>TEJAS &bull; Smart India Hackathon 2026 Prototype</div>
            <div>Offline Edge System &bull; Version 1.0.0</div>
          </div>
        </section>
      </main>

      {/* ------------------------------------------------------------- */}
      {/* ADD FIELD MODAL DIALOG                                        */}
      {/* ------------------------------------------------------------- */}
      {showAddFieldModal && (
        <div className="fixed inset-0 bg-slate-950/70 backdrop-blur-sm z-50 flex items-center justify-center p-4">
          <div className="bg-white border border-slate-200 rounded-2xl p-6 w-full max-w-md shadow-2xl space-y-4 text-slate-800">
            <div className="flex justify-between items-center">
              <h3 className="text-lg font-bold text-slate-900">{t('btn_add_field')}</h3>
              <button onClick={() => setShowAddFieldModal(false)} className="text-slate-400 hover:text-slate-600">
                <XCircle className="w-5 h-5" />
              </button>
            </div>

            <form onSubmit={handleCreateField} className="space-y-3.5">
              <div>
                <label className="block text-xs font-bold text-slate-700 mb-1">Field / Plot Name:</label>
                <input 
                  type="text" 
                  required
                  placeholder="e.g. North Tomato Sector"
                  value={newFieldName}
                  onChange={(e) => setNewFieldName(e.target.value)}
                  className="w-full bg-slate-50 border border-slate-300 rounded-xl px-3.5 py-2 text-xs text-slate-900 focus:outline-none focus:border-emerald-500 focus:ring-1 focus:ring-emerald-500"
                />
              </div>

              <div>
                <label className="block text-xs font-bold text-slate-700 mb-1">Soil Type:</label>
                <select 
                  value={newFieldSoilType}
                  onChange={(e) => setNewFieldSoilType(e.target.value)}
                  className="w-full bg-slate-50 border border-slate-300 rounded-xl px-3.5 py-2 text-xs text-slate-900 focus:outline-none focus:border-emerald-500 focus:ring-1 focus:ring-emerald-500"
                >
                  <option value="Black Cotton">Black Cotton Soil (Regur)</option>
                  <option value="Loamy">Loamy Soil</option>
                  <option value="Red Soil">Red Soil</option>
                  <option value="Alluvial">Alluvial Soil</option>
                  <option value="Clay">Clay Soil</option>
                </select>
              </div>

              <div>
                <label className="block text-xs font-bold text-slate-700 mb-1">Area (Acres):</label>
                <input 
                  type="number" 
                  step="0.1"
                  min="0.1"
                  value={newFieldArea}
                  onChange={(e) => setNewFieldArea(e.target.value)}
                  className="w-full bg-slate-50 border border-slate-300 rounded-xl px-3.5 py-2 text-xs text-slate-900 focus:outline-none focus:border-emerald-500 focus:ring-1 focus:ring-emerald-500"
                />
              </div>

              <div className="flex justify-end space-x-2.5 pt-2 border-t border-slate-100">
                <button 
                  type="button"
                  onClick={() => setShowAddFieldModal(false)}
                  className="px-4 py-2 rounded-xl text-xs font-bold text-slate-600 hover:bg-slate-100"
                >
                  Cancel
                </button>

                <button 
                  type="submit"
                  disabled={isCreatingField || !newFieldName.trim()}
                  className="bg-emerald-600 hover:bg-emerald-500 text-white px-5 py-2 rounded-xl text-xs font-bold flex items-center space-x-1.5 shadow"
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
