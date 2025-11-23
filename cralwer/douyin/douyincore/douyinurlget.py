#ulr获取
from DrissionPage import ChromiumPage, ChromiumOptions
import time
import csv
import json
import os

def write_row_csv(filename, row, fieldnames=None):
    """按行追加写入 CSV。如果文件不存在则写入 header。"""
    try:
        # 确保output目录存在
        output_dir = 'output'
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
        
        # 将文件保存到output目录
        filepath = os.path.join(output_dir, filename)
        
        normalized = {}
        for k, v in row.items():
            if isinstance(v, (list, dict)):
                try:
                    # 将列表/字典转换为JSON字符串，并处理换行符
                    json_str = json.dumps(v, ensure_ascii=False)
                    normalized[k] = json_str.replace('\n', ' ').replace('\r', ' ')
                except Exception:
                    normalized[k] = str(v).replace('\n', ' ').replace('\r', ' ')
            else:
                # 处理普通字符串中的换行符
                normalized[k] = str(v).replace('\n', ' ').replace('\r', ' ') if v is not None else ''

        # 动态获取表头（使用字典键）
        if fieldnames is None:
            fieldnames = list(normalized.keys())

        # 检查文件是否存在以决定是否写入表头
        file_exists = os.path.isfile(filepath) and os.path.getsize(filepath) > 0
        
        with open(filepath, 'a', encoding='utf-8-sig', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            
            # 只有文件不存在或为空时才写入表头
            if not file_exists:
                writer.writeheader()
            
            # 确保只写入fieldnames中定义的字段
            row_to_write = {k: normalized.get(k, '') for k in fieldnames}
            writer.writerow(row_to_write)
            
    except Exception as e:
        print(f"写入 CSV 文件 {filename} 出错: {e}")


#通过搜索关键词获取链接函数
def  Keywordget(keyword,dp,scroll_times):
    scroll_times=50#设置滚动次数
    #启动监听器
    dp.listen.start('search/item')#搜索结果的监听器

    '''方法一，通过主页搜索来访问目标关键词搜索(暂时弃用，点击视频标签会影响滚动)'''

    '''
    #打开抖音首页
    dp.get("https://www.douyin.com")

    # 定位到搜索框的input元素（使用XPath定位）
    search_input = dp.ele('xpath://*[@id="douyin-header"]/div[1]/header/div/div/div[1]/div//input')

    # 预设要输入的关键词
    # keyword = '美食'

    time.sleep(2)
    # 在搜索框中输入关键词并按回车
    search_input.input(f"{keyword}\n")
    time.sleep(2)
    #定位到视频的元素（可能使滚动失效）
    video_element = dp.ele('xpath://*[@id="search-toolbar-container"]/div[1]/div/div/span[3]')
    video_element.click()
    time.sleep(2)

    '''

    '''方法二，直接构建搜索目标页面'''
    dp.get(f'https://www.douyin.com/jingxuan/search/{keyword}?type=video')
    #创建空列表
    r=dp.listen.wait()
    urls=[]
    #创建向下滚动循环
    for i in range(scroll_times):
        data_packets =[]
        if i==0:
            #判断条件并且写入第一条数据包
            if r and hasattr(r, 'response') and hasattr(r.response, 'body'):
                data_packets.append(r)
            else:
                # 跳过无效的r对象
                continue


        #滚动到页面底部
        dp.scroll.to_bottom()
        print(f"已滚动{i+1}次")
        time.sleep(2)




        #创建数据包循环，获取所有数据包
        while True:
            try:
                r=dp.listen.wait(timeout=1)


                if r and hasattr(r, 'response') and hasattr(r.response, 'body'):
                    data_packets.append(r)
                else:
                    # 跳过无效的r对象
                    break
            except:
                break #没有新包，跳过循环


        if len(data_packets) == 0:#没有任何数据包，退出循环
            break


        print(f'共获取到{len(data_packets)}个数据包')
        for r in data_packets:
            json_data=r.response.body

            data=json_data['data']

            #创建for循环将数据存入字典a
            for dt in data:
                aweme_info = dt['aweme_info']
                author_info = aweme_info['author']
                statistics = aweme_info.get('statistics', {})
                
                if 'create_time' in aweme_info:
                    # 将时间戳转换为时间元组
                    time_tuple = time.localtime(aweme_info['create_time'])
                    # 将时间元组格式化为字符串
                    create_time = time.strftime("%Y-%m-%d %H:%M:%S", time_tuple)
                else:
                    create_time = '无信息'
                a={
                    '视频id': aweme_info['aweme_id'],
                    '视频标题': aweme_info['desc'],
                    '创建时间': create_time,
                    '作者昵称': author_info['nickname'],
                    '作者id': author_info['uid'],
                    '作者粉丝数': author_info['follower_count'],
                    '点赞数': statistics.get('digg_count', 0),
                    '评论数': statistics.get('comment_count', 0),
                    '收藏数': statistics.get('collect_count', 0),
                    '分享数': statistics.get('share_count', 0),
                    '播放数': statistics.get('play_count', 0),
                    '视频时长': aweme_info.get('duration', 0)
                }
                #从字典a提取视频id，创建视频链接列表
                video_id=a['视频id']
                urls.append(f"https://www.douyin.com/video/{video_id}")
                
                # 写入CSV文件
                filename = f'{keyword}_search_results.csv'
                write_row_csv(filename, a)





    urlscount=len(urls)
    print(f"已获取到{urlscount}个视频链接")
    return urls



#精确搜索用户主页获取链接函数
def Userget(keyword,dp):
    #创建浏览器实例
    

    urls=[]

    #启动监听器
    dp.listen.start('discover/search')#搜索结果（用户）的监听器

    '''方法一，通过主页搜索来访问目标关键词搜索(暂时弃用，点击标签会影响滚动)'''
    '''
    #打开抖音首页
    dp.get("https://www.douyin.com")

    # 定位到搜索框的input元素（使用XPath定位）
    search_input = dp.ele('xpath://*[@id="douyin-header"]/div[1]/header/div/div/div[1]/div//input')

    # 预设要输入的关键词
    #keyword = '好客山东'


    time.sleep(2)
    # 在搜索框中输入关键词并按回车
    search_input.input(f"{keyword}\n")
    time.sleep(2)
    #定位到用户的元素
    video_element = dp.ele('xpath://*[@id="search-toolbar-container"]/div/div/div/span[5]')
    video_element.click()
    time.sleep(2)


    '''

    #直接创建链接
    dp.get(f'https://www.douyin.com/search/{keyword}?type=user')


    r=dp.listen.wait()

    json_data=r.response.body

    user=json_data['user_list']

    for ue in user:
        user_info=ue['user_info']
        b={
            '用户id': user_info['uid'],
            '构建id': user_info['sec_uid'],
            '用户昵称': user_info['nickname'],
            '用户签名': user_info['signature'],
            '用户粉丝数': user_info['follower_count'],
            '用户获赞数': user_info['total_favorited'],
        }
        print(b)
        #提取构建id和用户昵称
        user_id=b['构建id']
        user_name=b['用户昵称']
        #添加判断条件（严格模式，确保搜索结果是目标用户）
        if user_name==keyword:
            target_url=f"https://www.douyin.com/user/{user_id}"
    
            #关闭监听
            dp.listen.stop()
            break
        else:
            continue
        #创建新的监听器
    dp.listen.start('aweme/post')
    dp.get(target_url)


    #创建循环
    r = dp.listen.wait()
    # 创建向下滚动循环 - 使用while循环替代for循环
    i = 0  # 在循环开始前定义计数器
    while True:  # 设置无限循环，退出机制是data_packets数量为0
        data_packets = []
        if i == 0:
            # 判断条件并且写入第一条数据包
            if r and hasattr(r, 'response') and hasattr(r.response, 'body'):
                data_packets.append(r)
            else:
                continue  # 跳过当前迭代[7,8](@ref)

        # 滚动到页面底部
        scroll_element = dp.ele('css:[class*="scroll-container"]')
        scroll_element.scroll.to_bottom()
        print(f"已滚动{i+1}次")
        time.sleep(2)


        # 创建数据包循环，获取所有数据包
        while True:
            try:
                r = dp.listen.wait(timeout=1)

                if r and hasattr(r, 'response') and hasattr(r.response, 'body'):
                    data_packets.append(r)
                else:
                    # 跳过无效的r对象
                    break
            except:
                break  # 没有新包，跳过循环

        if len(data_packets) == 0:  # 没有任何数据包，退出循环
            print(f'已获取到{len(data_packets)}个数据包')
            print('没有新的数据包，已退出循环')
            break  # 终止循环[6](@ref)

        print(f'共获取到{len(data_packets)}个数据包')
        for r in data_packets:
            json_data = r.response.body
            aweme_list = json_data['aweme_list']
            
            # 创建for循环将数据存入字典
            for aweme in aweme_list:
                statistics = aweme['statistics']
                
                if 'create_time' in aweme and aweme['create_time']:
                    # 将时间戳转换为时间元组
                    time_tuple = time.localtime(aweme['create_time'])
                    # 将时间元组格式化为字符串
                    create_time = time.strftime("%Y-%m-%d %H:%M:%S", time_tuple)
                else:
                    create_time = '无信息'
                c = {
                    '作者id': aweme['author']['uid'],
                    '作者昵称': aweme['author']['nickname'],
                    '视频id': aweme['aweme_id'],
                    '视频标题': aweme['desc'],
                    '创建时间': create_time,
                    '点赞数': statistics['digg_count'],
                    '评论数': statistics['comment_count'],
                    '收藏数': statistics['collect_count'],
                    '分享数': statistics['share_count']
                }
                # 从字典c提取视频id，创建视频链接列表
                video_id = c['视频id']
                urls.append(f"https://www.douyin.com/video/{video_id}")
                
                # 写入CSV文件
                filename = f'{keyword}_user_videos.csv'
                write_row_csv(filename, c)


        r=None  # 重置r以便下一次监听

        i += 1  # 在循环末尾增加计数器[2,5](@ref)

    return urls




#创建主函数

def urlget(choice, keyword, scroll_times):
    # 条件选择器
    co = ChromiumOptions()
    co.set_argument('--headless')
    dp = ChromiumPage()

    urls = []  # 初始化urls列表

    # 创建判断条件
    if choice == 1:
        urls = Keywordget(keyword, dp, scroll_times)
    elif choice == 2:
        urls = Userget(keyword, dp)
    else:
        print("无效的选择！")

    return urls  # 返回urls列表

if __name__ == '__main__':
    print("请选择搜索模式：\n1.关键词搜索\n2.目标用户主页")
    choice = int(input("请输入你的选择："))
    keyword = input("请输入关键词/用户名：")
    scroll_times=5#设置滚动次数
    urls = urlget(choice, keyword, scroll_times)
    print(len(urls))
