# Usage: python intermagnet.py > intermagnet.ttl

# Not all stations may have all combinations of qualities, cadences, and frames.
# Need to determine by reading catalog response.
# Combine duplicate code in functions.

# TODO: See
# https://github.com/rweigel/stct/blob/main/lists/toRDF/SPASE_2023_csv_to_rdf.py
# for examples of generating RDF using rdflib.Graph directly rather than
# writing Turtle strings manually.

frames = ['native', 'xyzf', 'hdzf', 'diff']
stations = ['aae']
cadences = ['PT1S', 'PT1M']
qualities = [ 'reported', 'definitive', 'quasi-def', 'best-avail']
parameters = ['Field_Magnitude', 'Field_Vector']
url = "https://imag-data.bgs.ac.uk/GIN_V1/hapi"


def write(ttl_str):
  from rdflib import Graph

  with open("intermagnet.ttl", "w") as f:
    f.write(ttl_str)

  g = Graph()
  g.parse("intermagnet.ttl", format="turtle")
  #g.parse(data=ttl_str, format="turtle")
  jsonld_data = g.serialize(format='json-ld', indent=2)

  with open("intermagnet.jsonld", "w") as f:
    f.write(jsonld_data)

  print("Conversion complete. Output written to intermagnet.jsonld")


def head():

  ttl_str = "@prefix hapi: <http://hapi.org/rdf/> .\n"
  ttl_str += "@prefix dcat: <http://www.w3.org/ns/dcat#> .\n"
  ttl_str += f"@prefix : <{url}> .\n"

  return ttl_str

def provides():

  ttl_str = "# Datasets\n"

  ttl_str += ": a hapi:Service;\n"
  ttl_str += "  hapi:provides\n"
  for station in stations:
    for quality in qualities:
      for cadence in cadences:
        for frame in frames:
          ttl_str += f"    <{url}/info?dataset={station}/{quality}/{cadence}/{frame}>,\n"
  # Replacing last comma with period
  ttl_str = ttl_str.rstrip(",\n") + " ;\n"
  ttl_str += f"  dcat:endpointURL <{url}> .\n"

  return ttl_str


def definitions():
  ttl_str = "# Definitions\n"
  for station in stations:
    for quality in qualities:
      for cadence in cadences:
        for frame in frames:
          path = f"<{url}/info?={station}/{quality}/{cadence}/{frame}>"
          ttl_str += f"{path} a hapi:Dataset;\n"
          for parameter in parameters:
            ttl_str += f"  hapi:hasParameter :{parameter};\n"
          ttl_str = ttl_str.rstrip(";\n") + " .\n"
      break
  return ttl_str


def cadence_relations():
  ttl_str = "# Cadence Relations\n"
  base_cadence = cadences[0]
  sub_cadences = set(cadences) - set([base_cadence])
  for station in stations:
    for quality in qualities:
      for cadence in sub_cadences:
        for frame in frames:
          for parameter in parameters:
            path = f"<{url}/info?dataset={station}/{quality}/{cadence}/{frame}>"
            ttl_str += f'{path} hapi:resampledMethod :average .\n'
            path = f"<{url}/info?dataset={station}/{quality}/{cadence}/{frame}>"
            ttl_str += f'{path} hapi:isResampledOf <{url}/info?dataset={station}/{quality}/{base_cadence}/{frame}> .\n'
            ttl_str += "\n"

  return ttl_str


def quality_relations():
  ttl_str = "# Quality Relations\n"
  base_quality = qualities[0]
  sub_qualities = set(qualities) - set([base_quality])

  for station in stations:
    for quality in sub_qualities:
      for cadence in cadences:
        for frame in frames:
          path1 = f"<{url}/info?dataset={station}/{quality}/{cadence}/{frame}>"
          path2 = f"<{url}/info?dataset={station}/{base_quality}/{cadence}/{frame}>"
          ttl_str += f'{path1} hapi:isVersionOf {path2} .\n'

  return ttl_str


def frame_relations():
  ttl_str = "# Frame Relations\n"
  base_frame = frames[0]
  sub_frames = set(frames) - set([base_frame])

  for station in stations:
    for quality in qualities:
      for cadence in cadences:
        for frame in sub_frames:
          path1 = f"<{url}/info?dataset={station}/{quality}/{cadence}/{frame}>"
          path2 = f"<{url}/info?dataset={station}/{quality}/{cadence}/{base_frame}>"
          ttl_str += f'{path1} hapi:isReferenceFrameTransformOf {path2} .\n'

  return ttl_str

ttl_str = head()
ttl_str += "\n" + provides()
ttl_str += "\n" + definitions()
ttl_str += "\n" + cadence_relations()
ttl_str += "\n" + quality_relations()
ttl_str += "\n" + frame_relations()

write(ttl_str)