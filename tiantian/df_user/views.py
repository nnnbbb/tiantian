# coding=utf-8
from django.shortcuts import render, redirect, HttpResponseRedirect
from django.http import JsonResponse
from models import *
from df_goods.models import GoodsInfo
from hashlib import sha1
from .islogin import islogin
from df_order.models import OrderInfo
from django.core.paginator import Paginator

# 注册页面
def register(request):
    return render(request,'df_user/register.html')


def register_handle(request):
    # 接收用户注册的请求
    post = request.POST
    uname = post.get('user_name')
    upwd = post.get('pwd')
    upwd2 = post.get('cpwd')
    uemail = post.get('email')
    # 判断两次密码是否相同
    if upwd != upwd2:
        return redirect('/user/register')

    # 加密
    s1 = sha1()
    s1.update(upwd)
    upwd3 = s1.hexdigest()
    # 创建对象
    user = UserInfo()
    user.uname = uname
    user.upwd = upwd3
    user.uemail = uemail
    user.save()
    # 成功重定向到登录界面
    return redirect('/user/login/')

# 验证注册的用户名是否已经存在
def register_exist(requset):
    uname = requset.GET.get('uname')
    # 向数据库内查用户名是否存在 count 值只有0或1
    count = UserInfo.objects.filter(uname=uname).count()
    return JsonResponse({'count': count})


def login(request):
    uname = request.COOKIES.get('uname', '')
    context = {'title':'用户登录', 'user_error':0, 'pwd_error':0, 'uname':uname}
    return render(request, 'df_user/login.html', context)

# 登录处理
def login_handle(request):
    # 接收请求信息
    post = request.POST
    uname = post.get('username')
    upwd = post.get('pwd')
    jizhu = post.get('jizhu', 0)
    # 根据用户名查询对象
    users = UserInfo.objects.filter(uname=uname)
    # print uname
    # 判断如果未查到则用户名错，查到再判断密码是否正确，正确则转到用户中心
    if len(users) == 1:
        s1 = sha1()
        s1.update(upwd)
        #登录带cookie值   必须 red = HttpResponseRedirect    red.set_cookie  renturn red
        if s1.hexdigest() == users[0].upwd:
            url = request.COOKIES.get('url','/')
            print ('url===', url)
            # red = HttpResponseRedirect('/user/info')
            red = HttpResponseRedirect(url)
            # count = CartInfo.objects.filter(user_id=users[0].id).count()

            # print '*'*10
            # print count
            # 记住用户名
            if jizhu != 0:
                red.set_cookie('uname', uname)
            else:
                red.set_cookie('uname', '', max_age=-1)
            # 用于登录验证
            request.session['user_id'] = users[0].id
            # 用在base.html
            request.session['user_name'] = uname
            # request.session['count'] = count
            # print('red', red)
            return red
        else:
            context = {'title': '用户登录', 'error_name': 0, 'error_pwd': 1, 'uname': uname}
            return render(request, 'df_user/login.html', context)
    else:
        context = {'title': '用户登录', 'error_name': 1, 'error_pwd': 0, 'uname': uname }
        return render(request, 'df_user/login.html', context)


def logout(request):
    request.session.flush()
    return redirect('/')


@islogin
def info(request):
    user_email = UserInfo.objects.get(id = request.session['user_id']).uemail

    # 最近浏览
    goods_ids = request.COOKIES.get('goods_ids', '')
    goods_id_list = goods_ids.split(',')
    goods_list = []
    if len(goods_ids):
        for goods_id in goods_id_list:
            goods_list.append(GoodsInfo.objects.get(id=int(goods_id)))

    # 构造上下文
    context = {'title':'用户中心',
               'user_email':user_email,
               'user_name':request.session['user_name'],
               'info':'123',
               'page_name':1,
               'goods_list': goods_list
               }
    return render(request, 'df_user/user_center_info.html', context)
    # return render(request, 'df_user/base.html')


# 订单
@islogin
def order(request, pageid):
    context = {'title': '用户中心','page_name':1,'order':1}
    return render(request, 'df_user/user_center_order.html', context)


@islogin
def site(request):
    user = UserInfo.objects.get(id=request.session['user_id'])
    if request.method == 'POST':
        post = request.POST
        user.ushou = post.get('ushou')
        user.uaddress = post.get('uaddress')
        user.uphone = post.get('uphone')
        user.uyoubian = post.get('uyoubian')
        user.save()
    context = {'title': '用户中心', 'user': user,'page_name':1,'site':1}
    return render(request, 'df_user/user_center_site.html', context)


@islogin
def user_center_order(request, pageid):
    """
    此页面用户展示用户提交的订单，由购物车页面下单后转调过来，也可以从个人信息页面查看
    根据用户订单是否支付、下单顺序进行排序
    """

    uid = request.session.get('user_id')
    # 订单信息，根据是否支付、下单顺序进行排序
    orderinfos = OrderInfo.objects.filter(
        user_id=uid).order_by('zhifu', '-oid')

    # 分页
    #获取orderinfos list  以两个为一页的 list
    paginator = Paginator(orderinfos, 2)
    # 获取 上面集合的第 pageid 个 值
    orderlist = paginator.page(int(pageid))
    #获取一共多少 页
    plist = paginator.page_range
    #3页分页显示
    qian1 = 0
    hou = 0
    hou2 = 0
    qian2 = 0
    # dd = dangqian ye
    dd = int(pageid)
    lenn = len(plist)
    if dd>1:
        qian1 = dd-1
    if dd>=3:
        qian2 = dd-2
    if dd<lenn:
        hou = dd+1
    if dd+2<=lenn:
        hou2 = dd+2



    # 构造上下文
    context = {'page_name': 1,
               'title': '全部订单',
               'pageid': int(pageid),
               'order': 1,
               'orderlist': orderlist,
               'plist': plist,
               'pre':qian1,
               'next':hou,
               'pree':qian2,
               'lenn':lenn,
               'nextt':hou2}

    return render(request, 'df_user/user_center_order.html', context)

