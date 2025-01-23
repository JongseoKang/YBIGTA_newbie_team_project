import requests as req
import json
import pandas as pd

url = f'https://comment.daum.net/apis/v1/posts/149513756/comments?parentId=0&offset=0&limit=10&sort=RECOMMEND&isInitial=false&hasNext=true'
res = req.get(url)

count_url = f"https://comment.daum.net/apis/v1/comments/on/149513756/flags"
count_res = req.get(count_url)
count_json = json.loads(count_res.text)

print(count_json)