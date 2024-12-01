from django.test import TestCase

from mediaBiasMonitor.articles.models import Article


# Create your tests here.
class ArticleTestCase(TestCase):
    def setUp(self):
        Article.objects.create(title=" Izraeli védelmi miniszter: Franciaország ellenséges a zsidó néppel  ", term="Izrael", website="HVG", link="http://hvg.hu/vilag/20241016_Izraeli-vedelmi-miniszter-Franciaorszag-ellenseges-a-zsido-neppel#rss")
        Article.objects.create(title=" Bemutatta győzelmi tervét Zelenszkij az ukrán parlamentben  ", term="Zelenszkij", website="HVG", link="http://hvg.hu/vilag/20241016_Zelenszkij-prezentalta-a-beketervet-Ukrajna-Oroszorszag-haboru-gyozelem-vege#rss")