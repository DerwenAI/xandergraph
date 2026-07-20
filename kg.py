#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Test usage of pyOTTR
"""

import pathlib
import sys

from icecream import ic
import ottr
import pyshacl
import rdflib


class KnowledgeGraph:
    """
Represents a knowledge graph, with accessors for both the `RDFlib`
semantic graph and the `NetworkX` property graph.
    """
    def __init__ (
        self,
        ) -> None:
        """
Constructor.
        """
        self.graph: rdflib.Graph = rdflib.Graph()
        self.graph.bind("bwyd", rdflib.Namespace("https://github.com/DerwenAI/bwyd/wiki/ns#"))

        self.ottr_generator: ottr.OttrGenerator = ottr.OttrGenerator()


    def load_stottr (
        self,
        stottr_path: pathlib.Path,
        ) -> rdflib.Graph:
        """
Define and load the OTTR templates.
        """
        with open(stottr_path, "r", encoding = "utf-8") as fp:
            stottr_template: str = fp.read().strip()

            self.ottr_generator.load_templates(
                stottr_template,
                format = "stottr",
            )


    def gen_ottr_rdf (
        self,
        rdf_data: str,
        ) -> rdflib.Graph:
        """
Generate RDF triples based on applying the given text data to the
loaded OTTR templates.
        """
        instances: ottr.generator.OttrInstances = self.ottr_generator.instanciate(
            rdf_data,
            format = "stottr",
        )

        for s, p, o in instances.execute(as_nt = False):
            self.graph.add((s, p, o))


if __name__ == "__main__":
    kg: KnowledgeGraph = KnowledgeGraph()
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


    """.strip()

    kg.gen_ottr_rdf(rdf_data)

    ## save to a file

    ttl_path: pathlib.Path = pathlib.Path("corpus.ttl")

    with open(ttl_path, "w", encoding = "utf-8") as fp:
        ttl: str = kg.graph.serialize(format = "turtle")
        fp.write(ttl)

    ## SHACL validation
    data_graph = "corpus.ttl"
    shacl_graph = "shapes.ttl"
    ont_graph = "domain.ttl"

    graph: rdflib.Graph = rdflib.Graph()
    graph.parse(data_graph)
    graph.parse(shacl_graph)
    graph.parse(ont_graph)

    #sys.exit(0)

    r = pyshacl.validate(
        data_graph,
        shacl_graph = shacl_graph,
        ont_graph = ont_graph,
        inference = "rdfs",
        abort_on_first = False,
        allow_infos = False,
        allow_warnings = False,
        meta_shacl = False,
        advanced = False,
        js = False,
        debug = False,
    )

    conforms, results_graph, results_text = r
    ic(conforms, results_graph, results_text)
