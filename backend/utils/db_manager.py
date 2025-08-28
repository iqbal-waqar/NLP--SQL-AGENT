import os
import json
from pathlib import Path
from backend.graph.tools import clear_schema_cache

CONFIG_FILE = Path(__file__).parent.parent / "config" / "database_config.json"

def load_database_config():
    try:
        if CONFIG_FILE.exists():
            with open(CONFIG_FILE, 'r') as f:
                return json.load(f)
    except Exception as e:
        pass
    
    return None

def save_database_config(config):
    try:
        CONFIG_FILE.parent.mkdir(parents=True, exist_ok=True)
        
        with open(CONFIG_FILE, 'w') as f:
            json.dump(config, f, indent=4)
    except Exception as e:
        pass

def apply_database_config():
    config = load_database_config()
    
    if config:
        os.environ["DB_NAME"] = config["db_name"]
        os.environ["DB_USER"] = config["db_user"] 
        os.environ["DB_PASS"] = config["db_pass"]
        os.environ["DB_HOST"] = config["db_host"]
        os.environ["DB_PORT"] = config["db_port"]
        return config
    
    return None

def switch_database(db_name, db_user=None, db_pass=None, db_host=None, db_port=None):
    current_user = db_user or os.getenv("DB_USER", "postgres")
    current_pass = db_pass or os.getenv("DB_PASS", "postgres")
    current_host = db_host or os.getenv("DB_HOST", "localhost")
    current_port = str(db_port) if db_port else os.getenv("DB_PORT", "5432")
    
    os.environ["DB_NAME"] = db_name
    os.environ["DB_USER"] = current_user
    os.environ["DB_PASS"] = current_pass
    os.environ["DB_HOST"] = current_host
    os.environ["DB_PORT"] = current_port
    
    config = {
        "db_name": db_name,
        "db_user": current_user,
        "db_pass": current_pass,
        "db_host": current_host,
        "db_port": current_port
    }
    save_database_config(config)
    
    clear_schema_cache()

def get_current_database_info():
    return {
        "host": os.getenv("DB_HOST"),
        "port": os.getenv("DB_PORT"),
        "user": os.getenv("DB_USER"),
        "database": os.getenv("DB_NAME")
    }