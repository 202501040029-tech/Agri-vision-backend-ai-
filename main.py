from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from database import Base,engine
import models
from config import settings
from routes.api import router

Base.metadata.create_all(bind=engine)
app=FastAPI(title=settings.app_name,version='1.0.0',description='Crop health mapping and targeted intervention API')
app.add_middleware(CORSMiddleware,allow_origins=settings.cors_origins,allow_credentials=True,allow_methods=['GET','POST','PUT','DELETE'],allow_headers=['*'])
app.include_router(router)
@app.get('/')
def root():return {"success":True,"message":"AgriVision AI backend is running","docs":"/docs"}
