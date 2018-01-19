from email.header import Header
from email.mime.text import MIMEText
from email.utils import parseaddr, formataddr
import smtplib


def _format_addr(s):
    name, addr = parseaddr(s)
    return formataddr((Header(name, 'utf-8').encode(), addr))


def sendqqmail(to_addr, kemu):
    from_addr = '759078664@qq.com'
    password = 'juomhzddjnvmbccj'
    to_addr = to_addr
    smtp_server = 'smtp.qq.com'
    msg = MIMEText('<html><body><h1>预约成功!</h1>' +
                   '<p>恭喜您在广科驾校的科目%s预约成功!...</p>' % kemu +
                   '</body></html>', 'html', 'utf-8')
    msg['From'] = _format_addr(' 广科驾校<%s>' % from_addr)
    msg['To'] = _format_addr('管理员 <%s>' % to_addr)
    msg['Subject'] = Header('恭喜您预约成功!', 'utf-8').encode()

    try:
        server = smtplib.SMTP_SSL(smtp_server, port=465)
        server.set_debuglevel(1)
        server.login(from_addr, password)
        server.sendmail(from_addr, [to_addr], msg.as_string())
        server.quit()
        return True
    except Exception as e:
        return str(e)
