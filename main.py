# coding=UTF-8
import datetime
import requests
import smtplib
from smtplib import SMTP, SMTPAuthenticationError, SMTPException
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import configparser
from bs4 import BeautifulSoup

# 將config讀進str，避開中文編碼問題
cfg_str = ''
with open('config.ini', 'r', encoding='utf-8') as cfg_file:
    for cfg in cfg_file:
        cfg_str += cfg

config = configparser.ConfigParser()
config.read_string(cfg_str)

# 取得日期
dt_cfg = config['Basic']['Date']
dt = dt_cfg if dt_cfg != 'today' else datetime.date.today().strftime('%Y%m%d')

url = config['Basic']['URL']

# 擷取網頁資料Get
url = url + '?ds={0}&root=tps'
url = url.format(dt)
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

rawdata_num = raw_data_to_dom.select('h3')
opentender_num = 0
opentender_modify = 0
limit_num = 0
for index in range(len(rawdata_num)):
    txt = str(rawdata_num[index].text)
    if(index == 1):
        open_num = int(txt[10:])
        opentender_num = int(txt[10:])
    if(index == 3):
        open_modify = int(txt[12:])
        opentender_modify = int(txt[12:])
    if(index == 5):
        limit_num = int(txt[11:])

# 取出限制性招標標案
limit_case = case_list[open_num + open_modify: open_num + open_modify + limit_num]

# 設定關鍵字
keyword = [x for x in config['Basic']['Keyword'].split(',')]

final_result = []  # 限制性招標篩選結果list
tender_num_list = []  # 標案編號(網址參數)
tender_unit_list = []  # 標案機構名稱
tender_name_list = []  # 標案名稱

# 文字處理-去除不必要的文字
for index in range(len(limit_case)):
    limit_case[index] = limit_case[index].replace(
        "<a class=\"tenderLink\" href=\"", "")
    limit_case[index] = limit_case[index].replace("</a>", "")
    limit_case[index] = limit_case[index].replace("\">&lt;", ";")
    limit_case[index] = limit_case[index].replace("&gt;", ":")

    # 關鍵字篩選
    for i in range(len(keyword)):
        if(keyword[i] in limit_case[index]):
            if (limit_case[index] not in final_result):
                final_result.append(limit_case[index])
# 切割資料
for index in range(len(final_result)):
    tender_num = final_result[index][:18]
    tender_num_list.append(tender_num)

    unit_point_start = final_result[index].find(":")
    unit_point_end = final_result[index].find("：")
    tender_unit = final_result[index][unit_point_start+2:unit_point_end]
    tender_unit_list.append(tender_unit)

    tender_name = final_result[index][unit_point_end+1:]
    tender_name_list.append(tender_name)

# 製作HRML內容
html_content = "<html><head><style type=\"text/css\"> body{ font-family:微軟正黑體; } table{ border-collapse: collapse;} tr:nth-child(even){background-color: #f2f2f2} th, td{ text-align: left; padding: 10px;} th {  background-color: #008B8B; color: white; }</style></head><body> "
html_content += "<h2>政府電子採購網-限制性招標公告-查詢結果</h2>"
html_content += "<p>查詢日期: " + str(datetime.date.today())+"</p>"
html_content += "<p>查詢關鍵字: "

# 加入關鍵字
for i in range(len(keyword)):
    if(i == len(keyword)-1):
        html_content += keyword[i]+"</p>"
    else:
        html_content += keyword[i]+"、"

# 表格內容
html_content += "<table>  <tr>  <th>序號</th>  <th>機關名稱</th>  <th>標案名稱</th>  </tr>"
for index in range(len(final_result)):
    no = index+1
    html_content += "  <tr>  <td>"+str(no)+"</td>"
    html_content += "  <td>"+str(tender_unit_list[index])+"</td>"
    html_content += "  <td> <a title=\"開啟連結查看詳細資訊\" href=\"" + url + "?ds="+dt+"0&fn="+str(tender_num_list[index])+"\">"+str(tender_name_list[index])+"</a></td>  </tr>"
html_content += "</table></body></htrml>"

# 輸入gmail信箱的資訊
host = config['Mail']['Host']
port = config['Mail']['Port']
username = config['Mail']['Username']
password = config['Mail']['Password']
from_email = config['Mail']['FromEmail']
to_list = [mail for mail in config['Mail']['ToList'].split(',')]
# 建立SMTP連線
email_conn = smtplib.SMTP(host, port)
# 跟Gmail Server溝通
email_conn.ehlo()
# TTLS安全認證機制
email_conn.starttls()

try:
    # 登入
    email_conn.login(username, password)

    # Create message container - the correct MIME type is multipart/alternative.
    # 網際網路郵件擴展（MIME，Multipurpose Internet Mail Extensions）是一個網際網路標準，它擴展了電子郵件標準，使其能夠支援聲音，圖像，文字。
    # 使用MIMEText有三個參數可以傳入，第一個參數為郵件正文(可以是純文字，或是HTML格式)，第二個參數告訴MIME是要用純文字解析還是HTML格式解析，第三個編碼保證多語言兼容性
    mail_info = MIMEMultipart("alternative")

    # 郵件內容
    mail_info['Subject'] = "政府電子採購網-限制性招標公告-"+dt+"查詢結果"  # 主旨
    mail_info["From"] = from_email  # 寄件者
    mail_info["To"] = to_list[0]  # 收件者
    html_content = MIMEText(html_content, 'html', 'utf-8')
    mail_info.attach(html_content)

    # 寄信
    email_conn.sendmail(from_email, to_list, mail_info.as_string())

except SMTPAuthenticationError:
    print("Could not login")

# 關閉連線
email_conn.quit()
print('finish~')
