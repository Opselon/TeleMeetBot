from sqlalchemy import create_engine, Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from datetime import datetime

DATABASE_URL = "sqlite:///./telemeet.db"

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

class Config(Base):
    __tablename__ = "config"
    key = Column(String, primary_key=True, index=True)
    value = Column(String)

class Automation(Base):
    __tablename__ = "automations"

    id = Column(Integer, primary_key=True, index=True)
    meet_link = Column(String, index=True)
    youtube_link = Column(String, index=True)
    status = Column(String, index=True)
    logs = relationship("Log", back_populates="automation")

class Log(Base):
    __tablename__ = "logs"

    id = Column(Integer, primary_key=True, index=True)
    automation_id = Column(Integer, ForeignKey("automations.id"))
    timestamp = Column(DateTime, default=datetime.utcnow)
    level = Column(String)
    message = Column(String)
    automation = relationship("Automation", back_populates="logs")

def init_db():
    Base.metadata.create_all(bind=engine)
    with SessionLocal() as db:
        if not db.query(Config).filter(Config.key == "telegram_token").first():
            db.add(Config(key="telegram_token", value=""))
            db.commit()

def get_config(key):
    with SessionLocal() as db:
        config = db.query(Config).filter(Config.key == key).first()
        return config.value if config else None

def set_config(key, value):
    with SessionLocal() as db:
        config = db.query(Config).filter(Config.key == key).first()
        if config:
            config.value = value
        else:
            config = Config(key=key, value=value)
            db.add(config)
        db.commit()
