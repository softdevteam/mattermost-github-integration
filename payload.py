class Payload(object):
    def __init__(self, data):
        self.data = data

    def user_link(self):
        name   = self.data['sender']['login']
        url    = self.data['sender']['html_url']
        avatar = self.data['sender']['avatar_url'] + "&s=18"
        return "![](%s) [%s](%s)" % (avatar, name, url)

    def repo_link(self):
        name = self.data['repository']['full_name']
        url  = self.data['repository']['html_url']
        return "[%s](%s)" % (name, url)

    def preview(self, text):
        if not text:
            return text
        l = text.split("\n")
        result = l[0]
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
        msg = """#### New pull request: [#%s %s](%s)
> %s

*Created by %s in %s.*""" % (self.number, self.title,
            self.url, body, self.user_link(), self.repo_link())
        return msg

    def closed(self):
        merged = self.data['pull_request']['merged']
        action = "merged" if merged else "closed"
        msg = """%s %s pull request [#%s %s](%s).""" % (self.user_link(),
            action, self.number, self.title, self.url)
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
        msg = """#### New issue: #%s [%s](%s)
> %s

*Created by %s in %s.*""" % (self.number, self.title,
            self.url, body, self.user_link(), self.repo_link())
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
        msg = """%s commented on [%s %s](%s):
> %s""" % (self.user_link(), self.number, self.title, self.url, body)
        return msg

class Repository(Payload):
    def __init__(self, data):
        Payload.__init__(self, data)

    def created(self):
        descr = self.data['repository']['description']
        msg = """#### New repository: %s
> %s

*Created by %s.*""" % (self.repo_link(), descr, self.user_link())
        return msg

class Branch(Payload):
    def __init__(self, data):
        Payload.__init__(self, data)
        self.name = self.data['ref']

    def created(self):
        msg = """%s added branch `%s` to %s.""" % (self.user_link(),
            self.name, self.repo_link())
        return msg
