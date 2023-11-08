from io import BytesIO
import requests
try:
    from PIL import Image
    from mattermostgithub.config import SHOW_AVATARS
except ImportError:
    SHOW_AVATARS = False

class Payload(object):
    def __init__(self, data):
        self.data = data

    def user_link(self):
        name   = self.data['sender']['login']
        url    = self.data['sender']['html_url']
        avatar = self.data['sender']['avatar_url'] + "&s=18"
        return self.create_user_link(name, url, avatar)

    def check_avatar_size(self, url):
        f = requests.get(url)
        img = Image.open(BytesIO(f.content))
        f.close()
        if img.size[0] <= 20 and img.size[1] <= 20:
            return True
        return False

    def create_user_link(self, name, url, avatar):
        if SHOW_AVATARS and self.check_avatar_size(avatar):
            return "![](%s) [%s](%s)" % (avatar, name, url)
        return "[%s](%s)" % (name, url)


    def repo_link(self):
        name = self.data['repository']['full_name']
        url  = self.data['repository']['html_url']
        return "[%s](%s)" % (name, url)

    def preview(self, text):
        if not text:
            return text
        l = text.split("\n")
        # Show the first 4 lines of a message.
        result = "".join(l[:4])
        # Remove trailing newlines.
        if result[-1] in "[\n, \r]":
            result = result[:-1]
        if result != text:
            result += " [...]"
        return result

class PullRequest(Payload):
    def __init__(self, data):
        Payload.__init__(self, data)
        self.number = self.data['pull_request']['number']
        self.title  = self.data['pull_request']['title']
        self.body   = self.data['pull_request']['body']
        self.url    = self.data['pull_request']['html_url']

    def opened(self):
        body = self.preview(self.body)
        msg = """%s opened new pull request [#%s %s](%s) in %s:
> %s""" % (self.user_link(), self.number, self.title,
            self.url, self.repo_link(), body)
        return msg

    def assigned(self):
        to_name   = self.data['assignee']['login']
        to_url    = self.data['assignee']['html_url']
        to_avatar = self.data['assignee']['avatar_url'] + "&s=18"
        to = self.create_user_link(to_name, to_url, to_avatar)
        msg = """%s assigned %s to pull request [#%s %s](%s).""" % (self.user_link(),
            to, self.number, self.title, self.url)
        return msg

    def closed(self):
        merged = self.data['pull_request']['merged']
        action = "merged" if merged else "closed"
        msg = """%s %s pull request [#%s %s](%s).""" % (self.user_link(),
            action, self.number, self.title, self.url)
        return msg

    def synchronize(self):
        msg = """%s modified pull request [#%s %s](%s).""" % (self.user_link(),
            self.number, self.title, self.url)
        return msg

    def review_requested(self):
        reviewers = ", ".join(self.data["requested_reviewers"])
        msg = """%s requested a review from %s on [#%s %s](%s)""" % (self.user_link(),
            reviewers,
            self.number, self.title, self.url)
        return msg

    def pr_enqueued(self):
        msg = """[#%s %s](%s) added to merge queue.""" % (
            self.number, self.title, self.url)
        return msg

    def pr_dequeued(self):
        reason = self.data["reason"]
        msg = """[#%s %s](%s) removed from merge queue. Reason: %s""" % (
            self.number, self.title, self.url, reason)
        return msg

class PullRequestReview(Payload):
    def __init__(self, data):
        Payload.__init__(self, data)
        self.number = self.data['pull_request']['number']
        self.title  = self.data['pull_request']['title']
        self.body   = self.data['review']['body']
        self.url    = self.data['review']['html_url']

    def submitted(self):
        body = self.preview(self.body)
        if body is None:
            # Ignore empty PR reviews
            return ""
        msg = """%s submitted a review on pull request [#%s %s](%s):
> %s""" % (self.user_link(), self.number, self.title, self.url, body)
        return msg

class PullRequestComment(Payload):
    def __init__(self, data):
        Payload.__init__(self, data)
        self.number = self.data['pull_request']['number']
        self.title  = self.data['pull_request']['title']
        self.body   = self.data['comment']['body']
        self.url    = self.data['comment']['html_url']

    def created(self):
        body = self.preview(self.body)
        msg = """%s commented on pull request [#%s %s](%s):
> %s""" % (self.user_link(), self.number, self.title, self.url, body)
        return msg

class Issue(Payload):
    def __init__(self, data):
        Payload.__init__(self, data)
        self.number = self.data['issue']['number']
        self.title  = self.data['issue']['title']
        self.url    = self.data['issue']['html_url']
        self.body   = self.data['issue']['body']

    def opened(self):
        body = self.preview(self.body)
        msg = """%s opened new issue [#%s %s](%s) in %s:
> %s""" % (self.user_link(), self.number, self.title, self.url, self.repo_link(), body)
        return msg

    def labeled(self):
        label = self.data['label']['name']
        msg = """%s added label `%s` to issue [#%s %s](%s) in %s.""" % (self.user_link(), label, self.number, self.title, self.url, self.repo_link())
        return msg

    def closed(self):
        msg = """%s closed issue [#%s %s](%s) in %s.""" % (self.user_link(), self.number, self.title, self.url, self.repo_link())
        return msg

    def assigned(self):
        name   = self.data['assignee']['login']
        url    = self.data['assignee']['html_url']
        avatar = self.data['assignee']['avatar_url'] + "&s=18"
        assignee = self.create_user_link(name, url, avatar)
        msg = """%s assigned %s to issue [#%s %s](%s) in %s.""" % (self.user_link(), assignee, self.number, self.title, self.url, self.repo_link())
        return msg

class IssueComment(Payload):
    def __init__(self, data):
        Payload.__init__(self, data)
        self.number = self.data['issue']['number']
        self.title  = self.data['issue']['title']
        self.url    = self.data['comment']['html_url']
        self.body   = self.data['comment']['body']

    def created(self):
        body = self.preview(self.body)
        msg = """%s commented on [#%s %s](%s):
> %s""" % (self.user_link(), self.number, self.title, self.url, body)
        return msg

class CommitComment(Payload):
    def __init__(self, data):
        Payload.__init__(self, data)
        self.cid    = self.data['comment']['commit_id'][:7]
        self.url    = self.data['comment']['html_url']
        self.body   = self.data['comment']['body']

    def created(self):
        body = self.preview(self.body)
        msg = """%s commented on [%s](%s):
> %s""" % (self.user_link(), self.cid, self.url, body)
        return msg

class Repository(Payload):
    def __init__(self, data):
        Payload.__init__(self, data)

    def created(self):
        descr = self.data['repository']['description']
        msg = """%s created new repository %s:
> %s""" % (self.user_link(), self.repo_link(), descr)
        return msg

class Branch(Payload):
    def __init__(self, data):
        Payload.__init__(self, data)
        self.name = self.data['ref']

    def created(self):
        msg = """%s added branch `%s` to %s.""" % (self.user_link(),
            self.name, self.repo_link())
        return msg

    def deleted(self):
        msg = """%s deleted branch `%s` in %s.""" % (self.user_link(),
            self.name, self.repo_link())
        return msg

class Tag(Payload):
    def __init__(self, data):
        Payload.__init__(self, data)
        self.name = self.data['ref']

    def created(self):
        msg = """%s added tag `%s` to %s.""" % (self.user_link(),
            self.name, self.repo_link())
        return msg

class Push(Payload):
    def __init__(self, data):
        Payload.__init__(self, data)

    def commits(self):
        commits = self.data['commits']
        branch = self.data['ref'].replace("refs/heads/", "")
        branch_url = self.data['repository']['html_url'] + "/tree/" + branch
        if not commits:
            commits = [self.data['head_commit']]
        changeset = "changesets" if len(commits) > 1 else "changeset"
        msg = []
        msg.append("%s pushed %s %s to [%s](%s) at %s:" % (self.user_link(), len(commits), changeset, branch, branch_url, self.repo_link()))
        for commit in commits:
            cid  = commit['id'][:7]
            curl = commit['url']
            cmsg = self.preview(commit['message'])
            ctext = "- [`%s`](%s): %s" % (cid, curl, cmsg)
            msg.append("\n")
            msg.append(ctext)
        return "".join(msg)

class Wiki(Payload):
    def __init__(self, data):
        Payload.__init__(self, data)

    def updated(self):
        pages = self.data['pages']

        msg = []
        msg.append("%s changes %s pages in Wiki at %s:" % (self.user_link(), len(pages), self.repo_link()))
        for page in pages:
            page_name  = page['page_name']
            title = page['title']
            summary = page['summary']
            url = "%s/_compare/%s" % (page['html_url'], page['sha'])
            action = page['action']
            if summary :
              ctext = "- %s [%s](%s)\n>%s" % (action, page_name, url,summary)
            else :
              ctext = "- %s [%s](%s)\n" % (action, page_name, url)
            msg.append("\n")
            msg.append(ctext)
        return "".join(msg)

class Status(Payload):
    def __init__(self, data):
        Payload.__init__(self, data)

    def updated(self):
        url = self.data["target_url"]
        description = self.data["description"]
        msg = "[%s](%s) in %s." % (description, url, self.repo_link())
        return msg
