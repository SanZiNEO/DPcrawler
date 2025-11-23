import douyincore
if __name__ == "__main__":
    # 调用urlget函数并接收返回的urls列表
    # 设置urlget所需的参数 
    choice = 1  # 操作选择 (根据实际功能调整，例如1表示搜索)
    #创建列表循环
    keywords = [
        '美食',
        '旅行',
           ]     # 搜索关键词 (根据需求修改,可以是多个)      

    scroll_times = 5
    for keyword in keywords:

        # 调用urlget函数并接收返回的urls列表
        urls = douyincore.douyinurlget.urlget(choice, keyword,scroll_times)


        # 打印获取到的urls数量和内容
        print(f"Main received {len(urls)} urls:")

        # 如果获取到了urls，则传递给爬虫处理
        if urls:
            print(f"开始处理视频链接... (共{len(urls)}个)")
        
            print("使用单线程模式")
            for i, url in enumerate(urls):
                print(f"正在处理第 {i+1} 个视频: {url}")
                douyincore.douyincrawler.crawler(url)
        else:
            print("未获取到任何视频链接")