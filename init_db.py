#from urllib.request import urlopen
import requests
import json
from zipfile import ZipFile
from io import BytesIO
import xml.etree.ElementTree as elemTree
from pymongo import MongoClient

api_key = '0d7e16db6f9cf5f87cab625673fd7c5fa70ebc82'
client = MongoClient('localhost',27017)
db = client.dbstock

# 고유번호 받아와서 상장주식 딕셔너리로 변환 후 MongoDB에 저장하는 함
def get_corpCode():
    db.corpCode.delete_many({})
    url = "https://opendart.fss.or.kr/api/corpCode.xml?crtfc_key=" + api_key
    resp = requests.get(url)

    with ZipFile(BytesIO(resp.content)) as zf:
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

    for i in range(len(corp_code)):
        if stock_code[i] == ' ':
            continue
        doc = {"corp_code":corp_code[i],"corp_name":corp_name[i], "stock_code":stock_code[i], "modify_date": modify_date[i]}
        db.corpCode.insert_one(doc)
    return

#상장사 재무제표 딕셔너리로 변환해서 몽고DB로 변환하는 코드.
def get_financials():

    db.financials.delete_many({})  # DB 비우기

    accounts_dirty = ["수익(매출액)"]  # 필요하지만 이름이 일관되지 않은 항목
    dirty2clean = {"수익(매출액)":"매출액"}   # 그래서 이름을 무엇으로 바꿀지 조회할 수 있는 딕셔너리
    accounts_clean = ["현금및현금성자산","재고자산","유형자산","무형자산","자산총계","매출액","매출총이익","영업이익(손실)", "당기순이익(손실)","영업활동현금흐름","재무활동현금흐름","투자활동현금흐름"]
    #다운받을 기업리스트
    sample_co = list(db.corpCode.find({}).sort("stock_code",-1).limit(50)) #개수 한정    corp_code = []
    corp_code=[]
    for i in range(len(sample_co)):
        corp_code.append(sample_co[i]["corp_code"])
    bsns_year = ["2019","2018","2017","2016","2015"]
    reprt_code = "11011"  #사업보고서
    fs_div = "CFS"  #연결

    for i in corp_code:
        for j in bsns_year:
            url = "https://opendart.fss.or.kr/api/fnlttSinglAcntAll.json?crtfc_key=" + api_key + "&corp_code=" + i + "&bsns_year=" + j + "&reprt_code=" + reprt_code + "&fs_div=" + fs_div
            resp = requests.get(url) #response object
            resp = resp.json() #json으로 변환;
            if resp["status"] !="000":
                print(resp)
                continue
            resp = resp["list"]
            #고유번호DB를 조회해서 주식번호와 회사이름 찾기
            stock_code = db.corpCode.find_one({"corp_code":i})["stock_code"]
            corp_name = db.corpCode.find_one({"corp_code":i})["corp_name"]

            output = {"stock_code":stock_code,"corp_name":corp_name,"corp_code":i,"bsns_year":j}

            for dict in resp:
                # 필요한 값만 빼내기
                if dict["account_nm"] in accounts_dirty:
                    output[dirty2clean[dict["account_nm"]]]=dict["thstrm_amount"]
                if dict["account_nm"] in accounts_clean:
                    output[dict["account_nm"]]=dict["thstrm_amount"]
            db.financials.insert_one(output) #몽고DB로 저장
    #print(list(db.financials.find({}))) #테스트
    return

def test():
    i= "01316236"
    j = "2019"
    k = "11011"  #사업보고서
    l = "CFS"  #연결
    url = "https://opendart.fss.or.kr/api/fnlttSinglAcntAll.json?crtfc_key=" + api_key + "&corp_code=" + i + "&bsns_year=" + j + "&reprt_code=" + k + "&fs_div=" + l
    resp = requests.get(url) #response object
    resp = resp.json() #json으로 변환;
    print(resp)

#get_corpCode()
get_financials()
#test()