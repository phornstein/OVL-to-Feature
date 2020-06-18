# -*- coding: utf-8 -*-

import xml.etree.ElementTree as ET
import arcpy
import os

class Toolbox(object):
    def __init__(self):
        """Define the toolbox (the name of the toolbox is the name of the
        .pyt file)."""
        self.label = "OVL Tools"
        self.alias = ""

        # List of tool classes associated with this toolbox
        self.tools = [OVLtoFeature, BatchOVLtoFeature]


class OVLtoFeature(object):
    def __init__(self):
        """Define the tool (tool name is the name of the class)."""
        self.label = "OVL to Feature"
        self.description = "OVL to Feature converts an OVL file from CPOF, C2PC, GCCS or similar system and converts it to a series of Feature Class for Point, Line, and Polygons."
        self.canRunInBackground = False

    def getParameterInfo(self):
        """Define parameter definitions"""
        ovl_file = arcpy.Parameter(
            displayName="OVL File",
            name="ovl_file",
            datatype="DEFile",
            parameterType="Required",
            direction="Input"
        )

        output_features = arcpy.Parameter(
            displayName="Output Features",
            name="output_features",
            datatype="DEFeatureClass",
            parameterType="Required",
            direction="Output"
        )

        output_points = arcpy.Parameter(
            displayName="Output Points",
            name="output_points",
            datatype="DEFeatureClass",
            parameterType="Required",
            direction="Output"
        )

        output_lines = arcpy.Parameter(
            displayName="Output Lines",
            name="output_lines",
            datatype="DEFeatureClass",
            parameterType="Required",
            direction="Output"
        )

        output_poly = arcpy.Parameter(
            displayName="Output Polygons",
            name="output_poly",
            datatype="DEFeatureClass",
            parameterType="Required",
            direction="Output"
        )

        ovl_file.filter.list = ['ovl']

        params = [ovl_file, output_features, output_points, output_lines, output_poly]

        return params

    def isLicensed(self):
        """Set whether tool is licensed to execute."""
        return True

    def updateParameters(self, parameters):
        """Modify the values and properties of parameters before internal
        validation is performed.  This method is called whenever a parameter
        has been changed."""
        #return
        parameters[2].enabled = 0
        parameters[3].enabled = 0
        parameters[4].enabled = 0

    def updateMessages(self, parameters):
        """Modify the messages created by internal validation for each tool
        parameter.  This method is called after internal validation."""
        return

    def execute(self, parameters, messages):
        """The source code of the tool."""
        parser = OVLParser()
        result = parser.toFeature(parameters[0].valueAsText,parameters[1].valueAsText)

        arcpy.SetParameter(2, parameters[1].valueAsText + '_points')
        arcpy.SetParameter(3, parameters[1].valueAsText + '_lines')
        arcpy.SetParameter(4, parameters[1].valueAsText + '_polygons')

class BatchOVLtoFeature(object):
    def __init__(self):
        """Define the tool (tool name is the name of the class)."""
        self.label = "Batch OVL to Feature"
        self.description = "Batch OVL to Feature searches a folder for OVL files from CPOF, C2PC, GCCS or similar system and converts it to a series of Feature Class for Point, Line, and Polygons."
        self.canRunInBackground = False

    def getParameterInfo(self):
        """Define parameter definitions"""
        ovl_folder = arcpy.Parameter(
            displayName="OVL Folder",
            name="ovl_file",
            datatype="DEFolder",
            parameterType="Required",
            direction="Input"
        )

        output_features = arcpy.Parameter(
            displayName="Output Features",
            name="output_features",
            datatype="DEFeatureClass",
            parameterType="Required",
            direction="Output"
        )

        output_points = arcpy.Parameter(
            displayName="Output Points",
            name="output_points",
            datatype="DEFeatureClass",
            parameterType="Required",
            direction="Output"
        )

        output_lines = arcpy.Parameter(
            displayName="Output Lines",
            name="output_lines",
            datatype="DEFeatureClass",
            parameterType="Required",
            direction="Output"
        )

        output_poly = arcpy.Parameter(
            displayName="Output Polygons",
            name="output_poly",
            datatype="DEFeatureClass",
            parameterType="Required",
            direction="Output"
        )

        params = [ovl_folder, output_features, output_points, output_lines, output_poly]

        return params

    def isLicensed(self):
        """Set whether tool is licensed to execute."""
        return True

    def updateParameters(self, parameters):
        """Modify the values and properties of parameters before internal
        validation is performed.  This method is called whenever a parameter
        has been changed."""
        #return
        parameters[2].enabled = 0
        parameters[3].enabled = 0
        parameters[4].enabled = 0

    def updateMessages(self, parameters):
        """Modify the messages created by internal validation for each tool
        parameter.  This method is called after internal validation."""
        return

    def execute(self, parameters, messages):
        """The source code of the tool."""
        parser = OVLParser()
        result = parser.batchToFeature(parameters[0].valueAsText,parameters[1].valueAsText)

        arcpy.SetParameter(2, parameters[1].valueAsText + '_points')
        arcpy.SetParameter(3, parameters[1].valueAsText + '_lines')
        arcpy.SetParameter(4, parameters[1].valueAsText + '_polygons')


class OVLParser():

    def __init__(self):
        self.points = []
        self.lines = []
        self.polygons = []
        self.circles = []

    def parsePOSITION(self, obj, output):
            
        pos = obj.findall('POSITION')
        positions = []
        if obj.findall('RADIUS'):
            positions.append(pos[0].text)
            output.append(positions)
            self.circles.append((output,obj.findall('RADIUS')[0].text))
        elif len(pos) == 1:
            positions.append(pos[0].text)
            output.append(positions)
            self.points.append(output)
        elif len(pos) == 2:
            positions.append(pos[0].text)
            positions.append(pos[1].text)
            output.append(positions)
            self.lines.append(output)
        else:
            for p in pos:
                positions.append(p.text)
                output.append(positions)
            self.polygons.append(output)

    def parseMilbobject(self, root):

        milobjects = root.findall('milbobject')

        for obj in milobjects:
            output = []
            output.append(obj.find('NAME').text)
            output.append(obj.find('MIL_ID').text)
            output.append(obj.find('CLOSED').text)
            output.append(None) #add field for CAT_THREAT

            self.parsePOSITION(obj, output)

    def parseCorridor(self, root):

        corridors = root.findall('corridor')

        for cor in corridors:
            output = []
            output.append(None) #name
            output.append(None) #mil_id
            output.append(None) #close
            output.append(None) #add field for CAT_THREAT

            self.parsePOSITION(cor, output)
            
    def parseTacSymbol(self, root):

        tacsymbols = root.findall('tacsymbol')

        for tac in tacsymbols:
            output = []
            output.append(tac.find('NAME').text)
            output.append(tac.find('MIL_ID').text)
            output.append(tac.find('CLOSED').text)
            output.append(None) #add field for CAT_THREAT

            self.parsePOSITION(tac, output)

    def parseUnit(self, root):

        units = root.findall('unit')

        for uni in units:
            output = []
            output.append(uni.find('NAME').text)
            output.append(None) #mil_id
            output.append(None) #closed
            output.append(None) #add field for CAT_THREAT

            self.parsePOSITION(uni, output)            


    def buildPointsFC(self, outputPath):

        pointsfc = arcpy.CreateFeatureclass_management(r'memory','ovl_points','POINT',None,None,None,4326)
        arcpy.AddField_management(pointsfc,'name','TEXT')
        arcpy.AddField_management(pointsfc,'sidc','TEXT')
        arcpy.AddField_management(pointsfc,'closed','TEXT')
        arcpy.AddField_management(pointsfc,'cat_threat','TEXT')

        with arcpy.da.InsertCursor(pointsfc,['name','sidc','closed','cat_threat','SHAPE@XY']) as cursor:
            for obj in self.points:
                ll = obj[4][0].split(' ')
                cursor.insertRow([obj[0],obj[1],obj[2],obj[3],arcpy.Point(ll[1],ll[0])])

        arcpy.CopyFeatures_management(pointsfc, outputPath)
        del pointsfc

    def buildLinesFC(self, outputPath):

        linesfc = arcpy.CreateFeatureclass_management(r'memory','ovl_lines','POLYLINE',None,None,None,4326)
        arcpy.AddField_management(linesfc,'name','TEXT')
        arcpy.AddField_management(linesfc,'sidc','TEXT')
        arcpy.AddField_management(linesfc,'closed','TEXT')
        arcpy.AddField_management(linesfc,'cat_threat','TEXT')

        with arcpy.da.InsertCursor(linesfc,['name','sidc','closed','cat_threat','SHAPE@']) as cursor:
            for obj in self.lines:
                array = arcpy.Array()

                ll = obj[4][0].split(' ')
                array.add(arcpy.Point(ll[1],ll[0]))
                ll = obj[4][1].split(' ')
                array.add(arcpy.Point(ll[1],ll[0]))

                cursor.insertRow([obj[0],obj[1],obj[2],obj[3],arcpy.Polyline(array)])

        arcpy.CopyFeatures_management(linesfc, outputPath)
        del linesfc

    def buildPolyFC(self, outputPath):

        polyfc = arcpy.CreateFeatureclass_management(r'memory','ovl_poly','POLYGON',None,None,None,4326)
        arcpy.AddField_management(polyfc,'name','TEXT')
        arcpy.AddField_management(polyfc,'sidc','TEXT')
        arcpy.AddField_management(polyfc,'closed','TEXT')
        arcpy.AddField_management(polyfc,'cat_threat','TEXT')

        with arcpy.da.InsertCursor(polyfc,['name','sidc','closed','cat_threat','SHAPE@']) as cursor:
            for obj in self.polygons:
                array = arcpy.Array()

                for coord in obj[4]:
                    ll = coord.split(' ')
                    array.add(arcpy.Point(ll[1],ll[0]))

                cursor.insertRow([obj[0],obj[1],obj[2],obj[3],arcpy.Polygon(array)])

        if len(self.circles) > 0:
            mem_circles = arcpy.CreateFeatureclass_management(r'memory','circle_points','POINT',None,None,None,4326)
            arcpy.AddField_management(mem_circles,'name','TEXT')
            arcpy.AddField_management(mem_circles,'sidc','TEXT')
            arcpy.AddField_management(mem_circles,'closed','TEXT')
            arcpy.AddField_management(mem_circles,'cat_threat','TEXT')
            arcpy.AddField_management(mem_circles,'radius','FLOAT')

            with arcpy.da.InsertCursor(mem_circles,['name','sidc','closed','cat_threat','radius','SHAPE@XY']) as cursor:
                for obj in self.circles:
                    ll = obj[0][4][0].split(' ')
                    cursor.insertRow([obj[0][0],obj[0][1],obj[0][2],obj[0][3],float(obj[1])*1852,arcpy.Point(ll[1],ll[0])])
                    #multiply to 1852 to covnert NM to Meters
            
            arcpy.Buffer_analysis(mem_circles,r'memory\buffered_points',"radius")

            arcpy.Merge_management([polyfc, r'memory\buffered_points'], outputPath)
        else:
            arcpy.CopyFeatures_management(polyfc, outputPath)
        del polyfc, mem_circles

    def toFeature(self, path, output_path):
                
        with open(path, 'r') as instream:
            xml = instream.read()

        tree = ET.ElementTree(ET.fromstring(xml))
        root = tree.getroot()

        functions = [self.parseCorridor,self.parseMilbobject,self.parseTacSymbol,self.parseUnit]
        for f in functions:
            try:
                f(root)
            except:
                arcpy.AddWarning('Unable to executre {}...'.format(str(f)))

        if len(self.points) > 0:
            self.buildPointsFC(output_path + '_points')
        if len(self.lines) > 0:
            self.buildLinesFC(output_path +'_lines')
        if len(self.polygons) > 0 or len(self.circles) > 0:
            self.buildPolyFC(output_path + '_polygons') 
    
    def batchToFeature(self, path, output_path):
                
        ovlfiles = [os.path.join(root, name)
             for root, dirs, files in os.walk(path)
             for name in files
             if name.endswith((".ovl"))]

        for file in ovlfiles:
            with open(path, 'r') as instream:
                xml = instream.read()

            tree = ET.ElementTree(ET.fromstring(xml))
            root = tree.getroot()

            functions = [self.parseCorridor,self.parseMilbobject,self.parseTacSymbol,self.parseUnit]
            for f in functions:
                f(root)

        if len(self.points) > 0:
            self.buildPointsFC(output_path + '_points')
        if len(self.lines) > 0:
            self.buildLinesFC(output_path +'_lines')
        if len(self.polygons) > 0:
            self.buildPolyFC(output_path + '_polygons') 