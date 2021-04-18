FROM python:3.8.2
MAINTAINER simonamnv
ADD . /root/
RUN pip3 install  -i https://pypi.doubanio.com/simple/  scrapy
RUN pip3 install pymongo -i https://pypi.doubanio.com/simple/
RUN pip3 install  -i https://pypi.doubanio.com/simple/ fake_useragent
RUN pip3 install  -i https://pypi.doubanio.com/simple/ pillow
RUN pip3 install  -i https://pypi.doubanio.com/simple/ scrapy_redis
RUN pip3 install  -i https://pypi.doubanio.com/simple/ django
WORKDIR /root/newscrawl/api
CMD ["python", "crawl_api.py"]