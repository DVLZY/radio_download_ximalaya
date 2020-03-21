'''
【适配性】
-*- coding:utf-8 -*-
网址爬取模式适用于如下形式【url0/[类目：kind]/[一级编号：id1]/[二级编号：id2/】
只要是这个格式的网址，更改对应这正则就可使用
【备用接口1】
https://www.ximalaya.com/search/album/搜索关键词
https://www.ximalaya.com/search/album/revision/album
https://www.ximalaya.com/revision/album/v1/getTracksList
【备用接口2】
#关键字搜索1https://www.ximalaya.com/revision/album/v1/getTracksList?albumId={}&pageNum=1
#获取下载链接1https://www.ximalaya.com/revision/play/v1/audio?id={搜索1ID}&ptype=1
#获取下载链接2 http://mobwsa.ximalaya.com/mobile/playlist/album/page?albumId={}&pageId=1
#关键字搜索http://searchwsa.ximalaya.com/front/v1?appid=0&condition=relation&core=chosen2&device=android&deviceId=9a68144e-de5b-3c60-be5e-adce947ab5ff&kw={}&live=true&needSemantic=true&network=wifi&operator=1&page=1&paidFilter=false&plan=c&recall=normal&rows=20&search_version=2.8&spellchecker=true&version=6.6.48&voiceAsinput=false
【更新日志】
【0.1】
1、实现了专辑网址匹配下载功能
2、解决了Windows下非法名称不能创建文件的问题
3、支持免登人下载
【0.2】
1、解决了下载音频有时候顺序会反过来的问题
2、优化了命名原则。名称更简练了
3、现在会自动下载的专辑同名的文件夹中了
4、调用了更简单的解构，优化了下载速度
【0.3】
1、加入了搜索下载的功能
【0.4】
1、解决了选择专辑时序号不连续的问题
2、现在序号都是两位数了，看起来更舒服
3、对搜索结果进行了判断，如果只有一个结果会自动开始下载
4、会判断输入的内容，如果是网址会自动开始下载专辑或者声音
'''
# 测试一下git
print('''
【喜马拉雅下载器0.4】
【----By 长河落----】
''')

import os
import re
import sys
import requests
import hashlib
import time
import random
from requests.packages.urllib3.exceptions import InsecureRequestWarning
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

# 【输入】处理用户输入内容
search_key = input('请输入要下载的专辑名称或者网址：')
print()

# 【配置】
# 生成签名
def xm_md5():
    url = 'https://www.ximalaya.com/revision/time'
    headrer = {'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/72.0.3626.96 Safari/537.36',
            'Host': 'www.ximalaya.com'}
    html = requests.get(url, headers = headrer)
    nowTime = str(round(time.time()*1000)) #13位时间戳
    sign = str(hashlib.md5("himalaya-{}".format(html.text).encode()).hexdigest()) + "({})".format(str(round(random.random()*100))) + html.text + "({})".format(str(round(random.random()*100))) + nowTime
    return sign
url0 = 'https://www.ximalaya.com/'  # 下载站点域名
page_sort = 0  # 下载排序方式；0为正序；1为倒序
search_size = 50  # 搜索结果展示数量
head = {
    'User-Agent': "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) "
                            "Chrome/80.0.3987.116 Safari/537.36",   # 用户代理
    'xm-sign':xm_md5(),     #签名验证
        }
param = {
    'core':'album',             # 结果类型：all全部；album专辑；track声音；user主播
    'kw':search_key,            # 搜索关键词
    'page':1,                   # 页码
    'condition':'play',         # 排序方式：relation相关度；play播放量；recent最近上传
    'spellchecker':'false',     # 拼写检查
    'rows':search_size,           # 展现结果数量
    'device':'iPhone',          # 设备类型
    'fq':'',                    # 收费类型：' '免费；',is_paid:true'付费
    'paidFilter':'true'         # 付费过滤
}

# 【用关键词搜索的方式下载】
album_id = re.compile('(\d{3,10})', re.S).findall(search_key)       # 尝试从输入的内容中提取专辑ID
fm_id = re.compile('\d{3,10}/(\d{3,10})', re.S).findall(search_key) # 尝试从输入的内容中提取声音ID
if len(album_id) == 0:  # 如果无法提取出专辑ID则在网页中搜索输入的关键词
    search_url = 'https://www.ximalaya.com/revision/search/main'
    search_contect = requests.get(search_url,headers=head,verify=False,params=param).text
    ablum_name_list = re.compile('"title":"(.*?)",', re.S).findall(search_contect) # 专辑名称列表
    ablum_id_list = re.compile('"albumId":(.*?),', re.S).findall(search_contect)   # 专辑ID列表
    ablum_paid_list = re.compile('"isPaid":(.*?),', re.S).findall(search_contect)  # 专辑是否付费列表
    ablum_anchor_list = re.compile('"nickname":"(.*?)",', re.S).findall(search_contect)  # 作者姓名列表

    # 判断有多少个搜索结果
    if len(ablum_name_list)==0:
        print('搜索结果为 0 ，请重新搜索')
        python = sys.executable
        os.execl(python, python, *sys.argv)
    elif len(ablum_name_list)==1:
        print('搜索结果为: 《' + ablum_name_list[0] + '》 ' + ablum_anchor_list[0])
        choose_num = 0
    else:

        # 输出免费的专辑列表
        for i in range(len(ablum_name_list)):
            if ablum_paid_list[i] == 'false':
                print(str(i + 1).rjust(2, '0') + ' 《' + ablum_name_list[i] + '》 ' + ablum_anchor_list[i])
            else:
                print('【付费产品无法下载】 《' + ablum_name_list[i] + '》 ' + ablum_anchor_list[i])
        print()
        # 让用户输入要下载的专辑的编号，并换算成对应的专辑ID
        choose_num = int(input('请输入要下载的专辑编号:')) - 1

    album_id = ablum_id_list[choose_num]
    ablum_anchor = ablum_anchor_list[choose_num]
    album_name = ablum_name_list[choose_num]

# 【用网址匹配的方式下载】
album_params = {"albumId": album_id, "sort": page_sort}  # 构造网址头信息
album_url = url0 + "revision/album"  # 构造专辑网址
album_content = requests.get(album_url, headers=head, verify=False, params=album_params).text  # 专辑网址内容
album_name = re.compile('"albumTitle":"(.*?)"', re.S).findall(album_content)[0]  # 提取专辑名称
ablum_anchor = re.compile('"anchorName":"(.*?)"', re.S).findall(album_content)[0]   # 提取作者名称
album_num = re.compile('"trackTotalCount":(\d{1,10}),', re.S).findall(album_content)[0]  # 提取音频数量
page_num = int(album_num) // 30 + 1

# 【获取所有的声音ID和名称】
all_fm_id = []
all_fm_name = []
for i in range(1, int(page_num) + 1):
    fm_url = "https://www.ximalaya.com/revision/album/v1/getTracksList"
    fm_params = {"albumId": album_id, "pageNum": i, "sort": page_sort}
    fm_content = requests.get(fm_url, headers=head, verify=False, params=fm_params).text  # 获取声音页面内容
    fm_name_list = re.compile('"title":"(.*?)"', re.S).findall(fm_content)  # 提取声音列表
    fm_id_list = re.compile('"trackId":(\d{1,10}),', re.S).findall(fm_content)  # 提取声音编号列表
    for k in range(len(fm_name_list)):
        all_fm_id.append(fm_id_list[k])
        all_fm_name.append(fm_name_list[k])

print()
if len(fm_id) == 0:
    print('准备下载：《' + album_name + '》 '+ ablum_anchor +' 一共' + album_num + '个音频')
else:
    print('准备下载：《' + album_name + '》 ' + ablum_anchor + ' ' + all_fm_name[0])
print()
print('初始化程序需要一定时间，请耐心等候……')
print()

# 【文件下载部分】
# 创建文件夹
album_name = re.sub(u"([^\u4e00-\u9fa5\u0030-\u0039\u0041-\u005a\u0061-\u007a])", "", album_name)
if not os.path.exists(r'./' + r'./' + album_name):  # 判断文件夹是否存在
    os.makedirs(r'./' + r'./' + album_name)  # 如果不存在则创建文件夹

# 提取真实下载地址
if len(fm_id) != 0:  # 如果提取出声音ID则直接下载该声音
    sound_url = 'https://www.ximalaya.com/revision/play/v1/audio?id=' + fm_id[0] + '&ptype=1'
    sound_content = requests.get(sound_url, headers=head, verify=False).text
    down_url = re.compile('src":"(.*?)",', re.S).findall(sound_content)[0]
    down_res = requests.get(down_url, verify=False)

    # 下载文件到指定路径
    try:
        file_url = r'./' + album_name + r'./01 ' + all_fm_name[0] + '.m4a'
        with open(file_url, 'wb') as fd:
            for chunk in down_res.iter_content():
                fd.write(chunk)
    except Exception as err:
        fm_id[0] = re.sub(u"([^\u4e00-\u9fa5\u0030-\u0039\u0041-\u005a\u0061-\u007a])", "", fm_id[0])
        file_url = r'./' + album_name + r'./01 ' + all_fm_name[0] + '.m4a'
        with open(file_url, 'wb') as fd:
            for chunk in down_res.iter_content():
                fd.write(chunk)
        pass
    print('01 ' + all_fm_name[0] + '.m4a' + ' 下载成功！')
else:
    for j in range(len(all_fm_id)):
        sound_url = 'https://www.ximalaya.com/revision/play/v1/audio?id=' + all_fm_id[j] + '&ptype=1'
        sound_content = requests.get(sound_url, headers=head, verify=False).text
        down_url = re.compile('src":"(.*?)",', re.S).findall(sound_content)[0]
        down_res = requests.get(down_url, verify=False)

        # 下载文件到指定路径
        try:
            file_url = r'./' + album_name + r'./' + str( j + 1).rjust(2, '0') + ' ' + all_fm_name[j] + '.m4a'
            with open(file_url, 'wb') as fd:
                for chunk in down_res.iter_content():
                    fd.write(chunk)
        except Exception as err:
            all_fm_name[j] = re.sub(u"([^\u4e00-\u9fa5\u0030-\u0039\u0041-\u005a\u0061-\u007a])", "", all_fm_name[j])
            file_url = r'./' + album_name + r'./' + str((i - 1) * 30 + j + 1).rjust(2, '0') + ' ' + all_fm_name[j] + '.m4a'
            with open(file_url, 'wb') as fd:
                for chunk in down_res.iter_content():
                    fd.write(chunk)
            pass
        print(str(j + 1).rjust(2, '0') + ' ' + all_fm_name[j] + '.m4a' + ' 下载成功！')
print()

if len(fm_id) == 0:
    print('专辑：《' + album_name + '》 下载完成')
print()
print('即将自动退出')
time.sleep(3)