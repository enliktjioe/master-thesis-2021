#!/usr/bin/env python
# coding: utf-8

# # References
# 
# - https://www.geeksforgeeks.org/spelling-checker-in-python/
# - https://rustyonrampage.github.io/text-mining/2017/11/28/spelling-correction-with-python-and-nltk.html
# - https://pyenchant.github.io/pyenchant/

# # Correcting Typos Libraries

# ## pyspellchecker

from spellchecker import SpellChecker

spell = SpellChecker()

# find those words that may be misspelled
misspelled = spell.unknown(['something', 'is', 'hapenning', 'here'])

for word in misspelled:
    # Get the one `most likely` answer
    print(spell.correction(word))

    # Get a list of `likely` options
    print(spell.candidates(word))


from spellchecker import SpellChecker
 
spell = SpellChecker()
 
# find those words that may be misspelled
misspelled = spell.unknown(["cmputr", "watr", "singg", "wrate"])
print(misspelled)
    
for word in misspelled:
    print(word)
    # Get the one `most likely` answer
    print(spell.correction(word))
 
    # Get a list of `likely` options
    print(spell.candidates(word))


# ## TextBlob

from textblob import TextBlob
 
a = "4you"           # incorrect spelling
print("original text: "+str(a))
 
b = TextBlob(a)
 
# prints the corrected spelling
print("corrected text: "+str(b.correct()))


# ## PyEnchant

import enchant
d = enchant.Dict("en_US")
d.check("Hello")
True
d.check("Helo")




