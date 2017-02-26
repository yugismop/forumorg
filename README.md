# forum-org

This is the repository for the official website of [Forum Organisation](http://www.forumorg.org).

## Getting Started

These instructions will get help get your own copy of the project running on your local machine for development and testing purposes.

### Prerequisites

To get your development environment running, you need

```
Python 2.7, pip, mongodb
```

### Installing

To install the necessary python dependencies

```
pip install -r requirements.txt
```

Before starting the application, launch a mongodb instance (`sudo mongod`).
Don't forget to set the environnement variable `MONDODB_URI` to the database uri.

```
export MONGODB_URI=mongodb://localhost:27017/<db-name>
```

Finally, to get the project running, simply start the Flask server:

```
python ./runserver.py
```

## Deploying
We use Heroku for cloud hosting, TravisCI for Continuous Integration and GitHub to tie it all together.

On ```git push origin master[:master]```:

- The code is pushed to this repository (on master)

On ```git push origin master:staging```:

- The code is pushed to this repository (on staging)
- A docker-based test process is trigered on TravisCI:
	- If the build passes -> The code is deployed to Heroku
	- If the build fails -> An email is sent

On ```git push origin master:production```:

- The code is pushed to this repository (on production)
- The code is directly deployed to Heroku
- This usually applies to quick config changes that need to be deployed instantly (TravisCI builds still take ~30 secs to complete)

## Stack

* [Python](https://www.python.org/) - Primary language for development
* [Mongodb](https://www.mongodb.com/) - Database platform

## Authors

* **Mehdi BAHA** - [mehdibaha](https://github.com/mehdibaha)
* **Juliette BRICOUT** - [jbricout](https://github.com/jbricout)

## Contributions

Contributions are very welcome! If you found a bug or some improvements, feel free to raise an issue and send a PR! Please see the CONTRIBUTING file for more information on how to contribute.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details
