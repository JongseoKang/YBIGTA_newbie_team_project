# app/review/review_router.py
from fastapi import APIRouter, HTTPException
from pymongo import MongoClient
from review_analysis.preprocessing.js_processor import JSProcessor
# 필요하다면, 전처리 클래스 딕셔너리 등도 임포트합니다.
from review_analysis.preprocessing.main import PREPROCESS_CLASSES

router = APIRouter(prefix="/review", tags=["review"])

# MongoDB 연결 설정 
client = MongoClient("mongodb+srv://haneul:gksmf3191%40@cluster0.feys2.mongodb.net/")
db = client["review"]  # MongoDB 데이터베이스 이름

@router.post("/preprocess/{site_name}")
async def preprocess_review(site_name: str):
    # site_name에 따라 컬렉션 이름 결정
    if site_name.lower() == "megabox":
        collection_name = "reviews_Megabox"
    elif site_name.lower() == "navermovie":
        collection_name = "reviews_NaverMovie"
    else:
        raise HTTPException(status_code=400, detail="지원하지 않는 site_name입니다.")
    
    # 해당 컬렉션에서 데이터 조회
    raw_data = list(db[collection_name].find())
    if not raw_data:
        raise HTTPException(status_code=404, detail=f"{collection_name}에서 데이터를 찾을 수 없습니다.")

    # 전처리 클래스 선택 (키 이름은 예시로 "reviews_<site_name>" 형식)
    preprocessor_key = f"reviews_{site_name}"
    if preprocessor_key not in PREPROCESS_CLASSES:
        raise HTTPException(status_code=400, detail="전처리 클래스를 찾을 수 없습니다.")
    
    # 전처리 클래스 생성 (생성자는 raw_data, db, 출력 컬렉션 이름을 받도록 구현)
    processor = JSProcessor(raw_data=raw_data, db=db, output_collection=f"preprocessed_{collection_name}")
    processor.preprocess()
    processor.feature_engineering()
    processor.save_to_database()
    
    return {"message": f"{site_name} 데이터 전처리가 완료되었습니다.",
            "output_collection": f"preprocessed_{collection_name}"}