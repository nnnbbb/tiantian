#coding=utf-8
from django.shortcuts import render
from models import GoodsInfo,TypeInfo
from django.core.paginator import Paginator


def index(request):
    count = request.session.get('count', 1)
    # 水果
    fruit = GoodsInfo.objects.filter(gtype__id=1).order_by("-id")[:4]
    # fruit2 = GoodsInfo.objects.filter(gtype__id=2).order_by("-gclick")[:4]
    # 海鲜
    fish2 = GoodsInfo.objects.filter(gtype__id=2).order_by("-id")[:4]
    # fish = GoodsInfo.objects.filter(gtype__id=4).order_by("-gclick")[:3]
    # 猪牛羊肉
    meat2 = GoodsInfo.objects.filter(gtype__id=3).order_by("-id")[:4]
    # meat = GoodsInfo.objects.filter(gtype__id=1).order_by("-gclick")[:4]
    # 禽类蛋品
    egg2 = GoodsInfo.objects.filter(gtype__id=4).order_by("-id")[:4]
    # egg = GoodsInfo.objects.filter(gtype__id=5).order_by("-gclick")[:4]
    # 新鲜蔬菜
    vegetables2 = GoodsInfo.objects.filter(gtype__id=5).order_by("-id")[:4]
    # vegetables2 = GoodsInfo.objects.filter(gtype__id=3).order_by("-gclick")[:4]
    # 速冻食品
    frozen2 = GoodsInfo.objects.filter(gtype__id=6).order_by("-id")[:4]
    # frozen2 = GoodsInfo.objects.filter(gtype__id=6).order_by("-gclick")[:4]
    context = {'title': '首页',
               'fruit': fruit,
               # 'fruit2': fruit2,
               'fish': fish2,
               # 'fish2': fish,
               'meat2': meat2,
               # 'meat2': meat,
               'egg2': egg2,
               # 'egg2': egg2,
               'vegetables2': vegetables2,
               # 'vegetables': vegetables,
               'frozen2': frozen2,
               # 'frozen': frozen,
               'guest_cart': 1,
               'page_name': 0,
               'count': count}
    return render(request, 'df_goods/index.html', context)

# 商品列表页
def list(request, typeid, pageid, sort):
    '''
    负责展示某类商品的信息
    typeid 查询商品类别id
    pageid 第几页
    sort 按点击量 or 最新 or 价格 排序
    '''
    count = request.session.get('count', "")

    # 获取最新发布的商品 推荐位
    newgood = GoodsInfo.objects.all().order_by('-id')[:2]
    if sort == '1': #按最新   gtype_id  , gtype__id  指typeinfo_id
        sumGoodList = GoodsInfo.objects.filter(
            gtype_id = typeid).order_by('-id')  # 比如typeid等于1 也就是生鲜水果 取出全部数据 按降序排序 取出最新添加的
    elif sort == '2': # 按价格
        sumGoodList = GoodsInfo.objects.filter(
            gtype__id = typeid).order_by('gprice')# 先查询到typeifo表对应的产品类别id 然后查询goodsinfo表的列
    # elif sort == '3': # 按点击量
    #     sumGoodList = GoodsInfo.objects.filter(
    #         gtype__id=typeid).order_by('-gclick')
        # 分页 传入列表,将其分成15条每页
    paginator = Paginator(sumGoodList, 15)
    # 返回第几页
    goodList = paginator.page(int(pageid))
    # 页码列表
    pindexlist = paginator.page_range
    # print pindexlist    xrange(1,2)
    # 确定商品的类型
    goodtype = TypeInfo.objects.get(id=typeid)
    context = {
        'title': '商品详情',
        'list': 1,
        'guest_cart': 1,
        'goodtype': goodtype,
        'newgood': newgood,
        'goodList': goodList,
        'typeid': typeid,
        'sort': sort,
        'pindexlist': pindexlist,
        'pageid': int(pageid),
        'count': count
    }

    return render(request, 'df_goods/list.html', context)


# 商品详情页
def detail(request, id):
    goods = GoodsInfo.objects.get(pk=int(id))
    # 取出访问的商品然后让点击量加1
    # goods.gclick += 1
    # goods.save()
    # 查询当前商品的类型   goodsinfo__id 值
    # goodtype = TypeInfo.objects.get(goodsinfo__id=id)
    goodtype = goods.gtype
    # type = TypeInfo()

    count = request.session.get('count','')
    # goods.gtype = typeinfo    goods.gtype.goodsinfo_set -> typeinfo.goodsinfo_set
    news = goods.gtype.goodsinfo_set.order_by('-id')[0:2]
    # print '*' * 10
    # print news[0].gtitle
    # print goodtype    猪牛羊肉
    # print goods.gtype  猪牛羊肉

    context = {'title': goods.gtype.ttitle,
               'guest_cart': 1,
               'g': goods,
               'newgood': news,
               'id': id,
               'isDetail': True,
               'list': 1,
               'goodtype': goodtype,
               'count': count
               }
    response = render(request, 'df_goods/detail.html', context)

    # 使用cookies记录最近浏览的商品id
    # 获取cookies
    goods_ids = request.COOKIES.get('goods_ids', '')
    # 获取当前点击商品id
    goods_id = '%d' % (goods.id)
    # 判断cookies中商品id是否为空
    if goods_ids != '':
        # 分割出每个商品id
        goods_id_list = goods_ids.split(',')
        # 判断商品是否已经存在于列表
        if goods_id_list.count(goods_id) >= 1:
            # 存在则移除
            goods_id_list.remove(goods_id)
        # 在第一位添加
        goods_id_list.insert(0, goods_id)
        # 判断列表数是否超过5个
        if len(goods_id_list) >= 6:
            # 超过五个则删除第6个
            del goods_id_list[5]
        # 添加商品id到cookies
        goods_ids = ','.join(goods_id_list)
    else:
        # 第一次添加，直接追加
        goods_ids = goods_id
    response.set_cookie('goods_ids', goods_ids)

    return response


