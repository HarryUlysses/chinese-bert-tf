#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
生产级模型训练器
"""

import tensorflow as tf
import numpy as np
import json
import os
import logging
from typing import Dict, Any, Optional, Tuple, List
from pathlib import Path
from datetime import datetime
import mlflow
import mlflow.tensorflow
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder
import pickle
import yaml

logger = logging.getLogger(__name__)

class ModelTrainer:
    """生产级模型训练器"""

    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.model = None
        self.label_encoder = LabelEncoder()
        self.vectorize_layer = None
        self.training_history = None

        # 创建必要目录
        self.checkpoint_dir = Path(config['checkpoint_dir'])
        self.model_registry_path = Path(config['model_registry_path'])

        self.checkpoint_dir.mkdir(parents=True, exist_ok=True)
        self.model_registry_path.mkdir(parents=True, exist_ok=True)

    def build_model(self, vocab_size: int, num_classes: int) -> tf.keras.Model:
        """构建模型架构"""
        model = tf.keras.Sequential([
            tf.keras.layers.Input(shape=(self.config['max_sequence_length'],)),
            tf.keras.layers.Embedding(vocab_size, 128, input_length=self.config['max_sequence_length']),
            tf.keras.layers.Bidirectional(tf.keras.layers.LSTM(64, return_sequences=True)),
            tf.keras.layers.GlobalAveragePooling1D(),
            tf.keras.layers.Dense(256, activation='relu'),
            tf.keras.layers.Dropout(0.3),
            tf.keras.layers.Dense(128, activation='relu'),
            tf.keras.layers.Dropout(0.2),
            tf.keras.layers.Dense(64, activation='relu'),
            tf.keras.layers.Dropout(0.1),
            tf.keras.layers.Dense(num_classes, activation='softmax')
        ])

        return model

    def prepare_data(self, texts: List[str], labels: List[str]) -> Tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
        """准备训练数据"""
        logger.info("🔄 准备训练数据...")

        # 编码标签
        labels_encoded = self.label_encoder.fit_transform(labels)

        # 数据分割
        train_texts, val_texts, train_labels, val_labels = train_test_split(
            texts, labels_encoded,
            test_size=0.3,
            random_state=42,
            stratify=labels_encoded
        )

        logger.info(f"训练样本: {len(train_texts)}, 验证样本: {len(val_texts)}")

        # 创建文本向量化层
        self.vectorize_layer = tf.keras.layers.TextVectorization(
            max_tokens=self.config.get('vocab_size', 10000),
            output_mode='int',
            output_sequence_length=self.config['max_sequence_length']
        )

        # 适配文本数据
        self.vectorize_layer.adapt(train_texts)

        # 向量化文本
        X_train = self.vectorize_layer(train_texts)
        X_val = self.vectorize_layer(val_texts)

        logger.info(f"词汇表大小: {len(self.vectorize_layer.get_vocabulary())}")

        return X_train, X_val, np.array(train_labels), np.array(val_labels)

    def train(self, texts: List[str], labels: List[str]) -> Dict[str, Any]:
        """训练模型"""
        logger.info("🚀 开始模型训练...")

        # 设置MLflow实验
        mlflow.set_experiment("chinese-text-classification")

        with mlflow.start_run() as run:
            # 记录参数
            mlflow.log_params(self.config)

            # 准备数据
            X_train, X_val, y_train, y_val = self.prepare_data(texts, labels)

            # 构建模型
            vocab_size = len(self.vectorize_layer.get_vocabulary())
            num_classes = len(np.unique(y_train))

            self.model = self.build_model(vocab_size, num_classes)

            # 编译模型
            self.model.compile(
                optimizer=tf.keras.optimizers.Adam(learning_rate=self.config['learning_rate']),
                loss='sparse_categorical_crossentropy',
                metrics=['accuracy']
            )

            # 回调函数
            callbacks = [
                tf.keras.callbacks.EarlyStopping(
                    patience=5,
                    restore_best_weights=True,
                    monitor='val_accuracy'
                ),
                tf.keras.callbacks.ReduceLROnPlateau(
                    factor=0.1,
                    patience=3,
                    monitor='val_loss'
                ),
                tf.keras.callbacks.ModelCheckpoint(
                    filepath=str(self.checkpoint_dir / 'best_model.h5'),
                    save_best_only=True,
                    monitor='val_accuracy',
                    save_weights_only=False
                ),
                mlflow.tensorflow.MlflowCallback()
            ]

            # 训练模型
            logger.info("📈 开始训练...")
            self.training_history = self.model.fit(
                X_train, y_train,
                validation_data=(X_val, y_val),
                epochs=self.config['epochs'],
                batch_size=self.config['batch_size'],
                callbacks=callbacks,
                verbose=1
            )

            # 评估模型
            val_loss, val_accuracy = self.model.evaluate(X_val, y_val, verbose=0)
            logger.info(f"✅ 训练完成 - 验证准确率: {val_accuracy:.4f}")

            # 记录指标
            mlflow.log_metrics({
                'val_accuracy': val_accuracy,
                'val_loss': val_loss,
                'vocab_size': vocab_size,
                'num_classes': num_classes
            })

            # 保存模型
            model_info = self.save_model(val_accuracy, num_classes, vocab_size)

            # 记录模型文件（确保文件存在后再记录）
            model_info_file = Path(model_info['model_path']) / 'model_info.json'
            if model_info_file.exists():
                mlflow.log_artifact(str(model_info_file))

            return model_info

    def save_model(self, val_accuracy: float, num_classes: int, vocab_size: int) -> Dict[str, Any]:
        """保存模型和相关信息"""
        # 生成模型版本
        model_version = f"v{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        model_path = self.model_registry_path / model_version

        # 创建模型目录（如果不存在）
        model_path.mkdir(parents=True, exist_ok=True)

        # 保存TensorFlow模型为Keras格式
        model_file_path = model_path / 'model.keras'
        self.model.save(str(model_file_path))

        # 保存预处理组件
        with open(model_path / 'label_encoder.pkl', 'wb') as f:
            pickle.dump(self.label_encoder, f)

        # 保存向量化层配置
        vectorize_config = {
            'max_tokens': getattr(self.vectorize_layer, 'max_tokens', None) or self.config.get('vocab_size', 10000),
            'output_mode': getattr(self.vectorize_layer, 'output_mode', 'int'),
            'output_sequence_length': getattr(self.vectorize_layer, 'output_sequence_length', self.config['max_sequence_length']),
            'vocabulary': self.vectorize_layer.get_vocabulary()
        }

        with open(model_path / 'vectorize_config.json', 'w', encoding='utf-8') as f:
            json.dump(vectorize_config, f, ensure_ascii=False, indent=2)

        # 保存训练历史
        if self.training_history:
            history_data = {k: [float(x) for x in v] for k, v in self.training_history.history.items()}
            with open(model_path / 'training_history.json', 'w') as f:
                json.dump(history_data, f, indent=2)

        # 保存模型信息
        model_info = {
            'model_version': model_version,
            'model_type': 'chinese_text_classifier',
            'framework': 'tensorflow',
            'val_accuracy': float(val_accuracy),
            'vocab_size': vocab_size,
            'num_classes': num_classes,
            'classes': self.label_encoder.classes_.tolist(),
            'max_sequence_length': self.config['max_sequence_length'],
            'training_config': self.config,
            'created_at': datetime.now().isoformat(),
            'model_path': str(model_path),
            'status': 'active'
        }

        with open(model_path / 'model_info.json', 'w', encoding='utf-8') as f:
            json.dump(model_info, f, ensure_ascii=False, indent=2)

        # 更新模型注册表
        self._update_model_registry(model_info)

        logger.info(f"✅ 模型已保存: {model_path}")
        return model_info

    def _update_model_registry(self, model_info: Dict[str, Any]):
        """更新模型注册表"""
        registry_file = self.model_registry_path / 'registry.json'

        if registry_file.exists():
            with open(registry_file, 'r', encoding='utf-8') as f:
                registry = json.load(f)
        else:
            registry = {'models': [], 'latest': None}

        registry['models'].append(model_info)
        registry['latest'] = model_info['model_version']

        # 按准确率排序
        registry['models'].sort(key=lambda x: x['val_accuracy'], reverse=True)

        with open(registry_file, 'w', encoding='utf-8') as f:
            json.dump(registry, f, ensure_ascii=False, indent=2)

        logger.info(f"✅ 模型注册表已更新: {model_info['model_version']}")

    def load_best_model(self) -> tf.keras.Model:
        """加载最佳模型"""
        registry_file = self.model_registry_path / 'registry.json'

        if not registry_file.exists():
            raise FileNotFoundError("模型注册表不存在")

        with open(registry_file, 'r', encoding='utf-8') as f:
            registry = json.load(f)

        if not registry['models']:
            raise ValueError("没有可用的模型")

        # 加载最佳模型
        best_model_info = registry['models'][0]
        model_path = Path(best_model_info['model_path'])
        model_file_path = model_path / 'model.keras'

        self.model = tf.keras.models.load_model(str(model_file_path))

        # 加载预处理组件
        with open(Path(best_model_info['model_path']) / 'label_encoder.pkl', 'rb') as f:
            self.label_encoder = pickle.load(f)

        logger.info(f"✅ 加载最佳模型: {best_model_info['model_version']}")
        return self.model

# 使用示例
if __name__ == "__main__":
    # 训练配置
    config = {
        'name': 'chinese-text-classifier',
        'version': '1.0.0',
        'batch_size': 32,
        'max_sequence_length': 128,
        'learning_rate': 0.001,
        'epochs': 10,
        'checkpoint_dir': 'models/checkpoints',
        'model_registry_path': 'models/registry',
        'vocab_size': 10000
    }

    # 示例数据 - 30个样本，每个类别10个
    texts = [
        # 天气类 (10个)
        "今天天气很好", "明天会下雨", "天气晴朗", "刮风了", "气温适宜",
        "可能要下雨", "阳光明媚", "乌云密布", "温差很大", "空气质量不错",

        # 科技类 (10个)
        "机器学习很有趣", "深度学习很棒", "人工智能发展", "大数据分析", "云计算技术",
        "区块链应用", "量子计算", "神经网络", "算法优化", "数据挖掘",

        # 生活类 (10个)
        "我喜欢运动", "健康很重要", "早睡早起", "均衡饮食", "定期体检",
        "锻炼身体", "保持好心情", "工作生活平衡", "充足睡眠", "营养搭配"
    ]
    labels = [
        # 天气类标签 (10个)
        "天气", "天气", "天气", "天气", "天气", "天气", "天气", "天气", "天气", "天气",

        # 科技类标签 (10个)
        "科技", "科技", "科技", "科技", "科技", "科技", "科技", "科技", "科技", "科技",

        # 生活类标签 (10个)
        "生活", "生活", "生活", "生活", "生活", "生活", "生活", "生活", "生活", "生活"
    ]

    # 训练模型
    trainer = ModelTrainer(config)
    model_info = trainer.train(texts, labels)

    print(f"训练完成: {model_info['model_version']}")
    print(f"验证准确率: {model_info['val_accuracy']:.4f}")