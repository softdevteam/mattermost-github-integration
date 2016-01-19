import os
import requests
from flask import Flask
from flask import request
import json
import config

app = Flask(__name__)

USERNAME = "Github"
ICON_URL = ""
MATTERMOST_WEBHOOK_URL = ""
CHANNEL = ""

@app.route('/', methods=['POST'])
def root():
    if request.json is None:
       print 'Invalid Content-Type'
       return 'Content-Type must be application/json and the request body must contain valid JSON', 400
    data = request.json

    event = request.headers['X-Github-Event']

    if event == "pull_request":
        process_prs(data)
    elif event == "issues":
        process_issues(data)
    elif event == "issue_comment":
        process_issue_comment(data)
    elif event == "repository":
        process_repository(data)

    return "Ok"

def process_issue_comment(data):
    if data['action'] != "created":
        return

    username = data['comment']['user']['login']
    userurl = data['comment']['user']['html_url']
    useravatar = data['comment']['user']['avatar_url']
    number = data['issue']['number']
    url = data['issue']['html_url']
    title = data['issue']['title']
    body = data['comment']['body']
    reponame = data['repository']['full_name']
    repourl = data['repository']['html_url']
    msg = """#### [%s](%s) commented on [%s](%s)
%s""" % (username, userurl, title, url, body)
    post_text(msg)

def process_issues(data):
    if data['action'] != "opened":
        return

    username = data['issue']['user']['login']
    userurl = data['issue']['user']['html_url']
    number = data['issue']['number']
    url = data['issue']['html_url']
    title = data['issue']['title']
    body = data['issue']['body']
    reponame = data['repository']['name']
    repourl = data['repository']['html_url']
    msg = """#### New issue: #%s - [%s](%s)
%s *Issue created by [%s](%s) in [%s](%s).*""" % (number, title, url, body, username, userurl, reponame, repourl)
    post_text(msg)

def process_repository(data):
    if data['action'] != "created":
        return

    username = data['sender']['login']
    userurl = data['sender']['html_url']
    reponame = data['repository']['full_name']
    repourl = data['repository']['html_url']
    repodescr = data['repository']['description']
    msg = """#### New repository: [%s](%s)
%s _Created by [%s](%s)._""" % (reponame, repourl, repodescr, username, userurl)
    post_text(msg)

def process_prs(data):
    # only process new PRs for now
    if data['action'] != "opened":
        return

    username = data['pull_request']['user']['login']
    userurl = data['pull_request']['user']['html_url']
    number = data['pull_request']['number']
    url = data['pull_request']['html_url']
    title = data['pull_request']['title']
    reponame = data['pull_request']['head']['repo']['name']
    repourl = data['pull_request']['head']['repo']['html_url']
    msg = """#### #%s - [%s](%s)
_Pull request created by [%s](%s) in [%s](%s)._""" % (number, title, url, username, userurl, reponame, repourl)
    post_text(msg)

def post_text(text):
    data = {}
    data['text'] = text
    data['channel'] = config.CHANNEL
    data['username'] = config.USERNAME
    data['icon_url'] = config.ICON_URL

    headers = {'Content-Type': 'application/json'}
    r = requests.post(config.MATTERMOST_WEBHOOK_URL, headers=headers, data=json.dumps(data), verify=False)

    if r.status_code is not requests.codes.ok:
        print 'Encountered error posting to Mattermost URL %s, status=%d, response_body=%s' % (config.MATTERMOST_WEBHOOK_URL, r.status_code, r.json())

if __name__ == "__main__":
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=True)
