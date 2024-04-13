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
import plotly.graph_objects as go
from plotly.offline import plot
import datetime as DT
import plotly.express as px


def print_value(request):
    if request.method == 'POST':
        submitted_value = request.POST.get('expression', '')
        # You can print the value or perform any other action here
        print(submitted_value)
    return HttpResponse(submitted_value)


def view_titles(request):
    if request.method == 'GET':
        submitted_value = request.GET.get('expression', '')
        start_date = request.GET.getlist('start_date')[0]
        end_date = request.GET.getlist('end_date')[0]
        today = DT.date.today()
        week_ago = today - DT.timedelta(days=7)

        if start_date == "":
            start_date = week_ago

        if end_date == "":
            end_date = today

        titles = Article.objects.filter(term=submitted_value,pub_date__range=(start_date, end_date)) # Retrieve all articles from the database
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
    websites, terms = load_config()
    plot_div = index_graph()

    return render(request, 'index.html', {'entries': entries, 'terms': terms, 'plot_div': plot_div})


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


def graph_view2(request):
    if request.method == 'GET':
        submitted_values = request.GET.getlist('expression')  # Get a list of submitted expressions
        start_date = request.GET.getlist('start_date')[0]
        end_date = request.GET.getlist('end_date')[0]
        today = DT.date.today()
        week_ago = today - DT.timedelta(days=7)

        if start_date == "":
            print("ürest startdate")
            start_date = week_ago

        if end_date == "":
            end_date = today

        if len(submitted_values) > 1:

            all_article_counts = []
            article_count_for_term = {}
            counter = 0
            for value in submitted_values:
                articles = Article.objects.filter(term__in=[value], pub_date__range=(start_date, end_date))
                websites = set([article.website for article in articles])
                article_counts = [articles.filter(website=website).count() for website in websites]
                article_count_for_term[counter] = article_counts
                all_article_counts.extend(article_counts)
                counter += 1

            fig = go.Figure(layout_title_text = "Kifejezést tartalmazó címek száma újságonként " + str(start_date) + " és " + str(end_date) + " között.")
            fig.add_trace(go.Bar(
                x=list(websites),
                y=article_count_for_term[0],
                name=submitted_values[0],
                marker_color='indianred'
            ))
            fig.add_trace(go.Bar(
                x=list(websites),
                y=article_count_for_term[1],
                name=submitted_values[1],
                marker_color='lightsalmon'
            ))

            # Here we modify the tickangle of the xaxis, resulting in rotated labels.
            fig.update_layout(barmode='group', xaxis_tickangle=-45)

            # Convert the figure to HTML
            plot_div = plot(fig, output_type='div', include_plotlyjs=False)

            # Pass the HTML content to the template
            return render(request, 'graph2.html', {'plot_div': plot_div})

        else:
            all_article_counts = []
            article_count_for_term = {}
            counter = 0
            for value in submitted_values:
                articles = Article.objects.filter(term__in=[value])
                websites = set([article.website for article in articles])
                article_counts = [articles.filter(website=website).count() for website in websites]
                article_count_for_term[counter] = article_counts
                all_article_counts.extend(article_counts)
                counter += 1

            fig = go.Figure(layout_title_text = "Kifejezést tartalmazó címek száma újságonként")
            fig.add_trace(go.Bar(
                x=list(websites),
                y=article_count_for_term[0],
                name=str(submitted_values),
                marker_color='indianred'
            ))
            fig.update_layout(barmode='group', xaxis_tickangle=-45)

            # Convert the figure to HTML
            plot_div = plot(fig, output_type='div', include_plotlyjs=False)

            # Pass the HTML content to the template
            return render(request, 'graph2.html', {'plot_div': plot_div})

def index_graph():
    today = DT.date.today()
    week_ago = today - DT.timedelta(days=7)
    terms = ["Varga Judit","Magyar Péter"]
    all_article_counts = []
    article_count_for_term = {}
    counter = 0
    for value in terms:
        articles = Article.objects.filter(term__in=[value], pub_date__range=(week_ago, today))
        websites = set([article.website for article in articles])
        article_counts = [articles.filter(website=website).count() for website in websites]
        article_count_for_term[counter] = article_counts
        all_article_counts.extend(article_counts)
        counter += 1

    fig = go.Figure( layout_title_text = "Kifejezést tartalmazó címek száma újságonként")

    fig.add_trace(go.Bar(
        x=list(websites),
        y=article_count_for_term[0],
        name=terms[0],
        marker_color='indianred'
    ))
    fig.add_trace(go.Bar(
        x=list(websites),
        y=article_count_for_term[1],
        name=terms[1],
        marker_color='lightsalmon'
    ))

    # Here we modify the tickangle of the xaxis, resulting in rotated labels.
    fig.update_layout(barmode='group', xaxis_tickangle=-45)
    fig.update_layout(
        autosize=False,
        width=500,
        height=500,
        margin=dict(
            l=50,
            r=50,
            b=100,
            t=100,
            pad=4
        ),
        paper_bgcolor="#f0f7ff",)
    # Convert the figure to HTML
    plot_div = plot(fig, output_type='div', include_plotlyjs=False)

    return plot_div
def daily_number_of_articles_graph():
    today = DT.date.today()
    week_ago = today - DT.timedelta(days=7)
    terms = ["Varga Judit", "Magyar Péter"]
    all_article_counts = []
    article_count_for_term = {}
    counter = 0
    for value in terms:
        articles = Article.objects.filter(term__in=[value], pub_date__range=(week_ago, today))
        websites = sorted(set([article.website for article in articles]))
        article_counts = [articles.filter(website=website).count() for website in websites]
        article_count_for_term[counter] = article_counts
        all_article_counts.extend(article_counts)
        counter += 1

    fig = go.Figure(layout_title_text="Kifejezést tartalmazó címek száma újságonként")

    for i in range(len(terms)):
        fig.add_trace(go.Scatter(
            x=websites,
            y=article_count_for_term[i],
            mode='lines+markers',
            name=terms[i],
            line=dict(color='rgb(31, 119, 180)'),
            marker=dict(color='rgb(31, 119, 180)', size=10)
        ))

    fig.update_layout(
        xaxis=dict(title='Websites'),
        yaxis=dict(title='Number of Articles'),
        autosize=False,
        width=800,
        height=600,
        margin=dict(l=50, r=50, b=100, t=100, pad=4),
        paper_bgcolor="#f0f7ff",
    )

    # Convert the figure to HTML
    plot_div = fig.to_html()

    return plot_div


class ArticleList(APIView):
    def get(self, request):
        articles = Article.objects.all()
        serializer = ArticleSerializer(articles, many=True)
        return Response(serializer.data)

