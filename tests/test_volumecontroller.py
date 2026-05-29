'''
Created on Apr 15, 2014

@author: u0490822
'''
import importlib.util
import os
import unittest
from pathlib import Path

import nornir_imageregistration
import nornir_volumecontroller
import nornir_volumemodel

import nornir_volumecontroller.spatial

from nornir_imageregistration import iBox

# Monorepo umbrella: ``import tests.*`` for imageregistration helpers; avoid top-level ``test`` (stdlib).
_spec = importlib.util.spec_from_file_location(
    "nornir_volumecontroller_test_base",
    Path(__file__).resolve().parent / "test_base.py",
)
assert _spec is not None and _spec.loader is not None
_test_base = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_test_base)
PlatformTest = _test_base.PlatformTest


class Test(PlatformTest):

    @property
    def VolumePath(self):
        return "IDocBuildTest"

    @property
    def Platform(self):
        return "IDOC"

    def CheckChannelList(self, volumeController, ExpectedChannels):
        self.assertEqual(volumeController.Channels, ExpectedChannels, "Channel list does not match")

    def setUp(self):
        PlatformTest.setUp(self)

        VolumeXML = os.path.join(self.ImportedDataPath, 'VolumeData.xml')

        self.volumeModel = nornir_volumemodel.Load_Xml(VolumeXML)
        self.assertIsNotNone(self.volumeModel)

        self.volumeController = nornir_volumecontroller.CreateVolumeController(self.volumeModel)
        self.assertIsNotNone(self.volumeController)

    def test_Load(self):

        self.CheckChannelList(self.volumeController, set(['Registered_TEM', 'TEM']))

        SectionChannelToVolumeMap = nornir_volumecontroller.spatial.BuildVolumeTransformMap(self.volumeModel)
        self.assertIsNotNone(SectionChannelToVolumeMap)

    def test_Bounds(self):
        bounds = self.volumeController.Bounds
        self.assertIsNotNone(bounds)

        print(str(bounds))

        max_res_scale = self.volumeController.GetHighestResolution(bounds)
        print(str(max_res_scale))

    def test_ImageServing(self):

        bounds = self.volumeController.Bounds
        self.assertIsNotNone(bounds)

        max_res_scale = self.volumeController.GetHighestResolution(bounds)

        images = self.volumeController.GetData(bounds, max_res_scale.X * 16.0, self.volumeController.Channels)
        self.assertIsNotNone(images)
        nornir_imageregistration.core.ShowGrayscale(images.values())

    def test_SmallHighResRegionImageServing(self):
        bounds = self.volumeController.Bounds
        self.assertIsNotNone(bounds)

        max_res_scale = self.volumeController.GetHighestResolution(bounds)

        smaller_bounds = bounds
        smaller_bounds[iBox.MinX] = bounds[iBox.MaxX] / 2.0
        smaller_bounds[iBox.MinY] = bounds[iBox.MaxY] / 2.0
        smaller_bounds[iBox.MinZ] = bounds[iBox.MinZ]
        smaller_bounds[iBox.MaxX] = smaller_bounds[iBox.MinX] + 1024
        smaller_bounds[iBox.MaxY] = smaller_bounds[iBox.MinY] + 1024
        smaller_bounds[iBox.MaxZ] = bounds[iBox.MinZ] + 1

        images = self.volumeController.GetData(smaller_bounds, max_res_scale.X * 16.0, self.volumeController.Channels)
        self.assertIsNotNone(images)
        nornir_imageregistration.core.ShowGrayscale(images.values())


if __name__ == "__main__":
    # import sys;sys.argv = ['', 'Test.testName']
    unittest.main()