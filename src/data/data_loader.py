#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
生产级数据加载器
"""

import pandas as pd
import numpy as np
import json
import sqlite3
import logging
from typing import List, Dict, Any, Optional, Tuple
from pathlib import Path
from abc import ABC, abstractmethod
import requests
from datetime import datetime
import asyncio
import aiohttp

logger = logging.getLogger(__name__)

class DataSource(ABC):
    """数据源抽象基类"""

    @abstractmethod
    def load(self) -> pd.DataFrame:
        pass

class CSVDataSource(DataSource):
    """CSV文件数据源"""

    def __init__(self, file_path: str, encoding: str = 'utf-8'):
        self.file_path = Path(file_path)
        self.encoding = encoding

    def load(self) -> pd.DataFrame:
        try:
            df = pd.read_csv(self.file_path, encoding=self.encoding)
            logger.info(f"✅ 加载CSV数据: {self.file_path}, 形状: {df.shape}")
            return df
        except Exception as e:
            logger.error(f"❌ 加载CSV失败: {e}")
            raise

class JSONDataSource(DataSource):
    """JSON文件数据源"""

    def __init__(self, file_path: str):
        self.file_path = Path(file_path)

    def load(self) -> pd.DataFrame:
        try:
            with open(self.file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)

            df = pd.DataFrame(data)
            logger.info(f"✅ 加载JSON数据: {self.file_path}, 形状: {df.shape}")
            return df
        except Exception as e:
            logger.error(f"❌ 加载JSON失败: {e}")
            raise

class DatabaseDataSource(DataSource):
    """数据库数据源"""

    def __init__(self, connection_string: str, query: str):
        self.connection_string = connection_string
        self.query = query

    def load(self) -> pd.DataFrame:
        try:
            conn = sqlite3.connect(self.connection_string)
            df = pd.read_sql_query(self.query, conn)
            conn.close()
            logger.info(f"✅ 加载数据库数据, 形状: {df.shape}")
            return df
        except Exception as e:
            logger.error(f"❌ 加载数据库失败: {e}")
            raise

class APIDataSource(DataSource):
    """API数据源"""

    def __init__(self, url: str, headers: Optional[Dict] = None):
        self.url = url
        self.headers = headers or {}

    def load(self) -> pd.DataFrame:
        try:
            response = requests.get(self.url, headers=self.headers)
            response.raise_for_status()

            data = response.json()
            df = pd.DataFrame(data)
            logger.info(f"✅ 加载API数据: {self.url}, 形状: {df.shape}")
            return df
        except Exception as e:
            logger.error(f"❌ 加载API数据失败: {e}")
            raise

class DataVersionControl:
    """数据版本控制"""

    def __init__(self, registry_path: str = "data/registry"):
        self.registry_path = Path(registry_path)
        self.registry_path.mkdir(parents=True, exist_ok=True)
        self.registry_file = self.registry_path / "data_registry.json"

    def register_data(self, data_source: str, version: str, metadata: Dict):
        """注册数据版本"""
        registry = self._load_registry()

        registry[data_source] = {
            'version': version,
            'timestamp': datetime.now().isoformat(),
            'metadata': metadata
        }

        with open(self.registry_file, 'w', encoding='utf-8') as f:
            json.dump(registry, f, indent=2, ensure_ascii=False)

        logger.info(f"✅ 注册数据版本: {data_source} v{version}")

    def _load_registry(self) -> Dict:
        """加载注册表"""
        if self.registry_file.exists():
            with open(self.registry_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        return {}

class DataLoader:
    """生产级数据加载器"""

    def __init__(self, config: Optional[Dict] = None):
        self.config = config or {}
        self.version_control = DataVersionControl()

    def load_data(self, sources: List[Dict[str, Any]]) -> pd.DataFrame:
        """
        加载多个数据源并合并

        Args:
            sources: 数据源配置列表
                [
                    {
                        'type': 'csv',
                        'path': 'data/raw/train.csv',
                        'version': '1.0.0'
                    },
                    {
                        'type': 'json',
                        'path': 'data/raw/labels.json',
                        'version': '1.0.0'
                    }
                ]
        """
        dataframes = []

        for source_config in sources:
            try:
                # 创建数据源
                data_source = self._create_data_source(source_config)

                # 加载数据
                df = data_source.load()

                # 添加元数据
                df['data_source'] = source_config.get('name', 'unknown')
                df['data_version'] = source_config.get('version', '1.0.0')
                df['load_timestamp'] = datetime.now().isoformat()

                dataframes.append(df)

                # 注册数据版本
                self.version_control.register_data(
                    source_config.get('name', 'unknown'),
                    source_config.get('version', '1.0.0'),
                    {
                        'source_type': source_config['type'],
                        'path': source_config.get('path', ''),
                        'shape': df.shape,
                        'columns': list(df.columns)
                    }
                )

            except Exception as e:
                logger.error(f"❌ 加载数据源失败: {source_config}, 错误: {e}")
                continue

        if not dataframes:
            raise ValueError("没有成功加载任何数据源")

        # 合并所有数据
        if len(dataframes) == 1:
            result_df = dataframes[0]
        else:
            result_df = pd.concat(dataframes, ignore_index=True)

        logger.info(f"✅ 数据加载完成, 最终形状: {result_df.shape}")
        return result_df

    def _create_data_source(self, source_config: Dict) -> DataSource:
        """根据配置创建数据源"""
        source_type = source_config['type'].lower()

        if source_type == 'csv':
            return CSVDataSource(
                source_config['path'],
                source_config.get('encoding', 'utf-8')
            )
        elif source_type == 'json':
            return JSONDataSource(source_config['path'])
        elif source_type == 'database':
            return DatabaseDataSource(
                source_config['connection_string'],
                source_config['query']
            )
        elif source_type == 'api':
            return APIDataSource(
                source_config['url'],
                source_config.get('headers')
            )
        else:
            raise ValueError(f"不支持的数据源类型: {source_type}")

    def validate_data(self, df: pd.DataFrame, required_columns: List[str]) -> bool:
        """验证数据质量"""
        # 检查必需列
        missing_columns = set(required_columns) - set(df.columns)
        if missing_columns:
            logger.error(f"❌ 缺少必需列: {missing_columns}")
            return False

        # 检查数据量
        if len(df) == 0:
            logger.error("❌ 数据为空")
            return False

        # 检查空值
        null_counts = df[required_columns].isnull().sum()
        high_null_columns = null_counts[null_counts > len(df) * 0.1]

        if not high_null_columns.empty:
            logger.warning(f"⚠️ 高空值率列: {high_null_columns.to_dict()}")

        logger.info("✅ 数据验证通过")
        return True

# 使用示例
if __name__ == "__main__":
    # 配置数据源
    data_sources = [
        {
            'name': 'training_data',
            'type': 'csv',
            'path': 'data/raw/training_data.csv',
            'version': '1.0.0'
        },
        {
            'name': 'labels',
            'type': 'json',
            'path': 'data/raw/labels.json',
            'version': '1.0.0'
        }
    ]

    # 加载数据
    loader = DataLoader()
    data = loader.load_data(data_sources)

    # 验证数据
    loader.validate_data(data, ['text', 'label'])

    print(f"数据形状: {data.shape}")
    print(f"列名: {list(data.columns)}")