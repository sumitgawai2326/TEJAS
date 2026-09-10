import axios from 'axios';

const api = axios.create({
  baseURL: '/api',
  timeout: 10000,
});

export interface SubsystemStatus {
  status: string;
  details: string | null;
  last_check: string;
  is_mock: boolean;
}

export interface PlatformInfo {
  board_model: string;
  is_raspberry_pi: boolean;
  rpi_version: string | null;
  os_name: string;
  os_release: string;
  os_version: string;
  architecture: string;
  python_version: string;
  hostname: string;
}

export interface SerialPortInfo {
  device: string;
  description: string;
  hardware_id: string;
  is_usb_rs485_candidate: boolean;
}

export interface DeviceStatus {
  status: string;
  app_version: string;
  app_name: string;
  demo_mode: boolean;
  mode_label: string;
  ai_status_label: string;
  soil_status_label: string;
  camera_status_label: string;
  uptime_seconds: number;
  cpu_temperature_celsius: number | null;
  cpu_usage_percent: number;
  ram_usage_percent: number;
  storage_usage_percent: number;
  storage_free_gb?: number;
  battery: {
    percent: number | null;
    power_plugged: boolean | null;
    status: string;
    is_mock: boolean;
    note?: string;
  };
  subsystems: {
    camera: SubsystemStatus;
    soil_sensor: SubsystemStatus;
    ai_engine: SubsystemStatus;
    database: SubsystemStatus;
  };
  platform?: PlatformInfo;
  serial_ports?: SerialPortInfo[];
}

export interface CameraStatus {
  driver: string;
  mode: string;
  available: boolean;
  status: string;
  is_mock: boolean;
  camera_device_index: number;
  resolution: string | null;
  fps: number | null;
  details: string | null;
  last_check: string;
}

export interface SoilStatus {
  driver: string;
  mode: string;
  connected: boolean;
  status: string;
  is_mock: boolean;
  port: string;
  baudrate: number;
  details: string | null;
  last_check: string;
}

export interface AIStatus {
  driver: string;
  mode: string;
  ready: boolean;
  status: string;
  accelerator_type: string;
  inference_mode: string;
  is_mock: boolean;
  model_name: string;
  model_version: string;
  details: string | null;
}

export interface HealthResponse {
  status: string;
  project: string;
  version: string;
  demo_mode: boolean;
  ai_mode: string;
  timestamp: string;
}

export interface SelfTestItem {
  subsystem: string;
  status: 'PASSED' | 'WARNING' | 'FAILED';
  critical: boolean;
  message: string;
  details?: string | null;
  latency_ms?: number | null;
}

export interface SelfTestResponse {
  overall_status: 'DEVICE READY' | 'DEVICE READY WITH WARNINGS' | 'DEVICE INITIALIZATION FAILED';
  passed_count: number;
  warning_count: number;
  failed_count: number;
  items: SelfTestItem[];
  timestamp: string;
  demo_mode: boolean;
}

export interface DeviceCapabilities {
  project_name: string;
  version: string;
  camera_available: boolean;
  soil_sensor_available: boolean;
  soil_sensor_register_configured: boolean;
  ai_accelerator_available: boolean;
  ai_accelerator_type: string;
  ai_inference_mode: string;
  ai_status_label: string;
  offline_capable: boolean;
  demo_mode: boolean;
  supported_crops: string[];
  supported_languages: string[];
  soil_sensor_parameters: string[];
  platform_info?: PlatformInfo;
}

export const fetchHealth = async (): Promise<HealthResponse> => (await api.get('/health')).data;
export const fetchDeviceStatus = async (): Promise<DeviceStatus> => (await api.get('/device/status')).data;
export const fetchDeviceCapabilities = async (): Promise<DeviceCapabilities> => (await api.get('/device/capabilities')).data;
export const fetchCameraStatus = async (): Promise<CameraStatus> => (await api.get('/subsystems/camera')).data;
export const fetchSoilStatus = async (): Promise<SoilStatus> => (await api.get('/subsystems/soil')).data;
export const fetchAIStatus = async (): Promise<AIStatus> => (await api.get('/subsystems/ai')).data;
export const fetchDeviceSelfTest = async (): Promise<SelfTestResponse> => (await api.get('/device/self-test')).data;

// Phase 3 Relational DB Types & APIs
export interface FarmModel {
  id: number;
  name: string;
  owner_name: string;
  location: string | null;
  created_at: string;
}

export interface FieldModel {
  id: number;
  farm_id: number;
  name: string;
  area: number | null;
  area_unit: string;
  soil_type: string | null;
  created_at: string;
}

export interface SoilReadingModel {
  id: number;
  field_id: number;
  timestamp: string;
  nitrogen: number | null;
  phosphorus: number | null;
  potassium: number | null;
  ph: number | null;
  moisture: number | null;
  temperature: number | null;
  is_mock: boolean;
  sensor_status: string;
  error_message: string | null;
}

export interface TimelineEventModel {
  type: 'SCAN' | 'SOIL_READING' | 'RISK_ASSESSMENT' | 'ADVISORY';
  id: number;
  timestamp: string;
  [key: string]: any;
}

export interface FieldHistoryModel {
  field_id: number;
  field_name: string;
  total_events: number;
  timeline: TimelineEventModel[];
}

export const fetchFarms = async (): Promise<FarmModel[]> => (await api.get('/farms')).data;
export const fetchFields = async (): Promise<FieldModel[]> => (await api.get('/fields')).data;
export const createField = async (data: { farm_id?: number; name: string; area?: number; soil_type?: string }): Promise<FieldModel> => {
  return (await api.post('/fields', { farm_id: data.farm_id || 1, ...data })).data;
};

export const fetchFieldHistory = async (fieldId: number): Promise<FieldHistoryModel> => {
  return (await api.get(`/fields/${fieldId}/history`)).data;
};

export const recordSoilReading = async (fieldId: number): Promise<SoilReadingModel> => {
  return (await api.post(`/fields/${fieldId}/soil-readings`)).data;
};

export const fetchFieldSoilReadings = async (fieldId: number): Promise<SoilReadingModel[]> => {
  return (await api.get(`/fields/${fieldId}/soil-readings`)).data;
};

export interface ImageQualityResult {
  passed: boolean;
  blur_score: number;
  brightness_score: number;
  resolution: string;
  error_reason?: string | null;
  farmer_instruction?: string | null;
  is_mock: boolean;
}

export interface ModelInfo {
  model_id: string;
  model_name: string;
  model_version: string;
  filename: string;
  model_hash: string;
  size_bytes: number;
  classes: string[];
  input_shape: number[];
  input_type: string;
  is_demo: boolean;
  model_status: 'REAL_MODEL' | 'DEMO_MODEL' | 'MODEL_MISSING' | 'CORRUPTED';
  validation_status: string;
  evaluation_summary?: {
    validation_status: string;
    dataset_name: string;
    total_samples: number;
    accuracy: number | null;
    macro_f1: number | null;
  };
}

export interface ModelRegistryResponse {
  total_models: number;
  active_model: ModelInfo;
  models: ModelInfo[];
  registry_status: string;
}

export interface VisionAnalysisResponse {
  scan_id?: number | null;
  status: 'accepted' | 'low_confidence' | 'rejected_quality' | 'ai_unavailable' | 'camera_unavailable' | 'error';
  prediction: string;
  confidence: number;
  confidence_tier?: 'HIGH' | 'MEDIUM' | 'LOW';
  crop: string;
  severity: string;
  inference_time_ms: number;
  inference_device: string;
  model_name: string;
  model_version: string;
  model_hash?: string | null;
  is_validated?: boolean;
  image_quality: ImageQualityResult;
  is_demo: boolean;
  message: string;
  farmer_guidance?: string;
  captured_at: string;
}

export interface VisionStatusResponse {
  ready: boolean;
  model_available: boolean;
  model_name: string;
  model_version: string;
  model_hash?: string | null;
  model_status?: string;
  accelerator: string;
  inference_mode: string;
  cpu_fallback_available: boolean;
  confidence_threshold: number;
  high_confidence_threshold?: number;
  demo_mode: boolean;
  validation_status?: string;
  reason_if_unavailable?: string | null;
  supported_classes: string[];
  profiling_summary?: {
    total_inferences_measured: number;
    avg_inference_ms: number | null;
    min_inference_ms?: number | null;
    max_inference_ms?: number | null;
    avg_total_ms: number | null;
    status: string;
  };
}

// Phase 5 Multi-Modal Fusion & Agronomic Risk Types
export interface SoilDataQuality {
  status: 'COMPLETE' | 'PARTIAL' | 'UNAVAILABLE' | 'MOCK';
  measured_parameters_count: number;
  total_parameters_count: number;
  completeness_ratio: number;
  is_mock: boolean;
  notes: string;
}

export interface EvidenceItem {
  category: string;
  source: string;
  title: string;
  description: string;
  severity: 'INFO' | 'LOW' | 'MEDIUM' | 'HIGH' | 'CRITICAL';
  score_impact: number;
  is_mock: boolean;
}

export interface RiskAssessmentResult {
  risk_level: 'LOW' | 'MODERATE' | 'HIGH' | 'CRITICAL' | 'UNKNOWN';
  disease_risk: string;
  soil_stress: string;
  water_stress: string;
  pest_risk: string;
  overall_score: number | null;
  confidence: number;
  data_completeness: number;
  explanation: string;
  is_prototype_heuristic: boolean;
}

export interface FarmerAdvisoryItem {
  advisory_id: string;
  priority: 'INFO' | 'LOW' | 'MEDIUM' | 'HIGH' | 'URGENT';
  title: string;
  message: string;
  recommended_action: string;
  reason: string;
  source: string;
  confidence: number;
  localization_key: string;
  is_demo: boolean;
  category: string;
}

export interface FieldAnalysisResponse {
  field: FieldModel;
  vision?: Record<string, any>;
  soil?: Record<string, any>;
  history?: Record<string, any>;
  risk: RiskAssessmentResult;
  evidence: EvidenceItem[];
  advisories: FarmerAdvisoryItem[];
  data_quality: SoilDataQuality;
  is_demo: boolean;
  generated_at: string;
}

// Phase 4 Vision Pipeline API Calls
export const analyzeCropImage = async (formData: FormData): Promise<VisionAnalysisResponse> => {
  const response = await api.post('/vision/analyze', formData, {
    headers: { 'Content-Type': 'multipart/form-data' }
  });
  return response.data;
};

export const fetchVisionStatus = async (): Promise<VisionStatusResponse> => (await api.get('/vision/status')).data;
export const fetchRegisteredModels = async (): Promise<ModelRegistryResponse> => (await api.get('/vision/models')).data;

// Phase 5 Fusion & Advisory API Calls
export const analyzeField = async (fieldId: number, formData?: FormData): Promise<FieldAnalysisResponse> => {
  const response = await api.post(`/fields/${fieldId}/analyze`, formData || {}, {
    headers: formData ? { 'Content-Type': 'multipart/form-data' } : undefined
  });
  return response.data;
};

export const fetchLatestRisk = async (fieldId: number): Promise<any> => (await api.get(`/fields/${fieldId}/risk/latest`)).data;
export const fetchRiskHistory = async (fieldId: number): Promise<any[]> => (await api.get(`/fields/${fieldId}/risk/history`)).data;
export const fetchFieldAdvisories = async (fieldId: number, language?: string): Promise<any[]> => {
  const params = language ? { language } : {};
  return (await api.get(`/fields/${fieldId}/advisories`, { params })).data;
};

// Phase 10 Real Disease Inference Types
export interface ClassPrediction {
  class_name: string;
  confidence: number;
}

export interface ImageDimension {
  width: number;
  height: number;
}

export interface DiseasePredictResponse {
  success: boolean;
  model: string;
  prediction: ClassPrediction;
  top_predictions: ClassPrediction[];
  image: ImageDimension;
}

// Phase 10 Tomato Disease Inference API Call
export const predictDisease = async (formData: FormData): Promise<DiseasePredictResponse> => {
  const response = await api.post('/v1/disease/predict', formData, {
    headers: { 'Content-Type': 'multipart/form-data' }
  });
  return response.data;
};

export default api;
