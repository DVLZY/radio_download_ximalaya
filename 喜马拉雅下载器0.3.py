"""
网址爬取模式适用于如下形式
【url0/[类目：kind]/[一级编号：id1]/[二级编号：id2/】
只要是这个格式的网址，更改对应这正则就可使用

1、文件会自动下载到含有专辑名称的文件夹下
2、解决了非法名称不能创建文件的问题
3、解决了下载音频逆序的问题
4、优化了下载速度（通过抓取更简单的页面结构）
5、免登入下载

可能会更新：
    VIP下载、付费下载
"""
print('''
---------------------喜马拉雅下载器0.3--------------------
---------------------By Davies_LIN----------------------
---------1、文件会自动下载到含有专辑名称的文件夹下-----------
--------2、优化了下载速度 通过抓取更简单的页面结构  ---------
---------3、免登入即可下载--------------------------------
''')

import os
import time
import re
import requests
from requests.packages.urllib3.exceptions import InsecureRequestWarning

requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

# 【配置】
User_Agent = {'User-Agent': "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) "
                            "Chrome/80.0.3987.116 Safari/537.36"}  # 用户代理
url0 = 'https://www.ximalaya.com/'  # 下载站点域名
page_sort = 0  # 排序方式；0为正序；1为倒序
page_size = 30  # 页面展示数量

# 【输入】处理用户输入内容
search_key = input('请输入要下载的专辑名称或者网址：')

# 【用关键词搜索的方式下载】
album_id = re.compile('(\d{3,10})', re.S).findall(search_key)  # 尝试从输入的内容中提取专辑ID
if len(album_id) == 0:  # 如果无法提取出专辑ID则在网页中搜索输入的关键词
    search_url = url0 + 'search/album/' + search_key
    search_contect = requests.get(search_url, headers=User_Agent, verify=False).text  # 专辑名称列表
    ablum_name_list = re.compile('","title":"(.*?)","categoryId', re.S).findall(search_contect)  # 专辑ID列表
    ablum_id_list = re.compile('"id":(.*?),"playCount"', re.S).findall(search_contect)  # 专辑是否付费列表
    ablum_paid_list = re.compile('","isPaid":(.*?),"vipType"', re.S).findall(search_contect)  # 作者ID列表
    ablum_anchor_list = re.compile('"anchor":(\d{1,11})', re.S).findall(search_contect)  # 作者ID——姓名列表
    # 制作作者ID——姓名的字典
    ablum_anchor_name_list = re.compile('"id":(\d{1,11}),"nickname":"(.*?)",', re.S).findall(search_contect)
    anchor_id_name = {}
    for ablum_anchor_name in ablum_anchor_name_list:
        anchor_id_name[ablum_anchor_name[0]] = ablum_anchor_name[1]
    # 输出可下载的专辑列表
    for i in range(len(ablum_name_list)):
        if ablum_paid_list[i] == 'false':
            print('【' + str(i + 1) + '】 《' + ablum_name_list[i] + '》_' + anchor_id_name[ablum_anchor_list[i]])
        else:
            print('【付费产品无法下载】 《' + ablum_name_list[i] + '》_' + anchor_id_name[ablum_anchor_list[i]])
    # 让用户输入要下载的专辑的编号，并换算成对应的专辑ID
    album_id = ablum_id_list[int(input('请输入要下载的专辑编号:')) - 1]

print()

# 【用网址匹配的方式下载】
album_params = {"albumId": album_id, "sort": page_sort}  # 构造网址头信息
album_url = url0 + "revision/album"  # 构造专辑网址
album_content = requests.get(album_url, headers=User_Agent, verify=False, params=album_params).text  # 专辑网址内容
album_name = re.compile('albumTitle":"(.*?)"', re.S).findall(album_content)[0]  # 提取专辑名称
album_num = re.compile('"trackTotalCount":(\d{1,10}),', re.S).findall(album_content)[0]  # 提取音频数量
page_num = int(album_num) // page_size + 1
print()
print('准备下载：《' + album_name + '》 一共' + album_num + '个音频')
print()

# 【动态加载页面】
for i in range(1, int(page_num) + 1):
    print("---开始下载第" + str(i) + "页---")
    print()
    fm_url = "https://www.ximalaya.com/revision/album/v1/getTracksList"
    fm_params = {"albumId": album_id, "pageNum": i, "sort": page_sort}
    fm_content = requests.get(fm_url, headers=User_Agent, verify=False, params=fm_params).text  # 获取声音页面内容
    fm_name_list = re.compile('"title":"(.*?)"', re.S).findall(fm_content)  # 提取声音列表
    fm_id_list = re.compile('"trackId":(\d{1,10}),', re.S).findall(fm_content)  # 提取声音编号列表

    # 【文件下载部分】
    # 创建文件夹
    if not os.path.exists(r'./' + r'./' + album_name):  # 判断文件夹是否存在
        os.makedirs(r'./' + r'./' + album_name)  # 如果不存在则创建文件夹
    # 提取真实下载地址
    for j in range(len(fm_id_list)):
        sound_url = 'https://www.ximalaya.com/revision/play/v1/audio?id=' + fm_id_list[j] + '&ptype=1'
        sound_content = requests.get(sound_url, headers=User_Agent, verify=False).text
        down_url = re.compile('src":"(.*?)",', re.S).findall(sound_content)[0]
        down_res = requests.get(down_url, verify=False)
        # 下载文件到指定路径
        try:
            file_url = r'./' + album_name + r'./' + str((i - 1) * 30 + j + 1) + '_' + fm_name_list[j] + '.m4a'
            with open(file_url, 'wb') as fd:
                for chunk in down_res.iter_content():
                    fd.write(chunk)
            print('【' + str((i - 1) * 30 + j + 1) + '】 ' + str((i - 1) * 30 + j + 1) + '_' + fm_name_list[
                j] + '.m4a' + ' 下载成功！')
        except Exception as err:
            fm_name_list[j] = re.sub(u"([^\u4e00-\u9fa5\u0030-\u0039\u0041-\u005a\u0061-\u007a])", "", fm_name_list[j])
            file_url = r'./' + album_name + r'./' + str((i - 1) * 30 + j + 1) + '_' + fm_name_list[j] + '.m4a'
            with open(file_url, 'wb') as fd:
                for chunk in down_res.iter_content():
                    fd.write(chunk)
            print('【' + str((i - 1) * 30 + j + 1) + '】 ' + str((i - 1) * 30 + j + 1) + '_' + fm_name_list[
                j] + '.m4a' + ' 下载成功！')
            pass

    print()
    print("---第" + str(i) + "页下载完成---")
    print()
print('专辑：《' + album_name + '》 下载完成')
print()
print('即将自动退出')
t1 = time.time()
time.sleep(3)
