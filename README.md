# awesome-crawler

## Setup
```sh
# Install dependencies
pipenv install --dev

# Setup pre-commit and pre-push hooks
pipenv run pre-commit install -t pre-commit
pipenv run pre-commit install -t pre-push
```

## Infrastructure

1. install aws cdk `npm install -g aws-cdk`
2. get into the shell `pipenv shell`
3. go to the `infrastructure` folder
4. execute `cdk deploy`

## Credits
This package was created with Cookiecutter and the [sourcery-ai/python-best-practices-cookiecutter](https://github.com/sourcery-ai/python-best-practices-cookiecutter) project template.
