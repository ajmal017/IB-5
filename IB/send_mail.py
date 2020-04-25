import yagmail
import pandas as pd

mail_to = ['shiming.zhou@ensae.fr', 'shengzhan.jia@ensae.fr']


def send_mail(subject, content):
    my_mail = yagmail.SMTP(user='zsmjoe@gmail.com', password='ayxuggfqjvekeujo')
    my_mail.send(to=mail_to, subject=subject, contents=content)

    print('mail sent')


if __name__ == '__main__':
    df = pd.read_csv('all.csv')

    df['difference'] = df['OverValued_IV'] - df['Normal_iv']

    df_new = df.sort_values(by='difference', ascending=False)
    df_new.dropna(how='any', inplace=True, axis=0)
    df_new['difference'] = df_new['difference'].apply(lambda x: str(round(x * 100)) + '%')
    subject = 'Stocks overvalued (spot > 20)'
    content = df_new.style.render()
    send_mail(subject, content)


