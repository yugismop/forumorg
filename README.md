# forumorg

[![Website](https://img.shields.io/website-up-down-green-red/http/shields.io.svg)](https://www.forumorg.org)
[![GitHub repository](https://img.shields.io/badge/GitHub-ForumOrganisation%2Fforumorg-blue.svg)](https://github.com/ForumOrganisation/forumorg)

This is the repository of [Forum Organisation](https://www.forumorg.org)'s official website.

## Getting Started

These instructions will get help get your own copy of the project running on your local machine for development and testing purposes.

### Requirements

To get your development environment running, you need:

- [python 3](https://www.python.org/downloads/)
- [bower](https://bower.io/#install-bower)
- [mongodb](https://www.mongodb.com/download-center#community)

### Install

To install the necessary dependencies:

```sh
git clone https://github.com/ForumOrganisation/forumorg.git
cd forumorg && pip install -r requirements.txt
bower install
```

### Configuration
To start the project, you need to provide the following environment variables:

```sh
export MONGODB_URI="mongodb://host:port/dbname" # Required: local running mongodb instance
export BUCKET_NAME="bucket_name" # Required: S3 bucket name
export DEBUG=True # Optional: Nice for debugging
export SENDGRID_API_KEY="sendgrid_key" # Optional: for emailing events
```

### Run
```sh
python runserver.py
```

## Deploying
We use Heroku for Cloud hosting and Continuous Integration.

On ```push to master```:

- A build is triggered on our [staging app](https://forumorg-staging.herokuapp.com) (useful for testing in a production-like environment).

On ```any pull request```:

- A review app is created, which can be live tested.
- If everything is working OK, the PR can be merged to `master`.
- If the app is working well, it is promoted to [production](https://www.forumorg.org).

## Localization
The app is localized using:

- Flask-Babel: used to indicate which strings needs to be translated (surrounded with `_('STRING')`)
- PhraseApp: provides a nice UI to translate the strings

You can cet familiar with the process [by following this tutorial](https://phraseapp.com/blog/posts/python-localization-flask-applications/).

## Contributions

Contributions are very welcome! If you find a bug or some improvements, feel free to raise an issue and send a PR! Please see the [CONTRIBUTING](CONTRIBUTING.md) file for more information on how to contribute.

## Authors

* **Mehdi BAHA** - [mehdibaha](https://github.com/mehdibaha)
* **Juliette BRICOUT** - [jbricout](https://github.com/jbricout)
* **Mohammed MEGZARI** - [momeg](https://github.com/momeg)

(Note to contributors: Add yourself!)

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details
