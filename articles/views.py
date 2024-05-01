from django.http import HttpResponse
from django.shortcuts import render
from .models import Article,Blog_Post  # Import your model for data storage
import threading
import time
from rest_framework.response import Response
from rest_framework.views import APIView
from .serializers import ArticleSerializer
from .rss_scraper import gather_data
#from .entity_manager import update_database
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import os
from .config_handler import load_config
import plotly.graph_objects as go
from plotly.offline import plot
import datetime as DT
import plotly.express as px
from django.shortcuts import render, get_object_or_404


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



def list_entries(request):
    entries = Blog_Post.objects.all()
    return render(request, 'entry_list.html', {'entries': entries})


def index(request):
    blog_posts = Blog_Post.objects.all()
    websites, terms = load_config()
    plot_div = daily_number_of_articles_graph_per_medium()

    return render(request, 'index.html', {'blog_posts': blog_posts, 'terms': terms, 'plot_div': plot_div})

def blog_post_detail(request, post_id):
    post = get_object_or_404(Blog_Post, pk=post_id)
    return render(request, 'post_detail.html', {'post': post})


#matplotlib graph
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

#plotly graph
def graph_view2(request):
    if request.method == 'GET':
        submitted_values = request.GET.getlist('expression')  # Get a list of submitted expressions
        start_date = request.GET.getlist('start_date')[0]
        end_date = request.GET.getlist('end_date')[0]
        today = DT.date.today()
        week_ago = today - DT.timedelta(days=7)

        if start_date == "":
            start_date = week_ago

        if end_date == "":
            end_date = today

        if len(submitted_values) > 1:
            all_article_counts = {}
            websites = set()

            for value in submitted_values:
                articles = Article.objects.filter(term__in=[value], pub_date__range=(start_date, end_date))
                new_websites = set([article.website for article in articles])
                websites.update(new_websites)
                article_count_for_term = {}
                for website in websites:
                    count = articles.filter(website=website).count()
                    article_count_for_term[website] = count
                all_article_counts[value] = article_count_for_term

            fig = go.Figure(
                layout_title_text="Kifejezést tartalmazó címek száma újságonként " + str(start_date) + " és " + str(
                    end_date) + " között.")

            for value in submitted_values:
                fig.add_trace(go.Bar(
                    x=list(websites),
                    y=[all_article_counts[value].get(website, 0) for website in websites],
                    name=value,
                    marker_color='indianred' if value == submitted_values[0] else 'lightsalmon'
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

            fig = go.Figure(layout_title_text = str(submitted_values[0]) +" kifejezést tartalmazó címek száma újságonként")
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

def index_graph(request):
    today = DT.date.today()
    week_ago = today - DT.timedelta(days=7)
    terms = ["Szentkirályi","Karácsony","Vitézy"]
    all_article_counts = []
    article_count_for_term = {}
    counter = 0
    websites = []
    set_size = 0
    for value in terms:
        articles = Article.objects.filter(term__in=[value], pub_date__range=(week_ago, today))
        if len(set([article.website for article in articles])) > set_size:
            websites = set([article.website for article in articles])
            set_size = len(set([article.website for article in articles]))
        article_counts = [articles.filter(website=website).count() for website in websites]
        print(websites)
        print(article_counts)
        article_count_for_term[value] = article_counts
        all_article_counts.extend(article_counts)
        counter += 1

    fig = go.Figure( layout_title_text = "Kifejezést tartalmazó címek száma újságonként")

    fig.add_trace(go.Bar(
        x=list(websites),
        y=article_count_for_term["Szentkirályi"],
        name="Szentkirályi",
        marker_color='orange'
    ))
    fig.add_trace(go.Bar(
        x=list(websites),
        y=article_count_for_term["Karácsony"],
        name="Karácsony",
        marker_color='rgb(169, 213, 34)'
    ))
    fig.add_trace(go.Bar(
        x=list(websites),
        y=article_count_for_term["Vitézy"],
        name="Vitézy",
        marker_color='#A0CDFF'
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

    return render(request, 'graph2.html', {'plot_div': plot_div})
def dates_between(start_date, end_date):
    delta = DT.timedelta(days=1)
    current_date = start_date
    while current_date <= end_date:
        yield current_date
        current_date += delta
def daily_number_of_articles_graph():
    today = DT.date.today()
    week_ago = today - DT.timedelta(days=7)
    terms = ["Varga Judit", "Magyar Péter"]
    all_article_counts = []
    article_count_for_term = {}
    counter = 0

    days = list(dates_between(week_ago, today))

    for value in terms:
        articles = Article.objects.filter(term__in=[value], pub_date__range=(week_ago, today))
        article_counts = [articles.filter(pub_date__date=day).count() for day in days]
        article_count_for_term[counter] = article_counts
        all_article_counts.extend(article_counts)
        counter += 1

    fig = go.Figure(layout_title_text="Kifejezést tartalmazó címek száma újságonként")

    fig.add_trace(go.Scatter(
        x=days,
        y=article_count_for_term[0],
        mode='lines+markers',
        name=terms[0],
        line=dict(color='indianred'),
        marker=dict(color='indianred', size=10)
    ))
    fig.add_trace(go.Scatter(
        x=days,
        y=article_count_for_term[1],
        mode='lines+markers',
        name=terms[1],
        line=dict(color='lightsalmon'),
        marker=dict(color='lightsalmon', size=10)
    ))

    fig.update_layout(
        xaxis=dict(title='Dátum', tickangle=-90, tickfont=dict(size=10)),
        yaxis=dict(title='Cikkek száma'),
        autosize=False,
        width=800,
        height=600,
        margin=dict(l=50, r=50, b=100, t=100, pad=4),
        plot_bgcolor="#ffffff",
        paper_bgcolor="#f0f7ff",
        xaxis_showgrid=True,
        yaxis_showgrid=True,
        xaxis_gridcolor='black',
        yaxis_gridcolor='black',
    )

    # Convert the figure to HTML
    plot_div = fig.to_html()

    return plot_div

def daily_number_of_articles_graph_per_medium():
    today = DT.date.today()
    week_ago = today - DT.timedelta(days=7)
    term = "Magyar Péter"
    article_count_for_website = {}
    website_color_dictionary = {
        "Telex": "rgb(0,255,187)",
        "444": "rgb(255,255,115)",
        "Origo": "rgb(5,25,210)",
        "Index": "rgb(255,153,0)",
        "Magyar Hang": "rgb(221,76,79)",
        "NÉPSZAVA": "rgb(21,126,252)",
        "mandiner": "rgb(176,133,32)",
        "Magyar Nemzet": "rgb(0,0,0)",
        "Ripost": "rgb(235,0,0)",
        "PestiSrácok": "rgb(140,140,140)",
        "NOL": "rgb(76,4,54)",
        "HVG": "rgb(226,89,0)"
    }
    days = list(dates_between(week_ago, today))

    articles = Article.objects.filter(term=term, pub_date__range=(week_ago, today))

    for article in articles:
        if article.website not in article_count_for_website:
            article_count_for_website[article.website] = [0] * len(days)
        idx = days.index(article.pub_date.date())
        article_count_for_website[article.website][idx] += 1

    fig = go.Figure(layout_title_text="\"" + term + "\" Kifejezést tartalmazó címek száma újságonként")

    for website, counts in article_count_for_website.items():
        fig.add_trace(go.Scatter(
            x=days,
            y=counts,
            mode='lines+markers',
            name=website,
            line=dict(color=website_color_dictionary.get(website, 'grey')),  # Default color to grey if not found
            marker=dict(color=website_color_dictionary.get(website, 'grey'), size=10)  # Default color to grey if not found
        ))

    fig.update_layout(
        xaxis=dict(title='Dátum', tickangle=-90, tickfont=dict(size=10)),
        yaxis=dict(title='Cikkek száma'),
        autosize=False,
        width=800,
        height=600,
        margin=dict(l=50, r=50, b=100, t=100, pad=4),
        plot_bgcolor="#ffffff",
        paper_bgcolor="#ffffff",
        xaxis_showgrid=True,
        yaxis_showgrid=True,
    )

    # Convert the figure to HTML
    plot_div = fig.to_html()

    return plot_div

class ArticleList(APIView):
    def get(self, request):
        articles = Article.objects.all()
        serializer = ArticleSerializer(articles, many=True)
        return Response(serializer.data)

