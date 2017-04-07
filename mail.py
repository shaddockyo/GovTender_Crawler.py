import smtplib
from smtplib import SMTP, SMTPAuthenticationError, SMTPException
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText


def send_mail(mail_cfg, dt, html_content):
    host = mail_cfg['Host']
    port = mail_cfg['Port']
    username = mail_cfg['Username']
    password = mail_cfg['Password']
    from_email = mail_cfg['FromEmail']
    to_list = [mail for mail in mail_cfg['ToList'].split(',')]

    # 建立SMTP連線
    email_conn = smtplib.SMTP(host, port)
    # 跟Server溝通
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
