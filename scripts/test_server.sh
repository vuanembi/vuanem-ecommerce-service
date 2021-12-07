export $(cat .env | xargs) && functions-framework --target=main --debug
