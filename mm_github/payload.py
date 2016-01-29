
from matterhorn import markdown as md


class Payload(dict):

    def dispatch(self):
        return getattr(self, self['data'], None)
    
    def get_user_link(self, user='sender'):
        name   = self[user]['login']
        url    = self[user]['html_url']
        avatar = self[user]['avatar_url'] + "&s=18"
        return '%s %s' %(md.image(avatar, alt=name), md.link(url, text=name)

    user_link = property(get_user_link)

    @property
    def repo_link(self):
        name = self.data['repository']['full_name']
        url  = self.data['repository']['html_url']
        
        return md.link(url, name)

    def preview(self, text):
        '''
            Return first line of text.
            Append [...] if there is more than one line.
        '''

        text = text.strip()

        # return empty string if text was empty
        if not text:
            return text

        lines = text.splitlines()

        if len(lines) == 0:
            return lines[0]
        else:
            return lines[0] + ' [...]'

    def _message(self, action):
        return '{user} {action} {link} in {repository}'.format(
            user=self.user_link,
            action=action,
            link=issue=md.link(self.url, "#%s %s" %(self.number, self.title)),
            repository=self.repo_link
        )

class CommentMixin(object):
    @property
    def url(self):
        return self['comment']['html_url']

class IssueMixin(object):
    @property
    def number(self):
        return self['issue']['number']
    
    @property
    def title(self):
        return self['issue']['title']

class PullRequest(Payload):
    @property
    def number(self):
        return self['pull_request']['number']

    @property
    def title(self):
        return self['pull_request']['title']

    @property
    def url(self):
        return self['pull_request']['html_url']

    def opened(self):
        preview = self.preview(self['pull_request']['body'])
        message = self._message('opened new pull request')

        return message + '\n' + md.blockquote(preview)

    def assigned(self):
        return self._message('assigned %s to pull request' % (
            self.get_user_link('assignee')
        ))

    def closed(self):
        merged = self['pull_request']['merged']
        action = ("merged" if merged else "closed")

        return self._message(action)


class PullRequestComment(Payload, CommentMixin):
    @property
    def created(self):
        preview = self.preview(self['comment']['body'])
        self._message('commented on pull pull request')

        return message + '\n' + md.blockquote(preview)

class Issue(Payload, IssueMixin):
    @property
    def url(self):
        return self['issue']['html_url']

    def opened(self):
        preview = self.preview(self['issue']['body'])
        message = self._message('opened issue')
        return message + '\n' + md.blockquote(preview)

    def closed(self):
        return self._message('closed issue')


class IssueComment(Payload, IssueMixin, CommentMixin):
    @property
    def created(self):
        preview = self.preview(self['comment']['body'])
        message = self._message('commented on issue')

        return message + '\n' + md.blockquote(preview)


class Repository(Payload):
    @property
    def created(self):
        message = '{user} created new repository {repository}'.format(
            user=self.user_link,
            repository=self.repo_link
        )
        preview = self.preview(self['repository']['description'])

        return message + '\n' + md.blockquote(preview)


class Branch(Payload):
    @property
    def created(self):
        return '%s added branch `%s` to %s.' % (
            self.user_link, self['ref'], self.repo_link)


class Push(Payload):
    @property
    def commits(self):
        commits = self['commits']
        changeset = "changesets" if len(commits) > 1 else "changeset"
        msg = [ "%s pushed %s %s to %s:" % (
                self.user_link, len(commits), changeset, self.repo_link
            )]
        
        for commit in commits:
            cid  = commit['id'][:7]
            curl = commit['url']
            cmsg = self.preview(commit['message'])
            msg.append("- %s: %s" % (md.link(curl, text=md.code(cid)), cmsg))

        return "\n".join(msg)
