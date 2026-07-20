# pyOTTR
[![Build Status](https://travis-ci.com/Callidon/pyOTTR.svg?branch=master)](https://travis-ci.com/Callidon/pyOTTR)

Manipulate [OTTR Reasonable Ontology Templates](http://ottr.xyz/) in Python.

[Package documentation](https://callidon.github.io/pyOTTR)

[OTTR documentation](http://ottr.xyz/)

:white_check_mark: **Supported features:**
* [Definition and execution of templates](http://spec.ottr.xyz/pOTTR/0.1/01-basics.html#2_Templates_and_Instances) in the [stOTTR syntax](http://spec.ottr.xyz/stOTTR/0.1/)
* [Nesting templates](http://spec.ottr.xyz/pOTTR/0.1/01-basics.html#3_Nesting_templates)
* [Type checking](http://spec.ottr.xyz/pOTTR/0.1/01-basics.html#4_Types)
* [Non blank](http://spec.ottr.xyz/pOTTR/0.1/01-basics.html#5_NonBlank), [Optional](http://spec.ottr.xyz/pOTTR/0.1/01-basics.html#6_Optionals_and_None) and [default values](http://spec.ottr.xyz/pOTTR/0.1/01-basics.html#7_Default_values) for template parameters.
* *RDF and RDFS templates* from the [OTTR template library](http://tpl.ottr.xyz/) are loaded by default.

:wrench: **In development:**
* [Expansion modes](http://spec.ottr.xyz/pOTTR/0.1/01-basics.html#8_Expansion_modes)
* Support for [OWL templates](http://tpl.ottr.xyz/owl/) from the template library

# Installation

## Using pip (recommended)

```
pip install ottr
```

## Manual installation

**Requirement:** [poetry](https://python-poetry.org/) (v0.12 or higher).

```
git clone https://github.com/Callidon/pyOTTR.git
cd pyOTTR/
poetry install
```

# Getting started

The main class to manipulate is `OttrGenerator`, which is used to load OTTR templates and expand template instances.
So, in practice, you only need to create a new generator, load some templates and then execute your instances to produce RDF triples.
Otherwise, everything else is done using classic OTTR syntax!

By default, **all templates** from the [OTTR template library](http://tpl.ottr.xyz/) are loaded when the generator is created.

```python
# an OttrGenerator is used to load templates and expand instances

import ottr

template: str = """
@prefix ex: <http://example.org#> .

ex:FirstName [ ottr:IRI ?uri, ?firstName ] :: {
  ottr:Triple ( ?uri, foaf:firstName, ?firstName )
} .

ex:Person[ ?firstName ] :: {
  ottr:Triple ( _:person, rdf:type, foaf:Person ),
  ex:FirstName ( _:person, ?firstName )
} .
""".strip()

# load a simple OTTR template definition

generator: ottr.OttrGenerator = ottr.OttrGenerator()
generator.load_templates(template)

# parse and prepare an instance for execution

rdf_data: str = """
@prefix ex: <http://example.org#> .

ex:Person("Ann") .
""".strip()

instances: ottr.generator.OttrInstances = generator.instanciate(rdf_data)

# execute the instance, which yield RDF triples
# the following prints (_:person0, rdf:type, foaf:Person) and (_:person0, foaf:firstName, "Ann")

for s, p, o in instances.execute(as_nt = True):
    print("# ----- RDF triple ----- #")
    print((s, p, o)
```


## Addendum

Updated for more recent releases of `RDFlib` by [Derwen](https://derwen.ai)
since the source did not appear to have been maintained for ~7 years.
