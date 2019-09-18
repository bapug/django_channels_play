from django.shortcuts import render
from django.utils.safestring import mark_safe
import json


def index(request):
    return render(request, 'chat/index.html', {})


def room(request, room_name):
    return render(request, 'chat/room.html', {
        'room_name_json': mark_safe(json.dumps(room_name))
    })


def comments(request, group, slug):
    return render(request, 'chat/comments.html', {
        'group_name_json': mark_safe(json.dumps(group)),
        'slug_name_json': mark_safe(json.dumps(slug)),
    })