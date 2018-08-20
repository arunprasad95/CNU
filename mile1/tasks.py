from __future__ import absolute_import, unicode_literals
from celery import shared_task,group,Celery,chain
import http.client, urllib.request, urllib.parse, urllib.error, base64
import ssl
import json
ssl._create_default_https_context = ssl._create_unverified_context
import mile1.models
import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'assignment7.settings')

@shared_task
def add(x, y):
    return x + y


@shared_task
def mul(x, y):
    return x * y


@shared_task
def xsum(numbers):
    return sum(numbers)
@shared_task
def update_rest_image_added(rest_id):
    res = mile1.models.Restaurant.objects.get(id=rest_id)
    res.images_added = True
    res.save()
@shared_task
def set_image(rest_id,url):
    image = mile1.models.Image()
    image.restaurant = mile1.models.Restaurant.objects.get(id=rest_id)
    image.url = url
    image.save()
@shared_task
def download_image(urls,rest_id):
    return group(set_image.s(rest_id,url) for url in urls)()
@shared_task
def retrieve_urls(rest_name,rest_id):
    print(rest_name,rest_id)
    headers = {
        # Request headers
        'Ocp-Apim-Subscription-Key': 'f575457044a04a678f057c64049f6b8a',
    }
    try:
        conn = http.client.HTTPSConnection('api.cognitive.microsoft.com')
        params = urllib.parse.urlencode({
            # Request parameters
            'q': rest_name,
            'count': '10',
            'offset': '0',
            'mkt': 'en-us',
            'safeSearch': 'Moderate',
        })
        conn.request("GET", "/bing/v7.0/images/search?%s" % params, "{body}", headers)
        response = conn.getresponse()
        data = response.read()
        obj = json.loads(data)
        conn.close()
        urls = [i['contentUrl'] for i in obj['value']]
        print(urls)
        return  urls
    except Exception as e:
        print("[Errno {0}] {1}".format(e.errno, e.strerror))
@shared_task
def download(rest_name,rest_id):
    chain(
        retrieve_urls.s(rest_name,rest_id),
        download_image.s(rest_id),
        update_rest_image_added.si(rest_id)
    )()