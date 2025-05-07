import fiona, itertools
from shapely.geometry import shape

LAYER = "verblijfsobject"   # the layer with address-unit points
SRC   = "bag-light.gpkg"

with fiona.open(SRC, layer=LAYER) as src:
    print(f"Schema for '{LAYER}':\n", src.schema, "\n")
    print("First 5 features:")
    for feat in itertools.islice(src, 5):
        props = feat["properties"]
        geom  = shape(feat["geometry"])
        # show only key address fields + the point geometry
        sample = {
            "identificatie":  props.get("identificatie"),
            "huisnummer":     props.get("huisnummer"),
            "openb_naam":     props.get("openbareruimtenaam"),
            "postcode":       props.get("postcode"),
            "woonplaats":     props.get("woonplaatsnaam")
        }
        print(sample, "→", geom.geom_type)
