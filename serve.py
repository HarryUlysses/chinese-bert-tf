#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
模型服务启动脚本
"""

import os
import sys
import subprocess
from pathlib import Path

def main():
    """启动API服务"""

    print("中文文本分类模型服务")
    print("=" * 50)

    # 检查模型是否存在
    model_registry = Path("models/registry")
    if not model_registry.exists():
        print("模型目录不存在，请先训练模型")
        print("运行命令: python src/models/trainer.py")
        sys.exit(1)

    registry_file = model_registry / "registry.json"
    if not registry_file.exists():
        print("模型注册表不存在，请先训练模型")
        print("运行命令: python src/models/trainer.py")
        sys.exit(1)

    print("模型文件检查通过")

    # 设置环境变量
    os.environ["PYTHONPATH"] = str(Path(__file__).parent)

    # 启动API服务
    try:
        print("启动API服务...")
        subprocess.run([
            sys.executable, "-m", "uvicorn",
            "src.api.main:app",
            "--host", "0.0.0.0",
            "--port", "8000",
            "--reload"
        ], check=True)
    except KeyboardInterrupt:
        print("\n服务已停止")
    except subprocess.CalledProcessError as e:
        print(f"服务启动失败: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()