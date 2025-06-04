import http.client

conn = http.client.HTTPSConnection("meteostat.p.rapidapi.com")

headers = {
    'x-rapidapi-key': "77129d1f44msh6caedb88d5797c4p191e1cjsn34d06f9324a7",
    'x-rapidapi-host': "meteostat.p.rapidapi.com"
}

conn.request("GET", "/point/monthly?lat=52.5244&lon=13.4105&alt=43&start=2020-01-01&end=2020-12-31", headers=headers)

res = conn.getresponse()
data = res.read()

print(data.decode("utf-8"))