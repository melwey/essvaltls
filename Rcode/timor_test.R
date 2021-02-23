# Timor-Leste

# comparison of World Ecosystems with Copernicus Hotspot land cover
# select one PA in Timor Leste, e.g. Nino Konis Santana WDPAID 352708
# choose a smaller PA: Lagoa Maurei no Alafalu 555547939: reported area 5 km2
sp_timor <- shapefile("/Users/mela/Documents/JRC/BIOPAMA/ESS/data/TimorLeste/WDPA_Apr2020_TLS-shapefile/WDPA_Apr2020_TLS-shapefile-polygons.shp")
sp_timor_nino <- subset(sp_timor, subset = grepl(555547939, sp_timor$WDPAID))
# load raster land cover
lc <- raster("/Users/mela/Documents/JRC/BIOPAMA/ESS/data/TimorLeste/PAC01_LCCS_MODULAR_LC_PERIOD_a_2016_RASTER_v3/PAC01_LCCS_MODULAR_LC_PERIOD_a_2016_RASTER_v3.tif")
# get raster area
timor_lc_area <- area(lc,
               filename = "./tmp_output/timor_lc_area",
               format = "GTiff",
               options = c("COMPRESS=DEFLATE"))
timor_lc_area <- raster("./tmp_output/timor_lc_area.tif")

# stack land_biomes, r_area
timor <- stack(lc, timor_lc_area)
# extract values from stack
df_nino <- extract(timor, sp_timor_nino, df = TRUE, cellnumbers = TRUE, along = TRUE)
names(df_nino)[3]<-"map_code"
save(df_nino, file = "./tmp_output/df_555547939.rdata")
# load lc_legend
lc_vat <- foreign::read.dbf("/Users/mela/Documents/JRC/BIOPAMA/ESS/data/TimorLeste/PAC01_LCCS_MODULAR_LC_PERIOD_a_2016_VECTOR_v3/PAC01_LCCS_MODULAR_LC_PERIOD_a_2016_VECTOR_v3.dbf")
# simplify and group lc classes
lc <- lc_vat %>%
  dplyr::select(map_code, class_name) %>%
  distinct() %>%
  # remove \n
  tidyr::separate(col = class_name, into = c("class_name", NA), sep = " *\n", fill = "right")%>%
  # group acquatic into wetlands
  mutate(Wetlands = grepl("Acquatic", class_name)) %>% 
  # group crops
  mutate(Cropland = grepl("Crops", class_name) | grepl("Agriculture", class_name)) %>%
  # group forest
  mutate(Forest = grepl("Forest", class_name)) %>%
  # group shrubs and grassland
  mutate(Grassland = grepl("Grass", class_name) | grepl("Shrub", class_name)) %>%
  # group urban
  mutate(Urban = grepl("Urban", class_name)) %>%
  # group open water
  mutate(Water = grepl("Water", class_name) | grepl("River", class_name) | grepl("Lake", class_name)) %>%
  # agregate classes
  mutate(lc_biomes = case_when(
    
  ))


# summarise area by lc class
nino_lc <- df_nino %>%
  group_by(map_code) %>%
  dplyr::select(map_code, timor_lc_area)   %>%
  summarise(Area = sum(Area = sum(timor_lc_area, na.rm = TRUE))) %>%
  arrange(desc(Area)) %>% 
  left_join(lc)
nino_lc %>% 
  mutate(Area_pc = round(Area/sum(Area) * 100, digits = 2))

# extract values from stack
df_nino_biomes <- extract(s_biomes_area, sp_timor_nino, df = TRUE, cellnumbers = TRUE, along = TRUE)
# load biomes_legend
biomes_legend <- readr::read_delim("biomes_legend.txt", delim = ",",col_names = FALSE , skip = 2)
names(biomes_legend) <- c("biome_code", "R", "G", "B", "alpha", "label")
# summarise area by biome
nino_biomes <- df_nino_biomes %>% 
  select(land_biomes, r_area)              %>%
  group_by(land_biomes)                    %>%
  summarise(Area = sum(r_area, na.rm = TRUE))%>%
  arrange(desc(Area)) %>%
  left_join(biomes_legend %>% 
            dplyr::select(biome_code, label)%>%
            distinct(),
          by = c("land_biomes" = "biome_code"))



