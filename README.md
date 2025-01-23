# YBIGTA_newbie_team_project

## 실행 방법
```
git clone https://github.com/JongseoKang/YBIGTA_newbie_team_project
pip install -r requirements.txt
cd ./app
uvicorn main:app --reload
```
브라우저를 이용하여 http://127.0.0.1:8000/static/index.html 접속

## 조장

![Image](https://github.com/user-attachments/assets/dee773e4-4777-48ae-8377-e5551dce5520)

### 이름: 강종서

### 학번: 20학번

### 전공: 컴퓨터과학과

### 관심사
안녕하세요. 증명사진 눈갱 죄송합니다 ㅎㅎ..

컴파일러 최적화에 관심이 있는 컴과 4학년입니다.

인공지능은 잘 몰라서 열심히 배우겠습니다. 잘 부탁드립니다 !

---

## 조원

![image](https://github.com/user-attachments/assets/7537ebb4-4a49-4c8e-8450-341e7755fe9a)

### 이름: 박하늘

### 학번: 20학번

### 전공: 산업공학과

### 관심사
안녕하세요, 박하늘입니다.

LLM, GNN에 관심을 갖고 있습니다.

앞으로 잘 부탁드립니다!

---
branch_protection.png
<img width="1440" alt="branch_protection" src="https://github.com/user-attachments/assets/e35daf48-8b7f-4b56-b4bf-b24e915e4045" />

push_rejected.png
<img width="1440" alt="push_rejected" src="https://github.com/user-attachments/assets/812a28a3-7626-45a6-ace7-1d692e56febe" />

merge_JongseoKang.png
<img width="1440" alt="merge_JongseoKang" src="https://github.com/user-attachments/assets/d27ed214-5325-400c-ae42-cb6be750754d" />

merge_0haneu1.png
<img width="1440" alt="merge_0haneu1" src="https://github.com/user-attachments/assets/1f0dd3f6-da04-4e1e-9b05-982c702232d4" />

### EDA/FE 및 시각화

## Dependencies
```
pip install pandas gensim konlpy numpy
brew install openjdk
```

## 전처리 및 FE 결과

# 전처리

null 값을 포함, 1~10이 아닌 별점 포함 또는 길이 10~60이 아닌 텍스트 포함의 데이터를 삭제하였으며 결과적으로 네이버 리뷰는 163개, 메가박스 리뷰는 463개의 데이터 획득

# FE 추가된 변수
개봉 이후 시간대 별로 작성된 리뷰의 개수

텍스트 벡터화(word2vec)
