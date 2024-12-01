from .models import Article, Blog_Post  # Import your model for data storage
from rest_framework.response import Response
from rest_framework.views import APIView
from .serializers import ArticleSerializer
import matplotlib
matplotlib.use('Agg')
from .config_handler import load_config
import plotly.graph_objects as go
from plotly.offline import plot
import datetime as DT
from django.shortcuts import render, get_object_or_404

today = DT.date.today()
week_ago = today - DT.timedelta(days=7)
websites, terms = load_config()


def view_titles(request):
    submitted_value = request.GET.get('expression', '')
    start_date_str = request.GET.get('start_date', '')
    end_date_str = request.GET.get('end_date', '')

    if start_date_str:
        start_date = DT.datetime.strptime(start_date_str, '%Y-%m-%d').date()
    else:
        start_date = week_ago

    if end_date_str:
        end_date = DT.datetime.strptime(end_date_str, '%Y-%m-%d').date() + DT.timedelta(days=1)
    else:
        end_date = today + DT.timedelta(days=1)

    plot_div = daily_number_of_articles_per_medium_graph(submitted_value, start_date, end_date)
    titles = Article.objects.filter(term=submitted_value, pub_date__range=(start_date, end_date))
    return render(request, 'titles.html', {'titles': titles, 'plot_div': plot_div})


def list_blog_posts(request):
    posts = Blog_Post.objects.all()
    return render(request, 'post_list.html', {'posts': posts})


def index(request):
    end_date = today + DT.timedelta(days=1)
    blog_posts = Blog_Post.objects.all()
    plot_div = daily_number_of_articles_per_medium_graph("Magyar Péter", start_date=week_ago, end_date=end_date)

    return render(request, 'index.html', {'blog_posts': blog_posts, 'terms': terms, 'plot_div': plot_div})

def blog_post_detail(request, slug):
    post = get_object_or_404(Blog_Post, slug=slug)
    return render(request, 'post_detail.html', {'post': post})


def total_nr_titles_per_medium_graph(request):
    blog_posts = Blog_Post.objects.all()
    if request.method == 'GET':
        submitted_values = request.GET.getlist('expression')  # Get a list of submitted expressions
        start_date_str = request.GET.get('start_date', '')
        end_date_str = request.GET.get('end_date', '')

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

            for value in submitted_values:
                articles = Article.objects.filter(term__in=[value], pub_date__range=(start_date, end_date))
                websites = set([article.website for article in articles])
                article_count_for_term = {}
                for website in websites:
                    count = articles.filter(website=website).count()
                    article_count_for_term[website] = count
                all_article_counts[value] = article_count_for_term

            fig = go.Figure(
                layout_title_text= str(start_date) + " és " + str(
                    end_date) + " között.")

            for value in submitted_values:
                fig.add_trace(go.Bar(
                    x=list(websites),
                    y=[all_article_counts[value].get(website, 0) for website in websites],
                    name=value,
                    marker_color='indianred' if value == submitted_values[0] else 'lightsalmon'
                ))

            # Here we modify the tickangle of the xaxis, resulting in rotated labels.
            fig.update_layout(barmode='group', xaxis_tickangle=-45,
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
            fig.update_layout(barmode='group', xaxis_tickangle=-45,
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
            plot_div = plot(fig, output_type='div', include_plotlyjs=False)

            # Pass the HTML content to the template
            return render(request, 'index.html', {'blog_posts': blog_posts, 'terms': terms, 'plot_div': plot_div})


def dates_between(start_date, end_date):
    delta = DT.timedelta(days=1)
    current_date = start_date
    end_date = end_date - delta
    while current_date <= end_date:
        yield current_date
        current_date += delta


def daily_number_of_articles_per_medium_graph(term, start_date, end_date):
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
