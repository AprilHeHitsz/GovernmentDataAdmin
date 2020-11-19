from django.shortcuts import render
from django.http import HttpResponse
from rest_framework.views import APIView

import json
from datetime import timedelta, date
import datetime
from pyecharts.charts import Sunburst, BMap, Line, WordCloud, Pie, Calendar, Bar, Grid, Funnel
from pyecharts.globals import SymbolType, GeoType, ThemeType
from pyecharts import options as opts

from event.models import Street, Event, Property, Achieve, Type
from .charts import Charts

BAIDU_MAP_AK = 'X3ATCKQWRjRxLNLI1Wv9NiTMFAa5bh8W'
properties = Property.objects.all()
street_list = Street.objects.all()

class IndexView(APIView):
    def get(self, request, *args, **kwargs):
        charts = Charts()
        context = {
            "properties": properties,
            "streets": street_list,
            'pie_chart': charts.pie,
            'line_charts': charts.get_line(),
            'sunburst_chart': charts.sunburst,
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
