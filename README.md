# WeiSaw: Slack App

[![License: GPL v3](https://img.shields.io/badge/License-GPL%20v3-blue.svg)](https://www.gnu.org/licenses/gpl-3.0)
[![Twitter](https://img.shields.io/twitter/follow/openebs.svg?style=social&label=Follow)](https://twitter.com/intent/follow?screen_name=5hirish)

WeiSaw is a Slack app that has the potential to be your workspace manager. So pitch in with feature requests, code contributions to make it your workspace manager.

## Current Features
* Apply leaves, Out of office, Work from home
* Track your leaves

## TODO
- [ ] API Unit Tests

--------

Built this Slack app on a rather less busy weekend to apply leave applications and track them in Slack workspaces. Currently it uses a very naive NLP approach to process leave applications posed in natural language.
Open sourced it for the community to try it out and may be suggest other use cases or features to add to that would simplify their workspace management.
Can't promise that I will implement each and every feature request :)

Feel free to contribute to the project or create feature requests, maybe somebody out their is also facing the same issue and is willing to contribute.

Suggest features under the label "**feature request**" [here](https://github.com/5hirish/weisaw/labels/feature%20request).



### Dependencies
* [Python Flask](http://flask.pocoo.org/): REST APIs
* [Python Celery](http://www.celeryproject.org/): Background Tasks 
* [Python spaCy](https://spacy.io): Natural Langugae Processing
* PostgreSQL

Python Package dependencies listed in [requirements.txt](requirements.txt)

Slack API: [https://api.slack.com/](https://api.slack.com/)

### Maintainer
* _@5hirish_, [shirishkadam.com](https://shirishkadam.com/)

### Wei Saw Dong Waterfall
One of the most beautiful and hidden waterfalls in Sohra, Meghalaya.
