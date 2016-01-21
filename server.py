import os
import requests
from flask import Flask
from flask import request
import json
import config

from payload import PullRequest, PullRequestComment, Issue, IssueComment, Repository, Branch

app = Flask(__name__)

@app.route('/', methods=['POST'])
def root():
    if request.json is None:
       print 'Invalid Content-Type'
       return 'Content-Type must be application/json and the request body must contain valid JSON', 400

    data = request.json
    event = request.headers['X-Github-Event']

    if event == "pull_request":
        if data['action'] == "opened":
            post(PullRequest(data).opened())
        elif data['action'] == "closed":
            post(PullRequest(data).closed())
        elif data['action'] == "assigned":
            post(PullRequest(data).assigned())
    elif event == "issues":
        if data['action'] == "opened":
            post(Issue(data).opened())
        elif data['action'] == "closed":
            post(Issue(data).closed())
    elif event == "issue_comment":
        if data['action'] == "created":
            post(IssueComment(data).created())
    elif event == "repository":
        if data['action'] == "created":
            post(Repository(data).created())
    elif event == "create":
        if data['ref_type'] == "branch":
            post(Branch(data).created())
    elif event == "pull_request_review_comment":
        if data['action'] == "created":
            post(PullRequestComment(data).created())

    return "Ok"

def post(text):
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
