import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
from selenium.common.exceptions import StaleElementReferenceException

driver = webdriver.Edge()

URL = 'https://sspai.com/post/90287'

comment_count = 0

def scroll_and_expand_comments():

    # 返回<body>元素的整体高度，包括不可见的部分
    last_height = driver.execute_script("return document.body.scrollHeight")
        # driver.execute_script用于在当前浏览的页面中执行JavaScript代码
    
    while True:
        # 滚动到页面底部
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            # 0是x坐标，表示水平方向不滚动
            # document.body.scrollHeight是y坐标，表示滚动到页面最底部
        time.sleep(2)  # 等待页面加载

        # 尝试展开所有可见的评论
        expand_buttons = driver.find_elements(By.XPATH, "//span[contains(.,'...展开')]")
            # driver.find_elements用于查找网页上的多个元素,返回的是一个元素列表
            # By.XPATH用于在XML文档中导航
            # //表示在文档的任何位置搜索(不从根节点开始)
            # span表示查找所有的span元素(展开按钮的标签)
            # .表示当前节点的文本内容
            # contains()是一个XPATH函数，检查第一个参数是否包含第二个参数
        for button in expand_buttons:
            try:
                driver.execute_script("arguments[0].click();", button)  # 模拟鼠标点击
                time.sleep(0.5)  # 给予一些时间让评论展开
            except StaleElementReferenceException:
                pass  # 忽略已经消失的元素

        # 检查是否到达页面底部
        new_height = driver.execute_script("return document.body.scrollHeight")
        if new_height == last_height:
            break
        last_height = new_height

try:
    # 使用 Selenium 加载页面
    driver.get(URL)

    # 等待评论区域加载
    WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.CLASS_NAME, "comment-list-wrapper"))  # 检测这个类名在不在源代码中
    )

    # 滚动页面并展开评论
    scroll_and_expand_comments()

    # 获取页面源码
    page_source = driver.page_source
    
    # 使用 BeautifulSoup 解析页面源码
    soup = BeautifulSoup(page_source, 'lxml')

    # 找到最外层的评论列表容器
    comment_list = soup.find('div', class_='comment-list-wrapper')


    # 找到所有的评论项
    comment_items = comment_list.find_all('div', class_='comment-item-wrapper')

    for parent_index, item in enumerate(comment_items, 1):
        # 先打开主评论
        parent_wrapper = item.find('div', class_='comment-parent-wrapper')
        parent_content_div = parent_wrapper.find('div', class_='_content')
            # 寻找展开或未展开的评论内容
        parent_comment_span = parent_content_div.find('span', class_=['wangEditor-txt', 'wangEditor-txt block'])
            # 未展开的类是wangEditor-txt
            # 展开的类是wangEditor-txt block
                
        print("-----------------------------------------------------------------")
        print(f"第{parent_index}个主评论说: {parent_comment_span.text.strip()}")  # 打印带序号的评论内容
        print("-----------------------------------------------------------------\n")
        comment_count = comment_count + 1
                

        # 再打开子评论
        children_wrapper = item.find('div', class_='comment-children-wrapper')
        if children_wrapper:
            children_items = children_wrapper.find_all('div', class_='_content')

            for children_index, children_item in enumerate(children_items, 1):
                children_comment_span = children_item.find('span', class_=['wangEditor-txt', 'wangEditor-txt block'])
                print("    **********************************************")
                print(f"    第{children_index}个子评论说: {children_comment_span.text.strip()}")
                print("    **********************************************\n")
                comment_count = comment_count + 1

        print("\n\n")
            
            

    

    # 等待一段时间，以便观察浏览器
    print("\n\n脚本执行完毕。浏览器将在3秒后自动关闭")
    print(f"本次共爬取到{comment_count}个评论~")
    time.sleep(3)

finally:
    driver.quit()


