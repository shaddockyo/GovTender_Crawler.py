from bs4 import BeautifulSoup
import datetime
import requests

# 取得今天日期
today = datetime.date.today().strftime('%Y%m%d')
print("查詢日期:" + today)

# 擷取網頁資料pe
url = 'http://web.pcc.gov.tw/prkms/prms-viewTenderStatClient.do?ds={0}&root=tps'
url = url.format('20170210')
RawData = requests.get(url)
RawDataToDom = BeautifulSoup(RawData.text, "lxml")

# 將全部標案儲存於List
Caselist = []

# list comprehension
# CaseList = [str(case.select('.tenderLink')[0]) for case in RawDataToDom.select('.tenderCase')]

for tenderCase in RawDataToDom.select('.tenderCase'):
    Case = str(tenderCase.select('.tenderLink')[0])
    # Caselist.insert(len(Caselist)+1,Case)
    Caselist.append(Case)

# 取得各類標案數量
NumRawData = RawDataToDom.select('h3')
OpenNum = 0
OpenModify = 0
LimitNum = 0

for index in range(len(NumRawData)):
    Txt = str(NumRawData[index].text)
    if(index == 1):
        OpenNum = int(Txt[10:])
    if(index == 3):
        OpenModify = int(Txt[12:])
    if(index == 5):
        LimitNum = int(Txt[11:])
        print("限制性招標公告總筆數:" + str(LimitNum))

# limit_case = Caselist[OpenNum + OpenModify-1: OpenNum + OpenModify + LimitNum]

del Caselist[0:OpenNum]  # 移除公開招標公告標案
del Caselist[0:OpenModify]  # 移除公開招標更正公告標案

LimitCase = []  # 限制性招標標案清單

# 取出限制性招標標案
for index in range(len(Caselist)):
    if(index < LimitNum):
        LimitCase.append(Caselist[index])
        # LimitCase.insert(len(LimitCase)+1,Caselist[index])

keyword = ["資訊", "監控", "管理系 統", "地理資訊", "GIS", "行動", "雲端"]

# 文字處理-去除不必要的文字
for index in range(len(LimitCase)):
    LimitCase[index] = LimitCase[index].replace(
        "<a class=\"tenderLink\" href=\"", "")
    LimitCase[index] = LimitCase[index].replace("</a>", "")
    LimitCase[index] = LimitCase[index].replace("\">&lt;", ":")
    LimitCase[index] = LimitCase[index].replace("&gt;", ":")

    # 關鍵字篩選
    for i in range(len(keyword)):
        if(keyword[i] in LimitCase[index]):
            print(LimitCase[index])

# http://web.pcc.gov.tw/prkms/prms-viewTenderDetailClient.do?ds=20170210&fn=TIQ-3-51874692.xml
