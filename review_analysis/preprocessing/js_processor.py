from os import path
import os
import datetime
import pandas as pd
from gensim.models import Word2Vec
from konlpy.tag import Okt

#이렇게 안하면 못찾길래 경로 설정을 했습니다
import sys
sys.path.append(path.abspath('./review_analysis/preprocessing'))
print(sys.path)

from base_processor import BaseDataProcessor


# class JSProcessor(BaseDataProcessor):
#     def __init__(self, input_path: str, output_dir: str):
#         '''constructor for JSProcessor'''
#         super().__init__(input_path, output_dir)
#         self.data = pd.read_csv(input_path)
#         self.base_name = os.path.splitext(os.path.basename(input_path))[0]
#         self.output_path = os.path.join(output_dir, f"preprocessed_{self.base_name}.csv")
#         print(self.output_path)
    
#     def preprocess(self):
#         '''preprocessor, remove outliers'''
#         data = self.data
        
#         data["date"] = data["date"].astype(str)
#         data["review"] = data["review"].astype(str)
#         data["rating"] = data["rating"].astype(int)
#         data = data[data["rating"] >= 1]
#         data = data[data["rating"] <= 10]

#         data = data[data["rating"] != None]
#         data = data[data["review"] != None]
#         data = data[data["date"] != None]

#         data = data[data["review"].apply(len) >= 10]
#         data = data[data["review"].apply(len) <= 60]

#         self.data = data
    
#     def feature_engineering(self):
#         '''gen two features, days from released, word embedding'''
#         data = self.data
       
#         def parse_date(date_str):
#             """
#             Calculate the difference in hours from the reference date (2025-01-22 00:00).

#             Args:
#                 date_str (str): The input date string to calculate hours difference.

#             Returns:
#                 float: The difference in hours.
#             """
#             # Define the reference datetime
#             reference_date = datetime.datetime(2025, 1, 22, 0, 0)

#             # Parse the input date string
#             try:
#                 # Check for type1 format
#                 input_date = datetime.datetime.strptime(date_str, "%Y-%m-%d %H:%M:%S.%f")
#             except ValueError:
#                 # Fallback to type2 format
#                 input_date = datetime.datetime.strptime(date_str, "%Y.%m.%d. %H:%M")

#             # Calculate the difference in hours
#             difference = (input_date - reference_date).total_seconds() / 3600

#             return round(difference)
#         data["from_release"] = data["date"].apply(parse_date)

#         # 2. 형태소 분석을 위한 Tokenizer (Okt 사용)
#         okt = Okt()

#         def tokenize(text):
#             return okt.morphs(text, stem=True)  # 어간 추출 포함

#         # 3. 모든 리뷰를 토크나이즈
#         tokens = data["review"].apply(tokenize)

#         # 4. Word2Vec 모델 학습
#         # Word2Vec 입력은 토큰화된 문장의 리스트로 구성됩니다.
#         sentences = tokens.tolist()  # 토큰화된 문장 리스트
#         model = Word2Vec(sentences, vector_size=100, window=5, min_count=1, workers=4)

#         # 5. 문장 벡터화 함수 정의
#         def sentence_to_vector(tokens):
#             vectors = [model.wv[word] for word in tokens if word in model.wv]  # 단어 벡터
#             if len(vectors) > 0:
#                 return sum(vectors) / len(vectors)  # 평균 벡터 계산
#             else:
#                 return [0] * model.vector_size  # 빈 문장은 0 벡터로 반환

#         # 6. 각 문장을 벡터화하여 word2vec 칼럼에 저장
#         data["word2vec"] = tokens.apply(sentence_to_vector)

#         self.data = data

#     def save_to_database(self):
#         '''export data to csv'''
#         self.data.to_csv(self.output_path)


class JSProcessor(BaseDataProcessor):
    # 기존 CSV 기반 생성자 (주석 처리)
    """
    def __init__(self, input_path: str, output_dir: str):
        '''constructor for JSProcessor'''
        super().__init__(input_path, output_dir)
        self.data = pd.read_csv(input_path)
        self.base_name = os.path.splitext(os.path.basename(input_path))[0]
        self.output_path = os.path.join(output_dir, f"preprocessed_{self.base_name}.csv")
        print(self.output_path)
    """

    # 새로운 MongoDB 기반 생성자
    def __init__(self, raw_data, db, output_collection):
        """
        새로운 생성자: MongoDB에서 가져온 raw_data를 기반으로 처리
        
        :param raw_data: MongoDB에서 조회한 데이터 (list of dict)
        :param db: pymongo database 객체 (예: client["review"])
        :param output_collection: 결과를 저장할 컬렉션 이름 (예: "preprocessed_reviews_Megabox")
        """
        # BaseDataProcessor의 초기화가 필요한 경우 super().__init__() 호출 (여기서는 생략)
        self.db = db
        self.output_collection = output_collection
        # raw_data를 DataFrame으로 변환
        self.data = pd.DataFrame(raw_data)
        # base_name은 출력 컬렉션 이름으로 설정 (또는 다른 식별자로 활용)
        self.base_name = output_collection
        print(f"Processing data for collection: {self.base_name}")

    def preprocess(self):
        '''preprocessor, remove outliers'''
        data = self.data

        # 날짜, 리뷰, 평점 형변환
        data["date"] = data["date"].astype(str)
        data["review"] = data["review"].astype(str)
        data["rating"] = data["rating"].astype(int)
        
        # 평점 범위 및 None 값 제거
        data = data[data["rating"] >= 1]
        data = data[data["rating"] <= 10]
        data = data[data["rating"].notnull()]
        data = data[data["review"].notnull()]
        data = data[data["date"].notnull()]

        # 리뷰 길이 제한 (10글자 이상, 60글자 이하)
        data = data[data["review"].apply(lambda x: len(x)) >= 10]
        data = data[data["review"].apply(lambda x: len(x)) <= 60]

        self.data = data

    def feature_engineering(self):
        '''Generate features: time from release and word embedding'''
        data = self.data

        def parse_date(date_str):
            """
            Calculate the difference in hours from the reference date (2025-01-22 00:00).
            """
            reference_date = datetime.datetime(2025, 1, 22, 0, 0)
            try:
                input_date = datetime.datetime.strptime(date_str, "%Y-%m-%d %H:%M:%S.%f")
            except ValueError:
                input_date = datetime.datetime.strptime(date_str, "%Y.%m.%d. %H:%M")
            difference = (input_date - reference_date).total_seconds() / 3600
            return round(difference)
        
        data["from_release"] = data["date"].apply(parse_date)

        # 형태소 분석: Okt 사용
        okt = Okt()

        def tokenize(text):
            return okt.morphs(text, stem=True)

        tokens = data["review"].apply(tokenize)
        sentences = tokens.tolist()

        # # Word2Vec 모델 학습
        # model = Word2Vec(sentences, vector_size=100, window=5, min_count=1, workers=4)

        # def sentence_to_vector(tokens):
        #     vectors = [model.wv[word] for word in tokens if word in model.wv]
        #     if len(vectors) > 0:
        #         return sum(vectors) / len(vectors)
        #     else:
        #         return [0] * model.vector_size

        # data["word2vec"] = tokens.apply(sentence_to_vector)
        # self.data = data

    # 기존 CSV 저장 메소드는 주석 처리
    """
    def save_to_database(self):
        '''export data to csv'''
        self.data.to_csv(self.output_path)
    """
    
    def save_to_database(self):
        '''Save the processed data to MongoDB'''
        # DataFrame을 딕셔너리 리스트로 변환
        data_dict = self.data.to_dict("records")
        result = self.db[self.output_collection].insert_many(data_dict)
        print(f"Inserted {len(result.inserted_ids)} documents into {self.output_collection}")