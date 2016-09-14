# Github integration for Mattermost

Inspired by [mattermost-integration-gitlab](https://github.com/NotSqrt/mattermost-integration-gitlab) this program creates a server using [flask](https://github.com/mitsuhiko/flask) that listens for incoming GitHub event webhooks. These are then processed, formatted, and eventually forwarded to Mattermost where they are displayed inside a specified channel.
![](preview.png)

## Requirements
- Python
- Flask (install with `pip install flask`)
- requests (install with `pip install requests`)

## Usage
Copy `config.template` to `config.py` and edit it with your details. For example:

```python
USERNAME = "Github"
ICON_URL = "yourdomain.org/github.png"
MATTERMOST_WEBHOOK_URLS = {
    'default' : ("yourdomain.org/hooks/hookid", "off-topic"),
    'teamname/repositoryname' : ("yourdomain.org/hooks/hookid2", "repository-channel-id"),
    'teamname' : ("yourdomain.org/hooks/hookid3", "town-square"),
    'teamname/unimportantrepo' : None,
}
SECRET = 'secretkey'
SHOW_AVATARS = True
```

GitHub messages can be delegated to different Mattermost hooks. The order is as
follows. First try to find a hook for the repositories full name.  If that
fails, try to find a hook for the organisation name. Otherwise use the default
hook. Repositories can be blacklisted by setting them to `None` instead of
`(url, channel)`.

The server is listening by default on port 5000. Make sure to point your Github
webhooks to `http://yourdomain.org:5000`.

Start the server with `python server.py`.

If you don't want to use a secret set the field to `None`.

## Supported Events

Not all Github events are forwarded to Mattermost. Currently supported events are:

* Ping, when you first added Github webhook
* Commit pushes and comments
* Issues (open, close, comment)
* Pull Requests (create, merge, remove, comment)
* Create/Delete repositories
* Create/Delete branches and tags

All other events will report back to GitHub with `400 Not Implemented`.

## Known issues

- Channel names need to use the spelling that is used in their URL (the channel ID), e.g. instead
of `Town Square` it needs to be `town-square`.
