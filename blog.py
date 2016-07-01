#!\urs\bin\env python
# encoding:utf-8

# 载入框架
import time
import uuid

import web
# 载入数据库操作model（稍后创建）
import model
import os

# URL映射
from Week12.blog.fetchpage import FetchThread
from Week12.blog.zip import autozip

urls = (
    '/', 'Index',
    '/view/(\d+)', 'View',
    '/new', 'New',
    '/delete/(\d+)', 'Delete',
    '/edit/(\d+)', 'Edit',
    '/login', 'Login',
    '/logout', 'Logout',
    '/fetch', 'Fetch',
    '/download/(\d+)', 'Download'
)
app = web.application(urls, globals())
# 模板公共变量
t_globals = {
    'datestr': web.datestr,
    'cookie': web.cookies,
}
# 指定模板目录，并设定公共模板
render = web.template.render('templates', base='base', globals=t_globals)
# 创建登录表单
login = web.form.Form(
    web.form.Textbox('username'),
    web.form.Password('password'),
    web.form.Button('login')
)


# 首页类
class Index:
    def GET(self):
        login_form = login()
        posts = model.get_posts()
        return render.index(posts, login_form)

    def POST(self):
        login_form = login()
        if login_form.validates():
            if login_form.d.username == 'admin' \
                    and login_form.d.password == 'admin':
                web.setcookie('username', login_form.d.username)
        raise web.seeother('/')


# 查看文章类
class View:
    form = web.form.Form(
        web.form.Textarea('content',
                          web.form.notnull,
                          rows=30,
                          cols=80,
                          description=''),
        web.form.Button('Post entry'),
    )

    def GET(self, id):
        print id
        post = model.get_post(int(id))
        comments = model.get_comments(int(id))
        print post
        print comments
        return render.view(post, comments, self.form)

    def POST(self, id):
        print id
        form = self.form()
        if form.validates():
            model.new_comment(id, form.d.content)
            raise web.seeother('/view/' + id)


# 新建文章类
class New:
    form = web.form.Form(
        web.form.Textbox('title',
                         web.form.notnull,
                         size=30,
                         description='Post title: '),
        web.form.Textarea('content',
                          web.form.notnull,
                          rows=30,
                          cols=80,
                          description='Post content: '),
        web.form.Button('Post entry'),
    )

    def GET(self):
        form = self.form()
        return render.new(form)

    def POST(self):
        form = self.form()
        if not form.validates():
            return render.new(form)
        model.new_post(form.d.title, form.d.content)
        raise web.seeother('/')


# 删除文章类
class Delete:
    def GET(self, id):
        model.del_post(int(id))
        raise web.seeother('/')


# 编辑文章类
class Edit:
    def GET(self, id):
        post = model.get_post(int(id))
        form = New.form()
        form.fill(post)
        return render.edit(post, form)

    def POST(self, id):
        form = New.form()
        post = model.get_post(int(id))
        if not form.validates():
            return render.edit(post, form)
        model.update_post(int(id), form.d.title, form.d.content)
        raise web.seeother('/')


# 退出登录
class Logout:
    def GET(self):
        web.setcookie('username', '', expires=-1)
        raise web.seeother('/')


# 定义404错误显示内容
def notfound():
    return web.notfound("Sorry, the page you were looking for was not found.")


class Fetch:
    form = web.form.Form(
        web.form.Textarea('content',
                          web.form.notnull,
                          rows=5,
                          cols=50,
                          description='Post content: '),
        web.form.Checkbox('html', value='html', checked=True),
        web.form.Checkbox('image', value='image', checked=True),
        web.form.Button('Post entry'),
    )

    def GET(self):
        form = self.form()
        urls = model.get_urls()
        return render.fetch(form, urls)

    def POST(self):
        form = self.form()
        if not form.validates():
            return render.fetch(form)
        # print form.d
        uid = uuid.uuid1()
        model.new_url(form.d.content, uid)
        os.mkdir(uid.__str__())
        thread = FetchThread()
        thread.add_url(form.d.content)
        thread.set_dir(uid.__str__())
        thread.set_html_flag(form.d.html)
        thread.set_image_flag(form.d.image)
        thread.start()

        raise web.seeother('/fetch')


class Download:
    BUF_SIZE = 262144

    def GET(self, id):
        print id
        url = model.get_url(id)

        print url
        file_name = url.uid + '.zip'

        file_path = os.path.join('./' + url.uid, file_name)

        # print file_path

        f = None
        try:
            f = open(file_path, "rb")
            web.header('Content-Type', 'application/octet-stream')
            web.header('Content-disposition', 'attachment; filename=%s' % file_name)
            while True:
                c = f.read(self.BUF_SIZE)
                if c:
                    yield c
                else:
                    break
        except Exception, e:
            print e
            yield 'Error'
        finally:
            if f:
                f.close()


app.notfound = notfound
# 运行
if __name__ == '__main__':
    app.run()
