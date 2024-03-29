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
import matplotlib
matplotlib.use('Agg')
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
        time.sleep(3600)  # Sleep for 5 minutes (300 seconds)


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

            all_article_counts = []  # List to store all article counts for finding the absolute maximum

            for value in submitted_values:
                articles = Article.objects.filter(term__in=[value])
                websites = set([article.website for article in articles])

                # Count the number of articles for each website
                article_counts = [articles.filter(website=website).count() for website in websites]

                all_article_counts.extend(article_counts)  # Add article counts to the list

                data_by_value.append((list(websites), article_counts, value))

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

            ax.set_xlabel('Híroldal')
            ax.set_ylabel('Hírek száma')
            ax.set_title('Kifejezést tartalmazó címek száma híroldalanként')
            ax.set_xticks([i + (width * (len(submitted_values) - 1) / 2) for i in range(len(x_values))])
            ax.set_xticklabels(x_values, rotation=15, ha='right')  # Rotate x-axis labels for better readability

            # Set y-axis limit to the absolute maximum value
            ax.set_ylim(0, max(all_article_counts) + 1)  # Add 1 to ensure the maximum value is fully visible

            # Set y-axis tick labels as integers
            plt.yticks(range(max(all_article_counts) + 1))

            ax.legend()

        else:
            articles = Article.objects.filter(term__in=submitted_values)
            websites = set([article.website for article in articles])

            # Count the number of articles for each website
            article_counts = [articles.filter(website=website).count() for website in websites]

            # Plot a bar chart
            plt.figure(figsize=(12, 8))  # Adjust the figure size as needed

            plt.bar(list(websites), article_counts)
            plt.xlabel('Híroldal')
            plt.ylabel('Hírek száma')
            plt.title('\"' + submitted_values[0] + '\" kifejezést tartalmazó címek száma híroldalanként')
            plt.xticks(rotation=15, ha='right')  # Rotate x-axis labels for better readability
            # Set y-axis tick labels as integers
            plt.yticks(range(max(article_counts) + 1))

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
