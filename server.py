import os
import requests
from flask import Flask
from flask import request
import json
import config
import hmac
import hashlib

from payload import PullRequest, PullRequestComment, Issue, IssueComment, Repository, Branch, Push, Tag

app = Flask(__name__)

SECRET = hmac.new(config.SECRET, digestmod=hashlib.sha1) if config.SECRET else None

@app.route('/', methods=['POST'])
def root():
    if request.json is None:
       print 'Invalid Content-Type'
       return 'Content-Type must be application/json and the request body must contain valid JSON', 400

    if SECRET:
        signature = request.headers.get('X-Hub-Signature', None)
        sig2 = SECRET.copy()
        sig2.update(request.data)

        if signature is None or sig2.hexdigest() != signature.split('=')[1]:
            return 'Invalid or missing X-Hub-Signature', 400

    data = request.json
    event = request.headers['X-Github-Event']

    msg = ""
    if event == "pull_request":
        if data['action'] == "opened":
            msg = PullRequest(data).opened()
        elif data['action'] == "closed":
            msg = PullRequest(data).closed()
        elif data['action'] == "assigned":
            msg = PullRequest(data).assigned()
    elif event == "issues":
        if data['action'] == "opened":
            msg = Issue(data).opened()
        elif data['action'] == "closed":
            msg = Issue(data).closed()
    elif event == "issue_comment":
        if data['action'] == "created":
            msg = IssueComment(data).created()
    elif event == "repository":
        if data['action'] == "created":
            msg = Repository(data).created()
    elif event == "create":
        if data['ref_type'] == "branch":
            msg = Branch(data).created()
        elif data['ref_type'] == "tag":
            msg = Tag(data).created()
    elif event == "pull_request_review_comment":
        if data['action'] == "created":
            msg = PullRequestComment(data).created()
    elif event == "push":
        if not (data['deleted'] and data['forced']):
            msg = Push(data).commits()

    if msg:
        url, channel = get_hook_info(data)
        post(msg, url, channel)

    return "Ok"

def post(text, url, channel):
    data = {}
    data['text'] = text
    data['channel'] = channel
    data['username'] = config.USERNAME
    data['icon_url'] = config.ICON_URL

    headers = {'Content-Type': 'application/json'}
    r = requests.post(url, headers=headers, data=json.dumps(data), verify=False)

    if r.status_code is not requests.codes.ok:
        print 'Encountered error posting to Mattermost URL %s, status=%d, response_body=%s' % (url, r.status_code, r.json())

def get_hook_info(data):
    if 'repository' in data:
        repo = data['repository']['full_name']
        if repo in config.MATTERMOST_WEBHOOK_URLS:
            return config.MATTERMOST_WEBHOOK_URLS[repo]
    if 'organization' in data:
        org = data['organization']['login']
        if org in config.MATTERMOST_WEBHOOK_URLS:
            return config.MATTERMOST_WEBHOOK_URLS[org]
    return config.MATTERMOST_WEBHOOK_URLS['default']

if __name__ == "__main__":
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=True)
