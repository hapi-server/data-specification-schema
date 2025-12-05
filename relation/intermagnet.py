# Usage: python intermagnet.py > intermagnet.ttl

# Not all stations may have all combinations of qualities, cadences, and frames.
# Need to determine by reading catalog response.
# Combine duplicate code in functions.

frames = ['native', 'xyzf', 'hdzf', 'diff']
stations = ['aae']
cadences = ['PT1S', 'PT1M']
qualities = [ 'reported', 'definitive', 'quasi-def', 'best-avail']
parameters = ['Field_Magnitude', 'Field_Vector']
url = "https://imag-data.bgs.ac.uk/GIN_V1/hapi"
def head():

  print("@prefix hapi : <http://hapi.org/rdf/> .")
  print(f"@prefix : <{url}> .")


def provides():

  print(":INTERMAGNET a hapi:Service;")
  print("  hapi:provides")
  for station in stations:
    for quality in qualities:
      for cadence in cadences:
        for frame in frames:
          print(f"    :{station}/{quality}/{cadence}/{frame},")
  print(f"  dcat:endpointURL <{url}/info?dataset=> .")


def definitions():
  for station in stations:
    for quality in qualities:
      for cadence in cadences:
        for frame in frames:
          path = f":{station}/{quality}/{cadence}/{frame}"
          definition = f"{path} a hapi:Dataset;"
          for parameter in parameters:
            definition += f"\n  hapi:hasParameter :{parameter} ."
          print("")
          print(definition)


def cadence_relations():
  base_cadence = cadences[0]
  sub_cadences = set(cadences) - set([base_cadence])
  for station in stations:
    for quality in qualities:
      for cadence in sub_cadences:
        for frame in frames:
          for parameter in parameters:
            path = f":{station}/{quality}/{cadence}/{frame} :{parameter}"
            definition = f'{path} hapi:resampledMethod "mean;"\n'
            path = f":{station}/{quality}/{base_cadence}/{frame} :{parameter}"
            definition += f'  hapi:isResampledOf {path} .'
            print("")
            print(definition)


def quality_relations():
  base_quality = qualities[0]
  sub_qualities = set(qualities) - set([base_quality])

  for station in stations:
    for quality in sub_qualities:
      for cadence in cadences:
        for frame in frames:
          for parameter in parameters:
              path1 = f":{station}/{quality}/{cadence}/{frame} :{parameter}"
              path2 = f":{station}/{base_quality}/{cadence}/{frame} :{parameter}"
              definition = f'{path1} hapi:isVersionOf {path2}\n'
              print(definition)


def frame_relations():
  base_frame = frames[0]
  sub_frames = set(frames) - set([base_frame])

  for station in stations:
    for quality in qualities:
      for cadence in cadences:
        for frame in sub_frames:
          for parameter in parameters:
              path = f":{station}/{quality}/{cadence}/{frame} :{parameter}"
              definition = f'{path} hapi:resampledMethod "mean;"\n'
              path = f":{station}/{quality}/{cadence}/{base_frame} :{parameter}"
              definition += f'  hapi:isResampledOf {path} .'
          print("")
          print(definition)


print("# Datasets")
provides()
print("")

print("# Definitions")
definitions()

print("\n# Cadence Relations")
cadence_relations()

print("\n# Quality Relations")
quality_relations()

print("\n# Frame Relations")
frame_relations()
