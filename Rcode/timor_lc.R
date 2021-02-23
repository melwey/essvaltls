# Timor Leste land cover comparison
# Ministry of agriculture 2001
# Copernicus Hotspot 2016
library(tidyverse)
library(sf)
LCinterCH <- sf::read_sf("./tmp_output/LCinterCH.gpkg", layer = "LCinterCH")
LCinterCH <- LCinterCH %>%
  mutate(poly_area = st_area(LCinterCH)) 

summaryLCinterCH <- as.data.frame(LCinterCH) %>%
  dplyr::select(LUCODE, LU_CLASS, LU_CATEGOR, OBSERVATIO, lcclevel, map_code, class_name, map_codeA, poly_area) %>%
  # remove \n in class_name
  mutate(class_name = sub("\n","", class_name))%>%
  group_by(class_name) %>%
  mutate(Area_CH = sum(poly_area)) %>%
  ungroup() %>%
  group_by( LU_CLASS) %>%
  mutate(Area_LC = sum(poly_area)) %>%
  ungroup() %>%
  group_by( LU_CLASS, class_name, Area_CH, Area_LC) %>%
  summarise(
    Area = sum(poly_area, na.rm = TRUE)
    ) %>%
  mutate(
    Area_pcLC = round(sum(Area, na.rm = TRUE)/Area_LC *100, digits = 2),
    Area_pcCH = round(sum(Area, na.rm = TRUE)/Area_CH *100, digits = 2)
    ) %>%
  arrange(class_name, desc(Area_pcCH))
  
write_csv(summaryLCinterCH, file = "./tmp_output/LCinterCH_area.csv")
sf::st_write(LCinterCH, "./tmp_output/LCinterCH.shp")


# union
LCunionCH <- sf::read_sf("./tmp_output/LCunionCH.shp")
LCunionCH <- LCunionCH %>%
  mutate(poly_area = st_area(LCunionCH)) 

summaryLCunionCH <- as.data.frame(LCunionCH) %>%
  dplyr::select(LUCODE, LU_CLASS, LU_CATEGOR, OBSERVATIO, lcclevel, map_code, class_name, map_codeA, poly_area) %>%
  # remove \n in class_name
  mutate(class_name = sub("\n","", class_name))%>%
  group_by(class_name) %>%
  mutate(Area_CH = sum(poly_area)) %>%
  ungroup() %>%
  group_by( LU_CLASS) %>%
  mutate(Area_LC = sum(poly_area)) %>%
  ungroup() %>%
  group_by( LU_CLASS, class_name, Area_CH, Area_LC) %>%
  summarise(
    Area = sum(poly_area, na.rm = TRUE)
  ) %>%
  mutate(
    Area_pcLC = round(sum(Area, na.rm = TRUE)/Area_LC *100, digits = 2),
    Area_pcCH = round(sum(Area, na.rm = TRUE)/Area_CH *100, digits = 2)
  ) %>%
  arrange(class_name, desc(Area_pcCH))

write_csv(summaryLCunionCH, file = "./tmp_output/LCunionCH_area.csv")
######## data edited in Excel
# load data again
summaryLCunionCH <- read_csv(file = "./tmp_output/LCunionCH_area.csv") %>%
# replace Mangrove by Mangroves
#sub(pattern, replace, x)
# use as reclassification table to edit LCunionCH
LCunionCHbiome <- LCunionCH %>%
  # remove trailing spaces (incl. \n) in class_name
  mutate(class_name = str_trim(class_name))%>%
  left_join(summaryLCunionCH %>% dplyr::select(LU_CLASS, class_name, BIOME))
# ######## something not working in the join #######
# tmp <- LCunionCHbiome %>% 
#   # discard geometry
#   as.data.frame() %>%
#   group_by(LU_CLASS, class_name, BIOME) %>% 
#   filter(is.na(BIOME)) %>%
#   summarise(sumArea = sum(poly_area), count = n()) %>%
#   arrange(class_name)
# cretine: j'ai foutu mes données en l'air en voulant écrire le nouvel LCunionCH dans le même gpkg LCinterCH.
# Mais j'ai sauvé une copie shp
sf::st_write(LCunionCHbiome, "./tmp_output/LCunionCHbiome.shp")
# sf::st_write(LCinterCH, "./tmp_output/LCinterCH.shp")
# sf::st_write(LCunionCH, "./tmp_output/LCunionCH.shp")
# NEXT (in Qgis)
  # select bare areas close to coastline
  # assign BIOME="Coastal systems"
  # dissolve and delete holes

# edit 2021/01/28: I've recomputed the union the other way around
CHunionLC <- sf::read_sf("./tmp_output/LCinterCH.gpkg", layer = "CHunionLC")
CHunionLCbiome <- CHunionLC %>%
  dplyr::select(OBJECTID, map_code, class_name, LUCODE, LU_CLASS) %>%
  # remove trailing spaces (incl. \n) in class_name
  mutate(class_name = str_trim(class_name))%>%
  left_join(summaryLCunionCH %>% dplyr::select(LU_CLASS, class_name, BIOME))
# write to file
sf::st_write(CHunionLCbiome, "./tmp_output/CHunionLCbiome.shp")

#############################################################
# CI Baricafa landmarks intersection with Copernicus Hotspot
baricafaInterCH <- sf::read_sf("./tmp_output/LCinterCH.gpkg", layer = "baricafaInterCH")
baricafaInterCH <- baricafaInterCH %>%
  mutate(poly_area = st_area(baricafaInterCH)) 

summaryBaricafaInterCH <- as.data.frame(baricafaInterCH) %>%
  dplyr::select(LU_Class, LU_Class__, lcclevel, map_code, class_name, map_codeA, poly_area) %>%
  # remove \n in class_name
  mutate(class_name = sub("\n","", class_name))%>%
  group_by(class_name) %>%
  mutate(Area_CH = sum(poly_area)) %>%
  ungroup() %>%
  group_by( LU_Class) %>%
  mutate(Area_LC = sum(poly_area)) %>%
  ungroup() %>%
  group_by( LU_Class, class_name, Area_CH, Area_LC) %>%
  summarise(
    Area = sum(poly_area, na.rm = TRUE)
  ) %>%
  mutate(
    Area_pcLC = round(sum(Area, na.rm = TRUE)/Area_LC *100, digits = 2),
    Area_pcCH = round(sum(Area, na.rm = TRUE)/Area_CH *100, digits = 2)
  ) %>%
  arrange(class_name, desc(Area_pcCH))

write_csv(summaryBaricafaInterCH, file = "./tmp_output/baricafaInterCH.csv")

# CI Uacala landmarks intersection with Copernicus Hotspot
uacalaInterCH <- sf::read_sf("./tmp_output/LCinterCH.gpkg", layer = "uacalaInterCH")
uacalaInterCH <- uacalaInterCH %>%
  mutate(poly_area = st_area(uacalaInterCH)) 

summaryUacalaInterCH <- as.data.frame(uacalaInterCH) %>%
  dplyr::select(LU_Class, LU_Class__, lcclevel, map_code, class_name, map_codeA, poly_area) %>%
  # remove \n in class_name
  mutate(class_name = sub("\n","", class_name))%>%
  group_by(class_name) %>%
  mutate(Area_CH = sum(poly_area)) %>%
  ungroup() %>%
  group_by( LU_Class) %>%
  mutate(Area_LC = sum(poly_area)) %>%
  ungroup() %>%
  group_by( LU_Class, class_name, Area_CH, Area_LC) %>%
  summarise(
    Area = sum(poly_area, na.rm = TRUE)
  ) %>%
  mutate(
    Area_pcLC = round(sum(Area, na.rm = TRUE)/Area_LC *100, digits = 2),
    Area_pcCH = round(sum(Area, na.rm = TRUE)/Area_CH *100, digits = 2)
  ) %>%
  arrange(class_name, desc(Area_pcCH))

write_csv(summaryUacalaInterCH, file = "./tmp_output/uacalaInterCH.csv")

