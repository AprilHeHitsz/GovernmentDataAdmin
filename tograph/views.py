from django.contrib.auth.decorators import login_required
from django.shortcuts import render

# Create your views here.
from django.http import HttpResponse


# def show(request):
#     return HttpResponse("hello")

@login_required(login_url='/user/login/')
def show(request):
    # search = request.GET.get('search')

    context = {
        # 'graph': kgraph,
        # 'kg_search': search,
        # "page": page,
        # 'cur_page': "kgraph",
    }

    return render(request, 'tograph/tograph.html', context)