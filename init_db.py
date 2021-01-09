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

# 고유번호 받아와서 상장주식 딕셔너리로 받아dhk MongoDB에 저장하는 코
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

#향후 필요한 작업: 분기별로 나누는 작업, 연도별로 쪼깨는 작업드
def get_financials():
    db.financials.delete_many({})

    corp_code = ["00126380"]
    bsns_year = ["2019","2018","2017"]
    reprt_code = ["11011"]  #사업보고서
    fs_div = ["CFS"]  #연결

    accounts = ["수익(매출액)", "현금및현금성자산"]  # 필요한 변수 리스트

    for i in corp_code:
        for j in bsns_year:
            for k in reprt_code:
                for l in fs_div:
                    url = "https://opendart.fss.or.kr/api/fnlttSinglAcntAll.json?crtfc_key=" + api_key + "&corp_code=" + i + "&bsns_year=" + j + "&reprt_code=" + k + "&fs_div=" + l
                    resp = requests.get(url) #response object
                    resp = resp.json() #json으로 변환;
                    resp = resp["list"] #list값만 빼내기. 변수타입 역시 리스트.

                    #고유번호DB를 조회해서 주식번호와 회사이름 찾
                    stock_code = db.corpCode.find_one({"corp_code":i})["stock_code"]
                    corp_name = db.corpCode.find_one({"corp_code":i})["corp_name"]

                    output = {"stock_code":stock_code,"corp_name":corp_name,"corp_code":i,"bsns_year":j}

                    for dict in resp:
                        # 필요한 값만 빼내기
                        if dict["account_nm"] in accounts:
                            output[dict["account_nm"]]=dict["thstrm_amount"]
                    db.financials.insert_one(output) #몽고DB로 저장
    #print(list(db.financials.find({}))) #테스트용
    return

#get_corpCode()
get_financials()