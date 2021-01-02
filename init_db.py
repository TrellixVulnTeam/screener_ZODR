
import requests
from urllib.request import urlopen
from zipfile import ZipFile
from io import BytesIO
import xml.etree.ElementTree as elemTree

api_key = '0d7e16db6f9cf5f87cab625673fd7c5fa70ebc82'
url = "https://opendart.fss.or.kr/api/corpCode.xml?crtfc_key=" + api_key
resp = urlopen(url)

# 수신된 resp의 bytes를 Buffer에 쌓고 zipfile을 로드한다.

def get_corpCode():
    with ZipFile(BytesIO(resp.read())) as zf:
        file_list = zf.namelist()
        while len(file_list) > 0:
            file_name = file_list.pop()
            corpCode = zf.open(file_name).read().decode()

    tree = elemTree.fromstring(corpCode)

    XML_stocklist = tree.findall("list")
    corp_code = [x.findtext("corp_code") for x in XML_stocklist]
    corp_name = [x.findtext("corp_name") for x in XML_stocklist]
    stock_code = [x.findtext("stock_code") for x in XML_stocklist]
    modify_date = [x.findtext("modify_date") for x in XML_stocklist]

    stocklist = {}

    for i in range(len(corp_code)):
        if stock_code[i] == ' ':
            continue
        stocklist[corp_code[i]] = (corp_name[i], stock_code[i], modify_date[i])

    return stocklist

#해당 고유번호의 전제재무제표를 받아오는 코드
#향후 필요한 작업: 분기별로 나누는 작업
#연도별로 쪼깨는 작업

def get_financials(corp_code):
    bsns_year = "2019"
    reprt_code = "11011"
    fs_div = "CFS"

    url = "https://opendart.fss.or.kr/api/fnlttSinglAcntAll.xml?crtfc_key=" + api_key + "&corp_code=" + corp_code + "&bsns_year=" + bsns_year + "&reprt_code=" + reprt_code + "&fs_div=" + fs_div
    # 재시도 하는 부분을 만든이유는 한번씩 연결이 불안정한지 120초 시간오버로 에러가 발생하는데 그럴때를 대비해 만들었다고 함
    # 출처: https://electromastersesi.tistory.com/150?category=823376 [sesi]
    # while True:
    #     try:
    #         resp = urlopen(url)
    #     except Exception as e:
    #         print(str(e))
    #         print("재시도합니다")
    #         continue
    #     break
    resp = urlopen(url)

    tree = elemTree.fromstring(resp.read().decode())
    if tree.findtext("status") == "020":
        print("일일 요청제한을 초과하여 종료합니다")
    else:
        elemTree.ElementTree(tree).write("testing.xml")

def save_to_mongoDB():
    

# 실행
# 00635134 = CJ제일제당
get_financials('00635134')

