import feedparser
import alkali
from alkali import fields

class RssLoader(alkali.Storage):

    def __init__(self, url):
        self.filename = url

    def read(self, model_class):
        feed = feedparser.parse(self.filename)
        for item in feed['items']:
            yield item


class Episode(alkali.Model):

    class Meta:
        storage = RssLoader('https://pythonbytes.fm/episodes/rss')

    guid           = fields.UUIDField(primary_key=True)
    title          = fields.StringField()
    published      = fields.DateTimeField()
    itunes_episode = fields.IntField()
    link           = fields.StringField()
    description    = fields.StringField()

    def __str__(self):
        return f"<Epsiode {self.itunes_episode} - {self.title}>"

    @property
    def num(self):
        return self.itunes_episode


db = alkali.Database(models=[Episode])
db.load()

# or directly but non-traditionally
# Episode.objects.load(Episode.Meta.storage)

print("last 10 episodes with 'python' in the title")
for ep in Episode.objects.filter(title__rei=r"\bpython\b").order_by('-published').limit(10):
    print('  ', ep)

print("total episode count:", Episode.objects.count)

e = Episode.objects.get(itunes_episode=100)
print(e.title, e.published.date())

print("episode featuring alkali:", Episode.objects.get(title__rei='alkali').link)
