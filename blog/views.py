from django.shortcuts import render
from django.http import HttpResponse
from . import crawler
from . import ptt_gossiping
# Create your views here.

def index(request):
    string=crawler.test_fun()
    dict_list=crawler.main()
    ptt_list=[i for i in dict_list]
    print(type(ptt_list))
    return HttpResponse(ptt_list[0]['title'])



def homeIndex(request):
    dict_list=crawler.main()
    img_urls=[]
    img_com=[]
    for a_dict in dict_list:
        img_urls+=(a_dict['img_urls'])
    for a_dict in dict_list:
        for img_url in a_dict['img_urls']:
            img_com.append(
                {
                    'title':a_dict['title'],
                    'img_url':img_url,
                }
            )
    return render(request,'index.html',{'list':img_urls,'img_com':img_com})



def gossip_controller(request):
    hot_article_list=ptt_gossiping.main()
    return render(request,'gossip.html',{'hot_article_list':hot_article_list})