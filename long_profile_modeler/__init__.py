# -*- coding: utf-8 -*-
"""
/***************************************************************************
 LongProfileModeler
                                 A QGIS plugin
 Creates Long Profiles from lsdtt-network-tool outputs
 Generated by Plugin Builder: http://g-sherman.github.io/Qgis-Plugin-Builder/
                             -------------------
        begin                : 2022-08-24
        copyright            : (C) 2022 by Josie Welsh
        email                : welsh162@umn.edu
        git sha              : $Format:%H$
 ***************************************************************************/

/***************************************************************************
 *                                                                         *
 *   This program is free software; you can redistribute it and/or modify  *
 *   it under the terms of the GNU General Public License as published by  *
 *   the Free Software Foundation; either version 2 of the License, or     *
 *   (at your option) any later version.                                   *
 *                                                                         *
 ***************************************************************************/
 This script initializes the plugin, making it known to QGIS.
"""


# noinspection PyPep8Naming
def classFactory(iface):  # pylint: disable=invalid-name
    """Load LongProfileModeler class from file LongProfileModeler.

    :param iface: A QGIS interface instance.
    :type iface: QgsInterface
    """
    #
    from .long_profile_modeler import LongProfileModeler
    return LongProfileModeler(iface)