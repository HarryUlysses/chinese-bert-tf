#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
中文文本分类FastAPI服务
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import logging
import sys
import os
import uvicorn
from datetime import datetime
from typing import Dict, Any, List
from .predictor import ModelPredictor

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# 创建FastAPI应用
app = FastAPI(
    title="Chinese Text Classification API",
    description="中文文本分类服务",
    version="2.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# 添加CORS中间件
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 全局状态
startup_time = datetime.now()
predictor = ModelPredictor()

@app.get("/")
async def root():
    """根端点"""
    uptime = (datetime.now() - startup_time).total_seconds()

    return {
        "service": "Chinese Text Classification API",
        "version": "2.0.0",
        "status": "running",
        "uptime_seconds": uptime,
        "timestamp": datetime.now().isoformat(),
        "endpoints": {
            "health": "/health",
            "docs": "/docs",
            "predict": "/predict"
        }
    }

@app.get("/health")
async def health_check():
    """健康检查"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "uptime_seconds": (datetime.now() - startup_time).total_seconds()
    }

@app.post("/predict")
async def predict_text(request: Dict[str, str]):
    """文本预测接口"""
    try:
        if not predictor.loaded:
            raise HTTPException(status_code=503, detail="模型未加载，请稍后再试")

        if "text" not in request:
            raise HTTPException(status_code=400, detail="缺少text字段")

        text = request["text"]

        # 使用真实模型预测
        result = predictor.predict(text)

        return result

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"预测失败: {e}")
        raise HTTPException(status_code=500, detail=f"预测失败: {str(e)}")

@app.post("/predict/batch")
async def predict_batch(request: Dict[str, List[str]]):
    """批量预测接口"""
    try:
        if not predictor.loaded:
            raise HTTPException(status_code=503, detail="模型未加载，请稍后再试")

        if "texts" not in request:
            raise HTTPException(status_code=400, detail="缺少texts字段")

        texts = request["texts"]

        if len(texts) > 100:
            raise HTTPException(status_code=400, detail="批量预测最多支持100个文本")

        # 使用真实模型批量预测
        result = predictor.predict_batch(texts)
        result["timestamp"] = datetime.now().isoformat()

        return result

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"批量预测失败: {e}")
        raise HTTPException(status_code=500, detail=f"批量预测失败: {str(e)}")

@app.get("/info")
async def get_info():
    """获取服务信息"""
    return {
        "service_info": {
            "name": "Chinese Text Classification API",
            "version": "2.0.0",
            "environment": os.getenv("ENVIRONMENT", "development"),
            "uptime": str(datetime.now() - startup_time)
        },
        "system_info": {
            "python_version": sys.version,
            "platform": sys.platform
        },
        "model_info": predictor.get_model_info()
    }

@app.on_event("startup")
async def startup_event():
    """启动时加载模型"""
    print("正在加载模型...")
    if predictor.load_best_model():
        print("模型加载成功")
    else:
        print("模型加载失败，服务将无法提供预测功能")

if __name__ == "__main__":
    host = os.getenv("HOST", "0.0.0.0")
    port = int(os.getenv("PORT", 8000))
    reload = os.getenv("DEBUG", "false").lower() == "true"

    print(f"启动中文文本分类服务...")
    print(f"服务地址: http://{host}:{port}")
    print(f"API文档: http://{host}:{port}/docs")

    uvicorn.run(
        app,
        host=host,
        port=port,
        reload=reload,
        log_level="info"
    )