

from flask import Blueprint, request
from matterhorn import Uphill


from payload import (PullRequest, PullRequestComment, Issue, IssueComment,
    Repository, Branch, Push)


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

def make_blueprint(name):
    blueprint = Blueprint('github', __name__, static_folder='static')

    github = Uphill(
        username='github'
    )

    @blueprint.route('/', methods=['POST'])
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
        
        elif event == "create":
            if data['ref_type'] == "branch":
                response = Branch(data).created
        
        elif event == "push":
            if not data['deleted'] or not data['forced']:
                response = Push(data).commits)

        if response is not None:
                gitub.send(response, request=data)

        return "Ok"