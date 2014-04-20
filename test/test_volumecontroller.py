'''
Created on Apr 15, 2014

@author: u0490822
'''
import os
import unittest

import nornir_volumecontroller
import nornir_volumexml
import test.test_base

import nornir_volumecontroller.spatial


class Test(test.test_base.PlatformTest):

    @property
    def VolumePath(self):
        return "IDocAlignTest"

    @property
    def Platform(self):
        return "IDOC"

    def CheckChannelList(self, volumeController, ExpectedChannels):
        self.assertEqual(volumeController.Channels, ExpectedChannels, "Channel list does not match")

    def test_Load(self):

        VolumeXML = os.path.join(self.ImportedDataPath, 'VolumeData.xml')

        volumeModel = nornir_volumexml.Load_Xml(VolumeXML)
        self.assertIsNotNone(volumeModel)

        volumeController = nornir_volumecontroller.CreateVolumeController(volumeModel)
        self.assertIsNotNone(volumeController)

        self.CheckChannelList(volumeController, set(['Registered_TEM', 'TEM']))

        SectionChannelToVolumeMap = nornir_volumecontroller.spatial.BuildVolumeTransformMap(volumeModel)
        self.assertIsNotNone(SectionChannelToVolumeMap)

        print(str(volumeController.Bounds))

if __name__ == "__main__":
    # import sys;sys.argv = ['', 'Test.testName']
    unittest.main()