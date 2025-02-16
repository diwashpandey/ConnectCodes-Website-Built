from django.shortcuts import render, redirect
from .models import Message, Room, Topic, SubTopic
from django.contrib.auth.decorators import login_required
from django.views.generic import DetailView
from django.http import JsonResponse
# from django.contrib.auth.models import User
# Create your views here.

def getroompage(request, pk):
    key = int(pk)
    
    room = Room.objects.get(id=key)
    room_members = room.members.all()
    messages = Message.objects.filter(room__id = key)
    is_member = False
    if request.user in room_members:
        is_member = True
    return render(request,
                  "rooms/room.html",
                  {
                      'messages': messages,
                      'room' : room,
                      'room_members': room_members,
                      "is_member": is_member
                      }
                    )


@login_required(login_url = "loginpage")
def getcreateroompage(request):
    if request.method == "POST":
        data = request.POST

        selected_topic = data.get('topic')
        selected_subtopic = data.get('sub_topic')
        description = data.get('description')

        topic = Topic.objects.get(topic = selected_topic)
        print("\n\n\n\n", topic)
        subtopic = SubTopic.objects.get(subtopic=selected_subtopic, main_topic=topic)
        print("Found sub topic", subtopic)

        room = Room.objects.create(topic = topic,
                                   discription = description,
                                   subtopic = subtopic,
                                   host=request.user)
        room.members.add(request.user)
        return redirect('homepage')
    
    topics = Topic.objects.all()
    return render(request, 'rooms/createroom.html',{'topics':topics})

@login_required(login_url = "loginpage")
def add_into_room(request, pk):
    user = request.user
    room = Room.objects.get(id = pk)
    room.members.add(user)
    return redirect('roompage', pk=pk)

@login_required(login_url="loginpage")
def delete_room(request, pk):
    success = False # This will be sent to the client as a success or not message
    try:
        room = Room.objects.get(id=pk)

        # checking if user is host of room or the manager of the website
        if (request.user.has_perm("rooms.delete_room") or room.host == request.user):
            room.delete()

            # Setting the success to True
            success = True
        else:
            # User don't have the permission
            success = False

    except:
        # Room not founs
        success = False

    finally:
        # Returning the success or not status to the client
        return JsonResponse({
            "success": success
        })

    