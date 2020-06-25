from urllib.parse import urlparse
import ast, json, requests

apiID = '1ddd0896'
apiKEY = '58ef01156cda25a59462f34755cb565d'
added = 'tofu'
addURL = "https://api.edamam.com/search?app_id={0}&app_key={1}&q={2}".format(apiID, apiKEY, added)
cBackDict = requests.get(addURL).json()['q']
cBackStr = json.dumps(cBackDict)
# cBack = str(cBackDict)
cBackConvert = json.loads(cBack)


print(type(cBack))
print(cBack)