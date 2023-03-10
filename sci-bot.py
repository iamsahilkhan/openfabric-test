import os
import warnings
import wikipedia
import nltk
from nltk.corpus import wordnet
from ontology_dc8f06af066e4a7880a5938933236037 import SimpleText
from openfabric_pysdk.context import OpenfabricExecutionRay
from openfabric_pysdk.loader import ConfigClass

nltk.download('wordnet')
nltk.download('punkt')
nltk.download('averaged_perceptron_tagger')


# function to process user input and return a response
def process_input(user_input):
    # search for a relevant Wikipedia article
    query = user_input.strip().lower()
    results = wikipedia.search(query)
    try:
        if results:
            page = wikipedia.page(results[0])
            response = page.summary
        else:
            response = "I'm sorry, I couldn't find any information on that topic."
    except wikipedia.exceptions.DisambiguationError as e:
        # if there are multiple possible results, suggest the first one
        response = f"Did you mean '{e.options[0]}'? Please try again with a more specific query."
    except wikipedia.exceptions.PageError:
        # if the query does not match any Wikipedia page, return an error message
        response = "I'm sorry, I couldn't find any information on that topic."
    except Exception as e:
        # handle any other unexpected exceptions
        response = f"An error occurred: {e}. Please try again later."
    return response


# function to identify and replace synonyms in user input
def replace_synonyms(text):
    words = nltk.word_tokenize(text)
    new_words = []
    for word in words:
        # find synonyms for the word
        synonyms = []
        for syn in wordnet.synsets(word):
            for lemma in syn.lemmas():
                if lemma.name() != word:
                    synonyms.append(lemma.name())
        # choose the most common synonym with the same part of speech
        if synonyms:
            pos = nltk.pos_tag([word])[0][1]
            synonyms_with_pos = [s for s in synonyms if nltk.pos_tag([s])[0][1] == pos]
            if synonyms_with_pos:
                most_common_synonym = max(set(synonyms_with_pos), key=synonyms_with_pos.count)
                new_word = most_common_synonym
            else:
                new_word = word
        else:
            new_word = word
        new_words.append(new_word)
    new_text = ' '.join(new_words)
    return new_text


# callback function called on update config
def config(configuration: ConfigClass):
    # set up Wikipedia API
    wikipedia.set_lang('en')
    # suppress warning messages from Wikipedia package
    warnings.filterwarnings("ignore", category=UserWarning, module='wikipedia')


# callback function called on each execution pass
def execute(request: SimpleText, ray: OpenfabricExecutionRay) -> SimpleText:
        output = []
        try:
            for text in request.text:
                # replace synonyms in user input
                processed_input = replace_synonyms(text)
                # process user input and generate response
                response = process_input(processed_input)
                output.append(response)
        except Exception as e:
            # handle any unexpected exceptions and return an error message
            output.append(f"An error occurred: {e}. Please try again later.")
        return SimpleText(dict(text=output))

# to get user input
    while True:
        user_input = input("Please enter your query: ")
        if user_input.lower() == 'quit':
            break
        response = process_input(user_input)
        print(response)
