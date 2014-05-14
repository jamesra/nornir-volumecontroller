'''
Created on Apr 15, 2014

@author: u0490822
'''
import os
import unittest

import nornir_imageregistration
import nornir_volumecontroller
import nornir_volumemodel
import test.test_base

import nornir_volumecontroller.spatial

from nornir_imageregistration import iBox


class Test(test.test_base.PlatformTest):

    @property
    def VolumePath(self):
        return "IDocBuildTest"

    @property
    def Platform(self):
        return "IDOC"

    def CheckChannelList(self, volumeController, ExpectedChannels):
        self.assertEqual(volumeController.Channels, ExpectedChannels, "Channel list does not match")

    def setUp(self):
        test.test_base.PlatformTest.setUp(self)

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