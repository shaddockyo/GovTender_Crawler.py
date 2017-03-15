from bs4 import BeautifulSoup
import datetime
import requests

# 取得今天日期
today = datetime.date.today().strftime('%Y%m%d')
print("查詢日期:" + today)

# 擷取網頁資料Get
url = 'http://web.pcc.gov.tw/prkms/prms-viewTenderStatClient.do?ds={0}&root=tps'
url = url.format(today)
raw_data = requests.get(url)
raw_data_to_dom = BeautifulSoup(raw_data.text, "lxml")

# 將全部標案儲存於List
case_list = []
for tender_case in raw_data_to_dom.select('.tenderCase'):
    case = str(tender_case.select('.tenderLink')[0])
    case_list.append(case)

# 取得各類標案數量
num_raw_data = raw_data_to_dom.select('h3')
open_num = 0
open_modify = 0
limit_num = 0
for index in range(len(num_raw_data)):
    txt = str(num_raw_data[index].text)
    if(index == 1):
        open_num = int(txt[10:])
    if(index == 3):
        open_modify = int(txt[12:])
    if(index == 5):
        limit_num = int(txt[11:])
        print("限制性招標公告總筆數:{0}".format(limit_num))

# 取出限制性招標標案
limit_case = case_list[open_num + open_modify: open_num + open_modify + limit_num]

# 設定關鍵字
keyword = ["資訊", "監控", "管理系 統", "地理資訊", "GIS", "行動", "雲端"]

# 文字處理-去除不必要的文字
for index in range(len(limit_case)):
    limit_case[index] = limit_case[index].replace(
        "<a class=\"tenderLink\" href=\"", "")
    limit_case[index] = limit_case[index].replace("</a>", "")
    limit_case[index] = limit_case[index].replace("\">&lt;", ":")
    limit_case[index] = limit_case[index].replace("&gt;", ":")

    # 關鍵字篩選
    for i in range(len(keyword)):
        if(keyword[i] in limit_case[index]):
            print(limit_case[index])

# http://web.pcc.gov.tw/prkms/prms-viewTenderDetailClient.do?ds=20170210&fn=TIQ-3-51874692.xml
