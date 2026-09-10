"""
Application Configuration Module for KrishiDrishti Edge.
Centralized settings management via Pydantic BaseSettings.
"""
from typing import List, Optional
from pydantic import Field, AliasChoices
from pydantic_settings import BaseSettings, SettingsConfigDict
import os

class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )

    # Core Application Settings
    PROJECT_NAME: str = "TEJAS"
    VERSION: str = "1.0.0-sih-prototype"
    TAGLINE: str = "Technology Enabled Judicious Agriculture And soil sensor"
    APP_ENV: str = "development"
    DEBUG: bool = True
    DEMO_MODE: bool = True  # Strict gating: True enables mock telemetry; False enforces real hardware

    # Server Configuration
    HOST: str = Field(default="0.0.0.0", validation_alias=AliasChoices("HOST", "API_HOST"))
    PORT: int = Field(default=8000, validation_alias=AliasChoices("PORT", "API_PORT"))
    FRONTEND_PORT: int = 5173

    # AI Inference & Gating Settings
    AI_MODE: str = Field(default="auto", validation_alias=AliasChoices("AI_MODE", "AI_ACCELERATOR"))  # 'auto', 'hailo', 'cpu'
    MODEL_PATH: str = "data/models/tejas_tomato_yolo11n.onnx"
    AI_CONFIDENCE_THRESHOLD: float = Field(default=0.70, validation_alias=AliasChoices("AI_CONFIDENCE_THRESHOLD", "CONFIDENCE_THRESHOLD"))
    MIN_IMAGE_QUALITY_SCORE: float = 0.60

    # Hardware Camera Settings
    CAMERA_DEVICE: int = Field(default=0, validation_alias=AliasChoices("CAMERA_DEVICE", "CAMERA_INDEX"))
    CAMERA_WIDTH: int = 1920
    CAMERA_HEIGHT: int = 1080
    CAMERA_FPS: int = 30

    # Hardware Serial & RS485 Modbus Settings
    SOIL_SENSOR_PORT: str = "COM3" if os.name == "nt" else "/dev/ttyUSB0"
    SOIL_SENSOR_BAUDRATE: int = 4800
    SOIL_SENSOR_SLAVE_ID: int = 1
    SOIL_SENSOR_TIMEOUT: float = 2.0
    SOIL_SENSOR_CONFIG: str = Field(default="hardware/sensor_protocol/soil_sensor.yaml", validation_alias=AliasChoices("SOIL_SENSOR_CONFIG", "SOIL_SENSOR_CONFIG_FILE"))

    # Logging
    LOG_LEVEL: str = "INFO"

    # Storage & Persistence
    DATA_DIR: str = "./data"
    DATABASE_PATH: str = "./data/krishidrishti.db"
    DATABASE_URL: str = "sqlite:///./data/krishidrishti.db"
    IMAGE_STORAGE_DIR: str = "./data/captures"

    # Localization
    DEFAULT_LANGUAGE: str = "en"  # "en", "hi", "mr"

    # Security & CORS
    CORS_ORIGINS: List[str] = [
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "http://localhost:8000"
    ]
    SECRET_KEY: str = "krishidrishti-local-edge-secret-key-change-in-production"

settings = Settings()
