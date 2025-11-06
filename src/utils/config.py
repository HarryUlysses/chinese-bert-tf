#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
简化配置管理
"""

import os
from typing import Dict, Any
from dataclasses import dataclass

@dataclass
class APIConfig:
    host: str = "0.0.0.0"
    port: int = 8000
    workers: int = 1
    reload: bool = False
    log_level: str = "info"
    cors_origins: list = None

    def __post_init__(self):
        if self.cors_origins is None:
            self.cors_origins = ["*"]

@dataclass
class ModelConfig:
    name: str = "chinese-text-classifier"
    version: str = "1.0.0"
    batch_size: int = 32
    max_sequence_length: int = 128
    learning_rate: float = 0.001
    epochs: int = 10
    checkpoint_dir: str = "models/checkpoints"
    model_registry_path: str = "models/registry"

class Config:
    def __init__(self):
        self.env = os.getenv("ENVIRONMENT", "development")
        self.api = APIConfig()
        self.model = ModelConfig()
        self._load_from_env()

    def _load_from_env(self):
        """从环境变量加载配置"""
        self.api.host = os.getenv("API_HOST", self.api.host)
        self.api.port = int(os.getenv("API_PORT", str(self.api.port)))
        self.api.workers = int(os.getenv("API_WORKERS", str(self.api.workers)))
        self.api.reload = os.getenv("API_RELOAD", "false").lower() == "true"
        self.api.log_level = os.getenv("LOG_LEVEL", self.api.log_level)

        self.model.batch_size = int(os.getenv("MODEL_BATCH_SIZE", str(self.model.batch_size)))
        self.model.learning_rate = float(os.getenv("MODEL_LEARNING_RATE", str(self.model.learning_rate)))
        self.model.epochs = int(os.getenv("MODEL_EPOCHS", str(self.model.epochs)))

# 全局配置实例
config = Config()

def get_config() -> Config:
    """获取配置实例"""
    return config