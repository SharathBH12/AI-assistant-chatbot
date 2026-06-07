import os
import google.generativeai as genai

from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages

from .models import Chat, Message

from django.http import HttpResponse
from reportlab.pdfgen import canvas
from PIL import Image


genai.configure(
    api_key=os.getenv("GEMINI_API_KEY")
)

model = genai.GenerativeModel(
    "gemini-2.5-flash"
)


def home(request):

    return render(
        request,
        'home.html'
    )


def register_page(request):

    if request.method == 'POST':

        first_name = request.POST['first_name']
        last_name = request.POST['last_name']
        username = request.POST['username']
        email = request.POST['email']
        password = request.POST['password']

        if User.objects.filter(
            username=username
        ).exists():

            messages.error(
                request,
                'Username already exists'
            )

            return redirect('register')

        if User.objects.filter(
            email=email
        ).exists():

            messages.error(
                request,
                'Email already registered'
            )

            return redirect('register')

        User.objects.create_user(
            first_name=first_name,
            last_name=last_name,
            username=username,
            email=email,
            password=password
        )

        messages.success(
            request,
            'Registration successful'
        )

        return redirect('login')

    return render(
        request,
        'register.html'
    )


def login_page(request):

    if request.method == 'POST':

        username = request.POST['username']
        password = request.POST['password']

        user = authenticate(
            request,
            username=username,
            password=password
        )

        if user is not None:

            login(
                request,
                user
            )

            return redirect('chat')

        else:

            messages.error(
                request,
                'Invalid Username or Password'
            )

    return render(
        request,
        'login.html'
    )


@login_required(login_url='login')
def chat_page(request):

    chats = Chat.objects.filter(
        user=request.user
    ).order_by(
        '-is_pinned',
        '-created_at'
    )

    return render(
        request,
        'chat.html',
        {
            'chats': chats
        }
    )


@login_required(login_url='login')
def chat_detail(request, chat_id):

    chats = Chat.objects.filter(
        user=request.user
    ).order_by(
        '-is_pinned',
        '-created_at'
    )

    selected_chat = Chat.objects.get(
        id=chat_id,
        user=request.user
    )

    if request.method == 'POST':

        user_message = request.POST.get(
            'message'
        )

        uploaded_image = request.FILES.get(
            'image'
        )

        if user_message or uploaded_image:

            if selected_chat.title == "New Chat":

                selected_chat.title = (
                    user_message[:30]
                    if user_message
                    else "Image Chat"
                )

                selected_chat.save()

            Message.objects.create(
                chat=selected_chat,
                sender='user',
                content=user_message or "",
                image=uploaded_image
            )

            try:

                conversation = ""

                previous_messages = (
                    selected_chat.messages.all()
                )

                for msg in previous_messages:

                    if msg.sender == "user":

                        conversation += (
                            f"User: {msg.content}\n"
                        )

                    else:

                        conversation += (
                            f"AI: {msg.content}\n"
                        )

                conversation += (
                    "Respond naturally based on "
                    "the conversation above.\n"
                )

                if uploaded_image:

                    image = Image.open(
                        uploaded_image
                    )

                    response = model.generate_content(
                        [
                            conversation,
                            image
                        ]
                    )

                else:

                    response = model.generate_content(
                        conversation
                    )

                ai_response = response.text

            except Exception as e:

                print(
                    "GEMINI ERROR:",
                    e
                )

                ai_response = (
                    "⚠️ AI service is temporarily busy. "
                    "Please wait a minute and try again."
                )

            Message.objects.create(
                chat=selected_chat,
                sender='ai',
                content=ai_response
            )

        return redirect(
            'chat_detail',
            chat_id=selected_chat.id
        )

    return render(
        request,
        'chat.html',
        {
            'chats': chats,
            'selected_chat': selected_chat
        }
    )


@login_required(login_url='login')
def new_chat(request):

    Chat.objects.create(
        user=request.user,
        title="New Chat"
    )

    return redirect('chat')


@login_required(login_url='login')
def rename_chat(request, chat_id):

    chat = Chat.objects.get(
        id=chat_id,
        user=request.user
    )

    if request.method == 'POST':

        title = request.POST.get(
            'title'
        )

        if title:

            chat.title = title
            chat.save()

    return redirect(
        'chat_detail',
        chat_id=chat.id
    )


@login_required(login_url='login')
def delete_chat(request, chat_id):

    chat = Chat.objects.get(
        id=chat_id,
        user=request.user
    )

    chat.delete()

    return redirect('chat')


@login_required(login_url='login')
def pin_chat(request, chat_id):

    chat = Chat.objects.get(
        id=chat_id,
        user=request.user
    )

    chat.is_pinned = not chat.is_pinned

    chat.save()

    return redirect('chat')


def shared_chat(request, share_id):

    chat = Chat.objects.get(
        share_id=share_id
    )

    return render(
        request,
        'shared_chat.html',
        {
            'shared_chat': chat
        }
    )


@login_required(login_url='login')
def export_pdf(request, chat_id):

    chat = Chat.objects.get(
        id=chat_id,
        user=request.user
    )

    response = HttpResponse(
        content_type='application/pdf'
    )

    response[
        'Content-Disposition'
    ] = (
        f'attachment; '
        f'filename="{chat.title}.pdf"'
    )

    pdf = canvas.Canvas(response)

    y = 800

    pdf.setFont(
        "Helvetica-Bold",
        16
    )

    pdf.drawString(
        50,
        y,
        chat.title
    )

    y -= 40

    pdf.setFont(
        "Helvetica",
        10
    )

    for message in chat.messages.all():

        text = (
            f"{message.sender.upper()}: "
            f"{message.content}"
        )

        lines = text.split("\n")

        for line in lines:

            pdf.drawString(
                50,
                y,
                line[:120]
            )

            y -= 20

            if y < 50:

                pdf.showPage()

                y = 800

    pdf.save()

    return response


@login_required(login_url='login')
def profile_page(request):

    total_chats = Chat.objects.filter(
        user=request.user
    ).count()

    total_messages = Message.objects.filter(
        chat__user=request.user
    ).count()

    return render(
        request,
        'profile.html',
        {
            'total_chats': total_chats,
            'total_messages': total_messages
        }
    )


def logout_page(request):

    logout(request)

    return redirect('login')