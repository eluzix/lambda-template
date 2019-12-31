MyApp Example Template
=======================

## Deployment

install requirements into vendors directory: `mkdir -p vendors/ && pip3 install -t vendors/ -r requirements.txt`

than deploy with `sls deploy`

## Local env

install development requirements:
`pip3 install -r requirements-dev.txt`

Run full testsuite:
``nose2``

Run local dynamodb:
``java -Djava.library.path=./DynamoDBLocal_lib -jar DynamoDBLocal.jar -sharedDb -inMemory``
