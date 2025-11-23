from DrissionPage import ChromiumPage, ChromiumOptions
import time
import random
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


def process_comments(json_data, video_id):
    """处理评论数据包，区分主评论和二级评论"""
    comments = json_data.get('comments', [])
    
    for index in comments:
        ip_label = index.get('ip_label', '无IP')
        user_info = index.get('user', {})
        signature = user_info.get('signature', '无签名') if isinstance(user_info, dict) else '无签名'
        create_time = index.get('create_time', '')
        
        if index.get('level', 1) == 1:  # 主评论
            comment_dit = {
                "用户": user_info.get('nickname', ''),
                "用户ID": user_info.get('sec_uid', ''),
                "内容": index.get('text', ''),
                "点赞数": index.get('digg_count', 0),
                "回复数": index.get('reply_comment_total', 0),
                "时间": create_time,
                "评论ID": index.get('cid', ''),
                "IP地址": ip_label,
                "用户头像": user_info.get('avatar_thumb', {}).get('url_list', [''])[0] if user_info.get('avatar_thumb') else '',
                "是否热门": index.get('is_hot', False),
                "用户主页链接": f"https://www.douyin.com/user/{user_info.get('sec_uid', '')}" if user_info.get('sec_uid') else '',
                "用户UID": user_info.get('uid', ''),
                "用户签名": signature,
                "图片链接": index.get('image_list', ''),
                "表情链接": index.get('sticker', {}).get('static_url', {}).get('url_list', [''])[0] if index.get('sticker') else '',
                "评论层级": 1
            }
            from datetime import datetime
            current_date = datetime.now().strftime('%Y%m%d')
            prefix = os.path.splitext('comment.csv')[0]
            new_filename = f"{prefix}_{video_id}_{current_date}.csv"
            write_row_csv(new_filename, comment_dit)
            
            rc_list = index.get('reply_comment', [])
            if isinstance(rc_list, list) and rc_list:
                for sub in rc_list:
                    try:
                        sub_user = sub.get('user', {}) if isinstance(sub, dict) else {}
                        sub_create_time = sub.get('create_time', '')
                        reply_dit = {
                            "用户": sub_user.get('nickname', ''),
                            "用户ID": sub_user.get('sec_uid', ''),
                            "指向用户": sub.get('reply_to_reply_id', '0'),
                            "内容": sub.get('text', ''),
                            "点赞数": sub.get('digg_count', 0),
                            "时间": sub_create_time,
                            "IP地址": sub.get('ip_label', ip_label),
                            "评论ID": sub.get('cid', ''),
                            "用户头像": sub_user.get('avatar_thumb', {}).get('url_list', [''])[0] if sub_user.get('avatar_thumb') else '',
                            "用户主页链接": f"https://www.douyin.com/user/{sub_user.get('sec_uid', '')}" if sub_user.get('sec_uid') else '',
                            "回复ID": sub.get('reply_id', index.get('cid', '0')),
                            "根评论ID": index.get('cid', sub.get('reply_id', '0')),
                            "评论层级": sub.get('level', 2),
                            "回复总数": sub.get('comment_reply_total', 0),
                            "用户UID": sub_user.get('uid', ''),
                            "用户签名": sub_user.get('signature', ''),
                            "图片链接": sub.get('image_list', ''),
                            "表情链接": sub.get('sticker', {}).get('static_url', {}).get('url_list', [''])[0] if sub.get('sticker') else '',
                        }
                        from datetime import datetime
                        current_date = datetime.now().strftime('%Y%m%d')
                        prefix = os.path.splitext('subcomment.csv')[0]
                        new_filename = f"{prefix}_{video_id}_{current_date}.csv"
                        write_row_csv(new_filename, reply_dit)
                    except Exception as e:
                        print(f"处理嵌套回复时出错: {e}")
        else:  # 二级评论
            comment_dit = {
                "用户": index.get('user', {}).get('nickname', ''),
                "用户ID": index.get('user', {}).get('sec_uid', ''),
                "指向用户": index.get('reply_to_reply_id', '0'),
                "内容": index.get('text', ''),
                "点赞数": index.get('digg_count', 0),
                "时间": create_time,
                "IP地址": ip_label,
                "评论ID": index.get('cid', ''),
                "用户头像": index.get('user', {}).get('avatar_thumb', {}).get('url_list', [''])[0] if index.get('user', {}).get('avatar_thumb') else '',
                "用户主页链接": f"https://www.douyin.com/user/{index.get('user', {}).get('sec_uid', '')}" if index.get('user', {}).get('sec_uid') else '',
                "回复ID": index.get('reply_id', '0'),
                "根评论ID": index.get('root_comment_id', index.get('reply_id', '0')),
                "评论层级": index.get('level', 2),
                "回复总数": index.get('comment_reply_total'),
                "用户UID": index.get('user', {}).get('uid', ''),
                "用户签名": signature,
                "图片链接": index.get('image_list', ''),
                "表情链接": index.get('sticker', {}).get('static_url', {}).get('url_list', [''])[0] if index.get('sticker') else '',
            }
            from datetime import datetime
            current_date = datetime.now().strftime('%Y%m%d')
            prefix = os.path.splitext('subcomment.csv')[0]
            new_filename = f"{prefix}_{video_id}_{current_date}.csv"
            write_row_csv(new_filename, comment_dit)
def dataget(dp, video_id):
    #载入所有可能数据包  
    while True:
        try:
            print('监听评论数据包...')
            r=dp.listen.wait(timeout=1)
            if r and getattr(r.request, 'method','').upper()=='GET':
                try:

                    json_data=r.response.body
                    print('获取到评论数据，正在处理...')
                    process_comments(json_data, video_id)
                except:
                    print('json_data获取失败')
                    continue
            else:
                print('r 获取失败')
                break
        except:
            print('监听超时')
            break

def comment_get(dp, video_id):
    #定义状态变量
    scroll_down=True
    button_click=True
    #创建整体循环

    while True:
        if scroll_down==True:
            #滚动循环
            for i in range(5):
                text ='加载中'
                try:
                    # 定位加载中元素（使用短超时避免长时间等待）
                    # 匹配以"加载"开头的文本
                    tab = dp.ele(f'xpath://*[text()="{text}" and not(self::script[@nonce="" and @crossorigin="anonymous"])]', timeout=0.5)

                    
                    # 如果找到元素，滚动到元素可见区域
                    if tab:
                        print(f'找到"{text}"元素')
                        try:
                            print('尝试滚动中...')
                            tab.scroll.to_see(text)
                            #获取评论
                            dataget(dp, video_id)
                        except:
                            try:
                                bottom = dp.ele(f'text:暂时没有更多', timeout=0.5)
                                print('找到"暂时没有更多"元素')
                                if bottom:
                                    scroll_down=False
                                    print('将scroll_down设为False')
                                    button_click = True
                                break
                            except:
                                break
                    else:
                        try:
                            bottom = dp.ele(f'text:暂时没有更多', timeout=0.5)

                            if bottom:
                                print('找到"暂时没有更多"元素')
                                scroll_down=False
                                print('将scroll_down设为False')
                                button_click = True
                            break
                        except:
                            break
                except:
                    try:
                        bottom = dp.ele(f'text:暂时没有更多', timeout=0.5)
                        
                        if bottom:
                            print('找到"暂时没有更多"元素')
                            scroll_down=False
                            print('将scroll_down设为False')
                            button_click = True
                        break
                    except:
                        break
        
        if button_click==True:
            #创建点击按钮循环：
            for i in range(5):
                #查找按钮并点击
                # 使用XPath定位包含"展开"文本的按钮
                xpath_pattern = '//span[contains(text(), "展开")]'
                buttons = dp.eles(f'xpath:{xpath_pattern}')
                print(f'找到{len(buttons)}个"展开"按钮')
                # 如果没有找到按钮，设置button_click为False
                if not buttons:
                    button_click = False
                    print('将button_click设为False')
                    break
        
                # 遍历找到的所有展开按钮
                for btn in buttons:
                    # 将按钮滚动到视图中（居中显示）
                    dp.scroll.to_see(btn, center=True)
                    print('滚动到展开按钮')
                    try:
                        dataget(dp, video_id)
                    except:
                        continue

                    # 添加短暂延迟确保元素完全可见
                    time.sleep(0.05)
                    
                    # 点击展开按钮
                    btn.click()
                    print('点击展开按钮')
                    try:
                        dataget(dp, video_id)
                    except:
                        continue
                    # 点击后等待页面响应
                    time.sleep(0.1)
        #退出条件
        if scroll_down == False and button_click==False:
            print('达到退出条件，程序结束')
            break


def crawl_video_content(dp, url):
    """爬取视频内容信息"""
    try:
        dp.listen.start('/aweme/v1/web/aweme/detail')
        dp.get(url)
        time.sleep(2)
        r = dp.listen.wait()
        json_data = r.response.body

        content = json_data.get('aweme_detail', {})
        author = content.get('author', {})
        stats = content.get('statistics', {})
        video = content.get('video', {})
        music = content.get('music', {})
        
        content_dit = {
            "标题": content.get('desc', ''),
            "作者": author.get('nickname', ''),
            "作者UID": author.get('uid', ''),
            "作者唯一ID": author.get('unique_id', ''),
            "作者签名": author.get('signature', ''),
            "作者粉丝数": author.get('follower_count', 0),
            "作者获赞数": author.get('total_favorited', 0),
            "视频ID": content.get('aweme_id', ''),
            "创建时间": content.get('create_time', ''),
            "视频时长(毫秒)": content.get('duration', 0),
            "视频类型": content.get('aweme_type', ''),
            "视频标签": [tag.get('hashtag_name') for tag in content.get('text_extra', []) if isinstance(tag, dict) and tag.get('hashtag_name')] if content.get('text_extra') else [],
            "视频描述": content.get('desc', ''),
            "点赞数": stats.get('digg_count', 0),
            "评论数": stats.get('comment_count', 0),
            "分享数": stats.get('share_count', 0),
            "收藏数": stats.get('collect_count', 0),
            "播放次数": stats.get('play_count', 0),
            "视频封面URL": video.get('cover', {}).get('url_list', [''])[0] if video.get('cover') else '',
            "视频原封面URL": video.get('origin_cover', {}).get('url_list', [''])[0] if video.get('origin_cover') else '',
            "视频动态封面URL": video.get('dynamic_cover', {}).get('url_list', [''])[0] if video.get('dynamic_cover') else '',
            "视频宽度": video.get('width', '') if video.get('width') else '',
            "视频高度": video.get('height', '') if video.get('height') else '',
            "视频格式": video.get('format', '') if video.get('format') else '',
            "音乐标题": music.get('title', '') if music.get('title') else '',
            "音乐作者": music.get('author', '') if music.get('author') else '',
            "音乐ID": music.get('id', '') if music.get('id') else '',
            "音乐时长": music.get('duration', 0) if music.get('duration') else 0,
            "音乐播放URL": music.get('play_url', {}).get('url_list', [''])[0] if music.get('play_url') else '',
            "地区": content.get('region', ''),
            "视频状态": content.get('status', {}).get('private_status', ''),
            "是否原创": content.get('original', False),
        }
        
#从字典里获取字段评论数
        from datetime import datetime
        current_date = datetime.now().strftime('%Y%m%d')
        video_id = content.get('aweme_id', 'unknown')
        prefix = os.path.splitext('content.csv')[0]
        new_filename = f"{prefix}_{video_id}_{current_date}.csv"
        write_row_csv(new_filename, content_dit)

        # 从字典里获取字段评论数
        comment_count = content_dit["评论数"]
        
        dp.listen.stop()
        return {
            'content': content,
            'comment_count': comment_count,
            'video_id': video_id
        }
    
    except Exception as e:
        print(f"爬取视频内容时出错: {e}")
        return None


def crawl_author_info(dp, content):
    """爬取作者信息"""
    try:
        dp.listen.start('user/profile')
        sec_uid = content.get('author', {}).get('sec_uid', '')
        
        if not sec_uid:
            print("未找到作者 sec_uid，跳过作者信息抓取")
            return

        dp.get(f'https://www.douyin.com/user/{sec_uid}')
        r = dp.listen.wait()
        json_data = r.response.body
        
        author = json_data.get('user', {})
        author_dit = {
            "昵称": author.get('nickname', ''),
            "抖音号": author.get('unique_id', ''),
            "签名": author.get('signature', ''),
            "签名": author.get('signature', ''),
            "粉丝数": author.get('follower_count', 0),
            "关注数": author.get('following_count', 0),
            "获赞数": author.get('total_favorited', 0),
            "作品数": author.get('aweme_count', 0),
            "UID": author.get('uid', ''),
            "安全UID": author.get('sec_uid', ''),
            "头像URL": author.get('avatar_thumb', {}).get('url_list', [''])[0] if author.get('avatar_thumb') else '',
            "头像大图URL": author.get('avatar_larger', {}).get('url_list', [''])[0] if author.get('avatar_larger') else '',
            "认证信息": author.get('custom_verify', ''),
            "企业认证原因": author.get('enterprise_verify_reason', ''),
            "地区": (author.get('country', '') or '') + (author.get('province', '') or '') + (author.get('city', '') or ''),
            "性别": "男" if author.get('gender') == 1 else ("女" if author.get('gender') == 2 else "未知"),
            "生日隐藏级别": author.get('birthday_hide_level', ''),
            "是否私密账号": author.get('secret') == 1,
            "直播状态": author.get('live_status', ''),
            "直播电商权限": author.get('live_commerce', ''),
            "电商入口": author.get('with_commerce_entry', ''),
            "个人资料封面URL": author.get('cover_url', [{}])[0].get('url_list', [''])[0] if author.get('cover_url') else '',
            "学校": author.get('school_name', ''),
            "年龄": author.get('user_age', ''),
            "是否被封禁": author.get('is_ban', False),
            "是否被拉黑": author.get('is_block', False),
            "IP归属地": author.get('ip_location', '') or '无IP',
            "收藏数": author.get('favoriting_count', 0),
            "动态数": author.get('dongtai_count', 0),
            "合集数": author.get('series_count', 0),
        }
        
        from datetime import datetime
        current_date = datetime.now().strftime('%Y%m%d')
        video_id = content.get('aweme_id', 'unknown')
        prefix = os.path.splitext('author.csv')[0]
        new_filename = f"{prefix}_{video_id}_{current_date}.csv"
        write_row_csv(new_filename, author_dit)

        dp.listen.stop()
    except Exception as e:
        print(f"爬取作者信息时出错: {e}")


def crawler(url):
    """处理单个URL的爬虫函数"""
    print(f"启动抖音评论爬虫程序，处理URL: {url}")
    # 为每个线程组创建独立的浏览器实例配置
    co = ChromiumOptions()

    
    # 创建隔离的浏览器实例
    dp = ChromiumPage(co)

    # 1. 爬取视频内容
    print("正在爬取视频内容...")
    result = crawl_video_content(dp, url)
    
    if not result or not result.get('content'):
        print("视频内容爬取失败，跳过作者和评论爬取")
        dp.quit()
        return
        
    content = result['content']
    comment_count = result['comment_count']
    video_id = result['video_id']

    # 2. 爬取作者信息
    print("正在爬取作者信息...")
    crawl_author_info(dp, content)
    
    # 3. 爬取评论
    if comment_count > 0:
        print("正在爬取评论...")
        try:
            dp.listen.start('comment/list')
            dp.get(url)
            try:
                dataget(dp, video_id)
            except:
                print('初始数据获取失败')
            comment_get(dp, video_id)
        except Exception as e:
            print(f'评论爬取过程中出错: {e}')
    else:
        print(f"评论数为 {comment_count}，无需爬取评论")

    print("程序执行完毕")
    dp.quit()


def main():
    print("启动抖音评论爬虫程序...")
    co= ChromiumOptions()
    co.set_argument('--headless')
    dp = ChromiumPage(co)
    
    url = 'https://www.douyin.com/video/7544641347483979017' 

    # 1. 爬取视频内容
    print("正在爬取视频内容...")
    result = crawl_video_content(dp, url)
    
    if not result or not result.get('content'):
        print("视频内容爬取失败，跳过作者和评论爬取")
        dp.quit()
        return
        
    content = result['content']
    comment_count = result['comment_count']
    video_id = result['video_id']

    # 2. 爬取作者信息
    print("正在爬取作者信息...")
    crawl_author_info(dp, content)
    
    # 3. 爬取评论
    if comment_count > 0:
        print("正在爬取评论...")
        try:
            dp.listen.start('comment/list')
            dp.get(url)
            try:
                dataget(dp, video_id)
            except:
                print('初始数据获取失败')
            comment_get(dp, video_id)
        except Exception as e:
            print(f'评论爬取过程中出错: {e}')
    else:
        print(f"评论数为 {comment_count}，无需爬取评论")

    dp.quit()

    print("程序执行完毕")


if __name__ == "__main__":
    main()