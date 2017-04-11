# forumorg

This is the repository for the official website of [Forum Organisation](https://forumorg.org).

## Getting Started

These instructions will get help get your own copy of the project running on your local machine for development and testing purposes.

### Prerequisites

To get your development environment running, you need

```
Python 3, mongodb
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
We use Heroku for Cloud hosting and Continuous Integration.

On ```git push origin master```:

- The code is pushed to this repository (on `master`).
- A build is triggered on our [staging app](https://forumorg-staging.herokuapp.com) (very useful for testing in a production-like environment).

On ```any approved PR request```:

- A review app is created, which can be live tested.
- If everything works perfectly, the PR can be merged to `master`.
- If the app is ready for production, we promote it to [production](https://www.forumorg.org) thanks to Heroku Pipelines.

## Contributions

Contributions are very welcome! If you find a bug or some improvements, feel free to raise an issue and send a PR! Please see the [CONTRIBUTING](CONTRIBUTING.md) file for more information on how to contribute.

## Stack

* [Python](https://www.python.org/) - Primary language for development
* [Mongodb](https://www.mongodb.com/) - Database platform

## Authors

* **Mehdi BAHA** - [mehdibaha](https://github.com/mehdibaha)
* **Juliette BRICOUT** - [jbricout](https://github.com/jbricout)

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details

## (Experimental) Packages view

![img](https://s3-eu-west-1.amazonaws.com/forumorg/packages_Pyreverse.png)
