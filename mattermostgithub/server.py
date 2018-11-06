import json
import hmac
import hashlib
import requests
from flask import request

try:
    from mattermostgithub import config
except ImportError:
    print("Could not import config. Using test-config instead.")
    from tests import config

from mattermostgithub.payload import (
    PullRequest, PullRequestReview, PullRequestComment, Issue, IssueComment,
    Repository, Branch, Push, Tag, CommitComment, Wiki, Status
)

from mattermostgithub import app

SECRET = hmac.new(config.SECRET.encode('utf8'), digestmod=hashlib.sha1) if config.SECRET else None

@app.route(config.SERVER['hook'] or "/", methods=['POST'])
def root():
    if request.json is None:
        print('Invalid Content-Type')
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
    if event == "ping":
        msg = "ping from %s" % data['repository']['full_name']
    elif event == "pull_request":
        if data['action'] == "opened":
            msg = PullRequest(data).opened()
        elif data['action'] == "closed":
            msg = PullRequest(data).closed()
        elif data['action'] == "assigned":
            msg = PullRequest(data).assigned()
        elif data['action'] == "synchronize":
            msg = PullRequest(data).synchronize()
    elif event == "issues":
        if data['action'] == "opened":
            msg = Issue(data).opened()
        elif data['action'] == "closed":
            msg = Issue(data).closed()
        elif data['action'] == "labeled":
            msg = Issue(data).labeled()
        elif data['action'] == "assigned":
            msg = Issue(data).assigned()
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
    elif event == "delete":
        if data['ref_type'] == "branch":
            msg = Branch(data).deleted()
    elif event == "pull_request_review":
        if data['action'] == "submitted":
            msg = PullRequestReview(data).submitted()
    elif event == "pull_request_review_comment":
        if data['action'] == "created":
            msg = PullRequestComment(data).created()
    elif event == "push":
        if not (data['deleted'] and data['forced']):
            if not data['ref'].startswith("refs/tags/"):
                msg = Push(data).commits()
    elif event == "commit_comment":
        if data['action'] == "created":
            msg = CommitComment(data).created()
    elif event == "gollum":
        msg = Wiki(data).updated()
    elif event == "status":
        if data["state"] in ["failure", "error"]:
            msg = Status(data).updated()

    if msg:
        hook_info = get_hook_info(data)
        if hook_info:
            url, channel = get_hook_info(data)

            action = None
            if data.has_key("action"):
                action = data["action"]
            elif data.has_key("ref_type"):
                action = data["ref_type"]

            if action:
                if hasattr(config, "GITHUB_IGNORE_ACTIONS") and \
                   event in config.GITHUB_IGNORE_ACTIONS and \
                   action in config.GITHUB_IGNORE_ACTIONS[event]:
                    return "Notification action ignored (as per configuration)"

            if hasattr(config, "IGNORE_USER_EVENTS") and data.has_key('sender') \
               and data['sender']['login'] in config.IGNORE_USER_EVENTS \
               and event in config.IGNORE_USER_EVENTS[data['sender']['login']]:
                return "User blocked from generating this notifications"

            if hasattr(config, "REDIRECT_EVENTS") and \
                    event in config.REDIRECT_EVENTS:
                channel = config.REDIRECT_EVENTS[event]

            post(msg, url, channel)
            return "Notification successfully posted to Mattermost"
        else:
            return "Notification ignored (repository is blacklisted)."
    else:
        return "Not implemented", 400

def post(text, url, channel):
    data = {}
    data['text'] = text
    data['channel'] = channel
    data['username'] = config.USERNAME
    data['icon_url'] = config.ICON_URL

    headers = {'Content-Type': 'application/json'}
    r = requests.post(url, headers=headers, data=json.dumps(data), verify=False)

    if r.status_code is not requests.codes.ok:
        print('Encountered error posting to Mattermost URL %s, status=%d, response_body=%s' % (url, r.status_code, r.json()))

def get_hook_info(data):
    if 'repository' in data:
        repo = data['repository']['full_name']
        if repo in config.MATTERMOST_WEBHOOK_URLS:
            return config.MATTERMOST_WEBHOOK_URLS[repo]
    if 'organization' in data:
        org = data['organization']['login']
        if org in config.MATTERMOST_WEBHOOK_URLS:
            return config.MATTERMOST_WEBHOOK_URLS[org]
    if 'repository' in data:
        if 'login' in data['repository']['owner']:
            owner = data['repository']['owner']['login']
            if owner in config.MATTERMOST_WEBHOOK_URLS:
                return config.MATTERMOST_WEBHOOK_URLS[owner]
        if 'name' in data['repository']['owner']:
            owner = data['repository']['owner']['name']
            if owner in config.MATTERMOST_WEBHOOK_URLS:
                return config.MATTERMOST_WEBHOOK_URLS[owner]
    return config.MATTERMOST_WEBHOOK_URLS['default']

if __name__ == "__main__":
    app.run(
        host=config.SERVER['address'] or "0.0.0.0",
        port=config.SERVER['port'] or 5000,
        debug=False
    )
