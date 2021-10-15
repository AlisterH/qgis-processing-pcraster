# -*- coding: utf-8 -*-

"""
***************************************************************************
*                                                                         *
*   This program is free software; you can redistribute it and/or modify  *
*   it under the terms of the GNU General Public License as published by  *
*   the Free Software Foundation; either version 2 of the License, or     *
*   (at your option) any later version.                                   *
*                                                                         *
***************************************************************************
"""

from qgis.core import (QgsProcessingParameterRasterDestination,
                       QgsProcessingParameterRasterLayer,
                       QgsProcessingException)

from pcraster_tools.processing.algorithm import PCRasterAlgorithm
from osgeo import gdal

class PCRasterSlopeAlgorithm(PCRasterAlgorithm):
    """
    Slope of cells using a digital elevation model
    """

    INPUT_DEM = 'INPUT'
    OUTPUT_SLOPE = 'OUTPUT'

    def createInstance(self):  # pylint: disable=missing-function-docstring
        return PCRasterSlopeAlgorithm()

    def name(self):  # pylint: disable=missing-function-docstring
        return 'Slope'

    def displayName(self):  # pylint: disable=missing-function-docstring
        return self.tr('slope')

    def group(self):  # pylint: disable=missing-function-docstring
        return self.tr('Derivatives of digital elevation models')

    def groupId(self):  # pylint: disable=missing-function-docstring
        return 'demderivatives'

    def shortHelpString(self):  # pylint: disable=missing-function-docstring
        return self.tr(
            """Slope of cells using a digital elevation model

            <a href="https://pcraster.geo.uu.nl/pcraster/4.3.1/documentation/pcraster_manual/sphinx/op_slope.html">PCRaster documentation</a>

            Parameters:

            * <b>Input DEM</b> (required) - scalar raster layer
            * <b>Output slope raster</b> (required) - scalar raster with slope in fraction
            """
        )

    def initAlgorithm(self, config=None):  # pylint: disable=missing-function-docstring,unused-argument
        # We add the input DEM.
        self.addParameter(
            QgsProcessingParameterRasterLayer(
                self.INPUT_DEM,
                self.tr('DEM layer')
            )
        )

        self.addParameter(
            QgsProcessingParameterRasterDestination(
                self.OUTPUT_SLOPE,
                self.tr('Slope layer'),
            )
        )

    def processAlgorithm(self, parameters, context, feedback):  # pylint: disable=missing-function-docstring,unused-argument,too-many-locals
        try:
            from pcraster import (   # pylint: disable=import-outside-toplevel
                setclone,
                readmap,
                report,
                slope
            )
        except ImportError as e:
            raise QgsProcessingException('PCRaster library is not available') from e

        input_dem = self.parameterAsRasterLayer(parameters, self.INPUT_DEM, context)
        RasterLayer = gdal.Open(input_dem.dataProvider().dataSourceUri())
        rows = RasterLayer.RasterYSize
        columns = RasterLayer.RasterXSize
        properties = RasterLayer.GetGeoTransform()
        cellsize = properties[1]
        ULX = properties[0]
        ULY = properties[3]

        setclone(rows, columns, cellsize, ULX, ULY)
        DEM = readmap(input_dem.dataProvider().dataSourceUri())
        slopeMap = slope(DEM)
        outputFilePath = self.parameterAsOutputLayer(parameters, self.OUTPUT_SLOPE, context)

        report(slopeMap, outputFilePath)

        self.set_output_crs(output_file=outputFilePath, crs=input_dem.crs(), feedback=feedback, context=context)

        return {self.OUTPUT_SLOPE: outputFilePath}
