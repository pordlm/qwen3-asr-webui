# 使用 Qwen 官方的基础镜像
FROM qwenllm/qwen3-asr:latest

# 设置工作目录
WORKDIR /app

# 设置环境变量，防止 Python 生成 .pyc 文件，并设置默认端口
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV GRADIO_SERVER_NAME="0.0.0.0"
ENV GRADIO_SERVER_PORT=80

# 换源并安装依赖
# 我们把刚才踩过的坑（缺少库、版本问题）在这里一次性解决
RUN pip config set global.index-url https://mirrors.aliyun.com/pypi/simple/ && \
    pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir \
    gradio \
    "transformers>=4.48.0" \
    accelerate \
    "qwen-asr>=0.0.4"

# 拷贝 WebUI 代码进去 (假设代码文件名为 web_ui.py)
COPY web_ui.py /app/app.py

# 暴露端口
EXPOSE 80

# 启动命令
CMD ["python", "/app/app.py"]
