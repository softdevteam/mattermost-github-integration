
## Work in progress. The following does not work (yet).

# Installation

```
pip install mm_github 
```

This also installs ``Flask`` and ``Matterhorn``.

# Usage

Standalone

```
from matterhorn import Matterhorn

# app is a normal Flask app
app = Matterhorn(__name__)

app.add_plugin(
    name='github',
    url_prefix='/',
    plugin='mm_github.github',
    url=yourdomain.org/hooks/hookid
)

if __name__ == '__main__':
    app.run(debug=True)
```
