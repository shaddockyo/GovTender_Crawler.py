# coding=UTF-8
import datetime
import requests
import configparser
from bs4 import BeautifulSoup
from jinja2 import Environment, FileSystemLoader
from mail import send_mail


def main():
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

    # 擷取網頁資料Get
    url = 'http://web.pcc.gov.tw/prkms/prms-viewTenderStatClient.do?ds={0}&root=tps'
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

    # 將標案資料建立成dict合併為list
    cases = []
    for index in range(len(final_result)):
        case = {}
        case['no'] = index+1
        case['unit'] = tender_unit_list[index]
        case['name'] = tender_name_list[index]
        detail_url = '{url}?ds={dt}0&fn={tender_num}'.format(
            url='http://web.pcc.gov.tw/prkms/prms-viewTenderDetailClient.do',
            dt=dt,
            tender_num=tender_num_list[index])
        case['url'] = detail_url
        cases.append(case)

    # 使用jinja2 render標案資料
    env = Environment(
        loader=FileSystemLoader('')
    )
    template = env.get_template('content.html')
    html_content = template.render(dt=dt, keyword=config['Basic']['Keyword'], cases=cases)

    send_mail(config['Mail'], dt, html_content)
    print('政府電子採購網-限制性招標公告{0}查詢結果已寄出!'.format(dt))

if __name__ == '__main__':
    main()
