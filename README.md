# textpipeliner

Library for extracting specific words from sentences of a document

Currently it works on sentences(and assumes this format) produced by [spaCy](https://spacy.io/) library.
Direction for future would be to make it independent on NLP parser libraries providers.

1. Installation
2. License
3. Description
4. Pipes
5. Example


## 1. Installation

textpipeliner is published on PyPi, so to install it run:
pip install textpipeliner

It requires spaCy and grammaregex libraries.


## 2. License

textpipeliner is available for everyone else to use on MIT license bases(liberal free usage).


## 3. Description

Idea of textpipeliner is to provide easy way of extracting parts of sentences in form of structured tuples from unstructured text. So for instance
it can be used to get RDFs from given text if you do some web semantics.

To achieve it, library provides 2 main parts - Pipes and PipelineEngine. From pipes you create a structure which will bu used to extract parts from every
sentence in document. Engine will use this pipes structure and apply processing of its for every sentence in provided document and return list of
extracted tuples.

All you need is pass doc and list of pipes - where every element of list will be responsible for return one of the tuple part - to the engine 
and launch processing of engine. "Pipes structure" word were used because the list of pipes is not everything - there are pipes which can contains
collection of another pipes so from the list of pipes you can create really complecated structure.

Every pipe has one method - process, which takes context(of document, like doc, current paragraph and current sentence) and list of tokens(from another 
pipe) and returns list of tokens extracted while processing from passed data. But this is generally hidden inside Engine.


## 4. Pipes
For now, library contains 7 pipes:

* AggregatePipe:
    This pipe gets list of another pipes and collect results from them.


* SequencePipe:
    This pipe gets list of another pipes and process them in sequence passing tokens as argument to next one using result from the previous one.


* AnyPipe:
    This pipe gets list of another pipes and process them till first returns not empty result.


* GenericPipe:
    This pipe gets a function as a argument which function will process on its own. This function will be called with 2 arguments - same as pipe's process
    method - context and tokens list.

* FindTokensPipe:
    This pipe gets a regex-like pattern to extract from tree-sentence according to this pattern using [grammaregex](https://github.com/krzysiekfonal/grammaregex) library.

* NamedEntityFilterPipe:
    This pipe filters passed tokens choosing the ones which are part of Named Entity. During creation of this pipe it is possible to pass specific
    NE type we want to filter(like PERSON, LOC etc.) 

* NamedEntityExtractorPipe:
    This pipe collects whole chain from single single token which is part of entity(if it is).


## 5. Example
Below you can see complete example of how to process a text getting triples - kind of RDF - consistent of: subject, connecting action, object.
This part of text obtained from wiki(World War Second page) will be used in example:

"The Empire of Japan aimed to dominate Asia and the
Pacific and was already at war with the Republic of China
in 1937, but the world war is generally said to have begun on
1 September 1939 with the invasion of Poland by Germany and
subsequent declarations of war on Germany by France and the United Kingdom.
From late 1939 to early 1941, in a series of campaigns and treaties, Germany conquered
or controlled much of continental Europe, and formed the Axis alliance with Italy and Japan.
Under the Molotov-Ribbentrop Pact of August 1939, Germany and the Soviet Union partitioned and 
annexed territories of their European neighbours, Poland, Finland, Romania and the Baltic states.
The war continued primarily between the European Axis powers and the coalition of the United Kingdom 
and the British Commonwealth, with campaigns including the North Africa and East Africa campaigns, 
the aerial Battle of Britain, the Blitz bombing campaign, the Balkan Campaign as well as the 
long-running Battle of the Atlantic. In June 1941, the European Axis powers launched an invasion 
of the Soviet Union, opening the largest land theatre of war in history, which trapped the major part 
of the Axis' military forces into a war of attrition. In December 1941, Japan attacked 
the United States and European territories in the Pacific Ocean, and quickly conquered much of 
the Western Pacific."

To process and get list of desired triples we can for instance do following steps:

```Python
import spacy
from textpipeliner import PipelineEngine, Context
from textpipeliner.pipes import *

nlp = spacy.load("en")
doc = nlp(u"The Empire of Japan aimed to dominate Asia and the " \
               "Pacific and was already at war with the Republic of China " \
               "in 1937, but the world war is generally said to have begun on " \
               "1 September 1939 with the invasion of Poland by Germany and " \
               "subsequent declarations of war on Germany by France and the United Kingdom. " \
               "From late 1939 to early 1941, in a series of campaigns and treaties, Germany conquered " \
               "or controlled much of continental Europe, and formed the Axis alliance with Italy and Japan. " \
               "Under the Molotov-Ribbentrop Pact of August 1939, Germany and the Soviet Union partitioned and " \
               "annexed territories of their European neighbours, Poland, Finland, Romania and the Baltic states. " \
               "The war continued primarily between the European Axis powers and the coalition of the United Kingdom " \
               "and the British Commonwealth, with campaigns including the North Africa and East Africa campaigns, " \
               "the aerial Battle of Britain, the Blitz bombing campaign, the Balkan Campaign as well as the " \
               "long-running Battle of the Atlantic. In June 1941, the European Axis powers launched an invasion " \
               "of the Soviet Union, opening the largest land theatre of war in history, which trapped the major part " \
               "of the Axis' military forces into a war of attrition. In December 1941, Japan attacked " \
               "the United States and European territories in the Pacific Ocean, and quickly conquered much of " \
               "the Western Pacific.")

pipes_structure = [SequencePipe([FindTokensPipe("VERB/nsubj/*"),
                                 NamedEntityFilterPipe(),
                                 NamedEntityExtractorPipe()]),
                   FindTokensPipe("VERB"),
                   AnyPipe([SequencePipe([FindTokensPipe("VBD/dobj/NNP"),
                                          AggregatePipe([NamedEntityFilterPipe("GPE"), 
                                                NamedEntityFilterPipe("PERSON")]),
                                          NamedEntityExtractorPipe()]),
                            SequencePipe([FindTokensPipe("VBD/**/*/pobj/NNP"),
                                          AggregatePipe([NamedEntityFilterPipe("LOC"), 
                                                NamedEntityFilterPipe("PERSON")]),
                                          NamedEntityExtractorPipe()])])]

engine = PipelineEngine(pipes_structure, Context(doc), [0,1,2])
engine.process()
```

It will returns:

```Python
>>>[([Germany], [conquered], [Europe]),
 ([Japan], [attacked], [the, United, States])]
```
