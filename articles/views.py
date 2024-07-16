from django.http import HttpResponse
from .models import Article,Blog_Post  # Import your model for data storage
from rest_framework.response import Response
from rest_framework.views import APIView
from .serializers import ArticleSerializer
import matplotlib
matplotlib.use('Agg')
import os
from .config_handler import load_config
import plotly.graph_objects as go
from plotly.offline import plot
import datetime as DT
from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings



def view_titles(request):
    if request.method == 'GET':
        submitted_value = request.GET.get('expression', '')
        start_date_str = request.GET.get('start_date', '')
        end_date_str = request.GET.get('end_date', '')
        today = DT.date.today()
        week_ago = today - DT.timedelta(days=7)

        if start_date_str:
            start_date = DT.datetime.strptime(start_date_str, '%Y-%m-%d').date()
        else:
            start_date = week_ago

        if end_date_str:
            end_date = DT.datetime.strptime(end_date_str, '%Y-%m-%d').date() + DT.timedelta(days=1)
        else:
            end_date = today + DT.timedelta(days=1)

        plot_div = daily_number_of_articles_graph_per_medium(submitted_value, start_date, end_date)
        titles = Article.objects.filter(term=submitted_value, pub_date__range=(start_date, end_date))
        return render(request, 'titles.html', {'titles': titles, 'plot_div': plot_div})
    return HttpResponse("Form submitted successfully")


def list_blog_posts(request):
    entries = Blog_Post.objects.all()
    return render(request, 'entry_list.html', {'entries': entries})


def index(request):
    today = DT.date.today()
    end_date = today + DT.timedelta(days=1)
    week_ago = today - DT.timedelta(days=7)
    blog_posts = Blog_Post.objects.all()
    websites, terms = load_config()
    plot_div = daily_number_of_articles_graph_per_medium("Magyar Péter",start_date= week_ago,end_date= end_date)

    return render(request, 'index.html', {'blog_posts': blog_posts, 'terms': terms, 'plot_div': plot_div})

def blog_post_detail(request, post_id):
    post = get_object_or_404(Blog_Post, pk=post_id)
    return render(request, 'post_detail.html', {'post': post})


#plotly graph
def graph_view(request):
    blog_posts = Blog_Post.objects.all()
    websites, terms = load_config()
    if request.method == 'GET':
        submitted_values = request.GET.getlist('expression')  # Get a list of submitted expressions
        start_date_str = request.GET.get('start_date', '')
        end_date_str = request.GET.get('end_date', '')
        today = DT.date.today()
        week_ago = today - DT.timedelta(days=7)

        if start_date_str:
            start_date = DT.datetime.strptime(start_date_str, '%Y-%m-%d').date()
        else:
            start_date = week_ago

        if end_date_str:
            end_date = DT.datetime.strptime(end_date_str, '%Y-%m-%d').date() + DT.timedelta(days=1)
        else:
            end_date = today + DT.timedelta(days=1)

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
            return render(request, 'index.html', {'blog_posts': blog_posts, 'terms': terms, 'plot_div': plot_div})

        else:
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
            return render(request, 'index.html', {'blog_posts': blog_posts, 'terms': terms, 'plot_div': plot_div})


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

    return render(request, 'graph.html', {'plot_div': plot_div})
def dates_between(start_date, end_date):
    delta = DT.timedelta(days=1)
    current_date = start_date
    end_date = end_date - delta
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

def daily_number_of_articles_graph_per_medium(term, start_date, end_date):
    article_count_for_website = {}
    #TODO pass this data in a config file
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
    days = list(dates_between(start_date, end_date))
    articles = Article.objects.filter(term=term, pub_date__range=(start_date, end_date))

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

    plot_div = fig.to_html()

    return plot_div

class ArticleList(APIView):
    def get(self, request):
        articles = Article.objects.all()
        serializer = ArticleSerializer(articles, many=True)
        return Response(serializer.data)


@csrf_exempt
def upload_image(request):
    if request.method == 'POST':
        file = request.FILES['file']
        file_path = os.path.join(settings.MEDIA_ROOT, file.name)
        with open(file_path, 'wb+') as destination:
            for chunk in file.chunks():
                destination.write(chunk)
        return JsonResponse({'location': f'{settings.MEDIA_URL}{file.name}'})
    return JsonResponse({'error': 'Invalid request'}, status=400)

