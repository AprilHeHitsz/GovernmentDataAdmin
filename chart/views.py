from django.shortcuts import render
from django.http import HttpResponse
from django.db.models import Q, Count
from rest_framework.views import APIView

import json
from datetime import timedelta, date
import datetime
from pyecharts.charts import Sunburst, BMap, Line, WordCloud, Pie, Calendar, Bar, Grid, Funnel
from pyecharts.globals import SymbolType, GeoType, ThemeType
from pyecharts import options as opts

from event.models import Street, Event, Property, Achieve, Type, Community, DisposeUnit, MainType, SubType
from .charts import Charts

BAIDU_MAP_AK = 'X3ATCKQWRjRxLNLI1Wv9NiTMFAa5bh8W'
properties = Property.objects.all()
street_list = Street.objects.all()
achieves = Achieve.objects.all()

class IndexView(APIView):
    def get(self, request, *args, **kwargs):
        charts = Charts()
        context = {
            "properties": properties,
            "streets": street_list,
            'pie_chart': charts.pie,
            'line_charts': charts.get_line(),
            # 'sunburst_chart': charts.sunburst,
            'map_chart': charts.map,
            'calendar_chart': charts.calendar,
            'wordcloud_chart': charts.wordcloud,
            'cur_page': "charts",
            'bar_chart': charts.bar,
            'funnel_chart': charts.funnel_base()
        }
        return render(request, 'chart/charts.html', context)


def get_pie_data(request):
    street_choice = request.GET.get("pie-choice")
    start = datetime.datetime.now()
    data = []
    data_value = []
    for pro in Property.objects.all():
        event_list = Event.objects.filter(property=pro)
        cnt = 0
        for event in event_list:
            if event.community.street.name == street_choice:
                cnt += 1
        data.append(pro.name)
        data_value.append(cnt)

    c = (
        Pie(init_opts=opts.InitOpts(theme=ThemeType.WESTEROS))
            .add("", [list(z) for z in zip(data, data_value)])
            .set_series_opts(label_opts=opts.LabelOpts(formatter="{b}: {c}"))
            .dump_options_with_quotes()
    )

    end = datetime.datetime.now()
    print("Pie: " + str(end - start))
    return HttpResponse(c, content_type='application/json')


def get_sun_data(request):
    sun_choice = request.GET.get("sun-choice")
    street = Street.objects.get(name=sun_choice)
    sun_data = []
    statuses = Achieve.objects.all()
    type_list = Type.objects.all()
    for status in statuses:
        type_value = {}
        for v in type_list:
            type_value.update({v.name: 0})

        events = status.event.get_queryset()

        for event in events:
            if event.community.street != street:
                continue
            type_value[event.type.name] += 1

        time_list = []
        for key in type_value.keys():
            if type_value[key]:
                single = opts.SunburstItem(name=key, value=type_value[key])
                time_list.append(single)

        if len(time_list):
            name = status.name
            s_item = opts.SunburstItem(name=name, children=time_list)
            sun_data.append(s_item)

    start = datetime.datetime.now()
    data = sun_data
    c = (
        Sunburst()
            .add(series_name="", data_pair=data, radius=[0, "90%"])
            .set_series_opts(label_opts=opts.LabelOpts(formatter="{b}"))
            .dump_options_with_quotes()
    )
    end = datetime.datetime.now()
    print("Sunburst: " + str(end - start))
    return HttpResponse(c, content_type='application/json')


def get_calender_data(request):
    def get_date(days):
        day = (date.today() - timedelta(days=555) - timedelta(days=days))
        return day
    property = Property.objects.get(name=request.GET.get("calender-choice"))
    event_list = Event.objects.filter(property=property)

    start = datetime.datetime.now()

    begin = get_date(365)
    end = datetime.date.today() - timedelta(days=465)
    data = []
    cur_day = end
    count = 0
    for event in event_list:
        if event.create_time < cur_day:
            data.insert(0, (cur_day, count))
            count = 0
            cur_day -= timedelta(days=1)

        if cur_day < begin:
            break

        if event.create_time == cur_day:
            count += 1

    c = (
        Calendar()
            .add("",
                 data,
                 calendar_opts=opts.CalendarOpts(
                     range_=[begin, end],
                     daylabel_opts=opts.CalendarDayLabelOpts(name_map="cn"),
                     monthlabel_opts=opts.CalendarMonthLabelOpts(name_map="cn"),
                     pos_right="20px"
                 ),
                 )
            .set_global_opts(
            visualmap_opts=opts.VisualMapOpts(
                max_=501,
                min_=1,
                orient="horizontal",
                is_piecewise=True,
                pos_left="40px"
            ),
        )
            .dump_options_with_quotes()
    )

    end = datetime.datetime.now()
    print("Calendar: " + str(end - start))
    return HttpResponse(c, content_type='application/json')


def get_bar_data(request):
    x_field = request.GET.get('x_choice')
    y_field = request.GET.get('y_choice')
    print(request.GET.get('begin_date'))
    start_date = request.GET.get('begin_date').split('-')
    end_date = request.GET.get('end_date').split('-')
    start = datetime.date(int(start_date[0]), int(start_date[1]), int(start_date[2]))
    end = datetime.date(int(end_date[0]), int(end_date[1]), int(end_date[2]))
    y_lists = []
    x_list = []
    b = Bar()
    if x_field == 'street' and y_field == 'property':
        event_counts = Street.objects.all().values('name', 'number').order_by('-number')
        for property in properties:
            new_list = [property.name]
            for street_node in event_counts:
                new_len = 0
                street = Street.objects.get(name=street_node['name'])
                for community in Community.objects.filter(street=street):
                    new_len += len(
                        Event.objects.filter(community=community, property=property,
                                             create_time__range=(start, end))
                    )
                new_list.append(new_len)
                # print(new_list)
            y_lists.append(new_list)
        for street_node in event_counts:
            x_list.append(street_node['name'])

    elif x_field == 'community' and y_field == 'property':
        event_counts = Community.objects.all().values('name', 'number').order_by('-number')
        for property in properties:
            new_list = [property.name]
            for street_node in event_counts:
                community = Community.objects.get(name=street_node['name'])
                new_len = len(
                    Event.objects.filter(
                        Q(create_time__range=(start, end)) & Q(community=community) & Q(property=property))
                )
                new_list.append(new_len)
                # print(new_list)
            y_lists.append(new_list)
        for community_node in event_counts:
            x_list.append(community_node['name'])

    elif x_field == 'dispose_unit' and y_field == 'property':
        event_counts = DisposeUnit.objects.all().values('name', 'number').order_by('-number')
        for property in properties:
            new_list = [property.name]
            limit = 0
            for dispose_unit_node in event_counts:
                dispose_unit = DisposeUnit.objects.get(name=dispose_unit_node['name'])
                if limit < 30:
                    new_len = len(
                        Event.objects.filter(
                            Q(create_time__range=(start, end)) & Q(dispose_unit=dispose_unit) & Q(property=property))
                    )
                    new_list.append(new_len)
                    new_len = 0
                else:
                    new_len += len(
                        Event.objects.filter(
                            Q(create_time__range=(start, end)) & Q(dispose_unit=dispose_unit) & Q(
                                property=property))
                    )
                limit += 1
            new_list.append(new_len)
            y_lists.append(new_list)
        limit = 0
        for dispose_unit_node in event_counts:
            if limit >= 30:
                break
            x_list.append(dispose_unit_node['name'])
            limit += 1
        x_list.append("其他")

    elif x_field == 'main_type' and y_field == 'property':
        event_counts = MainType.objects.all().values('name', 'number').order_by('-number')
        for property in properties:
            new_list = [property.name]
            limit = 0
            new_len = 0
            for main_type_node in event_counts:
                main_type = MainType.objects.get(name=main_type_node['name'])
                for sub_type in SubType.objects.filter(main_type=main_type):
                    new_len += len(
                        Event.objects.filter(sub_type=sub_type, property=property,
                                             create_time__range=(start, end))
                    )
                if limit < 30:
                    limit += 1
                    new_list.append(new_len)
                    new_len = 0
                # print(new_list)
            new_list.append(new_len)
            y_lists.append(new_list)
        limit = 0
        for main_type_node in event_counts:
            if limit >= 30:
                break
            x_list.append(main_type_node['name'])
            limit += 1
        x_list.append('其他')

    elif x_field == 'sub_type' and y_field == 'property':
        event_counts = SubType.objects.all().values('name', 'number').order_by('-number')
        for property in properties:
            new_list = [property.name]
            limit = 0
            new_len = 0
            for sub_type_node in event_counts:
                sub_type = SubType.objects.get(name=sub_type_node['name'])
                new_len += len(
                    Event.objects.filter(
                        Q(create_time__range=(start, end)) & Q(property=property) & Q(sub_type=sub_type))
                )
                if limit < 60:
                    limit += 1
                    new_list.append(new_len)
                    new_len = 0
                # print(new_list)
            new_list.append(new_len)
            y_lists.append(new_list)
        limit = 0
        for sub_type_node in event_counts:
            if limit >= 60:
                break
            x_list.append(sub_type_node['name'])
            limit += 1
        x_list.append('其他')

    elif x_field == 'street' and y_field == 'achieve':
        event_counts = Street.objects.all().values('name', 'number').order_by('-number')
        for achieve in achieves:
            new_list = [achieve.name]
            for street_node in event_counts:
                new_len = 0
                street = Street.objects.get(name=street_node['name'])
                for community in Community.objects.filter(street=street):
                    new_len += len(
                        Event.objects.filter(community=community, achieve=achieve,
                                             create_time__range=(start, end))
                    )
                new_list.append(new_len)
                # print(new_list)
            y_lists.append(new_list)
        for street_node in event_counts:
            x_list.append(street_node['name'])

    elif x_field == 'community' and y_field == 'achieve':
        event_counts = Community.objects.all().values('name', 'number').order_by('-number')
        for achieve in achieves:
            new_list = [achieve.name]
            for street_node in event_counts:
                community = Community.objects.get(name=street_node['name'])
                new_len = len(
                    Event.objects.filter(
                        Q(create_time__range=(start, end)) & Q(community=community) & Q(achieve=achieve))
                )
                new_list.append(new_len)
                # print(new_list)
            y_lists.append(new_list)
        for community_node in event_counts:
            x_list.append(community_node['name'])

    elif x_field == 'dispose_unit' and y_field == 'achieve':
        event_counts = DisposeUnit.objects.all().values('name', 'number').order_by('-number')
        for achieve in achieves:
            new_list = [achieve.name]
            limit = 0
            for dispose_unit_node in event_counts:
                dispose_unit = DisposeUnit.objects.get(name=dispose_unit_node['name'])
                if limit < 30:
                    new_len = len(
                        Event.objects.filter(
                            Q(create_time__range=(start, end)) & Q(dispose_unit=dispose_unit) & Q(achieve=achieve))
                    )
                    new_list.append(new_len)
                    new_len = 0
                else:
                    new_len += len(
                        Event.objects.filter(
                            Q(create_time__range=(start, end)) & Q(dispose_unit=dispose_unit) & Q(
                                achieve=achieve))
                    )
                limit += 1
            new_list.append(new_len)
            y_lists.append(new_list)
        limit = 0
        for dispose_unit_node in event_counts:
            if limit >= 30:
                break
            x_list.append(dispose_unit_node['name'])
            limit += 1
        x_list.append("其他")

    elif x_field == 'main_type' and y_field == 'achieve':
        event_counts = MainType.objects.all().values('name', 'number').order_by('-number')
        for achieve in achieves:
            new_list = [achieve.name]
            limit = 0
            new_len = 0
            for main_type_node in event_counts:
                main_type = MainType.objects.get(name=main_type_node['name'])
                for sub_type in SubType.objects.filter(main_type=main_type):
                    new_len += len(
                        Event.objects.filter(sub_type=sub_type, achieve=achieve,
                                             create_time__range=(start, end))
                    )
                if limit < 30:
                    limit += 1
                    new_list.append(new_len)
                    new_len = 0
                # print(new_list)
            new_list.append(new_len)
            y_lists.append(new_list)
        limit = 0
        for main_type_node in event_counts:
            if limit >= 30:
                break
            x_list.append(main_type_node['name'])
            limit += 1
        x_list.append('其他')

    elif x_field == 'sub_type' and y_field == 'achieve':
        event_counts = SubType.objects.all().values('name', 'number').order_by('-number')
        for achieve in achieves:
            new_list = [achieve.name]
            limit = 0
            new_len = 0
            for sub_type_node in event_counts:
                sub_type = SubType.objects.get(name=sub_type_node['name'])
                new_len += len(
                    Event.objects.filter(Q(create_time__range=(start, end)) & Q(achieve=achieve) & Q(sub_type=sub_type))
                )
                if limit < 60:
                    limit += 1
                    new_list.append(new_len)
                    new_len = 0
                # print(new_list)
            new_list.append(new_len)
            y_lists.append(new_list)
        limit = 0
        for sub_type_node in event_counts:
            if limit >= 60:
                break
            x_list.append(sub_type_node['name'])
            limit += 1
        x_list.append('其他')

    b.add_xaxis(x_list)
    for y_list in y_lists:
        b.add_yaxis(y_list[0], y_list[1:], stack="stack1", category_gap="60%")
    b.set_series_opts(label_opts=opts.LabelOpts(is_show=False)) \
        .set_global_opts(
        xaxis_opts=opts.AxisOpts(axislabel_opts=opts.LabelOpts(rotate=-15)),
        # title_opts=opts.TitleOpts(title="处理事件最多的部门"),
        datazoom_opts=[opts.DataZoomOpts(), opts.DataZoomOpts(type_="inside")], )
    c = (
        b
    )

    grid = Grid()

    grid.add(c, grid_opts=opts.GridOpts(pos_bottom="20%"))

    c = grid.dump_options_with_quotes()
    return HttpResponse(c, content_type='application/json')
