#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
模型预测器
"""

import tensorflow as tf
import numpy as np
import pickle
import json
import logging
from pathlib import Path
from typing import Dict, Any, List, Tuple
import time

logger = logging.getLogger(__name__)

class ModelPredictor:
    """模型预测器"""

    def __init__(self, model_registry_path: str = "models/registry"):
        self.model_registry_path = Path(model_registry_path)
        self.model = None
        self.label_encoder = None
        self.vectorize_config = None
        self.vectorize_layer = None
        self.loaded = False

    def load_best_model(self) -> bool:
        """加载最佳模型"""
        try:
            registry_file = self.model_registry_path / 'registry.json'

            if not registry_file.exists():
                logger.error("模型注册表不存在")
                return False

            with open(registry_file, 'r', encoding='utf-8') as f:
                registry = json.load(f)

            if not registry['models']:
                logger.error("没有可用的模型")
                return False

            # 加载最佳模型（按准确率排序的第一个）
            best_model_info = registry['models'][0]
            return self._load_model_from_info(best_model_info)

        except Exception as e:
            logger.error(f"加载最佳模型失败: {e}")
            return False

    def _create_vectorize_layer(self):
        """创建文本向量化层"""
        self.vectorize_layer = tf.keras.layers.TextVectorization(
            max_tokens=self.vectorize_config['max_tokens'],
            output_mode=self.vectorize_config['output_mode'],
            output_sequence_length=self.vectorize_config['output_sequence_length'],
            vocabulary=self.vectorize_config['vocabulary']
        )

    def predict(self, text: str) -> Dict[str, Any]:
        """单个文本预测"""
        if not self.loaded:
            raise RuntimeError("模型未加载，请先调用 load_best_model()")

        start_time = time.time()

        try:
            # 向量化文本
            vectorized_text = self.vectorize_layer([text])

            # 模型预测
            predictions = self.model.predict(vectorized_text, verbose=0)

            # 处理预测结果
            predicted_class_idx = np.argmax(predictions[0])
            predicted_class = self.label_encoder.inverse_transform([predicted_class_idx])[0]
            confidence = float(predictions[0][predicted_class_idx])

            # 所有类别的概率
            class_probabilities = {}
            for i, class_name in enumerate(self.label_encoder.classes_):
                class_probabilities[class_name] = float(predictions[0][i])

            processing_time = time.time() - start_time

            return {
                "text": text,
                "predicted_class": predicted_class,
                "confidence": confidence,
                "class_probabilities": class_probabilities,
                "processing_time": processing_time
            }

        except Exception as e:
            logger.error(f"预测失败: {e}")
            raise RuntimeError(f"预测失败: {str(e)}")

    def predict_batch(self, texts: List[str]) -> Dict[str, Any]:
        """批量文本预测"""
        if not self.loaded:
            raise RuntimeError("模型未加载，请先调用 load_best_model()")

        start_time = time.time()

        try:
            # 向量化文本
            vectorized_texts = self.vectorize_layer(texts)

            # 批量预测
            predictions = self.model.predict(vectorized_texts, verbose=0)

            # 处理预测结果
            results = []
            for i, text in enumerate(texts):
                predicted_class_idx = np.argmax(predictions[i])
                predicted_class = self.label_encoder.inverse_transform([predicted_class_idx])[0]
                confidence = float(predictions[i][predicted_class_idx])

                # 所有类别的概率
                class_probabilities = {}
                for j, class_name in enumerate(self.label_encoder.classes_):
                    class_probabilities[class_name] = float(predictions[i][j])

                results.append({
                    "text": text,
                    "predicted_class": predicted_class,
                    "confidence": confidence,
                    "class_probabilities": class_probabilities
                })

            processing_time = time.time() - start_time

            return {
                "results": results,
                "total_texts": len(texts),
                "processing_time": processing_time
            }

        except Exception as e:
            logger.error(f"批量预测失败: {e}")
            raise RuntimeError(f"批量预测失败: {str(e)}")

    def get_model_info(self) -> Dict[str, Any]:
        """获取模型信息"""
        if not self.loaded:
            return {"status": "not_loaded"}

        return {
            "status": "loaded",
            "classes": self.label_encoder.classes_.tolist(),
            "num_classes": len(self.label_encoder.classes_),
            "vocab_size": self.vectorize_config['max_tokens'],
            "max_sequence_length": self.vectorize_config['output_sequence_length']
        }

    def load_model_by_version(self, model_version: str) -> bool:
        """根据版本号加载指定模型"""
        try:
            registry_file = self.model_registry_path / 'registry.json'

            if not registry_file.exists():
                logger.error("模型注册表不存在")
                return False

            with open(registry_file, 'r', encoding='utf-8') as f:
                registry = json.load(f)

            # 查找指定版本的模型
            target_model = None
            for model_info in registry['models']:
                if model_info['model_version'] == model_version:
                    target_model = model_info
                    break

            if not target_model:
                logger.error(f"模型版本 {model_version} 不存在")
                return False

            # 加载指定模型
            return self._load_model_from_info(target_model)

        except Exception as e:
            logger.error(f"加载模型版本 {model_version} 失败: {e}")
            return False

    def _load_model_from_info(self, model_info: Dict[str, Any]) -> bool:
        """从模型信息加载模型"""
        try:
            # 标准化路径格式，确保使用正斜杠
            model_path_str = model_info['model_path'].replace('\\', '/')
            model_path = Path(model_path_str)
            logger.info(f"加载模型: {model_info['model_version']}")

            # 加载Keras模型
            model_file = model_path / 'model.keras'
            if not model_file.exists():
                logger.error(f"模型文件不存在: {model_file}")
                return False

            self.model = tf.keras.models.load_model(str(model_file))

            # 加载标签编码器
            label_encoder_file = model_path / 'label_encoder.pkl'
            with open(label_encoder_file, 'rb') as f:
                self.label_encoder = pickle.load(f)

            # 加载向量化配置
            vectorize_config_file = model_path / 'vectorize_config.json'
            with open(vectorize_config_file, 'r', encoding='utf-8') as f:
                self.vectorize_config = json.load(f)

            # 创建向量化层
            self._create_vectorize_layer()

            self.loaded = True
            logger.info(f"模型加载成功 - 类别: {self.label_encoder.classes_.tolist()}")
            return True

        except Exception as e:
            logger.error(f"模型加载失败: {e}")
            return False

    def get_available_models(self) -> List[Dict[str, Any]]:
        """获取所有可用模型列表"""
        try:
            registry_file = self.model_registry_path / 'registry.json'

            if not registry_file.exists():
                return []

            with open(registry_file, 'r', encoding='utf-8') as f:
                registry = json.load(f)

            return registry['models']

        except Exception as e:
            logger.error(f"获取模型列表失败: {e}")
            return []

    def unload_model(self):
        """卸载当前模型"""
        if self.loaded:
            self.model = None
            self.label_encoder = None
            self.vectorize_config = None
            self.vectorize_layer = None
            self.loaded = False
            logger.info("模型已卸载")