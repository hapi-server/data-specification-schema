# Usage: python intermagnet.py


from rdflib import Graph, Namespace, URIRef
from rdflib.namespace import RDF, DCAT, DCTERMS, PROV

# Not all stations may have all combinations of qualities, cadences, and frames.
# Need to determine by reading catalog response.
# Combine duplicate code in functions.

# TODO: See
# https://github.com/rweigel/stct/blob/main/lists/toRDF/SPASE_2023_csv_to_rdf.py
# for examples of generating RDF using rdflib.Graph directly rather than
# writing Turtle strings manually.

# define lists for iterators

frames = ['native', 'xyzf', 'hdzf', 'diff']
stations = ['aae']
cadences = ['PT1S', 'PT1M']
qualities = [ 'reported', 'definitive', 'quasi-def', 'best-avail']
parameters = ['Field_Magnitude', 'Field_Vector']
url = "https://imag-data.bgs.ac.uk/GIN_V1/hapi"

# define base URL: this is the local server base URL.
# TODO:
#  This should probably be changed in the future to be consistent with the SPASE resource ID, rather than to
#  the server HAPI endpoint URL
base_url = URIRef(url)

# define the HAPI namespace
HAPI = Namespace("http://hapi.org/rdf/")

def write(g, basename="intermagnet"):
    # with open("intermagnet.ttl", "w") as f:
    #    f.write(ttl_str)
    g.serialize(destination=f"{basename}.ttl", format='turtle')

    # g = Graph()
    # g.parse("intermagnet.ttl", format="turtle")
    # g.parse(data=ttl_str, format="turtle")
    # jsonld_data = g.serialize(format='json-ld', indent=2)
    # with open("intermagnet.jsonld", "w") as f:
    #    f.write(jsonld_data)

    g.serialize(destination=f"{basename}.jsonld", format='json-ld')

    print(f"Conversion complete. Output written to {basename}.ttl and {basename}.jsonld")


def head(g):
    # Define the header of the graph
    # - bind namespaces that are not included by default
    # - define the base urt

    # ttl_str = "@prefix hapi: <http://hapi.org/rdf/> .\n"
    g.bind('hapi', HAPI)
    # ttl_str += "@prefix dcat: <http://www.w3.org/ns/dcat#> .\n"
    g.bind('dcat', DCAT)
    #   ttl_str += f"@prefix : <{url}> .\n"
    g.base = URIRef(url)


def provides(g):
    # Include the relations between the Server and the Datasets
    # we use here the dcat:servesDataset relation, rather than the HAPI one (which should be removed)

    # ttl_str = "# Datasets\n"
    # ttl_str += ": a hapi:Service;\n"
    g.add((base_url, RDF.type, HAPI.Service))
    # ttl_str += "  hapi:provides\n"
    for station in stations:
        for quality in qualities:
            for cadence in cadences:
                for frame in frames:
                    # ttl_str += f"    <{url}/info?dataset={station}/{quality}/{cadence}/{frame}>,\n"
                    g.add((
                        base_url,
                        DCAT.servesDataset,
                        URIRef(f"{url}/info?dataset={station}/{quality}/{cadence}/{frame}")
                    ))
    # Replacing last comma with period
    # ttl_str = ttl_str.rstrip(",\n") + " ;\n"
    # ttl_str += f"  dcat:endpointURL <{url}> .\n"
    g.add((base_url, DCAT.endpointURL, URIRef(url)))


def definitions(g):
    # Include the relation between Datasets and Parameters

    # ttl_str = "# Definitions\n"
    for station in stations:
        for quality in qualities:
            for cadence in cadences:
                for frame in frames:
                    uri_dataset = URIRef(f"{url}/info?dataset={station}/{quality}/{cadence}/{frame}")
                    # ttl_str += f"{path} a hapi:Dataset;\n"
                    g.add((uri_dataset, RDF.type, HAPI.Dataset))
                    for parameter in parameters:
                        # the parameter object must be a URI I propose to compose it as follows:
                        # ex: https://imag-data.bgs.ac.uk/GIN_V1/hapi/info?dataset=aae/reported/PT1S/native#Field_Magnitude
                        uri_parameter = URIRef(f"{str(uri_dataset)}#{parameter}")
                        # ttl_str += f"  hapi:hasParameter :{parameter};\n"
                        g.add((uri_dataset, HAPI.hasParameter, uri_parameter))
                        # ttl_str = ttl_str.rstrip(";\n") + " .\n"


def cadence_relations(g):
    # Include the cadence information for each Dataset
    # NB: use new property name of hapi:resamplingMethod (see base.ttl)

    # ttl_str = "# Cadence Relations\n"
    base_cadence = cadences[0]
    sub_cadences = set(cadences) - {base_cadence}
    for station in stations:
        for quality in qualities:
            for cadence in sub_cadences:
                for frame in frames:
                    uri_resample = URIRef(f"{url}/info?dataset={station}/{quality}/{cadence}/{frame}")
                    uri_source = URIRef(f"{url}/info?dataset={station}/{quality}/{base_cadence}/{frame}")
                    # ttl_str += f'{path} hapi:resampledMethod :average .\n'
                    g.add((uri_resample, HAPI.resamplingMethod, HAPI.average))
                    # ttl_str += f'{path} hapi:isResampledOf <{url}/info?dataset={station}/{quality}/{base_cadence}/{frame}> .\n'
                    g.add((uri_resample, HAPI.isResampledOf, uri_source))
                    # ttl_str += "\n"


def quality_relations(g):
    # Include the dependences between Datasets

    # ttl_str = "# Quality Relations\n"
    base_quality = qualities[0]
    sub_qualities = set(qualities) - {base_quality}
    for station in stations:
        for quality in sub_qualities:
            for cadence in cadences:
                for frame in frames:
                    uri1 = URIRef(f"{url}/info?dataset={station}/{quality}/{cadence}/{frame}")
                    uri2 = URIRef(f"{url}/info?dataset={station}/{base_quality}/{cadence}/{frame}")
                    # ttl_str += f'{path1} hapi:isVersionOf {path2} .\n'
                    g.add((uri1, DCTERMS.isVersionOf, uri2))
                    # we could also say:
                    # g.add((uri1, PROV.wasDerivedFrom, uri2))


def frame_relations(g):
    # Include the frame relations between Datasets

    # ttl_str = "# Frame Relations\n"
    base_frame = frames[0]
    sub_frames = set(frames) - {base_frame}
    for station in stations:
        for quality in qualities:
            for cadence in cadences:
                for frame in sub_frames:
                    uri1 = URIRef(f"{url}/info?dataset={station}/{quality}/{cadence}/{frame}")
                    uri2 = URIRef(f"{url}/info?dataset={station}/{quality}/{cadence}/{base_frame}")
                    # ttl_str += f'{path1} hapi:isReferenceFrameTransformOf {path2} .\n'
                    g.add((uri1, HAPI.isReferenceFrameTransformOf, uri2))

# Create graph
g = Graph()

# ttl_str = head()
head(g)
# ttl_str += "\n" + provides()
provides(g)
# ttl_str += "\n" + definitions()
definitions(g)
# ttl_str += "\n" + cadence_relations()
cadence_relations(g)
# ttl_str += "\n" + quality_relations()
quality_relations(g)
# ttl_str += "\n" + frame_relations()
frame_relations(g)

# Write the output files, in RDF/TTL and JSON-LD
write(g, basename="intermagnet")
