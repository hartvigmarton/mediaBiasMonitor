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
import matplotlib.pyplot as plt
import os
from .config_handler import load_config


def print_value(request):
    if request.method == 'POST':
        submitted_value = request.POST.get('expression', '')
        # You can print the value or perform any other action here
        print(submitted_value)
    return HttpResponse(submitted_value)


def view_titles(request):
    if request.method == 'GET':
        submitted_value = request.GET.get('expression', '')
        titles = Article.objects.filter(term=submitted_value) # Retrieve all articles from the database
        return render(request, 'titles.html', {'titles': titles})
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
    websites,terms = load_config()

    return render(request, 'index.html', {'entries': entries, 'terms': terms})


def graph_view(request):
    if request.method == 'GET':
        submitted_values = request.GET.getlist('expression')  # Get a list of submitted expressions

        if len(submitted_values) > 1:
            # Create a list to store data for each submitted value
            data_by_value = []

            for value in submitted_values:
                print(value)
                articles = Article.objects.filter(term__in=[value])
                x_values = [article.website for article in articles]
                y_values = [len(article.title) for article in articles]
                data_by_value.append((x_values, y_values, value))

            # Plot a grouped bar chart
            fig, ax = plt.subplots()
            width = 0.35  # Width of the bars
            offset = 0  # Initial offset for positioning bars

            for x_values, y_values, label in data_by_value:
                bars = ax.bar([i + offset for i in range(len(x_values))], y_values, width, label=label)
                offset += width

                # Optionally, add labels to each bar
                for bar, x_value in zip(bars, x_values):
                    height = bar.get_height()
                    ax.annotate('{}'.format(height),
                                xy=(bar.get_x() + bar.get_width() / 2, height),
                                xytext=(0, 3),  # 3 points vertical offset
                                textcoords="offset points",
                                ha='center', va='bottom')

            ax.set_xlabel('Website')
            ax.set_ylabel('Nr Articles')
            ax.set_title('Nr terms on websites')
            ax.set_xticks([i + (width * (len(submitted_values) - 1) / 2) for i in range(len(x_values))])
            ax.set_xticklabels(x_values, rotation=45, ha='right')  # Rotate x-axis labels for better readability
            ax.legend()

        else:
            articles = Article.objects.filter(term__in=submitted_values)
            x_values = [article.website for article in articles]
            y_values = [len(article.title) for article in articles]

            # Plot a bar chart
            plt.bar(x_values, y_values)
            plt.xlabel('Website')
            plt.ylabel('Nr Articles')
            plt.title('Articles by Website for Submitted Values')
            plt.xticks(rotation=45, ha='right')  # Rotate x-axis labels for better readability

    # Modify filename generation
    cleaned_values = [value.replace(' ', '_').replace('á', 'a').replace('ö', 'o').replace('ú', 'u') for value in submitted_values]
    filename = "_".join(cleaned_values) + ".png"

    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    static_folder = os.path.join(BASE_DIR, 'static')
    graph_path = os.path.join(static_folder, 'graphs', filename)
    plt.savefig(graph_path)
    plt.close()

    return render(request, 'graph.html', {'graph_path': 'graphs/' + filename})

class ArticleList(APIView):
    def get(self, request):
        articles = Article.objects.all()
        serializer = ArticleSerializer(articles, many=True)
        return Response(serializer.data)
