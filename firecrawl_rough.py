import requests

url = "https://www.cs.washington.edu/academics/courses/"

payload = {
    "url": "https://www.cs.washington.edu/academics/courses/",
    # "excludePaths": ["<string>"],
    # "includePaths": ["<string>"],
    "maxDepth": 10,
    "maxDiscoveryDepth": 2,
    "ignoreSitemap": False,
    "ignoreQueryParameters": False,
    "limit": 10000,
    "allowBackwardLinks": False,
    "allowExternalLinks": True,
    
}
headers = {
    "Authorization": "Bearer <token>",
    "Content-Type": "application/json"
}

response = requests.request("POST", url, json=payload, headers=headers)

print(response.text)