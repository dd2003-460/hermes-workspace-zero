#!/usr/bin/env python3
"""IMAP 测试拉取（understanding-d T3）— 验证邮件通道
用法:
  export GOOGLE_IMAP_USER=xxx@gmail.com GOOGLE_IMAP_PASS=<app-password>
  export QQ_IMAP_USER=xxx@qq.com QQ_IMAP_PASS=<app-password>
  python3 imap-test.py            # 两个都测
  python3 imap-test.py gmail      # 只测 google
  python3 imap-test.py qq         # 只测 qq
产出: tools/objfunc/imap-test-receipt.json（每账号: ok/err/fetched_subject/date/count）
凭证只从环境变量读，绝不写文件/日志。
"""
import imaplib, email, json, os, sys, datetime

ACCOUNTS = {
    'gmail': dict(host='imap.gmail.com', port=993,
                  user=os.environ.get('GOOGLE_IMAP_USER',''),
                  pw=os.environ.get('GOOGLE_IMAP_PASS','')),
    'qq': dict(host='imap.qq.com', port=993,
               user=os.environ.get('QQ_IMAP_USER',''),
               pw=os.environ.get('QQ_IMAP_PASS','')),
}
OUT = os.path.join(os.path.dirname(__file__), 'imap-test-receipt.json')

def test(acc_name, cfg):
    if not cfg['user'] or not cfg['pw']:
        return dict(ok=False, err='credentials_missing', hint='export ' + acc_name.upper() + '_IMAP_USER/_PASS')
    try:
        m = imaplib.IMAP4_SSL(cfg['host'], cfg['port'])
        m.login(cfg['user'], cfg['pw'])
        typ, data = m.select('INBOX')
        if typ != 'OK' or not data or data[0] is None:
            return dict(ok=False, err='select_failed', detail=str(data))
        total = int(data[0])
        # 拉最新 1 封的 subject
        typ, msg_data = m.fetch(str(max(total,1)), '(BODY.PEEK[HEADER.FIELDS (SUBJECT DATE)])')
        subj = date = ''
        if typ == 'OK' and msg_data and msg_data[0] is not None and isinstance(msg_data[0], tuple):
            hdr = email.message_from_bytes(msg_data[0][1])
            subj = str(hdr.get('Subject',''))[:120]
            date = str(hdr.get('Date',''))
        m.logout()
        return dict(ok=True, host=cfg['host'], user=cfg['user'],
                    inbox_total=total, fetched_subject=subj, date=date,
                    tested_at=datetime.datetime.now(datetime.timezone.utc).isoformat())
    except Exception as e:
        return dict(ok=False, err=type(e).__name__, detail=str(e)[:200])

def main():
    which = sys.argv[1:] or list(ACCOUNTS)
    receipt = {}
    for name in which:
        if name not in ACCOUNTS:
            print(f'unknown account {name}'); continue
        r = test(name, ACCOUNTS[name])
        receipt[name] = r
        print(f"{name}: ok={r['ok']} {r.get('err','')} inbox={r.get('inbox_total','-')} subj={r.get('fetched_subject','-')[:60]}")
    receipt['_meta'] = dict(ran_at=datetime.datetime.now(datetime.timezone.utc).isoformat(),
                            note='凭证仅环境变量，不落盘')
    json.dump(receipt, open(OUT,'w'), ensure_ascii=False, indent=1)
    print('→', OUT)

if __name__ == '__main__':
    main()
