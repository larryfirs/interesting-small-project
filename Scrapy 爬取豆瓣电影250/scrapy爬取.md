## scrapy学习(豆瓣电影top250为例)

1、安装scrapy库	`pip install scrapy`

2、进入到目标文件夹下创建一个新的scrapy项目

```python
cd scrapy   #进入目标文件夹
scrapy startproject douban_top  #创建一个名为douban_top的爬虫项目
# 创建好项目后，进入项目中的子文件夹douban_top中，创建爬虫文件
cd douban_top
cd douban_top
#doubantop是爬虫文件的名称，movie.douban.com是需要爬取的网站网址去除https://
scrapy genspider doubantop movie.douban.com
```

3、执行后，如图所示：

​	![](C:\Users\sune\Desktop\2.jpg)

4、项目文件结构及作用

- **`scrapy.cfg`:** 项目的配置文件，包含了 Scrapy 项目的配置信息，比如项目的名称以及项目中使用的设置文件位置等。
- **`myproject/`**: 项目的 Python 包，包含了项目的代码和其他资源文件。
  - **`__init__.py`**: 表明该目录是一个 Python 包。
  - **`items.py`**: 可选的文件，用于定义爬取的数据结构，通常使用 Scrapy 的 Item 类来定义数据模型。
  - **`middlewares.py`**: 可选的文件，包含了自定义的中间件，用于在请求和响应之间进行操作，例如添加代理、用户代理等。
  - **`pipelines.py`**: 可选的文件，包含了自定义的管道，用于对爬取到的数据进行处理，例如数据清洗、存储等操作。
  - **`settings.py`**: 项目的设置文件，包含了各种配置选项，如爬虫的延迟时间、并发请求数、用户代理等。
  - **`spiders/`**: 存放爬虫代码的目录，每个爬虫通常都是一个单独的 Python 文件。
    - **`__init__.py`**: 表明该目录是一个 Python 包。

5、实战开始



5.1  定义数据结构

```python
# items.py
 
import scrapy
class MovieItem(scrapy.Item):
    # 定义了要爬取的关键信息字段
    ranking = scrapy.Field()    # 排名
    name = scrapy.Field()       # 电影名
    introduce = scrapy.Field()  # 简介
    star = scrapy.Field()       # 星级
    comments = scrapy.Field()   # 评论数
    describe = scrapy.Field()   # 描述
```

5.2  编写爬虫程序

​	需要注意的是：使用xpath提取数据时，当网站源码变幻时需要及时修改代码

```python
# doubantop.py
 
import scrapy
# 使用相对导入的方式，从doubantop.py所在模块spiders的上一级目录douban_top里的items模块中导入MovieItem类
from ..items import MovieItem   # .. 表示上一级目录
# 定义爬虫程序
class DoubantopSpider(scrapy.Spider):
    """
    该 Spider 用于爬取豆瓣电影 Top250 页面的信息
    """
    
    name = 'doubantop'  # Spider 的名称，即该爬虫文件的名称
    allowed_domains = ['movie.douban.com']  # 允许爬取的域名
    start_urls = ['https://movie.douban.com/top250']  # 起始 URL（网址）
    
    """
    parse 方法是 Scrapy 中用于解析页面响应的方法
    当Scrapy发起请求并获取到页面响应后，会自动调用parse方法来处理响应，并用其中编写代码来提取数据
    parse方法中的response参数包含了爬取到的页面响应，可以使用它来提取页面中的信息
    """
    def parse(self, response):
        """
        解析页面响应，提取电影信息并存储到 MovieItem 对象中
        输入参数: 爬取到的页面响应
        返回值: MovieItem 对象
        """
        # 使用 XPath 选择器提取电影信息
        movies = response.xpath('//div[@class="item"]')   # 选取了页面中所有 class 属性为 "item" 的 div 元素，这些元素包含了每部电影的信息
        for movie in movies:
            item = MovieItem()  # 创建 MovieItem 对象来存储电影信息
            """
            需要注意的是：从movie中提取数据时，应以.//开头，表示从当前节点开始选择元素，而不是从整个文档开始选择元素。
            """
            # 提取电影排名信息
            item['ranking'] = movie.xpath('.//em/text()').get()
            # 提取电影名称
            item['name'] = movie.xpath('.//span[@class="title"]/text()').get()
            # 提取电影简介
            item['introduce'] = movie.xpath('.//span[@class="inq"]/text()').get()
            # 提取电影星级评分
            item['star'] = movie.xpath('.//div[@class="star"]/span[@class="rating_num"]/text()').get()
            # 提取电影评论数
            item['comments'] = movie.xpath('.//div[@class="star"]/span[4]/text()').get()
            # 提取电影描述信息
            item['describe'] = movie.xpath('.//div[@class="bd"]/p[1]/text()').get()
            yield item  # 将 MovieItem 对象传递给 Scrapy 引擎

        # 继续爬取下一页数据
        next_page = response.xpath('//span[@class="next"]/a/@href').get()
        # 判断下一页的链接是否为空，若下一页存在，则继续爬取下一页数据
        if next_page:
            yield scrapy.Request(response.urljoin(next_page), callback=self.parse)
            # response.urljoin(next_page) 获取下一页的完整链接，并将其传递给 scrapy.Request 对象，并指定回调函数为 self.parse
            # yield 关键字用于生成器(generator)，在这里它创建了一个请求对象(scrapy.Request)，并将这个请求对象作为生成器的一个输出项
```

5.3  中间件设置

​	为了应对网站的反爬虫，有时需要设置IP代理

```python
# 在中间件mddlewares.py中，新加入IP代理设置代码
import random
class user_agent(object):
    def process_request(self, request, spider):
        # user agent 列表（IP代理）
        USER_AGENT_LIST = [
            'MSIE (MSIE 6.0; X11; Linux; i686) Opera 7.23',
            'Opera/9.20 (Macintosh; Intel Mac OS X; U; en)',
            'Opera/9.0 (Macintosh; PPC Mac OS X; U; en)',
            'iTunes/9.0.3 (Macintosh; U; Intel Mac OS X 10_6_2; en-ca)',
            'Mozilla/4.76 [en_jp] (X11; U; SunOS 5.8 sun4u)',
            'iTunes/4.2 (Macintosh; U; PPC Mac OS X 10.2)',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.6; rv:5.0) Gecko/20100101 Firefox/5.0',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.6; rv:9.0) Gecko/20100101 Firefox/9.0',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.8; rv:16.0) Gecko/20120813 Firefox/16.0',
            'Mozilla/4.77 [en] (X11; I; IRIX;64 6.5 IP30)',
            'Mozilla/4.8 [en] (X11; U; SunOS; 5.7 sun4u)'
        ]
        agent = random.choice(USER_AGENT_LIST)  # 从上面列表中随机抽取一个代理
        request.headers['User-Agent'] = agent # 设置请求头的用户代理
```

​	需要注意的是：还应在设置文件中启用中间件，并设置优先级

```python
# 在settings.py中添加代码

# 优先级在0~1000之间，数量越小，越优先

# 设置下载中间件，这里使用了自定义的 user_agent 中间件，用于设置请求的 User-Agent
DOWNLOADER_MIDDLEWARES = {
    'douban_top.middlewares.user_agent': 100,  # 设置随机User-Agent中间件的优先级
}
```

5.4  存储数据

​	将数据存储到CSV文件中，需要自定义管道文件

​	5.4.1  需要实现的方法

```markdown
__init__ 方法：用于初始化 CSV 文件路径
from_crawler 类方法：用于从 Scrapy 的配置中获取 CSV 文件路径
open_spider 方法：在 Spider 开始爬取时调用，用于打开 CSV 文件并写入表头
close_spider 方法：在 Spider 结束爬取时调用，用于关闭 CSV 文件
process_item 方法：处理每个 Item 对象，将其写入 CSV 文件中
```

​	5.4.2  具体代码如下

```python
import csv

class CSVPipeline:
    """
    Pipeline 类，用于将爬取到的数据存储到 CSV 文件中
    """

    def __init__(self, csv_file_path):
        """
        初始化方法，设置 CSV 文件路径
        """
        self.csv_file_path = csv_file_path
        self.csv_file = None  # 添加初始化属性

    @classmethod
    def from_crawler(cls, crawler):
        """
        类方法，从 Scrapy 配置中获取 CSV 文件路径
        """
        return cls(
            csv_file_path=crawler.settings.get('CSV_FILE_PATH')
        )

    def open_spider(self, spider):
        """
        在 Spider 开始爬取时调用，打开 CSV 文件并写入表头
        """
        self.csv_file = open(self.csv_file_path, 'w', newline='', encoding='utf-8')
        # 创建 CSV 写入器，并写入表头，这里的表头根据 MovieItem 的字段来确定
        self.csv_writer = csv.DictWriter(self.csv_file, fieldnames=['排名', '电影名', '简介', '星级', '评论数', '描述'])
        self.csv_writer.writeheader()

    def close_spider(self, spider):
        """
        在 Spider 结束爬取时调用，关闭 CSV 文件
        """
        if self.csv_file:  # 添加检查，确保属性已经被正确初始化
            self.csv_file.close()

    def process_item(self, item, spider):
        """
        处理每个 Item 对象，将其写入 CSV 文件中
        """
        # 使用 CSV 写入器将 Item 写入 CSV 文件
        self.csv_writer.writerow(item)
        return item
```

​	5.4.3  同时也需要在settings.py中启用管道文件

```python
# 指定CSV文件输出路径
CSV_FILE_PATH = 'C:/Users/Desktop/douban.csv'

# 配置Item Pipeline，将数据写入CSV文件
ITEM_PIPELINES = {
    'douban_top.pipelines.CSVPipeline': 300,
}
```

5.5  运行`scrapy`项目

​	启动scrapy项目的方式有：

```
1、使用命令行工具
2、编写脚本运行
3、使用scrapy的CrawlerProcess类
4、使用Scrapyd
```

​	本次使用最简单的命令行工具：

```python
# 进入到spiders文件夹的上一个文件夹下
#运行程序
scrapy crawl doubantop
```

