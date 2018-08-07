import requests
import json
import subprocess
import pytest
from flask import url_for


def dummy(text, url, channel):
    pass

from tests import config

from mattermostgithub import server
server.post = dummy
server.config = config # use testing config instead

@pytest.mark.usefixtures('live_server')
class TestLiveServer:

    def send(self, filename, _type):
        f = open("tests/{}".format(filename), "r")
        payload = json.load(f)
        f.close()
        headers = {"X-GitHub-Event": _type}
        res = requests.post(url_for("root", _external=True), json=payload, headers=headers)
        return res.status_code

    def test_pull_request_review(self):
        assert self.send("json/commit_comment.json", "commit_comment") == 200
        assert self.send("json/create.json", "create") == 200
        assert self.send("json/delete_tag.json", "delete") == 400
        assert self.send("json/fork.json", "fork") == 400
        assert self.send("json/gollum.json", "gollum") == 200
        assert self.send("json/issue_comment_created.json", "issue_comment") == 200
        assert self.send("json/issues_edited.json", "issues") == 400
        assert self.send("json/pull_request_closed.json", "pull_request") == 200
        assert self.send("json/pull_request_review.json", "pull_request_review") == 200
        assert self.send("json/pull_request_review_comment.json", "pull_request_review_comment") == 200
        assert self.send("json/push_deleted.json", "push") == 400
