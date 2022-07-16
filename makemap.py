import leafmap.foliumap as leafmap
def crearMapa(california):
	geojson = leafmap.gdf_to_geojson(california, epsg="4326")
	m = leafmap.Map()
	m.add_gdf(california, layer_name="CALL_FIRE_EMERGENCY", fill_colors=["red", "green", "blue"])
	m.add_basemap("HYBRID")
	return m
