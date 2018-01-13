import requests
import time
import json
from bs4 import BeautifulSoup
from datetime import datetime,timedelta

PTT_URL = 'https://www.ptt.cc'


def get_web_page(url):
    resp = requests.get(
        url=url,
        cookies={'over18': '1'}
    )
    if resp.status_code != 200:
        print('Invalid url:', resp.url)
        return None
    else:
        return resp.text


def get_articles(dom, date):
    soup = BeautifulSoup(dom, 'html5lib')

    # 取得上一頁的連結
    paging_div = soup.find('div', 'btn-group btn-group-paging')
    #上一頁的button
    prev_url = paging_div.find_all('a')[1]['href']

    articles = []  # 儲存取得的文章資料
    divs = soup.find_all('div', 'r-ent')
    for d in divs:
        if d.find('div', 'date').text.strip() == date:  # 發文日期正確
            # 取得推文數
            push_count = 0
            push_str = d.find('div', 'nrec').text
            if push_str:
                try:
                    push_count = int(push_str)  # 轉換字串為數字
                except ValueError:
                    # 若轉換失敗，可能是'爆'或 'X1', 'X2', ...
                    # 若不是, 不做任何事，push_count 保持為 0
                    if push_str == '爆':
                        push_count = 99
                    elif push_str.startswith('X'):
                        push_count = -10

            # 取得文章連結及標題
            if d.find('a'):  # 有超連結，表示文章存在，未被刪除
                href = d.find('a')['href']
                title = d.find('a').text
                author = ''  # author = d.find('div', 'author').text if d.find('div', 'author') else ''
                articles.append({
                    'title': title,
                    'href': href,
                    'push_count': push_count,
                    'author': author
                })
    return articles, prev_url


def get_author_ids(posts, pattern):
    ids = set()
    for post in posts:
        if pattern in post['author']:
            ids.add(post['author'])
    return ids

def main():
    current_page = get_web_page(PTT_URL + '/bbs/Gossiping/index.html')
    if current_page:
        articles = []  # 全部的今日文章
        # yesterday = datetime.today() + timedelta(-1)
        # print("Yesterday is : "+yesterday.strftime("%m/%d"))
        # date=yesterday.strftime("%m/%d").lstrip('0')
        today = time.strftime("%m/%d").lstrip('0')  # 今天日期, 去掉開頭的 '0' 以符合 PTT 網站格式
        current_articles, prev_url = get_articles(current_page, today)  # 目前頁面的昨日文章
        while current_articles:  # 若目前頁面有今日文章則加入 articles，並回到上一頁繼續尋找是否有今日文章
            #裡面dict可以加上去 ex list1=[1,2,3] list2=[4,5,6] list1+list2=[1,2,3,4,5,6]
            articles += current_articles
            current_page = get_web_page(PTT_URL + prev_url)
            current_articles, prev_url = get_articles(current_page, today)

        # 印出所有不同的 5566 id
        # print(get_author_ids(articles, '5566'))

        # 儲存或處理文章資訊
        print('今天有', len(articles), '篇文章')
        threshold = 50
        hot_article_list=[]
        print('熱門文章(> %d 推):' % (threshold))
        for a in articles:
            if int(a['push_count']) > threshold:
                hot_article_list.append(a)
        return hot_article_list
        # with open('gossiping.json', 'w', encoding='utf-8') as f:
        #     json.dump(articles, f, indent=2, sort_keys=True, ensure_ascii=False)