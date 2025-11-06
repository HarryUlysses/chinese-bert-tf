#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
中文文本分类API客户端示例
"""

import requests
import json

class TextClassificationClient:
    """文本分类API客户端"""

    def __init__(self, base_url="http://localhost:8000"):
        self.base_url = base_url

    def health_check(self):
        """健康检查"""
        try:
            response = requests.get(f"{self.base_url}/health")
            return response.json()
        except Exception as e:
            return {"error": str(e)}

    def get_service_info(self):
        """获取服务信息"""
        try:
            response = requests.get(f"{self.base_url}/info")
            return response.json()
        except Exception as e:
            return {"error": str(e)}

    def predict_text(self, text):
        """单文本预测"""
        try:
            response = requests.post(
                f"{self.base_url}/predict",
                json={"text": text}
            )
            response.raise_for_status()
            return response.json()
        except Exception as e:
            return {"error": str(e)}

    def predict_batch(self, texts):
        """批量预测"""
        try:
            response = requests.post(
                f"{self.base_url}/predict/batch",
                json={"texts": texts}
            )
            response.raise_for_status()
            return response.json()
        except Exception as e:
            return {"error": str(e)}

def main():
    """使用示例"""
    # 创建客户端
    client = TextClassificationClient("http://localhost:8000")

    print("=== 中文文本分类API客户端测试 ===")
    print()

    # 1. 健康检查
    print("1. 健康检查")
    health = client.health_check()
    print(f"服务状态: {health}")
    print()

    # 2. 获取服务信息
    print("2. 服务信息")
    info = client.get_service_info()
    if 'error' not in info:
        print(f"服务版本: {info['service_info']['version']}")
        print(f"模型状态: {info['model_info']['status']}")
        if info['model_info']['status'] == 'loaded':
            print(f"支持类别: {info['model_info']['classes']}")
    else:
        print(f"获取信息失败: {info}")
    print()

    # 3. 单文本预测
    print("3. 单文本预测")
    test_texts = [
        "今天天气很好，适合出门散步",
        "人工智能技术发展很快",
        "我喜欢运动，保持健康的生活方式"
    ]

    for text in test_texts:
        result = client.predict_text(text)
        if 'error' not in result:
            print(f"文本: {text}")
            print(f"预测: {result['predicted_class']} (置信度: {result['confidence']:.3f})")
            print(f"处理时间: {result['processing_time']:.3f}s")
            print("-" * 50)
        else:
            print(f"预测失败: {result}")
    print()

    # 4. 批量预测
    print("4. 批量预测")
    batch_result = client.predict_batch(test_texts)
    if 'error' not in batch_result:
        print(f"批量预测完成，处理 {batch_result['total_texts']} 个文本")
        print(f"总处理时间: {batch_result['processing_time']:.3f}s")
        for i, result in enumerate(batch_result['results']):
            print(f"  {i+1}. {result['text']} -> {result['predicted_class']} ({result['confidence']:.3f})")
    else:
        print(f"批量预测失败: {batch_result}")

if __name__ == "__main__":
    main()