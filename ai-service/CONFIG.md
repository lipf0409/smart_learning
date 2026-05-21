# 智能学习系统 AI服务配置说明

## 讯飞星火API配置

### 1. 获取API凭证

访问讯飞开放平台: https://console.xfyun.cn/

1. 登录/注册账号
2. 创建应用，选择"星火认知大模型"
3. 获取以下凭证:
   - APPID
   - API Key
   - API Secret

### 2. 配置环境变量

#### Windows PowerShell (临时)
```powershell
$env:SPARK_APP_ID="你的APPID"
$env:SPARK_API_KEY="你的APIKey"
$env:SPARK_API_SECRET="你的APISecret"
$env:SPARK_MODEL_VERSION="v3.5"
```

#### Windows PowerShell (永久)
```powershell
[Environment]::SetEnvironmentVariable("SPARK_APP_ID", "你的APPID", "User")
[Environment]::SetEnvironmentVariable("SPARK_API_KEY", "你的APIKey", "User")
[Environment]::SetEnvironmentVariable("SPARK_API_SECRET", "你的APISecret", "User")
[Environment]::SetEnvironmentVariable("SPARK_MODEL_VERSION", "v3.5", "User")
```

#### 创建 .env 文件
在 `ai-service` 目录下创建 `.env` 文件:
```
SPARK_APP_ID=你的APPID
SPARK_API_KEY=你的APIKey
SPARK_API_SECRET=你的APISecret
SPARK_MODEL_VERSION=v3.5
```

### 3. 星火模型版本说明

| 版本 | 说明 | 推荐场景 |
|------|------|----------|
| v1.5 | 基础版本 | 简单对话 |
| v2.0 | 进阶版本 | 通用场景 |
| v3.0 | 高级版本 | 复杂推理 |
| v3.5 | 推荐版本 | 数学解题、多学科 |
| v4.0 | 最新版本 | 最强能力 |

### 4. 启动服务

```powershell
cd E:\PY_CODE\Small_project_code\smart_learning\ai-service
conda activate zuozi
uvicorn app.main:app --reload --port 8000
```

### 5. 测试接口

```powershell
# 健康检查
curl http://localhost:8000/api/question/health

# 拍照搜题
curl -X POST "http://localhost:8000/api/question/solve" -F "file=@题目图片.jpg"
```

## 注意事项

1. 讯飞星火API需要付费，请确保账户有余额
2. 多模态功能(图片识别)需要使用v3.5或更高版本
3. API调用有频率限制，请参考讯飞官方文档
