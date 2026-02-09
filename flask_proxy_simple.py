#!/usr/bin/env python3
"""
Midscene.js Flask 中转服务（简洁版）
部署在 10.10.16.11，转发请求到 111.6.123.48:6013

使用：
1. 安装依赖：pip install flask requests flask-cors
2. 运行服务：python3 flask_proxy_simple.py
3. midscene.js 配置：MIDSCENE_MODEL_BASE_URL="http://10.10.16.11:6013/v1"
"""

from flask import Flask, request, Response
import requests

app = Flask(__name__)

# 配置
MODEL_URL = 'http://111.6.123.48:6013'  # 模型服务地址
LISTEN_HOST = '0.0.0.0'
LISTEN_PORT = 6013

@app.route('/', defaults={'path': ''})
@app.route('/<path:path>', methods=['GET', 'POST', 'PUT', 'DELETE', 'OPTIONS'])
def proxy(path):
    """转发所有请求到模型服务"""
    target_url = f"{MODEL_URL}/{path}"
    
    # 获取请求头和数据
    headers = {k: v for k, v in request.headers if k.lower() not in ['host', 'content-length']}
    data = request.get_data()
    
    try:
        # 转发请求
        resp = requests.request(
            method=request.method,
            url=target_url,
            headers=headers,
            data=data,
            params=request.args,
            stream=True,
            timeout=(10, 300)
        )
        
        # 流式返回响应
        def generate():
            for chunk in resp.iter_content(chunk_size=8192):
                if chunk:
                    yield chunk
        
        return Response(
            generate(),
            status=resp.status_code,
            headers={k: v for k, v in resp.headers.items() if k.lower() not in ['transfer-encoding', 'content-encoding']}
        )
        
    except Exception as e:
        return {'error': str(e)}, 502

if __name__ == '__main__':
    print(f"[*] Midscene.js Proxy Server")
    print(f"[*] Listening: http://{LISTEN_HOST}:{LISTEN_PORT}")
    print(f"[*] Target: {MODEL_URL}")
    print(f"[*] Press Ctrl+C to stop\n")
    
    app.run(host=LISTEN_HOST, port=LISTEN_PORT, threaded=True)
