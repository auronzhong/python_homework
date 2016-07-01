#!\urs\bin\env python
# encoding:utf-8

import web
import datetime

# 数据库连接
db = web.database(dbn='mysql', host='192.168.99.100', port=32771, db='test', user='root', pw='123456')


# 获取所有文章
def get_posts():
    return db.select('blog', order='id DESC')


# 获取文章内容
def get_post(id):
    try:
        return db.select('blog', where='id=$id', vars=locals())[0]
    except IndexError:
        return None


# 新建文章
def new_post(title, text):
    db.insert('blog',
              title=title,
              content=text,
              posted_on=datetime.datetime.utcnow())


# 删除文章
def del_post(id):
    db.delete('blog', where='id = $id', vars=locals())


# 修改文章
def update_post(id, title, text):
    db.update('blog',
              where='id = $id',
              vars=locals(),
              title=title,
              content=text)


def new_comment(id, text):
    db.insert('comment',
              blog_id=id,
              content=text,
              posted_on=datetime.datetime.utcnow())


def get_comments(id):
    return db.select('comment', where='blog_id=$id', vars=locals())


# 新建链接
def new_url(url, uid):
    # print 'url:' + url
    db.insert('url',
              url=url,
              uid=uid,
              posted_on=datetime.datetime.utcnow())


# 获取所有链接
def get_urls():
    return db.select('url', order='id DESC')


def finish_url(uid):
    db.update('url',
              where='uid = $uid',
              vars=locals(),
              status='complete'
              )


def get_url(id):
    try:
        return db.select('url', where='id=$id', vars=locals())[0]
    except IndexError:
        return None
