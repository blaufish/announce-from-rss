#import http.client
#import urllib.request
import requests
url = 'https://t.co/heKq5Lf9rr'

#s = url.split("//")
#h = http.client.HTTPConnection(url)

#with urllib.request.urlopen(url) as h:
#    print(h)
#    print(h.read().decode('utf-8'))

r = requests.get(url, allow_redirects=False)
print(r.status_code, r.headers['Location'])
