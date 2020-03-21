"""
网址爬取模式适用于如下形式
【url0/[类目：album_kind]/[一级编号：album_id]/[二级编号：fm_id]/】
只要是这个格式的网址，更改对应这正则就可使用

1、文件会自动下载到含有专辑名称的文件夹下
2、解决了非法名称不能创建文件的问题
3、解决了下载音频逆序的问题
4、优化了下载速度（通过抓取更简单的页面结构）
5、免登入下载

可能会更新：
    VIP下载、付费下载
    搜索下载

"""
import os
import time
import re
import requests
from requests.packages.urllib3.exceptions import InsecureRequestWarning
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)


# 【配置】
# 用户代理
User_Agent = {'User-Agent': "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) "
                            "Chrome/80.0.3987.116 Safari/537.36"}
# 下载站点域名
url0 = 'https://www.ximalaya.com/'
# 排序方式；0为正序；1为倒序
album_sort = 0
# 单页面展示音频的数量，不一定能实现
album_size = 30
print()

# 【处理输入信息】
input_url = input('请输入需要下载的专辑网址：')
# 获取专辑ID
album_id = str(re.compile('(\d{1,10})', re.S).findall(input_url)[0])

# 【信息抓取部分】
album_params = {"albumId": album_id,"sort": album_sort}
# 构造专辑网址
album_url = url0+"revision/album"
# 专辑网址内容
album_content = requests.get(album_url, headers=User_Agent, verify=False,params=album_params).text
# 提取专辑名称
album_name = re.compile('albumTitle":"(.*?)"', re.S).findall(album_content)[0]
# 提取音频数量
album_num = re.compile('"trackTotalCount":(\d{1,10}),', re.S).findall(album_content)[0]
page_num = int(album_num) // album_size + 1
print()
print('准备下载：《' + album_name + '》 一共' + album_num + '个音频')
print()
#
# 【动态加载页面】
for i in range(1, int(page_num)+1):
    print("---开始下载第"+str(i)+"页---")
    print()
    page_url = "https://www.ximalaya.com/revision/album/v1/getTracksList"
    fm_params = {"albumId": album_id, "pageNum": i, "sort": album_sort}
    fm_content = requests.get(page_url, headers=User_Agent, verify=False, params=fm_params).text  # 声音页面内容
    fm_name = re.compile('"title":"(.*?)"', re.S).findall(fm_content)  # 提取声音列表
    fm_id = re.compile('"trackId":(\d{1,10}),', re.S).findall(fm_content)  # 9位数文件页面编号

    # 【文件下载部分】
    if not os.path.exists(r'./' + r'./' + album_name):
        os.makedirs(r'./' + r'./' + album_name)

    for j in range(len(fm_id)):
        fm_url = 'https://www.ximalaya.com/revision/play/v1/audio?id=' + fm_id[j] + '&ptype=1'
        fm_content = requests.get(fm_url, headers=User_Agent, verify=False).text
        down_url = re.compile('src":"(.*?)",', re.S).findall(fm_content)[0]
        down_res = requests.get(down_url, verify=False)

        try:
            file_url = r'./' + album_name + r'./' + str((i - 1) * 30 + j + 1) + '_' + fm_name[j] + '.m4a'
            with open(file_url, 'wb') as fd:
                for chunk in down_res.iter_content():
                    fd.write(chunk)
            print('【' + str((i - 1) * 30 + j+1) + '】 ' + str((i - 1) * 30 + j+1) + '_' + fm_name[j] + '.m4a' + ' 下载成功！')
        except Exception as err:
            fm_name[j] = re.sub(u"([^\u4e00-\u9fa5\u0030-\u0039\u0041-\u005a\u0061-\u007a])", "", fm_name[j])
            file_url = r'./' + album_name + r'./' + str((i - 1) * 30 + j + 1) + '_' + fm_name[j] + '.m4a'
            with open(file_url, 'wb') as fd:
                for chunk in down_res.iter_content():
                    fd.write(chunk)
            print('【' + str((i - 1) * 30 + j+1) + '】 ' + str((i - 1) * 30 + j+1) + '_' + fm_name[j] + '.m4a' + ' 下载成功！')
            pass

    print()
    print("---第" + str(i) + "页下载完成---")
    print()
print('专辑：《' + album_name + '》 下载完成')
print()
print('即将自动退出')
t1 = time.time()
time.sleep(3)