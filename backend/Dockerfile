FROM python:3.10-slim

WORKDIR /app

# 安装系统依赖
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    default-libmysqlclient-dev \
    pkg-config \
    && rm -rf /var/lib/apt/lists/*

# 安装 Python 依赖
COPY requirements.txt .
RUN pip install --no-cache-dir --default-timeout=120 -r requirements.txt
RUN pip install --no-cache-dir cryptography

# 复制应用代码
COPY . .

# 创建上传目录
RUN mkdir -p uploads/tmp

EXPOSE 5000

CMD ["waitress-serve", "--host=0.0.0.0", "--port=5000", "--threads=4", "wsgi:app"]
