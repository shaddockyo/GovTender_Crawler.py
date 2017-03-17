from bs4 import BeautifulSoup
import datetime
import requests

# 取得今天日期
today = datetime.date.today().strftime('%Y%m%d')
print("查詢日期:" + today)

# 擷取網頁資料Get
url = 'http://web.pcc.gov.tw/prkms/prms-viewTenderStatClient.do?ds={0}&root=tps'
url = url.format(today)
RawData = requests.get(url)
RawDataToDom = BeautifulSoup(RawData.text, "lxml")

# 將全部標案儲存於List
Caselist = []
for tenderCase in RawDataToDom.select('.tenderCase'):
    Case = str(tenderCase.select('.tenderLink')[0])
    # Caselist.insert(len(Caselist)+1,Case)
    Caselist.append(Case)

# list comprehension
# CaseList = [str(case.select('.tenderLink')[0]) for case in RawDataToDom.select('.tenderCase')]

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

# 取出限制性招標標案
limit_case = Caselist[OpenNum + OpenModify: OpenNum + OpenModify + LimitNum]

# 設定關鍵字
keyword = ["資訊", "監控", "管理系 統", "地理資訊", "GIS", "行動", "雲端"]

final_result=[]

# 文字處理-去除不必要的文字
for index in range(len(limit_case)):
    limit_case[index] = limit_case[index].replace(
        "<a class=\"tenderLink\" href=\"", "")
    limit_case[index] = limit_case[index].replace("</a>", "")
    limit_case[index] = limit_case[index].replace("\">&lt;", ":")
    limit_case[index] = limit_case[index].replace("&gt;", ":")

    # 關鍵字篩選
    for i in range(len(keyword)):
        if(keyword[i] in LimitCase[index]):
            if (limit_case[index] not in final_result):
                final_result.append(limit_case[index])
                
#製作HRML內容
html_content = "<html><head></head><body>"
html_content += "查詢日期:" + today+"<br>"
html_content += "關鍵字: "

#加入關鍵字
for i in range(len(keyword)):
    if(i==len(keyword)-1):
        html_content += keyword[i]
    else:
        html_content += keyword[i]+"、"
html_content += "<br>"

#加入最終篩選結果
for index in range(len(final_result)):
    html_content += str(final_result[index])+"<br>"

html_content += "</body></htrml>"

print(html_content)

# http://web.pcc.gov.tw/prkms/prms-viewTenderDetailClient.do?ds=20170210&fn=TIQ-3-51874692.xml
