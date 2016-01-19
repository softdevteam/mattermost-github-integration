# Github integration for Mattermost

## Requirements
- Python
- Flask (install with `pip install flask`)

## Usage
Copy `config.template` to `config.py` and edit it with your details. For example:

```
USERNAME = "Github"
ICON_URL = "yourdomain.org/github.png"
MATTERMOST_WEBHOOK_URL = "yourmain.org/hooks/hookid"
CHANNEL = "off-topic"
```

The server is listening by default on port 5000. Make sure to point your Github webhooks to `http://yourdomain.org:5000`.

Start the server with `python server.py`.
