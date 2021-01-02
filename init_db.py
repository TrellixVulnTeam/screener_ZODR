
import requests

# 상장기업 리스트:  http://marketdata.krx.co.kr/mdi#document=undefined

# 글로벌 변수
api_key = '0d7e16db6f9cf5f87cab625673fd7c5fa70ebc82'

# 고유번호를 먼저 내려받아야함
def get_corpCode():
    api_corpCode = 'https://opendart.fss.or.kr/api/corpCode.xml'
    list_corpCode = requests.get(api_corpCode,crtfc_key=api_key)
    print(list_corpCode)

# 업데이트된 상장기업리스트를 만든다

def get_data():
    api_url = 'https://opendart.fss.or.kr/api/fnlttSinglAcntAll.json'

# 루프로 돌려서 일일이 기업정보를 요청해본다



#