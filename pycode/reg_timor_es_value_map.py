# timor_es_map
import qgis.utils
from qgis.gui import *

import processing
import numpy as np
import os

os.chdir("/Users/Mela/documents/JRC/BIOPAMA/ESS/essvaltls")
project = QgsProject.instance() 
#project.write('timorLC.qgs')
project.setCrs(QgsCoordinateReferenceSystem("EPSG:4326"))

# join timorBiomes with Ecosystem Services Values
# ./output/global_mainESvalue.csv
ESval = QgsVectorLayer(
    #"./output/global_mainESvalue.csv",
    #"Ecosystem Services value","ogr")
     "file:///Users/mela/Documents/JRC/BIOPAMA/ESS/essvaltls/output/regional_mainESvalue.csv?type=csv&trimFields=Yes&detectTypes=Yes&geomType=none&subsetIndex=no&watchFile=no",
     "ES main", 'delimitedtext')
if not ESval.isValid():
    print("Layer failed to load!")
else :
    project.addMapLayer(ESval)

# 
timorBiomes = QgsVectorLayer('./tmp_output/timorBiomes.gpkg|layername=final',
    "Biomes", 'ogr')
if not timorBiomes.isValid():
    print("Layer failed to load!")
else :
    project.addMapLayer(timorBiomes)

# native:joinattributestable
timorBiomesESval = processing.run("native:joinattributestable", {
    'DISCARD_NONMATCHING' : False,
    'FIELD' : 'BIOME',
    'FIELDS_TO_COPY' : [], 
    'FIELD_2' : 'Biome', 
    'INPUT' : timorBiomes, 
    'INPUT_2' : ESval, 
    'METHOD' : 0, 
    'OUTPUT' : 'TEMPORARY_OUTPUT', 
    'PREFIX' : '' 
    })['OUTPUT']

project.addMapLayer(timorBiomesESval)

# background
uri = "url=http://basemaps.cartocdn.com/light_all/%7Bz%7D/%7Bx%7D/%7By%7D.png&zmax=19&zmin=0&type=xyz"
mts_layer=QgsRasterLayer(uri,'Background: CartoDb Positron','wms')
bckgr = project.addMapLayer(mts_layer)

# wdpa
wdpa = QgsVectorLayer("../data/TimorLeste/WDPA_WDOECM_TLS_shp/WDPA_WDOECM_TLS_shp-polygons.gpkg|layername=WDPA_WDOECM_TLS_shp-polygons", "WDPA", "ogr")
wdpa.setName("Protected areas")
project.addMapLayer(wdpa)
renderer = wdpa.renderer() #singleSymbol renderer
symLayer = QgsSimpleFillSymbolLayer.create({ 
    'outline_style': 'solid', 
    'outline_width': '0.5', 
    'outline_width_unit': 'MM', 
    'style': 'no',
    'outline_color': '#333333'})
renderer.symbols(QgsRenderContext())[0].changeSymbolLayer(0,symLayer)
wdpa.setRenderer(renderer)
wdpa.triggerRepaint()
iface.layerTreeView().refreshLayerSymbology(wdpa.id())


# set symbology of Joined layer as gradient of value for different types of services
# total ES value
timorBiomesESval.setName("Total")
myVectorLayer = timorBiomesESval
myTargetField = 'Total'
simpleFillLayer = QgsSimpleFillSymbolLayer.create({ 
    'outline_style': 'no', 
    'outline_width': '0', 
    'outline_width_unit': 'MM', 
    'style': 'solid'})
    
mySymbol = QgsSymbol.defaultSymbol(myVectorLayer.geometryType())
mySymbol.changeSymbolLayer(0, simpleFillLayer)
myColorRamp = QgsGradientColorRamp(QColor('#ffffcc'), QColor('#564135'))#'#253494'))# #490c7b

graduated_renderer = QgsGraduatedSymbolRenderer()
graduated_renderer.setClassAttribute(myTargetField)
graduated_renderer.setSourceSymbol(mySymbol)
graduated_renderer.setSourceColorRamp(myColorRamp)
graduated_renderer.setMode(QgsGraduatedSymbolRenderer.Jenks)
graduated_renderer.updateClasses(myVectorLayer, 5)

myVectorLayer.setRenderer(graduated_renderer)

myVectorLayer.triggerRepaint()
iface.layerTreeView().refreshLayerSymbology(myVectorLayer.id())

# Cultural
# duplicate layer
cul = timorBiomesESval.clone()
cul.setName("Cultural")
project.addMapLayer(cul)
myRenderer = cul.renderer()
myRenderer.setClassAttribute("Cultural")
myColorRamp = QgsGradientColorRamp(QColor('#ffffcc'), QColor('#253494'))
myRenderer.setSourceColorRamp(myColorRamp)
myRenderer.updateClasses(cul, 5)
cul.triggerRepaint()
iface.layerTreeView().refreshLayerSymbology(cul.id())

# Regulating
# duplicate layer
reg = timorBiomesESval.clone()
reg.setName("Regulating")
project.addMapLayer(reg)
myRenderer = reg.renderer()
myRenderer.setClassAttribute("Regulating")
myColorRamp = QgsGradientColorRamp(QColor('#ffffcc'), QColor('#006837'))
myRenderer.setSourceColorRamp(myColorRamp)
myRenderer.updateClasses(reg, 5)
reg.triggerRepaint()
iface.layerTreeView().refreshLayerSymbology(reg.id())

# Provisioning
pro = timorBiomesESval.clone()
pro.setName("Provisioning")
project.addMapLayer(pro)
myRenderer = pro.renderer()
myRenderer.setClassAttribute("Provisioning")
myColorRamp = QgsGradientColorRamp(QColor('#ffffcc'), QColor('#993404'))
myRenderer.setSourceColorRamp(myColorRamp)
myRenderer.updateClasses(pro, 5)
pro.triggerRepaint()
iface.layerTreeView().refreshLayerSymbology(pro.id())

# Total
tot = timorBiomesESval.clone()
tot.setName("All")
project.addMapLayer(tot)

# use for extent# Copernicus Hotspot
timorCH = QgsVectorLayer("../data/TimorLeste/PAC01/01_LCCS_MAPS_v4/PAC01_LCCS_MODULAR_LC_PERIOD_a_2016_VECTOR_v4/PAC01_LCCS_MODULAR_LC_PERIOD_a_2016_VECTOR_v4.shp", 
    "PAC01_LCCS_MODULAR_LC_PERIOD_a_2016_VECTOR_v4", "ogr")

# Set canvas extent
canvas = iface.mapCanvas()

# base print layout
# get a reference to the layout manager
manager = project.layoutManager()
# make a new print layout object
layout = QgsPrintLayout(project)
# needs to call this according to API documentaiton
layout.initializeDefaults()
# set layout page size
pc = layout.pageCollection()
pc.pages()[0].setPageSize('A4', QgsLayoutItemPage.Orientation.Landscape)
# set name
layout.setName('map_es_val_reg')
# add layout to manager
manager.addLayout(layout)

#create a map item to add
itemMap = QgsLayoutItemMap.create(layout)
# lock layers
itemMap.setKeepLayerSet(False)
itemMap.setLayers([wdpa, tot, pro, reg, cul, bckgr])
itemMap.setKeepLayerSet(True)

# add to layout
layout.addLayoutItem(itemMap)
# set size
itemMap.attemptResize(QgsLayoutSize(152, 131, QgsUnitTypes.LayoutMillimeters))
itemMap.attemptMove(QgsLayoutPoint(5,5,QgsUnitTypes.LayoutMillimeters))
itemMap.zoomToExtent(timorBiomesESval.extent())

# add grid linked to map
itemMap.grid().setName("graticule")
itemMap.grid().setEnabled(True)
itemMap.grid().setStyle(QgsLayoutItemMapGrid.FrameAnnotationsOnly)
itemMap.grid().setCrs(QgsCoordinateReferenceSystem("EPSG:4326"))
itemMap.grid().setIntervalX(1)
itemMap.grid().setIntervalY(1)
itemMap.grid().setAnnotationEnabled(True)
itemMap.grid().setFrameStyle(QgsLayoutItemMapGrid.InteriorTicks)
itemMap.grid().setFramePenSize(0.5)
itemMap.grid().setAnnotationFormat(1) # DegreeMinuteSuffix
itemMap.grid().setAnnotationPrecision(0) # integer
#itemMap.grid().setBlendMode(QPainter.CompositionMode_SourceOver) # ?
# fontsize?
itemMap.grid().setAnnotationFont(QFont("Fira Sans", 6))
# 
itemMap.grid().setAnnotationDisplay(QgsLayoutItemMapGrid.HideAll, QgsLayoutItemMapGrid.Right)
itemMap.grid().setAnnotationDisplay(QgsLayoutItemMapGrid.HideAll, QgsLayoutItemMapGrid.Top)
itemMap.grid().setAnnotationPosition(QgsLayoutItemMapGrid.OutsideMapFrame, QgsLayoutItemMapGrid.Bottom)
itemMap.grid().setAnnotationDirection(QgsLayoutItemMapGrid.Horizontal, QgsLayoutItemMapGrid.Bottom)
itemMap.grid().setAnnotationPosition(QgsLayoutItemMapGrid.OutsideMapFrame, QgsLayoutItemMapGrid.Left)
itemMap.grid().setAnnotationDirection(QgsLayoutItemMapGrid.Vertical, QgsLayoutItemMapGrid.Left)

# Legend
itemLegend = QgsLayoutItemLegend.create(layout)
itemLegend.setAutoUpdateModel(False)
itemLegend.setLinkedMap(itemMap)
itemLegend.setLegendFilterByMapEnabled(True)
itemLegend.setTitle("Ecosystem Services Value (2020 USD/ha)")
itemLegend.setWrapString("_n")
itemLegend.setResizeToContents(False)
itemLegend.setStyleFont(QgsLegendStyle.Title, QFont("Fira Sans", 10))
itemLegend.setStyleFont(QgsLegendStyle.Subgroup, QFont("Fira Sans", 10))
itemLegend.setStyleFont(QgsLegendStyle.SymbolLabel, QFont("Fira Sans", 8))
itemLegend.setSymbolWidth(5)
itemLegend.setLineSpacing(0.5)
itemLegend.setColumnCount(4)
itemLegend.setWmsLegendHeight(8)
layout.addLayoutItem(itemLegend)
itemLegend.attemptResize(QgsLayoutSize(155, 64, QgsUnitTypes.LayoutMillimeters))
itemLegend.attemptMove(QgsLayoutPoint(5,141,QgsUnitTypes.LayoutMillimeters))
itemLegend.updateLegend()

# North arrow
itemNorth = QgsLayoutItemPicture.create(layout)
itemNorth.setPicturePath(":/images/north_arrows/layout_default_north_arrow.svg")
itemNorth.setFixedSize(QgsLayoutSize(10,10,QgsUnitTypes.LayoutMillimeters))
itemNorth.attemptMove(QgsLayoutPoint(10,120,QgsUnitTypes.LayoutMillimeters))
layout.addLayoutItem(itemNorth)

# text box
itemLabelAll = QgsLayoutItemLabel.create(layout)
itemLabelAll.setText("All services")
itemLabelAll.setFont(QFont("Fira Sans", 10))
itemLabelAll.setFixedSize(QgsLayoutSize(90,20,QgsUnitTypes.LayoutMillimeters))
itemLabelAll.attemptMove(QgsLayoutPoint(7,7,QgsUnitTypes.LayoutMillimeters))
layout.addLayoutItem(itemLabelAll)

# add small maps
# pro
#create a map item to add
itemMap1 = QgsLayoutItemMap.create(layout)
# lock layers
itemMap1.setKeepLayerSet(False)
itemMap1.setLayers([wdpa, pro, bckgr])
itemMap1.setKeepLayerSet(True)
# add to layout
layout.addLayoutItem(itemMap1)
# set size
itemMap1.attemptResize(QgsLayoutSize(130, 63, QgsUnitTypes.LayoutMillimeters))
itemMap1.attemptMove(QgsLayoutPoint(162,5,QgsUnitTypes.LayoutMillimeters))
itemMap1.zoomToExtent(timorCH.extent())
# text box
itemLabelPro = QgsLayoutItemLabel.create(layout)
itemLabelPro.setText("Provisioning services")
itemLabelPro.setFont(QFont("Fira Sans", 10))
itemLabelPro.setFixedSize(QgsLayoutSize(90,20,QgsUnitTypes.LayoutMillimeters))
itemLabelPro.attemptMove(QgsLayoutPoint(164,7,QgsUnitTypes.LayoutMillimeters))
layout.addLayoutItem(itemLabelPro)
# add grid linked to map
itemMap1.grid().setName("graticule")
itemMap1.grid().setEnabled(True)
itemMap1.grid().setStyle(QgsLayoutItemMapGrid.FrameAnnotationsOnly)
itemMap1.grid().setCrs(QgsCoordinateReferenceSystem("EPSG:4326"))
itemMap1.grid().setIntervalX(1)
itemMap1.grid().setIntervalY(1)
itemMap1.grid().setAnnotationEnabled(True)
itemMap1.grid().setFrameStyle(QgsLayoutItemMapGrid.InteriorTicks)
itemMap1.grid().setFramePenSize(0.5)
itemMap1.grid().setAnnotationFormat(1) # DegreeMinuteSuffix
itemMap1.grid().setAnnotationPrecision(0) # integer
#itemMap.grid().setBlendMode(QPainter.CompositionMode_SourceOver) # ?
# fontsize?
itemMap1.grid().setAnnotationFont(QFont("Fira Sans", 6))
# 
itemMap1.grid().setAnnotationDisplay(QgsLayoutItemMapGrid.HideAll, QgsLayoutItemMapGrid.Right)
itemMap1.grid().setAnnotationDisplay(QgsLayoutItemMapGrid.HideAll, QgsLayoutItemMapGrid.Top)
itemMap1.grid().setAnnotationPosition(QgsLayoutItemMapGrid.OutsideMapFrame, QgsLayoutItemMapGrid.Bottom)
itemMap1.grid().setAnnotationDirection(QgsLayoutItemMapGrid.Horizontal, QgsLayoutItemMapGrid.Bottom)
itemMap1.grid().setAnnotationPosition(QgsLayoutItemMapGrid.OutsideMapFrame, QgsLayoutItemMapGrid.Left)
itemMap1.grid().setAnnotationDirection(QgsLayoutItemMapGrid.Vertical, QgsLayoutItemMapGrid.Left)

# reg
#create a map item to add
itemMap2= QgsLayoutItemMap.create(layout)
# lock layers
itemMap2.setKeepLayerSet(False)
itemMap2.setLayers([wdpa, reg, bckgr])
itemMap2.setKeepLayerSet(True)
# add to layout
layout.addLayoutItem(itemMap2)
# set size
itemMap2.attemptResize(QgsLayoutSize(130, 63, QgsUnitTypes.LayoutMillimeters))
itemMap2.attemptMove(QgsLayoutPoint(162,73,QgsUnitTypes.LayoutMillimeters))
itemMap2.zoomToExtent(timorCH.extent())
# text box
itemLabelReg = QgsLayoutItemLabel.create(layout)
itemLabelReg.setText("Regulating services")
itemLabelReg.setFont(QFont("Fira Sans", 10))
itemLabelReg.setFixedSize(QgsLayoutSize(90,20,QgsUnitTypes.LayoutMillimeters))
itemLabelReg.attemptMove(QgsLayoutPoint(164,75,QgsUnitTypes.LayoutMillimeters))
layout.addLayoutItem(itemLabelReg)
# add grid linked to map
itemMap2.grid().setName("graticule")
itemMap2.grid().setEnabled(True)
itemMap2.grid().setStyle(QgsLayoutItemMapGrid.FrameAnnotationsOnly)
itemMap2.grid().setCrs(QgsCoordinateReferenceSystem("EPSG:4326"))
itemMap2.grid().setIntervalX(1)
itemMap2.grid().setIntervalY(1)
itemMap2.grid().setAnnotationEnabled(True)
itemMap2.grid().setFrameStyle(QgsLayoutItemMapGrid.InteriorTicks)
itemMap2.grid().setFramePenSize(0.5)
itemMap2.grid().setAnnotationFormat(1) # DegreeMinuteSuffix
itemMap2.grid().setAnnotationPrecision(0) # integer
#itemMap.grid().setBlendMode(QPainter.CompositionMode_SourceOver) # ?
# fontsize?
itemMap2.grid().setAnnotationFont(QFont("Fira Sans", 6))
# 
itemMap2.grid().setAnnotationDisplay(QgsLayoutItemMapGrid.HideAll, QgsLayoutItemMapGrid.Right)
itemMap2.grid().setAnnotationDisplay(QgsLayoutItemMapGrid.HideAll, QgsLayoutItemMapGrid.Top)
itemMap2.grid().setAnnotationPosition(QgsLayoutItemMapGrid.OutsideMapFrame, QgsLayoutItemMapGrid.Bottom)
itemMap2.grid().setAnnotationDirection(QgsLayoutItemMapGrid.Horizontal, QgsLayoutItemMapGrid.Bottom)
itemMap2.grid().setAnnotationPosition(QgsLayoutItemMapGrid.OutsideMapFrame, QgsLayoutItemMapGrid.Left)
itemMap2.grid().setAnnotationDirection(QgsLayoutItemMapGrid.Vertical, QgsLayoutItemMapGrid.Left)

# cul
#create a map item to add
itemMap3 = QgsLayoutItemMap.create(layout)
# lock layers
itemMap3.setKeepLayerSet(False)
itemMap3.setLayers([wdpa, cul, bckgr])
itemMap3.setKeepLayerSet(True)
# add to layout
layout.addLayoutItem(itemMap3)
# set size
itemMap3.attemptResize(QgsLayoutSize(130, 64, QgsUnitTypes.LayoutMillimeters))
itemMap3.attemptMove(QgsLayoutPoint(162,141,QgsUnitTypes.LayoutMillimeters))
itemMap3.zoomToExtent(timorCH.extent())
# text box
itemLabelCul = QgsLayoutItemLabel.create(layout)
itemLabelCul.setText("Cultural services")
itemLabelCul.setFont(QFont("Fira Sans", 10))
itemLabelCul.setFixedSize(QgsLayoutSize(90,20,QgsUnitTypes.LayoutMillimeters))
itemLabelCul.attemptMove(QgsLayoutPoint(164,143,QgsUnitTypes.LayoutMillimeters))
layout.addLayoutItem(itemLabelCul)
# add grid linked to map
itemMap3.grid().setName("graticule")
itemMap3.grid().setEnabled(True)
itemMap3.grid().setStyle(QgsLayoutItemMapGrid.FrameAnnotationsOnly)
itemMap3.grid().setCrs(QgsCoordinateReferenceSystem("EPSG:4326"))
itemMap3.grid().setIntervalX(1)
itemMap3.grid().setIntervalY(1)
itemMap3.grid().setAnnotationEnabled(True)
itemMap3.grid().setFrameStyle(QgsLayoutItemMapGrid.InteriorTicks)
itemMap3.grid().setFramePenSize(0.5)
itemMap3.grid().setAnnotationFormat(1) # DegreeMinuteSuffix
itemMap3.grid().setAnnotationPrecision(0) # integer
#itemMap.grid().setBlendMode(QPainter.CompositionMode_SourceOver) # ?
# fontsize?
itemMap3.grid().setAnnotationFont(QFont("Fira Sans", 6))
# 
itemMap3.grid().setAnnotationDisplay(QgsLayoutItemMapGrid.HideAll, QgsLayoutItemMapGrid.Right)
itemMap3.grid().setAnnotationDisplay(QgsLayoutItemMapGrid.HideAll, QgsLayoutItemMapGrid.Top)
itemMap3.grid().setAnnotationPosition(QgsLayoutItemMapGrid.OutsideMapFrame, QgsLayoutItemMapGrid.Bottom)
itemMap3.grid().setAnnotationDirection(QgsLayoutItemMapGrid.Horizontal, QgsLayoutItemMapGrid.Bottom)
itemMap3.grid().setAnnotationPosition(QgsLayoutItemMapGrid.OutsideMapFrame, QgsLayoutItemMapGrid.Left)
itemMap3.grid().setAnnotationDirection(QgsLayoutItemMapGrid.Vertical, QgsLayoutItemMapGrid.Left)

# text box
itemLabel = QgsLayoutItemLabel.create(layout)
itemLabel.setText("Reference Coordinate System: [% @project_crs %] \n\
Data sources: UNEP-WCMC ; Copernicus Hotspot land cover 2016 ; \
Conservation International ; ESVD 2020")
itemLabel.setFont(QFont("Fira Sans", 8))
itemLabel.setFixedSize(QgsLayoutSize(90,20,QgsUnitTypes.LayoutMillimeters))
itemLabel.attemptMove(QgsLayoutPoint(5,195,QgsUnitTypes.LayoutMillimeters))
layout.addLayoutItem(itemLabel)

# BIOPAMA logo
itemLogo = QgsLayoutItemPicture.create(layout)
itemLogo.setPicturePath("/Users/mela/JRCbox/BIOPAMA/DOC/pen_biopama_logo_1.png")
layout.addLayoutItem(itemLogo)
itemLogo.setFixedSize(QgsLayoutSize(25,10,QgsUnitTypes.LayoutMillimeters))
itemLogo.attemptMove(QgsLayoutPoint(132,200,QgsUnitTypes.LayoutMillimeters))
## contact text box
#itemContact = QgsLayoutItemLabel.create(layout)
#itemContact.setText("Contact: melanie.weynants@ec.europa.eu")
##itemContact.adjustSizeToText()
#itemContact.setFixedSize(QgsLayoutSize(100,10,QgsUnitTypes.LayoutMillimeters))
#itemContact.attemptMove(QgsLayoutPoint(220,200,QgsUnitTypes.LayoutMillimeters))
#layout.addLayoutItem(itemContact)

# export general map
# print to png
export = QgsLayoutExporter(layout)
expSett = QgsLayoutExporter.ImageExportSettings()
expSett.dpi = 300
export.exportToImage("./fig/"  + layout.name() + ".png", expSett)
