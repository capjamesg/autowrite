https://github.com/capjamesg/autowrite/assets/37276661/a5f8b6e0-19ac-4550-a67a-ba858bc2e563

# AutoWrite

AutoWrite is a context-aware autocomplete developed with [surprisals](https://en.wikipedia.org/wiki/Information_content) (information content).

Given an article of text, AutoWrite generates an autocomplete system that works with unigrams (single words), bigrams (two word phrases), and trigrams (three word phrases).

AutoWrite can also fix the spelling of words that appear in the given article.

## Getting Started

First, clone the AutoWrite GitHub repository and install the project requirements:

```bash
git clone https://github.com/capjames/autowrite
cd autowrite
pip install -r requirements.txt
```

Then, run the application:

```bash
python autocomplete.py
```

The web application will be available at `http://localhost:5000`.

## How to Use

First, open the web application. Click "Choose URLs" and add all of the URLs you want to use to fine-tune your autocompleter.

Then, start writing. Suggestions will appear as you type. If you make a typo for proper nouns, AutoWrite will attempt to correct it when you start typing the next word.

## License

This project is licensed under an [MIT license](LICENSE).

## Contributors

- capjamesg
