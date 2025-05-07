import fiona
import itertools
from shapely.geometry import shape

# 1. Replace ‘pand’ with whichever layer you want to inspect.
LAYER = "pand"  
SRC = "bag-light.gpkg"

with fiona.open(SRC, layer=LAYER) as src:
    print(f"Schema for layer '{LAYER}':\n", src.schema, "\n")
    print("First 5 features:")
    for feat in itertools.islice(src, 5):
        props = feat["properties"]
        geom = shape(feat["geometry"])
        # print just a few key/value pairs plus geometry type
        sample = {k: props[k] for k in list(props)[:5]}
        print(sample, "→", geom.geom_type)
