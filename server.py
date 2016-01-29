import os
import requests
from flask import Flask
from flask import request
import json
import config

from payload import PullRequest, PullRequestComment, Issue, IssueComment, Repository, Branch, Push

app = Flask(__name__)

event_map = {
    'pull_request': PullRequest,
    'issues': Issue,
    'issue_comment': IssueComment,
    'repository': Repository,
    'pull_request_review_comment': PullRequestComment,

    # these are handeled separetly
    # 'create': Branch,
    # 'push': Push,

}

@app.route('/', methods=['POST'])
def root():
    if request.json is None:
       print 'Invalid Content-Type'
       return 'Content-Type must be application/json and the request body must contain valid JSON', 400

    data = request.json
    event = request.headers['X-Github-Event']

    action_class = event_map.get(event, None)

    if action_class is not None:
        instance = action_class(data)
        response = instance.dispatch()
        if response is not None:
            post(response)
    
    elif event == "create":
        branch = Branch(data)
        if data['ref_type'] == "branch":
            post(branch.created)
    
    elif event == "push":
        if not data['deleted'] or not data['forced']:
            post(Push(data).commits)

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
