import fiona

print("Layers in bag-light.gpkg:")
for name in fiona.listlayers("bag-light.gpkg"):
    print(" •", name)
