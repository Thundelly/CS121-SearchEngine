# CS121-SearchEngine

## How to run
---
(Text based version)
- run `python3 src/search_engine.py`

(Web GUI based version)
- run `python3 src/api.py`

## Current progress
---
- Completed search engine development.
- Completed optimization by caching words.

(Web GUI -- Flask API)
- Completed implementing Flask API to handle HTTP request / response.

## Project directory
---
```
root_directory
|
|__ db
    |
    |__ index.txt
    |__ fp_locations.json
    |__ doc_id.json
|
|__ DEV
|__ nltk_data
|__ src
    |
    |__ api.py
    |__ endpoints.py
    |__ file_handler.py
    |__ indexer.py
    |__ query.py
    |__ search_engine.py
|__ .gitignore
|__ README.md
|__ index_status.log
```

### Dependencies

- bs4
- lxml
- nltk
- ssl

(Web GUI -- Flask API)
- flask
- flask_restful
- flask_cors
