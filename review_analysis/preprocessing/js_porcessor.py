from base_processor import BaseDataProcessor
import os
import datetime
import pandas as pd
from gensim.models import Word2Vec
from konlpy.tag import Okt



class JSProcessor(BaseDataProcessor):
    def __init__(self, input_path: str, output_dir: str):
        '''constructor for JSProcessor'''
        super().__init__(input_path, output_dir)
        self.data = pd.read_csv(input_path)
        self.base_name = os.path.splitext(os.path.basename(input_path))[0]
        self.output_path = os.path.join(output_dir, f"preprocessed_{self.base_name}.csv")
        print(self.output_path)
    
    def preprocess(self):
        '''preprocessor, remove outliers'''
        data = self.data
        
        data["date"] = data["date"].astype(str)
        data["review"] = data["review"].astype(str)
        data = data[data["rating"] >= 1]
        data = data[data["rating"] <= 10]

        data = data[data["rating"] != None]
        data = data[data["review"] != None]
        data = data[data["date"] != None]

        data = data[data["review"].apply(len) >= 10]
        data = data[data["review"].apply(len) <= 60]

        self.data = data
    
    def feature_engineering(self):
        '''gen two features, days from released, word embedding'''
        data = self.data
       
        def parse_date(date_str):
            """
            Calculate the difference in hours from the reference date (2025-01-22 00:00).

            Args:
                date_str (str): The input date string to calculate hours difference.

            Returns:
                float: The difference in hours.
            """
            # Define the reference datetime
            reference_date = datetime.datetime(2025, 1, 22, 0, 0)

            # Parse the input date string
            try:
                # Check for type1 format
                input_date = datetime.datetime.strptime(date_str, "%Y-%m-%d %H:%M:%S.%f")
            except ValueError:
                # Fallback to type2 format
                input_date = datetime.datetime.strptime(date_str, "%Y.%m.%d. %H:%M")

            # Calculate the difference in hours
            difference = (input_date - reference_date).total_seconds() / 3600

            return round(difference)
        data["from_release"] = data["date"].apply(parse_date)

        # 2. 형태소 분석을 위한 Tokenizer (Okt 사용)
        okt = Okt()

        def tokenize(text):
            return okt.morphs(text, stem=True)  # 어간 추출 포함

        # 3. 모든 리뷰를 토크나이즈
        tokens = data["review"].apply(tokenize)

        # 4. Word2Vec 모델 학습
        # Word2Vec 입력은 토큰화된 문장의 리스트로 구성됩니다.
        sentences = tokens.tolist()  # 토큰화된 문장 리스트
        model = Word2Vec(sentences, vector_size=100, window=5, min_count=1, workers=4)

        # 5. 문장 벡터화 함수 정의
        def sentence_to_vector(tokens):
            vectors = [model.wv[word] for word in tokens if word in model.wv]  # 단어 벡터
            if len(vectors) > 0:
                return sum(vectors) / len(vectors)  # 평균 벡터 계산
            else:
                return [0] * model.vector_size  # 빈 문장은 0 벡터로 반환

        # 6. 각 문장을 벡터화하여 word2vec 칼럼에 저장
        data["word2vec"] = tokens.apply(sentence_to_vector)

        self.data = data

    def save_to_database(self):
        '''export data to csv'''
        self.data.to_csv(self.output_path)
