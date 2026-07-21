#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Test usage of pyOTTR
"""

import fileinput
import os
import pathlib
import sys
import tempfile

from icecream import ic
import xandergraph as xg
import pyshacl
import rdflib


if __name__ == "__main__":
    kg: xg.KnowledgeGraph = xg.KnowledgeGraph(
        ns = {
            "bwyd": "https://github.com/DerwenAI/bwyd/wiki/ns#",
        },
    )

    kg.load_stottr(pathlib.Path("bwyd.stottr"))

    ## generate models from the data
    rdf_data: str = """
@prefix bwyd:     <https://github.com/DerwenAI/bwyd/wiki/ns#> .

bwyd:Recipe(
  <urn:bwyd:pacoid:panna_cotta> ,
  "Panna Cotta"@en ,
  "A light, creamy dessert which pairs with so many fruits"@en ,
  <https://spdx.org/licenses/CC-BY-NC-SA-4.0> ,
  <https://derwen.ai/paco> ,
  "2022-07-16"^^xsd:dateTime ,
) .

bwyd:RecipeImage(
  <urn:bwyd:pacoid:panna_cotta> ,
  <https://www.instagram.com/p/CgGYEZFL7Dx/> ,
) .

bwyd:RecipeSource(
  <urn:bwyd:pacoid:panna_cotta> ,
  <https://www.thekitchn.com/how-to-make-panna-cotta-cooking-lessons-from-the-kitchn-200070> ,
) .

bwyd:RecipeSource(
  <urn:bwyd:pacoid:panna_cotta> ,
  <https://mytastefulrecipes.com/almond-milk-panna-cotta-recipe/> ,
) .

bwyd:RecipeDepends(
  <urn:bwyd:pacoid:panna_cotta> ,
  <urn:bwyd:pacoid:panna_cotta/closure_1> ,
) .

bwyd:RecipeDepends(
  <urn:bwyd:pacoid:panna_cotta> ,
  <urn:bwyd:pacoid:panna_cotta/closure_2> ,
) .

bwyd:Closure(
  <urn:bwyd:pacoid:panna_cotta/closure_1> ,
  "mix the cream"@en ,
  "Prepare the cream filling"@en ,
) .

bwyd:ClosureConsumes(
  <urn:bwyd:pacoid:panna_cotta/closure_1> ,
  <urn:bwyd:ingredient:cream> ,
) .

bwyd:ClosureConsumes(
  <urn:bwyd:pacoid:panna_cotta/closure_1> ,
  <urn:bwyd:ingredient:granulated_sugar> ,
) .

bwyd:ClosureProduces(
  <urn:bwyd:pacoid:panna_cotta/closure_1> ,
  <urn:bwyd:pacoid:panna_cotta/closure_1/product/filling> ,
) .


bwyd:Closure(
  <urn:bwyd:pacoid:panna_cotta/closure_2> ,
  "chill in containers"@en ,
  "Fill the ramekins and chill"@en ,
) .

bwyd:ClosureConsumes(
  <urn:bwyd:pacoid:panna_cotta/closure_2> ,
  <urn:bwyd:pacoid:panna_cotta/closure_1/product/filling> ,
) .

bwyd:ClosureProduces(
  <urn:bwyd:pacoid:panna_cotta/closure_2> ,
  <urn:bwyd:pacoid:product:panna_cotta> ,
) .


bwyd:Product(
  <urn:bwyd:pacoid:panna_cotta/closure_1/product/filling> ,
  "filling"@en ,
) .

bwyd:Product(
  <urn:bwyd:pacoid:product:panna_cotta> ,
  "panna_cotta"@en ,
) .
    """.strip()

    kg.gen_ottr_rdf(rdf_data)

# need to add programmatically:
#   rdfs:subClassOf <urn:bwyd:subject:dessert> , <urn:bwyd:subject:pudding> ;
#   skos:related <urn:bwyd:keyword:italian> ;


    ## save generated RDF to a file
    ttl_path: pathlib.Path = pathlib.Path("corpus.ttl")

    with open(ttl_path, "w", encoding = "utf-8") as fp:
        ttl: str = kg.graph.serialize(format = "turtle")
        fp.write(ttl)


    ## check for RDF syntax errors within the data graph
    file_list: list[ str ] = [
        "corpus.ttl",
        "search.ttl",
        "pantry.ttl",
    ]

    graph: rdflib.Graph = rdflib.Graph()

    for ttl_file in file_list:
        print(ttl_file)
        graph.parse(ttl_file)

    tf: tempfile.NamedTemporaryFile = tempfile.NamedTemporaryFile(
        delete = False,
        suffix = ".ttl",
    )

    with open(tf.name, "w", encoding = "utf-8") as fp:
        with fileinput.input(files = file_list, encoding = "utf-8") as stream:
            for line in stream:
                fp.write(line)

    tf.close()
    print(tf.name)

    graph = rdflib.Graph()
    graph.parse(tf.name)


    ## SHACL validation
    conforms, results_graph, results_text = pyshacl.validate(
        tf.name,
        shacl_graph = "shapes.ttl",
        ont_graph = "domain.ttl",
        inference = "rdfs",
        abort_on_first = False,
        allow_infos = False,
        allow_warnings = False,
        meta_shacl = False,
        advanced = False,
        js = False,
        debug = False,
    )

    print(results_text)

    tf.close()
    os.unlink(tf.name)
