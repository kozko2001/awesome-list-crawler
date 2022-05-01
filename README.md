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

## Next steps
- Create two jsons (one for the first 4 days)
- Create a sqlite with text search format
- Add API to search / get 

## Credits
This package was created with Cookiecutter and the [sourcery-ai/python-best-practices-cookiecutter](https://github.com/sourcery-ai/python-best-practices-cookiecutter) project template.
