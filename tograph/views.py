from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from django.db.models import Count
from django.http import JsonResponse

from pyecharts.charts import Graph
from pyecharts import options as opts
# Create your views here.
from django.http import HttpResponse
from django.template.loader import get_template

from event.views import filter_model
from event.models import Community, SubType, Type, MainType, Event, \
    Street, District, DisposeUnit, Property, EventSource, Achieve

import kgraph.views as kgv
import time


def show(request):
    return HttpResponse("hello")


@login_required(login_url='/user/login/')
def crawl(request):
    data_num = request.GET.get('data_num')
    print("----------------time:" + str(time) + "-------------------")
    data_all = ["@第一现场 @深圳市城市管理和综合执法局 @深圳身边事@深圳公安 @深圳新闻播报"
                " 能不能管管了，每天晚上这样城市作业车在楼下作业，从12点开始一直到1点多，"
                "有时到两点。投诉无数次了，每次都说处理，结果到现在也没有解决，"
                "怎么老百姓跟政府部门打交道就这么心累呢？而且所谓的福田城管根本不干活，"
                "上班时间打电话都是无人接听的，还号称9-18点上班，人呢？拿钱不干活？"
                " 2深圳·香景大厦 O网页链接 收起全文"
                "今天09:44  来自 iPhone客户端",
                "@深圳市场监管 @深圳市消费者委员会 @深圳微博发布厅向深圳政府职能部门投诉个"
                "别公司的市场欺诈行为，立即得积极响应，市场监督局（所）的领导多次到商家协商"
                "，与我电话沟通。至此，问题已圆满 解决！感谢政府职能部门，为百姓着想，"
                "工作落实到实处，这才是先行示范真有应有风采！为你们点赞！ "
                "11月23日 14:57  来自 iPhone客户端",
                "一看到皇岗口岸附近有施工项目就头皮发麻，拜托你们也关注一下皇岗口岸的施工扰民吧"
                "。[二哈][二哈][二哈] 昼夜不停，噪音超标，投诉就是没管不了，管了也是没效果，"
                "然后干脆不回应 @深圳特区报 不让评论只能艾特你了"
                "11月24日 18:28 来自 微博 weibo.com",
                "#深圳生活##深圳身边事# 深圳2020年噪音扰民标准，给了施工扰民时间，早上七点就可以施工"
                "，且全年无休，休息日更甚！深圳到处在修路，旧改，很多城中村在施工（包括本人所在小区），"
                "且没有降噪措施，每天都被施工噪音惊醒，投诉回复此类施工没有工作日和休息日之分，"
                "想请问深圳人居委，你们定这个施工时间标准是否合理有效？？？监督投诉是否按标准有效处理？？？"
                "@新浪深圳 @深圳新闻网 @深圳身边事 @深圳人居委 @深圳人居环境委 2深圳·三联山咀头小区 "
                "收起全文d"
                "11月21日 09:39  来自 荣耀8X",
                "来深圳两年多[doge]对这个城市的好感因为“宜停车”这个辣鸡app全无[拜拜]这个软件简直是钓鱼执法的好帮手"
                "[微笑]对异地牌车的恶意写得明明白白[骷髅]投诉无用申诉无门[跪了]这违反常理和正常逻辑"
                "的规定简直为创收而设😊来了就是深圳人[费解]不了不了我不配[哈欠]"
                "最后再说一句深圳交委不愧是宁[微笑]"
                "蒸的辣鸡[可爱] 收起全文d"
                "11月21日 06:27  来自 微博国际版"
                ]

    data = data_all[0:int(data_num)]
    context = {
        'data': data,
        'datalength': data_num,

    }
    return JsonResponse(context)


def part(request):
    data_num = request.GET.get('data_num')
    data_all = [['@', '第一', '现场', '@', '深圳市', '城市', '管理', '和', '综合', '执法局', '@', '深圳', '身边', '事', '@', '深圳', '公安', '@',
                  '深圳', '新闻', '播报', '能', '不'
                                         '能', '管管', '了', '每天晚上', '这样', '城市', '作业', '车', '在', '楼下', '作业', '从', '12', '点',
                  '开始', '一直', '到', '1', '点多', '有时', '到', '两点', '。',
                  '投诉', '无数次', '了', '每次', '都', '说', '处理', '结果', '到', '现在', '也', '没有', '解决', '怎么', '老百姓', '跟', '政府部门',
                  '打交道', '就', '这么', '心累', '呢'
                                          '', '而且', '所谓', '的', '福田', '城管', '根本', '不', '干活', '上班时间', '打电话', '都', '是',
                  '无人', '接听', '的', '还', '号称', '9', '-', '18', '点', '上班', '，'
                                                                         '人', '呢', '拿', '钱', '不', '干活', '2', '深圳', '·',
                  '香景', '大厦', 'O', '网页', '链接', '收起', '全文', '今天', '09', ':', '44', '来自',
                  ' ', 'iPhone', '客户端'],
                 ['@', '深圳', '市场监管', '@', '深圳市', '消费者', '委员会', '@', '深圳', '微博', '发布厅', '向', '深圳', '政府', '职能部门', '投诉',
                  '个别', '公司', '的', '市场', '欺诈',
                  '行为', '立即', '得', '积极响应', '市场', '监督局', '（', '所', '）', '的', '领导', '多次', '到', '商家', '协商', '与', '我', '电话',
                  '沟通', '。', '至此', '问题'
                                   '', '已', '圆满', '解决', '！', '感谢', '政府', '职能部门', '为', '百姓', '着想', '工作', '落实', '到', '实处',
                  '这才', '是', '先行', '示范', '真有', '应有', '风'
                                                     '采', '！', '为', '你们', '点赞', '！', '11', '月', '23', '日', '14', ':',
                  '57', '来自', 'iPhone', '客户端'],
                 ['一', '看到', '皇岗', '口岸', '附近', '有', '施工', '项目', '就', '头皮发麻', '拜托', '你们', '也', '关注', '一下', '皇岗', '口岸',
                  '的', '施工', '扰民', '吧', '。', '[', '二哈',
                  ']', '[', '二哈', ']', '[', '二哈', ']', '昼夜', '不停', '噪音', '超标', '投诉', '就是', '没', '管不了', '管', '了', '也',
                  '是', '没', '效果', '然后',
                  '干脆', '不', '回应', '@', '深圳特区', '报', '不让', '评论', '只能', '艾特', '你', '了', '11', '月', '24', '日', '18', ':',
                  '28', '来自', '微博', 'weibo',
                  '.', 'com'],
                 ['#', '深圳', '生活', '##', '深圳', '身边', '事', '#', '深圳', '2020', '年', '噪音', '扰民', '标准', '给', '了', '施工',
                  '扰民', '时间', '早上', '七点', '就', '可以',
                  '施工', '且', '全年', '无休', '休息日', '更', '甚', '！', '深圳', '到处', '在', '修路', '旧改', '很多', '城中村', '在', '施工', '（',
                  '包括', '本人', '所在',
                  '小区', '）', '且', '没有', '降噪', '措施', '每天', '都', '被', '施工', '噪音', '惊醒', '投诉', '回复', '此类', '施工', '没有',
                  '工作日', '和', '休息日', '之分',
                  '想', '请问', '深圳', '人', '居委', '你们', '定', '这个', '施工', '时间', '标准', '是否', '合理', '有效', '监督', '投诉', '是否',
                  '按', '标准', '有效', '处理', '@', '新浪', '深圳',
                  '@', '深圳', '新闻网', '@', '深圳', '身边', '事', '@', '深圳', '人', '居委', '@', '深圳', '人居', '环境', '委', '2',
                  '深圳', '·', '三联', '山咀', '头', '小区', '收起', '全文', 'd11', '月', '21', '日', '09', ':', '39', '来自', '荣耀',
                  '8X'],
                 ['来', '深圳', '两年', '多', '[', 'doge', ']', '对', '这个', '城市', '的', '好感', '因为', '“', '宜', '停车', '”', '这个',
                  '辣鸡', 'app', '全无', '[', '拜拜', ']', '这个', '软件',
                  '简直', '是', '钓鱼', '执法', '的', '好帮手', '[', '微笑', ']', '对', '异地', '牌车', '的', '恶意', '写得', '明明白白', '[',
                  '骷髅', ']', '投诉', '无用', '申诉', '无门', '[', '跪', '了'
                     , ']', '这', '违反常理', '和', '正常', '逻辑', '的', '规定', '简直', '为', '创收', '而设', '�', '来', '了', '就是', '深圳',
                  '人', '[', '费解', ']', '不了', '不了', '我', '不配', '[',
                  '哈欠', ']', '最后', '再说', '一句', '深圳', '交委', '不愧', '是', '宁', '[', '微笑', ']', '蒸', '的', '辣鸡', '[', '可爱',
                  ']', '收起', '全文', 'd11', '月', '21', '日', '06'
                     , ':', '27', '来自', '微博', '国际版']]

    data = data_all[0:int(data_num)]
    context = {
        'data': data,
        'datalength': data_num,
    }
    time.sleep(1)
    return JsonResponse(context)


def table(request):
    data_num = request.GET.get('data_num')

    data_all = [["2020/11/29", "福田区 香景大厦", "深圳市城市管理和综合执法局", "投诉", "晚上城市作业车在楼下作业"],
                 ["2020/11/23", " ", "市场监督局", "感谢", "投诉积极响应"],
                 ["2020/11/24", "皇岗口岸附近", " ", "投诉", "施工扰民", "噪音超标"],
                 ["2020/11/21", "三联山咀头小区", "深圳人居委", "投诉", "施工 没有降噪措施"],
                 ["2020/11/21s", " ", "深圳交委", "投诉", "宜停车 钓鱼执法"]]

    data = data_all[0:int(data_num)]
    print(data)
    context = {
        'data': data,

        'datalength': data_num,
    }
    return JsonResponse(context)


def get_graph(request):
    # data_num = request.GET.get('data_num')
    data_all = [["2020/11/29", "福田区 香景大厦", "深圳市城市管理和综合执法局", "投诉", "晚上城市作业车在楼下作业"],
            ["2020/11/23", " ", "市场监督局", "感谢", "投诉积极响应"],
            ["2020/11/24", "皇岗口岸附近", " ", "投诉", "施工扰民", "噪音超标"],
            ["2020/11/21", "三联山咀头小区", "深圳人居委", "投诉", "施工 没有降噪措施"],
            ["2020/11/21", " ", "深圳交委", "投诉", "宜停车 钓鱼执法"]]

    data = data_all

    cate = ["时间", "地点", "部门", "性质", "事件"]

    link_value = ["发生时间", "发生地点", "责任部门", "事件性质", "事件本身"]

    categories_all = []
    nodes_all = []
    links_all = []
    nodes_name = []

    node_index = 0

    for record in data:
        categories = []
        nodes = []
        links = []
        for c in cate:
            print("cate:" + c + "\n")
            categories.append(opts.GraphCategory(name=c))

        for anode, i in zip(record, range(0, len(cate))):
            print("node:" + anode + "\n")
            if anode == " ":
                pass
            else:
                if is_node_exist(nodes_name, anode) == -1:
                    nodes.append(opts.GraphNode(name=anode, symbol_size=80, category=i))
                    nodes_name.append(anode)
                    node_index += len(nodes_name) - 1
                else:
                    node_index = is_node_exist(nodes_name, anode)

        for anode, i in zip(record, range(0, len(link_value) - 1)):
            print("link:" + record[4] + "->" + link_value[i] + "->" + record[i] + "\n")
            if anode == record[4]:
                pass
            else:
                links.append(opts.GraphLink(source=record[4], target=anode, value=link_value[i]))

        categories_all = categories_all + categories
        nodes_all = nodes_all + nodes
        links_all = links_all + links

    page = "graph"
    kgraph = to_graph(categories_all, nodes_all, links_all)

    context = {
        'graph': kgraph,
        "page": page,
        'cur_page': "kgraph",
    }
    return render(request, 'tograph/tograph.html', context)


def to_graph(categories, nodes, links) -> Graph:
    c = (
        Graph(
            init_opts=opts.InitOpts(width="1600px", height="800px")
        )
            .add(
            "",
            nodes=nodes,
            links=links,
            categories=categories,
            gravity=0.01,
            repulsion=300,
            linestyle_opts=opts.LineStyleOpts(color="black", curve=0.2),
            label_opts=opts.LabelOpts(is_show=True, position='inside', font_size=15),
            is_draggable=True,
            is_rotate_label=True,
            is_focusnode=True,
            layout="force",
            edge_length=200,
            edge_label=opts.LabelOpts(
                is_show=True,
                position="middle",
                font_size=15,
                formatter="{c}"
            ),
            edge_symbol=[None, 'arrow']
        )
            .set_global_opts(
            legend_opts=opts.LegendOpts(is_show=True),
            title_opts=opts.TitleOpts(),
        )
            .dump_options_with_quotes()
    )

    return c


def is_node_exist(nodes, node):
    if node in set(nodes):
        return nodes.index(node)

    else:
        return -1
