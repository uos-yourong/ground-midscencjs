================================================================================
Flask 中转服务 - 简洁版
================================================================================

场景：
  - midscene.js 运行在 10.10.12.14
  - Flask 中转服务部署在 10.10.16.11
  - 模型服务在 111.6.123.48:6013

架构：
  10.10.12.14 (midscene.js)  
      |
      | HTTP请求
      v
  10.10.16.11 (Flask中转服务)
      |
      | 转发请求
      v
  111.6.123.48:6013 (模型服务)

================================================================================
部署步骤（在 10.10.16.11 上执行）
================================================================================

1. 安装依赖
   pip3 install flask requests flask-cors

2. 复制 flask_proxy_simple.py 到 10.10.16.11

3. 运行服务
   python3 flask_proxy_simple.py

   或使用后台运行：
   nohup python3 flask_proxy_simple.py > proxy.log 2>&1 &

================================================================================
配置 midscene.js（在 10.10.12.14 上）
================================================================================

修改 .env 文件：

  # 修改前
  MIDSCENE_MODEL_BASE_URL="http://111.6.123.48:6013/v1"

  # 修改后 - 指向 Flask 中转服务
  MIDSCENE_MODEL_BASE_URL="http://10.10.16.11:6013/v1"

运行测试：
  npx midscene-uos test --case examples/test.ts --task-id test-001

================================================================================
Systemd 服务化（推荐生产环境使用）
================================================================================

1. 创建服务文件 /etc/systemd/system/midscene-proxy.service：

[Unit]
Description=Midscene.js Flask Proxy
After=network.target

[Service]
Type=simple
WorkingDirectory=/opt/midscene-proxy
ExecStart=/usr/bin/python3 /opt/midscene-proxy/flask_proxy_simple.py
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target

2. 启用并启动服务：
   sudo systemctl daemon-reload
   sudo systemctl enable midscene-proxy
   sudo systemctl start midscene-proxy
   sudo systemctl status midscene-proxy

================================================================================
测试命令
================================================================================

# 在 10.10.16.11 上测试中转服务
curl http://localhost:6013/v1/models

# 在 10.10.12.14 上测试连通性
curl http://10.10.16.11:6013/v1/models

# 测试聊天接口
curl -X POST http://10.10.16.11:6013/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{"model":"ui-tars","messages":[{"role":"user","content":"Hello"}]}'

================================================================================
注意事项
================================================================================

1. 确保 10.10.16.11 可以访问 111.6.123.48:6013
2. 确保防火墙开放 10.10.16.11 的 6013 端口
3. 如果 10.10.16.11 需要通过代理访问模型服务，需修改 MODEL_URL 配置

================================================================================
