import re

import nltk
import pygtrie
import requests
from bs4 import BeautifulSoup
from flask import Flask, jsonify, render_template, request
from spellchecker import SpellChecker

from pysurprisal import Surprisal

SUFFIX_PREFIX_CHARS = (",", ".", "!", "?")
PRIORITY_BOOST = 1.2

indices = {}


def get_words(url):
    words = ""

    post = (
        BeautifulSoup(requests.get(url).text, "html.parser")
        .get_text()
        .replace("\n", " ")
    )

    try:
        post_text = (
            BeautifulSoup(post, "html.parser")
            .get_text()
            .replace("\n", " ")
            #
        )
        words += post_text
    except Exception as e:
        print(e)
        pass

    # rstrp all words
    words = " ".join([re.sub(r"[^a-zA-Z0-9]+", " ", word) for word in words.split(" ")])

    # remove words < 3 chars and > 20 chars
    words = " ".join(
        [word for word in words.split(" ") if len(word) > 3 and len(word) < 20]
    )

    bigrams = nltk.bigrams(words.split(" "))

    # lowercase all words
    bigrams = [(word[0], word[1]) for word in bigrams]

    trigrams = nltk.trigrams(words.split(" "))
    trigrams = [(word[0], word[1], word[2]) for word in trigrams]

    quadgrams = nltk.ngrams(words.split(" "), 4)
    quadgrams = [(word[0], word[1], word[2], word[3]) for word in quadgrams]

    return words, bigrams, trigrams, quadgrams


def build_surprisal_index(words):
    surprisals = Surprisal(words)

    surprisals.calculate_surprisals()

    # print(surprisals.surprisals)

    vocab = surprisals.surprisals.keys()

    return surprisals, vocab


def autocomplete(query, trie):
    N = 10

    # distances = {}

    # for word in vocab:
    #     word_distance = distance(word, query)
    #     distances[word] = word_distance

    # print(sorted(distances.items(), key=lambda x: x[1])[0:N])

    results = trie.keys(prefix=query)

    # order by surprisals
    results = sorted(results, key=lambda x: trie[x])

    return results[0:N]


app = Flask(__name__)


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/surprisal")
def surprisal():
    query = request.args.get("query")
    previous_word = request.args.get("previous_word")
    urls = request.args.get("urls").split(",")

    all_surprisals = {}
    vocabulary = set()
    all_bigrams = []
    all_bigrams = []
    all_quadgrams = []

    for url in urls:
        if url not in indices:
            words, bigrams, trigrams, quadgrams = get_words(url)
            surprisals, vocab = build_surprisal_index(words)

            if url.endswith("?priority"):
                surprisals.surprisals = {
                    k: v * PRIORITY_BOOST for k, v in surprisals.surprisals.items()
                }

            all_surprisals.update(surprisals.surprisals)
            vocabulary.update(vocab)
            all_bigrams += bigrams

    trie = pygtrie.CharTrie()

    for bigram in all_bigrams:
        bigram = " ".join(bigram)
        trie[bigram] = surprisals.surprisals.get(
            bigram[0], 0
        ) - surprisals.surprisals.get(bigram[1], 0)

    for word in vocab:
        trie[word] = surprisals.surprisals[word]

    # add all quadgrams ending in with surprisals / 2
    for quadgram in all_quadgrams:
        quadgram = " ".join(quadgram)
        if quadgram.endswith(query):
            trie[quadgram] = 1

    trie = autocomplete(query, trie)

    # try to correct
    if previous_word not in surprisals.surprisals:
        spell = SpellChecker()

        # add all surprisal words to spellcheck that appear more than 3 times (to prevent typos from being populated as correct words)
        word_counts = surprisals.counts

        words_with_counts = [word for word in word_counts if word_counts[word] > 3]

        spell.word_frequency.load_words(words_with_counts)

        corrected_word = spell.correction(previous_word)

        if corrected_word in surprisals.surprisals:
            previous_word = corrected_word

        # if upper first char has lower surprisal, use that
        if surprisals.surprisals.get(
            previous_word.capitalize(), 100
        ) < surprisals.surprisals.get(previous_word, 100):
            previous_word = previous_word.capitalize()

    return jsonify(
        {
            "next_word_predictions": trie,
            "previous_word": previous_word,
        }
    )


if __name__ == "__main__":
    app.run(host="localhost", port=5000, debug=True)
