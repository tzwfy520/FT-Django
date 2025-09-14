# FT-Django 股票分析系统

一个基于Django + Vue.js的股票分析和自选股票管理系统。

## 功能特性

- 📈 股票数据获取和分析
- ⭐ 自选股票管理
- 🔍 股票搜索功能
- 📊 实时数据展示
- 🤖 AI分析功能
- 📱 响应式前端界面

## 技术栈

### 后端
- Django 4.2.7
- Django REST Framework
- Celery (异步任务)
- Redis (缓存)
- MySQL (数据库)
- AkShare (股票数据源)

### 前端
- Vue.js 3
- TypeScript
- Element Plus
- Vite

## 快速开始

### 环境要求
- Python 3.10+
- Node.js 16+
- MySQL 8.0+
- Redis

### 安装步骤

1. 克隆项目
```bash
git clone https://github.com/tzwfy520/FT-Django.git
cd FT-Django
```

2. 后端设置
```bash
# 创建虚拟环境
python -m venv venv
source venv/bin/activate  # Linux/Mac
# 或 venv\Scripts\activate  # Windows

# 安装依赖
pip install -r requirements.txt

# 数据库迁移
python manage.py migrate

# 启动后端服务
python manage.py runserver 8000
```

3. 前端设置
```bash
cd frontend
npm install
npm run dev
```

## 项目结构

```
FT-Django/
├── apps/                   # Django应用
│   ├── stocks/            # 股票相关功能
│   ├── ai/                # AI分析功能
│   ├── market/            # 市场数据
│   └── ...
├── frontend/              # Vue.js前端
│   ├── src/
│   │   ├── views/         # 页面组件
│   │   ├── components/    # 通用组件
│   │   └── services/      # API服务
│   └── ...
├── utils/                 # 工具函数
├── requirements.txt       # Python依赖
└── manage.py             # Django管理脚本
```

## 主要功能

### 自选股票管理
- 搜索股票并添加到自选列表
- 实时查看自选股票价格变动
- 支持批量操作

### 数据分析
- 股票历史数据分析
- 技术指标计算
- AI智能分析

## 开发说明

### API文档
访问 `http://localhost:8000/swagger/` 查看完整的API文档。

### 数据源
本项目使用AkShare获取股票数据，支持A股、港股等多个市场。

## 贡献

欢迎提交Issue和Pull Request！

## 许可证

MIT License