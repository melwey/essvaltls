# Timor Leste land cover classification
# create look-up table to match global biomes with local land cover classif
# and Copernicus Hotspot

import qgis.utils
from qgis.gui import *

import processing
import numpy as np
import os

os.chdir("/Users/Mela/documents/JRC/BIOPAMA/ESS/essvalpa")

# Get the project instance
project = QgsProject.instance() 
#project.write('timorLC.qgs')
project.setCrs(QgsCoordinateReferenceSystem("EPSG:4326"))

## load data
# minister of Agriculture of Timor-Leste
timorLC = QgsVectorLayer("/vsizip/../data/TimorLeste/TL Land Types and uses 2001.zip/TL Land Types and uses 2001/Landcover 2001 Timor-Leste UTM.shp",
    "Landcover 2001 Timor-Leste UTM","ogr")
if not timorLC.isValid():
  print("Layer failed to load!")

# Copernicus Hotspot
timorCH = QgsVectorLayer("../data/TimorLeste/PAC01/01_LCCS_MAPS_v4/PAC01_LCCS_MODULAR_LC_PERIOD_a_2016_VECTOR_v4/PAC01_LCCS_MODULAR_LC_PERIOD_a_2016_VECTOR_v4.shp", 
    "PAC01_LCCS_MODULAR_LC_PERIOD_a_2016_VECTOR_v4", "ogr")
if not timorCH.isValid():
    print("Layer failed to load!")
else :
    project.addMapLayer(timorCH)

### processing
# intersect land covers
LCinterCH = processing.run("native:intersection",{
    'INPUT': timorLC,
    'OVERLAY':timorCH,
    'OUTPUT':'ogr:dbname=\'./tmp_output/LCinterCH.gpkg\' table= \"LCinterCH\" (geom) sql='
    })['OUTPUT']
project.addMapLayer(LCinterCH)

# union land covers
LCunionCH = processing.run("native:union",{
    'INPUT': timorLC, # UTM 32751
    'OVERLAY':timorCH,# WGS84 4326
    'OUTPUT':'ogr:dbname=\'./tmp_output/LCinterCH.gpkg\' table= \"LCunionCH\" (geom) sql='
    })['OUTPUT']
project.addMapLayer(LCunionCH)

CHunionLC = processing.run("native:union",{
    'INPUT':timorCH,# WGS84 4326
    'OVERLAY': timorLC, # UTM 32751
    'OUTPUT':'ogr:dbname=\'./tmp_output/LCinterCH.gpkg\' table= \"CHunionLC\" (geom) sql='
    })['OUTPUT']

# go to R to analyse area stats


# CI landmarks polygons.
# merge layers with single classes
# clean attributes
baricafa = QgsVectorLayer("../data/TimorLeste/CI/Baricafa NRM -sharing/commondata/landmarks_baricafa/merged.shp", 
    "merged", "ogr")
if not baricafa.isValid():
  print("Layer failed to load!")

# intersect with timorCH
baricafaInterCH = processing.run("native:intersection",{
    'INPUT': baricafa,
    'OVERLAY':timorCH,
    'OUTPUT':'ogr:dbname=\'./tmp_output/LCinterCH.gpkg\' table= \"baricafaInterCH\" (geom) sql='
    })['OUTPUT']
project.addMapLayer(baricafaInterCH)

# CI landmarks polygons.
# merge layers with single classes
# clean attributes
uacala = QgsVectorLayer("../data/TimorLeste/CI/Uacala NRM-sharing/commondata/landmarks_uacala/merged.shp", 
    "merged", "ogr")
if not uacala.isValid():
  print("Layer failed to load!")
# check validity
val = processing.run("qgis:checkvalidity", { 
    'ERROR_OUTPUT' : 'TEMPORARY_OUTPUT', 
    'IGNORE_RING_SELF_INTERSECTION' : False, 
    'INPUT_LAYER' : '/Users/mela/Documents/JRC/BIOPAMA/ESS/data/TimorLeste/CI/Uacala NRM-sharing/commondata/landmarks_uacala/merged.shp', 
    'INVALID_OUTPUT' : 'TEMPORARY_OUTPUT', 
    'METHOD' : 2, 
    'VALID_OUTPUT' : 'TEMPORARY_OUTPUT' })

# intersect with timorCH
uacalaInterCH = processing.run("native:intersection",{
    'INPUT': uacala,
    'OVERLAY':timorCH,
    'OUTPUT':'ogr:dbname=\'./tmp_output/LCinterCH.gpkg\' table= \"uacalaInterCH\" (geom) sql='
    })['OUTPUT']
project.addMapLayer(uacalaInterCH)

# compute percentages of coverage in R and look at them in Excel.

## Assign biomes to Copernicus land cover classes + mangroves, coral reefs, seagrass beds, estuaries from global datasets
# 

# check validity of timorCH
val = processing.run("qgis:checkvalidity", { 
    'ERROR_OUTPUT' : 'TEMPORARY_OUTPUT', 
    'IGNORE_RING_SELF_INTERSECTION' : False, 
    'INPUT_LAYER' : timorCH, 
    'INVALID_OUTPUT' : 'TEMPORARY_OUTPUT', 
    'METHOD' : 2, 
    'VALID_OUTPUT' : 'TEMPORARY_OUTPUT' })
# 2 errors
project.addMapLayer(val['ERROR_OUTPUT'])
# changed in the original file.

### create working copy of timorCH for editting
timorCH.selectAll()
timorCHedit = processing.run("native:saveselectedfeatures", {
    'INPUT' : timorCH,
    'OUTPUT' : 'ogr:dbname=\'./tmp_output/timorBiomes.gpkg\' table=\"timorCHedit\" (geom) sql='
    })['OUTPUT']
project.addMapLayer(timorCHedit)

# add attribute biome
timorCHedit.dataProvider().addAttributes(
    [QgsField("biome", QVariant.String)])

# the layer CHedit does not seem to be used. rather use the output of the union with timorLC, with BIOME already set.
###
# reclassify map_code to biome from Excel spreasheet
# copy data from excel. done in R. LCunionCHbiome
# 2021/01/28 edit: use CHunionLC instead (4326 instead of 32751)
timorCHedit = QgsVectorLayer('./tmp_output/CHunionLCbiome.shp', "CHunionLCbiome", "ogr")
if not timorCHedit.isValid():
  print("Layer failed to load!")
else:
    project.addMapLayer(timorCHedit)


# postprocessing: coastal ecosystems
## download coastal line from EUROSTAT GISCO 1:1M (polygon)
coast = QgsVectorLayer("../data/GISCO_coastline-2016-01m/COAS_RG_01M_2016_4326.geojson",
    "Coastline", "ogr")
# select polygons: COAS_ID IN (63, 1562, 6349)
coast.selectByExpression('"COAS_ID" IN (63, 1562, 6349)', QgsVectorLayer.SetSelection)
# save selection to layer
timorCoastPoly = processing.run("native:saveselectedfeatures", {
    'INPUT' : coast,
    'OUTPUT' : 'TEMPORARY_OUTPUT'
    })['OUTPUT']
timorCoastLine = processing.run("native:polygonstolines", {
    'INPUT': timorCoastPoly,
    'OUTPUT': 'ogr:dbname=\'./tmp_output/timorCoastLine.gpkg\' table=\"timorCoastLine\" (geom) sql='
    })['OUTPUT']
project.addMapLayer(timorCoastLine)
# reproject coastline to equal distance
timorCoastLineED = processing.run("native:reprojectlayer", {
    'INPUT': timorCoastLine,                                     # layer: QgsVectorLayer
    'TARGET_CRS':QgsCoordinateReferenceSystem(54032),            # destCRS: QgsCoordinateReferenceSystem()
    'OUTPUT':'memory:'
    })['OUTPUT']
timorCoastLineED.setCrs(QgsCoordinateReferenceSystem(54032, QgsCoordinateReferenceSystem.EpsgCrsId))
# buffer 500 m
timorCoastLineEDbuf = processing.run("native:buffer",{
        'INPUT': timorCoastLineED,
        'DISTANCE':500,
        'SEGMENTS':5,
        'END_CAP_STYLE':0,
        'JOIN_STYLE':0,
        'MITER_LIMIT':2,
        'DISSOLVE':True,
        'OUTPUT':'memory:'
        })['OUTPUT']
# back transform to 4326
timorCoastLineBuf =  processing.run("native:reprojectlayer", {
    'INPUT': timorCoastLineEDbuf,                               # layer: QgsVectorLayer
    'TARGET_CRS':QgsCoordinateReferenceSystem(4326),            # destCRS: QgsCoordinateReferenceSystem()
    'OUTPUT':'ogr:dbname=\'./tmp_output/timorCoastLine.gpkg\' table=\"timorCoastLineBuf500\" (geom) sql='
    })['OUTPUT']
timorCoastLineBuf = QgsVectorLayer(os.path.abspath('./tmp_output/timorCoastLine.gpkg')+'|layername=timorCoastLineBuf500', 'ogr', 'timorCoastLineBuf')
if not timorCoastLineBuf.isValid():
    print("Layer failed to load")
else:
    project.addMapLayer(timorCoastLineBuf)

# select bare areas that are < 500 m from the shore: select by location

# select bare areas
timorCHedit.selectByExpression('"map_code" IN (11)', 
    QgsVectorLayer.SetSelection)
# select those that intersect timorCoastLineBuf
processing.run('qgis:selectbylocation', {
    'INPUT' : timorCHedit,
    'INTERSECT' : './tmp_output/timorCoastLine.gpkg|layername=timorCoastLineBuf500',
    'METHOD' : 2, # within current selection
    'PREDICATE' : [0] # intersect
    })

# edit attribute biome to "Coastal systems"
index = timorCHedit.dataProvider().fieldNameIndex('BIOME')
layer = timorCHedit
value = "Coastal systems"
layer.startEditing()
for feature in layer.getSelectedFeatures():
    layer.changeAttributeValue(feature.id(), index, value)

layer.commitChanges()

## 
## dissolve on BIOME to create multipart polygons BUT we loose the origin!!!!
#biomes = processing.run("native:dissolve", {
#    'INPUT':timorCHedit,
#    'FIELD': "BIOME",
#    'OUTPUT': 'ogr:dbname=\'./tmp_output/timorBiomes.gpkg\' table=\"timorLandBiomesDissolved\" (geom) sql='
#    })['OUTPUT']
#
#project.addMapLayer(biomes)
#
# delete holes: do not: it does something wrong at least with BIOME Urban Built-up
#biomes = processing.run("native:deleteholes", {
#        'INPUT':biomes,
#        'MIN_AREA':0,
#        'OUTPUT': 'ogr:dbname=\'./tmp_output/timorBiomes.gpkg\' table=\"timorLandBiomesNoholes\" (geom) sql='
#        })['OUTPUT']
#project.addMapLayer(biomes)

####################
## union with coastal and marine ecosystems
# basis: EEZ_land
TLS_EEZ_land = QgsVectorLayer("../data/TimorLeste/TLS_EEZ_land.shp", "TLS_EEZ_land", "ogr")

# clip mangroves, seagrass, coral to EEZ
# global mangrove watch: pxlval = 1
gmw = QgsVectorLayer("../data/GMW_001_GlobalMangroveWatch_2016/01_Data/GMW_2016_v2.shp", "GMW", "ogr")
if not gmw.isValid():
    print("Layer gmw failed to load")
else:
    # clip to EEZ
    mangrove = processing.run("native:clip", {
        'INPUT' : gmw,
        'OVERLAY' : TLS_EEZ_land,
        'OUTPUT' : 'ogr:dbname=\'./tmp_output/timorBiomes.gpkg\' table=\"mangroveClipped\" (geom) sql='
        })['OUTPUT']
    mangrove.setName("GMW_2016_v2")

project.addMapLayer(mangrove)
# update Attributes
layer = mangrove
layer.dataProvider().addAttributes(
    [QgsField("layerName", QVariant.String),
    QgsField("BIOME", QVariant.String)])

index = layer.dataProvider().fieldNameIndex('layerName')
value = "GMW_2016_v2"
layer.selectAll()
layer.startEditing()
for feature in layer.getSelectedFeatures():
    layer.changeAttributeValue(feature.id(), index, value)

layer.commitChanges()

layer.dataProvider().deleteAttributes(layer.attributeList()[1:-1])
layer.updateFields()

# WCMC coral: "LAYER_NAME" = 'CRR'
coral = QgsVectorLayer("../data/14_001_WCMC008_CoralReefs2018_v4/01_Data/WCMC008_CoralReef2018_Py_v4.shp", "coral", "ogr")
if not coral.isValid():
    print("Layer coral failed to load")
else:
    # clip to EEZ
    coral = processing.run("native:clip", {
        'INPUT':coral,
        'OVERLAY':TLS_EEZ_land,
        'OUTPUT':'ogr:dbname=\'./tmp_output/timorBiomes.gpkg\' table=\"coralClipped\" (geom) sql='
        })['OUTPUT']
    coral.setName("WCMC008_CoralReef2018_Py_v4")

project.addMapLayer(coral)
# deleteAttributes
layer = coral
layer.dataProvider().deleteAttributes(layer.attributeList()[2:])
layer.updateFields()

# WCMW seagrass: "LAYER_NAME" = 'SGS'
seagr = QgsVectorLayer("../data/WCMC_SeagrassPtPy2018_v6/01_Data/WCMC_013_014_SeagrassesPy_v6.shp", "seagrass", "ogr")
if not seagr.isValid():
    print("Layer seagr failed to load")
else:
    # clip to EEZ
    seagr0 = processing.run("native:clip", {
        'INPUT':seagr,
        'OVERLAY':TLS_EEZ_land,
        'OUTPUT':'TEMPORARY_OUTPUT'
        })['OUTPUT']
    seagr0.setName("WCMC_013_014_SeagrassesPy_v6")

project.addMapLayer(seagr0)
# the polygon in the global dataset doesn not appear in the local datasets and vice versa.
# maybe it would be best to just discard it (it is huge! not sure it is very reliable)
# CI seagrass!!!! other sites monitored
# Seagrass_national_coast: use all polygons (reef flat)
# Seagrass_national_coast_V2: use all polygons (reef flat)
seagr1 = QgsVectorLayer("../data/TimorLeste/CI/Seagrass_Dugong2018/Seagrass_national_coast.shp", "Seagrass_national_coast", "ogr")
seagr2 = QgsVectorLayer("../data/TimorLeste/CI/Seagrass_Dugong2018/Seagrass_national_coast_V2.shp", "Seagrass_national_coast_V2", "ogr")
# merge all 3 layers and edit attributes: remove all and add BIOME = 'Coastal sytems'
seagr = processing.run("native:mergevectorlayers", {
    'LAYERS':[seagr0, seagr1, seagr2],
    'CRS': "EPSG:4326",
    'OUTPUT':'ogr:dbname=\'./tmp_output/timorBiomes.gpkg\' table=\"seagrMerged\" (geom) sql='
    })['OUTPUT']

seagr.setName("seagrMerged")
# add attribute BIOME and set value
layer = seagr
layer.dataProvider().addAttributes(
    [QgsField("BIOME", QVariant.String)])

index = layer.dataProvider().fieldNameIndex('BIOME')
value = "Coastal systems"
layer.selectAll()
layer.startEditing()
for feature in layer.getSelectedFeatures():
    layer.changeAttributeValue(feature.id(), index, value)

layer.commitChanges()
project.addMapLayer(layer)
# delete all other attributes
# deleteAttributes
layer.dataProvider().deleteAttributes(layer.attributeList()[1:-3] + [layer.attributeList()[-2]])
layer.updateFields()

## put everything together
# union 2 by 2
# 
# native:fixgeometries
seagr = processing.run("native:fixgeometries", {
    'INPUT': seagr,
    'OUTPUT' : 'ogr:dbname=\'./tmp_output/timorBiomes.gpkg\' table=\"seagrMergedFixed\" (geom) sql='
    })['OUTPUT']

seagr.setName("seagrMergedFixed")
project.addMapLayer(seagr)

union1 = processing.run("native:union", {
    'INPUT' : seagr,
    'OVERLAY' : coral,
    'OUTPUT' : 'ogr:dbname=\'./tmp_output/timorBiomes.gpkg\' table=\"seagrUcoral\" (geom) sql='
    })['OUTPUT']
union1.setName("seagrUcoral")
project.addMapLayer(union1)

# if LAYER_NAME = "CCR", BIOME = "Coral reefs"
# intersections: set BIOME to coral, but keep info on seagr? how?
layer = union1
index = layer.dataProvider().fieldNameIndex('BIOME')
index1 = layer.dataProvider().fieldNameIndex('layer')
# coral # WCMC coral: "LAYER_NAME" = 'CRR'
layer.selectByExpression('"LAYER_NAME" = \'CRR\' ', 
    QgsVectorLayer.SetSelection)
value = 'Coral reefs'
layer.startEditing()
for feature in layer.getSelectedFeatures():
    layer.changeAttributeValue(feature.id(), index, value)
    current = feature.attributes()[index1]
    layer.changeAttributeValue(feature.id(), index1,  (current if current != NULL else "") + ';' + 'WCMC008_CoralReef2018_Py_v4')

layer.commitChanges()

layer.selectByExpression('"BIOME" = \'Coastal systems\' ',
    QgsVectorLayer.SetSelection)
layer.startEditing()
for feature in layer.getSelectedFeatures():
    current = feature.attributes()[index1]
    layer.changeAttributeValue(feature.id(), index1, (current if current != NULL else "") + ';' )

layer.commitChanges()

# deleteAttributes
layer.dataProvider().deleteAttributes(layer.attributeList()[3:] )
layer.updateFields()


# union seagrUcoral with mangrove

# fix mangroves
mangrove = processing.run("native:fixgeometries", {
    'INPUT': mangrove,
    'OUTPUT' : 'ogr:dbname=\'./tmp_output/timorBiomes.gpkg\' table=\"mangroveFixed\" (geom) sql='
    })['OUTPUT']

mangrove.setName("mangroveFixed")
project.addMapLayer(mangrove)

union2 = processing.run("native:union", {
    'INPUT' : union1,
    'OVERLAY' : mangrove,
    'OUTPUT' : 'ogr:dbname=\'./tmp_output/timorBiomes.gpkg\' table=\"seagrUcoralUmangrove\" (geom) sql='
    })['OUTPUT']
union2.setName("seagrUcoralUmangrove")
union2 = QgsVectorLayer("./tmp_output/timorBiomes.gpkg|layername=seagrUcoralUmangrove", "seagrUcoralUmangrove", "ogr")
if not union2.isValid():
    print("Layer failed to load!")
else:
    project.addMapLayer(union2)

layer = union2
index = layer.dataProvider().fieldNameIndex('BIOME')
index1 = layer.dataProvider().fieldNameIndex('layer')
index2 = layer.dataProvider().fieldNameIndex('layerName')

# mangrove # global mangrove watch: pxlval = 1
layer.selectByExpression('"layerName" = \'GMW_2016_v2\' AND "BIOME" IS NULL', 
    QgsVectorLayer.SetSelection)
value = 'Mangroves'

layer.startEditing()
for feature in layer.getSelectedFeatures():
    layer.changeAttributeValue(feature.id(), index, value)

layer.selectAll()
for feature in layer.getSelectedFeatures():
    layerName = feature.attributes()[index2]
    current = feature.attributes()[index1]
    layer.changeAttributeValue(feature.id(), index1,  (current if current != NULL else ";") + ';' + (layerName if layerName == "GMW_2016_v2" else ""))

layer.commitChanges()

# deleteAttributes
layer.dataProvider().deleteAttributes(layer.attributeList()[3:] )
layer.updateFields()

# TLS_EEZ_land fix geom
TLS_Fixed = processing.run("native:fixgeometries", {
    'INPUT': TLS_EEZ_land,
    'OUTPUT' : 'ogr:dbname=\'./tmp_output/timorBiomes.gpkg\' table=\"TLS_EEZ_landFixed\" (geom) sql='
    })['OUTPUT']
TLS_Fixed.setName("TLS_Fixed")
TLS_Fixed = QgsVectorLayer("./tmp_output/timorBiomes.gpkg|layername=TLS_EEZ_landFixed","TLS_Fixed","ogr")
if not TLS_Fixed.isValid():
    print("Layer failed to load!")
else:
    project.addMapLayer(TLS_Fixed)

############# what about clipping CHunionLCbiomes to CH (but first dissolve and fill holes)
CHdissolved = processing.run("native:dissolve", {
    'INPUT' : timorCH,
    'OUTPUT' : 'ogr:dbname=\'./tmp_output/timorBiomes.gpkg\' table=\"CHdissolved\" (geom) sql='
    })['OUTPUT']
CHdissolved.setName("CHdissolved")
CHdissolved = QgsVectorLayer("./tmp_output/timorBiomes.gpkg|layername=CHdissolved", "CHdissolved", "ogr")
if not CHdissolved.isValid():
    print("Layer failed to load!")
else:
    project.addMapLayer(CHdissolved)

# delete holes
CHdissFilled = processing.run("native:deleteholes", {
    'INPUT' : CHdissolved,
    'MIN_AREA' : 0,
    'OUTPUT' : 'ogr:dbname=\'./tmp_output/timorBiomes.gpkg\' table=\"CHdissFilled\" (geom) sql='
    })['OUTPUT']
CHdissFilled.setName("CHdissFilled")
CHdissFilled = QgsVectorLayer("./tmp_output/timorBiomes.gpkg|layername=CHdissFilled", "CHdissFilled", "ogr")
if not CHdissFilled.isValid():
    print("Layer failed to load!")
else:
    project.addMapLayer(CHdissFilled)

# edit 2021/01/29 try to snap geometries and then fix them
# multipart to single parts
landSP = processing.run("native:multiparttosingleparts", {
    'INPUT' : timorCHedit,
    'OUTPUT' : 'ogr:dbname=\'./tmp_output/timorBiomes.gpkg\' table=\"CHunionLCbiomeSP\" (geom) sql='
    })['OUTPUT']
landSP.setName("landSP")
project.addMapLayer(landSP)
#####
# land biomes fix geom
landFix = processing.run("native:fixgeometries", {
    'INPUT': landSP,
    'OUTPUT' : 'ogr:dbname=\'./tmp_output/timorBiomes.gpkg\' table=\"CHunionLCbiomeFixed\" (geom) sql='
    })['OUTPUT']
project.addMapLayer(landFix)
landFix.setName("CHunionLCbiomeFixed")

# clip
landClipped = processing.run('native:clip', {
    'INPUT': landFix,
    'OVERLAY' : CHdissFilled,
    'OUTPUT': 'ogr:dbname=\'./tmp_output/timorBiomes.gpkg\' table=\"CHunionLCbiomeClip\" (geom) sql='
    })['OUTPUT']
project.addMapLayer(landClipped)
landClipped.setName("CHunionLCbiomeClip")
####
# delete polygons $area < 10
# extract by expression
landExtract = processing.run("native:extractbyexpression", {
    'INPUT' : landClipped,
    'EXPRESSION' : '$area >= 10',
    'OUTPUT' : 'ogr:dbname=\'./tmp_output/timorBiomes.gpkg\' table=\"CHunionLCbiomeExtract\" (geom) sql='
    })['OUTPUT']
landExtract.setName("landExtract")
project.addMapLayer(landExtract)
####
## snap at 0.00005 (~5m)
#landSnap = processing.run("qgis:snapgeometries", {
#    'INPUT': landExtract,
#    'REFERENCE_LAYER' : landExtract,
#    'TOLERANCE' : 0.00005,
#    'BEHAVIOR' : 0,
#    'OUTPUT' : 'ogr:dbname=\'./tmp_output/timorBiomes.gpkg\' table=\"CHunionLCbiomeSnap\" (geom) sql='
#    })['OUTPUT']
#project.addMapLayer(landSnap)
#landSnap.setName("CHunionLCbiomeSnap")
## after snapping, I have again very small polygons
## delete polygons $area < 10
## extract by expression
#landExtract1 = processing.run("native:extractbyexpression", {
#    'INPUT' : landSnap,
#    'EXPRESSION' : '$area >= 10',
#    'OUTPUT' : 'ogr:dbname=\'./tmp_output/timorBiomes.gpkg\' table=\"CHunionLCbiomeExtract1\" (geom) sql='
#    })['OUTPUT']
#landExtract1.setName("landExtract1")
#project.addMapLayer(landExtract1)
#
################3
##
# edit 2021/01/28: manually delete seagrass polygon from global dataset.

#########
# union land with seagrUcoralUmangrove and set BIOME to BIOME_2
union3 = processing.run("native:union", {
    'INPUT' : union2,
    'OVERLAY' : landExtract,
    'OUTPUT' : 'ogr:dbname=\'./tmp_output/timorBiomes.gpkg\' table=\"seagrUcoralUmangroveUland\" (geom) sql='
    })['OUTPUT']

union3.setName("seagrUcoralUmangroveUland")
union3 = QgsVectorLayer("./tmp_output/timorBiomes.gpkg|layername=seagrUcoralUmangroveUland", "seagrUcoralUmangroveUland", "ogr")

if not union3.isValid():
    print("Layer failed to load!")
else:
    project.addMapLayer(union3)

###
layer = union3
index = layer.dataProvider().fieldNameIndex('BIOME')
index1 = layer.dataProvider().fieldNameIndex('BIOME_2')
index2 = layer.dataProvider().fieldNameIndex('layer')

# assign BIOME_2 to BIOME IS NULL
layer.startEditing()
layer.selectByExpression('NOT("BIOME_2" IS NULL) AND "BIOME" IS NULL', 
    QgsVectorLayer.SetSelection)

for feature in layer.getSelectedFeatures():
    value = feature.attributes()[index1]
    v = layer.changeAttributeValue(feature.id(), index, value)

layer.selectAll()
for feature in layer.getSelectedFeatures():
    biome2 = feature.attributes()[index1]
    current = feature.attributes()[index2]
    v = layer.changeAttributeValue(feature.id(), index2,  
        (current if current != NULL else ";;") + ';' + ("landCover" if biome2 != QVariant(NULL) else ""))

layer.commitChanges()
#######

############
# deleteAttributes
layer.dataProvider().deleteAttributes( [3,4,5,7,9] )
layer.updateFields()
######

# union land with seagrUcoralUmangrove and set BIOME to Open sea/ocean
# since there are some topological errors, try doing a union betwen CHdissFilled and seagrUcoralUmagrove, then do the diff, then merge
# difference between TLS_EEZ_land and biomes
tmp = processing.run("native:difference", {
    'INPUT' : TLS_Fixed,
    'OVERLAY' : CHdissFilled, # use dissolved biomes for quicker computation
    'OUTPUT' : "memory:"
    })['OUTPUT']
tmp1 = processing.run("native:multiparttosingleparts", {
    'INPUT' : tmp,
    'OUTPUT' : "memory:"
    })['OUTPUT']
tmp2 = processing.run("native:extractbyexpression", {
    'INPUT' : tmp1,
    'EXPRESSION' : "$area > 1e9",
    'OUTPUT' : 'ogr:dbname=\'./tmp_output/timorBiomes.gpkg\' table=\"TLS_EEZ\" (geom) sql='
    })['OUTPUT']


# difference between TLS_EEZ and seagrUcoralUmangrove
oo = processing.run("native:difference", {
    'INPUT' : tmp2,
    'OVERLAY' : union2, # seagrUcoralUmangrove
    'OUTPUT': 'ogr:dbname=\'./tmp_output/timorBiomes.gpkg\' table=\"openOcean\" (geom) sql='
    })['OUTPUT']
oo.setName("openOcean")
# oo = QgsVectorLayer()    
if not oo.isValid():
    print("Layer failed to load!")
else:
    project.addMapLayer(oo)

# set attributes so that they match union3
oo.dataProvider().deleteAttributes( oo.attributeList()[1:] )
oo.dataProvider().addAttributes(
    [QgsField("layer", QVariant.String),
    QgsField("BIOME", QVariant.String),
    QgsField("class_name", QVariant.String),
    QgsField("LU_CLASS", QVariant.String)])
oo.updateFields()
oo.startEditing()
oo.selectAll()
for feature in oo.getSelectedFeatures():
    v = oo.changeAttributeValue(feature.id(), 1, ";;;;EEZ")
    v = oo.changeAttributeValue(feature.id(), 2, "Open sea/ocean")

oo.commitChanges()
# merge
merge1 = processing.run("native:mergevectorlayers", {
    'LAYERS' : [union3, oo],
    'OUTPUT': 'ogr:dbname=\'./tmp_output/timorBiomes.gpkg\' table=\"seagrUcoralUmangroveMoo\" (geom) sql='
    })['OUTPUT']
merge1 = QgsVectorLayer("./tmp_output/timorBiomes.gpkg|layername=seagrUcoralUmangroveMoo", "seagrUcoralUmangroveUlandMoo", "ogr")
merge1.setName("seagrUcoralUmangroveUlandMoo")

if not merge1.isValid():
    print("Layer failed to load!")
else:
    project.addMapLayer(merge1)

merge1.dataProvider().deleteAttributes([merge1.attributeList()[-1]])
merge1.updateFields()

# correct mangrove value
index = merge1.dataProvider().fieldNameIndex('BIOME')
merge1.selectByExpression('"BIOME" = \'Mangrove\'')
merge1.startEditing()
for feature in merge1.getSelectedFeatures() :
    v = merge1.changeAttributeValue(feature.id(), index, "Mangroves")

merge1.commitChanges()

# snap to grid
snapped = processing.run("native:snappointstogrid", {
    'HSPACING' : 1e-06, 
    'INPUT' : merge1,
    'MSPACING' : 0,
    'OUTPUT' : 'TEMPORARY_OUTPUT',
    'VSPACING' : 1e-06,
    'ZSPACING' : 0
    })['OUTPUT']

fixed = processing.run("native:fixgeometries", {
    'INPUT' : snapped,
    'OUTPUT' : 'ogr:dbname=\'./tmp_output/timorBiomes.gpkg\' table=\"final\" (geom) sql='
    })['OUTPUT']

# save as final output
from pathlib import Path
Path("./output").mkdir(parents=True, exist_ok=True)

save_options = QgsVectorFileWriter.SaveVectorOptions()
save_options.driverName = "ESRI Shapefile"
save_options.fileEncoding = "UTF-8"
transform_context = QgsProject.instance().transformContext()
error = QgsVectorFileWriter.writeAsVectorFormatV2(fixed,
                                                  "./output/timorBiomes",
                                                  transform_context,
                                                  save_options)
if error[0] == QgsVectorFileWriter.NoError:
    print("success again!")
else:
  print(error)

## union with WDPA
wdpa = QgsVectorLayer("../data/TimorLeste/WDPA_WDOECM_TLS_shp/WDPA_WDOECM_TLS_shp-polygons.gpkg|layername=WDPA_WDOECM_TLS_shp-polygons", "WDPA", "ogr")
tlsBiomesUpa = processing.run("native:union", {
    'INPUT' : fixed,
    'OVERLAY' : wdpa,
    'OUTPUT' : 'ogr:dbname=\'./tmp_output/timorBiomes.gpkg\' table=\"biomesUwdpa\" (geom) sql='
    })['OUTPUT']
tlsBiomesUpa.setName("biomesUwdpa")
project.addMapLayer(tlsBiomesUpa)
# add attribute $area
# done manually.
# export to shp (can't open the gpkg in R???)
error = QgsVectorFileWriter.writeAsVectorFormatV2(tlsBiomesUpa,
                                                  "./output/timorBiomesUwdpa",
                                                  transform_context,
                                                  save_options)
if error[0] == QgsVectorFileWriter.NoError:
    print("success again!")
else:
  print(error)
# export attribute table as csv manually