#!\urs\bin\env python
# encoding:utf-8

import sys

from Week12.blog import model
from Week12.blog.zip import autozip

reload(sys)
sys.setdefaultencoding('utf8')
import urllib

from HTMLParser import HTMLParser


class HP(HTMLParser):
    def __init__(self):
        HTMLParser.__init__(self)
        self.links = []
        self.images = []
        self.host = ""

    def set_host(self, host):
        self.host = host.split("/")[0] + "//" + host.split("/")[2] + "/"

    def append_host(self, url):
        if url.startswith("/"):
            url = url[1:]
        return self.host + url

    def handle_starttag(self, tag, attrs):
        if tag == "a":
            if len(attrs) == 0:
                pass
            else:
                for (variable, value) in attrs:
                    if variable == "href" and value != '#':
                        if not value.startswith('http://') and not value.startswith('https://'):
                            value = self.append_host(value)
                        self.links.append(value)
        if tag == "img":
            if len(attrs) == 0:
                pass
            else:
                for (variable, value) in attrs:
                    if variable == "src" and value != '#':
                        if not value.startswith('http://') and not value.startswith('https://'):
                            value = self.append_host(value)
                        self.images.append(value)


import threading


class FetchThread(threading.Thread):
    """docstring for myThread"""

    def __init__(self):
        super(FetchThread, self).__init__()
        self.image_flag = True
        self.html_flag = True
        self.pre_url_list = []
        self.post_url_list = []
        self.exclude_url_list = []
        self.error_url_list = []
        self.img_dir = "image"
        self.html_dir = "html"

    def add_url(self, url):
        self.pre_url_list.append(url)

    def set_dir(self, dirname):
        self.img_dir = dirname
        self.html_dir = dirname

    def set_image_flag(self, flag):
        self.image_flag = flag

    def set_html_flag(self, flag):
        self.html_flag = flag

    def run(self):
        self.fetch_page()
        if self.img_dir == self.html_dir:
            autozip(r'./' + self.img_dir)
            model.finish_url(self.img_dir)

    def fetch_page(self):
        count = 0
        while self.pre_url_list and count < 10:
            print 'pre_url_list: %s' % len(self.pre_url_list)
            print 'post_url_list: %s' % len(self.post_url_list)
            url = self.pre_url_list.pop()
            print 'current url: %s' % url
            html = self.get_html(url)
            print 'html => ', html
            if not html:
                continue
            hp = HP()

            hp.set_host(url)
            hp.feed(html)
            hp.close()
            print hp.links
            for link in hp.links:
                if not link.startswith('http'):
                    continue
                if link not in self.post_url_list and link not in self.pre_url_list and link != url and \
                                link not in self.exclude_url_list and link not in self.error_url_list:
                    for image in hp.images:
                        self.get_img(image, None, self.img_dir)
                    self.pre_url_list.append(link)
            self.write_html(html)
            self.post_url_list.append(url)
            count += 1
            print 'url count: %s' % count

    def get_html(self, url):
        proto, rest = urllib.splittype(url)
        res, rest = urllib.splithost(rest)
        if not res:
            print "unkonw url"
            return None
        else:
            if '@' in res:
                print 'SKIP...'
                return None
        try:
            obj = urllib.urlopen(url)
            if obj.getcode() != 200:
                print 'INFO: get html with error code ', obj.getcode()
                url.error_url_list.append(url)
                return None
            print 'HTTP MESSAGE: ', obj.info()
            if 'text/html' not in obj.info().get('Content-Type'):
                print 'INFO: SKIP for Non-HTML Content'
                url.exclude_url_list.append(url)
                return None
            html = obj.read()
            for code in ['gbk', 'utf-8', 'base64']:
                if html.decode(code, 'ignore') == html.decode(code, 'replace'):
                    return html.decode(code)
            raise UnicodeDecodeError('HTML decoding error!')
        except Exception, e:
            print 'INFO: get HTML failed with URL %s' % url
            print e.message

    def write_html(self, html):
        if self.html_flag:
            import hashlib
            import codecs

            m = hashlib.md5()
            m.update(html)
            fn = m.hexdigest()
            # print fn
            codecs.open(self.html_dir + '/%s.html' % fn, 'w', 'utf-8').write(html)

    def get_img(self, url, filename=None, path=r'D:/temp'):
        if self.image_flag:
            import os

            if not filename:
                filename = url.rsplit('/', 1)[1]
            urllib.urlretrieve(url, os.path.join(path, filename))


def start_fetch(urls):
    for url in urls:
        thread = FetchThread()
        thread.add_url(url)
        thread.start()


if __name__ == '__main__':
    start_fetch([
        "http://tieba.baidu.com/p/2738151262",
        'http://rrztnn@163.com.home.news.cn/portal/home',
        'http://bbs.sdc.icbc/default.aspx?g=posts&m=363563#363563',
        "http://120.55.193.51:8081/imf/sign"
    ])
