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

#print(html_content)

# http://web.pcc.gov.tw/prkms/prms-viewTenderDetailClient.do?ds=20170210&fn=TIQ-3-51874692.xml

# 輸入gmail信箱的資訊
host = "smtp.gmail.com"
port = 587
username = "your email"
password = "your password"
from_email = username
to_list = ["sandra@mail.pstcom.com.tw"]
 
# 建立SMTP連線
email_conn = smtplib.SMTP(host,port)
# 跟Gmail Server溝通
email_conn.ehlo()
# TTLS安全認證機制
email_conn.starttls()

try:
    #登入
    email_conn.login(username,password)
    
    # Create message container - the correct MIME type is multipart/alternative.
    #網際網路郵件擴展（MIME，Multipurpose Internet Mail Extensions）是一個網際網路標準，它擴展了電子郵件標準，使其能夠支援聲音，圖像，文字。
    #使用MIMEText有三個參數可以傳入，第一個參數為郵件正文(可以是純文字，或是HTML格式)，第二個參數告訴MIME是要用純文字解析還是HTML格式解析，第三個編碼保證多語言兼容性
    mail_info = MIMEMultipart("alternative")
    
    # 郵件內容
    mail_info['Subject'] = "每日查詢結果" #主旨
    mail_info["From"] = from_email #寄件者
    mail_info["To"] = to_list[0] #收件者
    html_content = MIMEText(html_content, 'html', 'utf-8')    
    mail_info.attach(html_content)
    
    #寄信
    email_conn.sendmail(from_email, to_list, mail_info.as_string())
    
except SMTPAuthenticationError:
    print("Could not login")
    
except:
    print("an error occured!")

# 關閉連線
email_conn.quit()
