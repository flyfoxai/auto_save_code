# sample file


## 项目结构概览

```
cursor-code-change-manager/
├── backend/
│   ├── app/
│   │   ├── __init__.py
│   │   ├── models/
│   │   ├── routes/
│   │   ├── services/
│   │   └── utils/
│   ├── config.py
│   ├── requirements.txt
│   └── run.py
├── frontend/
│   ├── public/
│   ├── src/
│   │   ├── components/
│   │   ├── pages/
│   │   ├── services/
│   │   ├── utils/
│   │   ├── App.tsx
│   │   └── index.tsx
│   ├── package.json
│   └── tsconfig.json
├── scripts/
│   ├── install.sh
│   └── build.sh
├── tests/
│   ├── backend/
│   └── frontend/
├── .gitignore
├── README.md
└── setup.py
```



# Cursor代码变动管理项目文档 - 后端主要模块详细说明

## backend/app/__init__.py

```python
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from config import Config

db = SQLAlchemy()

def create_app(config_name: str) -> Flask:
    """
    创建并返回配置好的Flask应用实例
    
    参数:
    config_name: str - 配置名称（'development', 'production', 'testing'）
    
    返回:
    Flask - 配置好的Flask应用实例
    """
    app = Flask(__name__)
    app.config.from_object(Config[config_name])
    
    db.init_app(app)
    
    # 注册蓝图
    from .routes import project_bp, change_bp, user_bp
    app.register_blueprint(project_bp)
    app.register_blueprint(change_bp)
    app.register_blueprint(user_bp)
    
    return app
```


end of file.
