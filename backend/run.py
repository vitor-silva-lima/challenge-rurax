#!/usr/bin/env python3
"""
Script para executar a aplicação FastAPI.
"""
import uvicorn

if __name__ == "__main__":
    uvicorn.run(
        "src.infrastructure.api.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
