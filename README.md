# textpipeliner

Library for extracting specific words from sentences of a document.

Currently it works on documents produced by the [spaCy](https://spacy.io/) library.
A possible direction for future would be to make it independent on NLP parser library providers.


## Installation

textpipeliner is published on PyPi, so to install it run:
```
pip install textpipeliner
```

It requires spaCy and grammaregex libraries.


## License

textpipeliner is available for everyone else to use under the [MIT license](LICENSE).


## Description

The main aim of textpipeliner is to provide easy way of extracting parts of sentences in the form of structured tuples from unstructured text. So for instance it can be used to get RDFs from given text if you do some web semantics.

To achieve it, the library provides 2 main parts - Pipes and the `PipelineEngine`. From pipes you create a structure which will be used to extract parts from every sentence in document. `PipelineEngine` will use this pipes structure and apply processing of each sentence in the provided document and return list of extracted tuples.

All you need is to pass a spaCy document object and a list of pipes (where each element of the list is responsible for returning one element of the tuple) to the engine, and launch processing of the engine. "Pipes structure" is used because the list of pipes is not everything - there are pipes which can contain a collection of sub-pipes.

Every pipe has one method - `process`, which takes context (of document, like doc, current paragraph and current sentence) and list of tokens (from another pipe) and returns the list of tokens extracted while processing from passed data. However, usage of this is generally hidden inside `PipelineEngine`.


## Pipes
For now, the library contains 7 pipes:

* `AggregatePipe`:
    This pipe gets a list of other pipes and collects results from them.


* `SequencePipe`:
    This pipe gets a list of other pipes and processes them in sequence, passing tokens as an argument to next one using the result from the previous one.


* `AnyPipe`:
    This pipe gets list of another pipes and processes them until one returns a non-empty result.


* `GenericPipe`:
    This pipe takes a function as a argument which can be used to implement a custom process. This function will be called with 2 arguments - same as the pipe's process method: context and tokens list.

* `FindTokensPipe`:
    This pipe takes a regex-like pattern to extract using the [grammaregex](https://github.com/krzysiekfonal/grammaregex) library.

* `NamedEntityFilterPipe`:
    This pipe filters passed tokens choosing the ones which are part of a named entity. During creation of this pipe it is possible to pass a specific named entity type we want to filter (like `PERSON`, `LOC`...).

* `NamedEntityExtractorPipe`:
    This pipe collects a whole chain from a single token which is part of an entity.


## Example
Below you can see a complete example of how to process a text getting triples - kind of RDF - consistent of: subject, connecting action, object.

The text used is obtained from https://www.americanhistoryusa.com/topic/world-war-ii/.

```Python
import spacy
from textpipeliner import PipelineEngine, Context
from textpipeliner.pipes import *

nlp = spacy.load("en")
doc = nlp(
    "The Empire of Japan aimed to dominate Asia and the Pacific and was "
    "already at war with the Republic of China in 1937, but the world war is "
    "generally said to have begun on 1 September 1939 with the invasion of "
    "Poland by Germany and subsequent declarations of war on Germany by "
    "France and the United Kingdom. From late 1939 to early 1941, in a "
    "series of campaigns and treaties, Germany conquered or controlled much "
    "of continental Europe, and formed the Axis alliance with Italy and "
    "Japan. Under the Molotov-Ribbentrop Pact of August 1939, Germany and the "
    "Soviet Union partitioned and annexed territories of their European "
    "neighbours, Poland, Finland, Romania and the Baltic states. The war "
    "continued primarily between the European Axis powers and the coalition "
    "of the United Kingdom and the British Commonwealth, with campaigns "
    "including the North Africa and East Africa campaigns, the aerial Battle "
    "of Britain, the Blitz bombing campaign, the Balkan Campaign as well as "
    "the long-running Battle of the Atlantic. In June 1941, the European Axis "
    "powers launched an invasion of the Soviet Union, opening the largest "
    "land theatre of war in history, which trapped the major part of the "
    "Axis' military forces into a war of attrition. In December 1941, Japan "
    "attacked the United States and European territories in the Pacific "
    "Ocean, and quickly conquered much of the Western Pacific.")

pipes_structure = [
    SequencePipe([
        FindTokensPipe("VERB/nsubj/*"),
        NamedEntityFilterPipe(),
        NamedEntityExtractorPipe()
    ]),
    FindTokensPipe("VERB"),
    AnyPipe([
        SequencePipe([
            FindTokensPipe("VBD/dobj/NNP"),
            AggregatePipe([
                NamedEntityFilterPipe("GPE"),
                NamedEntityFilterPipe("PERSON")
            ]),
            NamedEntityExtractorPipe()
        ]),
        SequencePipe([
            FindTokensPipe("VBD/**/*/pobj/NNP"),
            AggregatePipe([
                NamedEntityFilterPipe("LOC"),
                NamedEntityFilterPipe("PERSON")
            ]),
            NamedEntityExtractorPipe()
        ])
    ])
]

engine = PipelineEngine(pipes_structure, Context(doc), [0, 1, 2])
engine.process()
```

It will return:

```Python
[
    ([Germany], [conquered], [Europe]),
    ([Japan], [attacked], [the, United, States])
]
```
