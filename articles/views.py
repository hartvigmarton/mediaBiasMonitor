from django.http import HttpResponse
from django.shortcuts import render
from .models import Article,Blog_Post  # Import your model for data storage
import threading
import time
from rest_framework.response import Response
from rest_framework.views import APIView
from .serializers import ArticleSerializer
from .rss_scraper import gather_data
from .entity_manager import update_database


def print_value(request):
    if request.method == 'POST':
        submitted_value = request.POST.get('expression', '')
        # You can print the value or perform any other action here
        print(submitted_value)
    return HttpResponse(submitted_value)


def rss_test(request):
    titles = gather_data()
    return render(request,'rss_titles.html', {'titles': titles})

def get_terms_on_sites(request):
    if request.method == 'GET':
        submitted_values = request.GET.getlist('expression')  # Get a list of submitted expressions


        articles = Article.objects.filter(term__in=submitted_values)  # Retrieve articles with terms in the submitted list

        return render(request, 'articles.html', {'articles': articles})

    return HttpResponse("Form submitted successfully")


def view_articles(request):
    if request.method == 'GET':
        submitted_value = request.GET.get('expression', '')
        articles = Article.objects.filter(term=submitted_value)  # Retrieve all articles from the database
        return render(request, 'articles.html', {'articles': articles})
    return HttpResponse("Form submitted successfully")


def periodic_task():
    while True:
        update_database()  # Call your function
        time.sleep(900)  # Sleep for 5 minutes (300 seconds)


def start_periodic_task(request):
    periodic_thread = threading.Thread(target=periodic_task)
    periodic_thread.daemon = True  # This ensures the thread terminates when the main program does
    periodic_thread.start()
    return HttpResponse("Adatbázis frissítése")


def list_entries(request):
    entries = Blog_Post.objects.all()
    return render(request, 'entry_list.html', {'entries': entries})


def index(request):
    entries = Blog_Post.objects.all()
    return render(request, 'index.html',{'entries': entries})


class ArticleList(APIView):
    def get(self, request):
        articles = Article.objects.all()
        serializer = ArticleSerializer(articles, many=True)
        return Response(serializer.data)
