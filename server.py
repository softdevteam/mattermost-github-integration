import os
import requests
from flask import Flask
from flask import request
import json
import config

app = Flask(__name__)

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
    elif event == "create":
        process_create(data)

    return "Ok"

def process_create(data):
    ref_type = data['ref_type']
    if ref_type == "branch":
        branchname = data['ref']
        user = create_user_link(data)
        repo = create_repo_link(data)

        msg = """#### %s added branch `%s` to %s""" % (user, branchname, repo)
        post_text(msg)

def process_issue_comment(data):
    if data['action'] != "created":
        return

    user = create_user_link(data)
    number = data['issue']['number']
    url = data['issue']['html_url']
    title = data['issue']['title']
    body = data['comment']['body']
    msg = """#### %s commented on [%s](%s)
%s""" % (user, title, url, body)
    post_text(msg)

def process_issues(data):
    if data['action'] != "opened":
        return

    user = create_user_link(data)
    repo = create_repo_link(data)
    number = data['issue']['number']
    url = data['issue']['html_url']
    title = data['issue']['title']
    body = data['issue']['body']
    msg = """#### New issue: #%s [%s](%s)
%s *Issue created by %s in %s.*""" % (number, title, url, body, user, repo)
    post_text(msg)

def process_repository(data):
    if data['action'] != "created":
        return

    user = create_user_link(data)
    repo = create_repo_link(data)
    repodescr = data['repository']['description']
    msg = """#### New repository: %s
%s _Created by %s._""" % (repo, repodescr, user)
    post_text(msg)

def process_prs(data):
    # only process new PRs for now
    if data['action'] != "opened":
        return

    user = create_user_link(data)
    repo = create_repo_link(data)
    number = data['pull_request']['number']
    url = data['pull_request']['html_url']
    title = data['pull_request']['title']
    msg = """#### New pull request: #%s [%s](%s)
_Pull request created by %s in %s._""" % (number, title, url, user, repo)
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

def create_repo_link(data):
    full_name = data['repository']['full_name']
    url = data['repository']['html_url']
    return "[%s](%s)" % (full_name, url)

def create_user_link(data):
    username = data['sender']['login']
    url = data['sender']['html_url']
    return "[%s](%s)" % (username, url)

if __name__ == "__main__":
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=True)
