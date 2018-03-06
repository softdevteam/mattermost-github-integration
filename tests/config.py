USERNAME = "Github"
ICON_URL = ""
MATTERMOST_WEBHOOK_URLS = {
    'default' : ("yourdomain.org/hooks/hookid", "off-topic2"),
}
SECRET = ""
SHOW_AVATARS = True
SERVER = {
    'hook': "/",
    'address': "0.0.0.0",
    'port': 5000,
}

# Ignore specified event actions
GITHUB_IGNORE_ACTIONS = {
    "create": ["tag"]
}
