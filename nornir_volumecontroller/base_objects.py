import nornir_volumecontroller
import nornir_volumemodel
import nornir_imageregistration

from . import spatial


class VolumeInterface(object):

    @property
    def Bounds(self):
        '''Bounding box of the entire volume'''
        raise NotImplemented("Abstract base class")

    @property
    def Channels(self):
        '''List of all channels available in the volume'''
        raise NotImplemented("Abstract base class")

    def GetData(self, region, resolution, channels):
        '''Get the raw data inside the boundaries
        :param box region: Data within the region is returned
        :param ndarray resolution: The resolution to return data in
        :param list channels: List of channels to assign to the output array
        :returns: 4D Matrix with Channel,Z,Y,X axes 
        :rtype: ndarray
        '''
        raise NotImplemented("Abstract base class")


class Volume(VolumeInterface):
    '''Interface for a volume'''

    @property
    def Bounds(self):
        '''Bounding box of the entire volume
        :return: (minZ, minY, minX, maxZ, maxY, maxX)'''
        if self._bounds is None:
            boundsXY = self.Calculate2DBoundingBox()
            minZ = min(self.transform_path_map.keys())
            maxZ = max(self.transform_path_map.keys())

            self._bounds = [minZ,
                            boundsXY[nornir_imageregistration.iRect.MinY],
                            boundsXY[nornir_imageregistration.iRect.MinX],
                            maxZ,
                            boundsXY[nornir_imageregistration.iRect.MaxY],
                            boundsXY[nornir_imageregistration.iRect.MaxX]]
        return self._bounds

    @property
    def Name(self):
        return self._volume.Name

    @Name.setter
    def Name(self, val):
        self._volume.Name = val

    @property
    def Channels(self):
        '''List of all channels in the volume'''
        if self._channels is None:
            self._channels = self._BuildVolumeChannelList()

        return self._channels

    @property
    def transform_path_map(self):
        if self._transform_path_map is None:
            self._transform_path_map = nornir_volumecontroller.spatial.BuildVolumeTransformMap(self._volume)

        return self._transform_path_map

    def __init__(self, volumeModel=None):

        self._volume = volumeModel
        self._channels = None

        self._transform_path_map = None
        self._transform_map = None
        self._bounds = None

    def _BuildVolumeChannelList(self):

        channelList = []

        for block in self._volume.Blocks:
            for section in block.Sections:
                for channel in section.Channels:
                    channelList.append(channel.Name)

        channelList.sort()
        # Set restricts itself to unique values
        return set(channelList)


    def _KnownSectionNumbersInBoundingBox(self, boundingbox):
        for sectionNumber in nornir_volumecontroller.spatial.SectionsInBoundingBox(boundingbox):
            if sectionNumber in self.transform_path_map:
                yield sectionNumber

        return


    def GetHighestResolution(self, region=None, channel_names=None):
        '''Return the highest resolution of data within the bounding box'''

        ScaleObj = nornir_volumemodel.model.Scale()
        if region is None:
            region = self.Bounds

        boundingbox = nornir_imageregistration.BoundingBox.CreateFromBounds(region)
        for sectionNumber in self._KnownSectionNumbersInBoundingBox(boundingbox):
            channelmap = self.transform_path_map[sectionNumber]
            vol_registered_channel = GetChannels(channelmap, channel_names)
            for channel in vol_registered_channel:
                ScaleObj = Scale.MinAxisScales(ScaleObj, channel.Scale)

        return Scale(ScaleObj)


    def GetData(self, region, resolution, channel_names):
        '''Return data for the specified region
           :param ndarray region: (minZ, minY, minX, maxZ, maxY, maxX)
           :param float resolution: resolution of output data
           :param list channels: channels to include in output
           :returns: list of ndarray images
        '''
        boundingbox = nornir_imageregistration.BoundingBox.CreateFromBounds(region)
        rect = boundingbox.RectangleXY
        images = {}
        if channel_names is None:
            channel_names = GetChannels(channelmap, channel_names)

        for sectionNumber in self._KnownSectionNumbersInBoundingBox(boundingbox):
            channelmap = self.transform_path_map[sectionNumber]
            vol_registered_channels = GetChannels(channelmap, channel_names)

            for channel in vol_registered_channels:
                mosaic = nornir_imageregistration.Mosaic.LoadFromMosaicFile(channel.Transform.FullPath)
                downsample = resolution / channel.Scale.X.UnitsPerPixel
                tilesPath = channel.GetTilesPath(filtername='Leveled', level=int(downsample))
                [image, mask] = mosaic.AssembleTiles(tilesPath, FixedRegion=rect.ToArray(), usecluster=True)
                # TODO: Scale the image to the requested size
                images[sectionNumber] = image

        return images

    ##########Non interface methods##############
#
#     def MatchingSectionChannels(self, section):
#         for section, channelmap in self.transform_path_map.items():
#


    def Calculate2DBoundingBox(self):
        transforms = []
        for vol_registered_channel in self._MatchingChannels(channelname=None):
            transform_fullpath = vol_registered_channel.Transform.FullPath
            transform = nornir_imageregistration.Mosaic.LoadFromMosaicFile(transform_fullpath)
            transforms.append(transform)

        return nornir_imageregistration.transforms.utils.FixedBoundingBox(transforms)

    def _MatchingChannels(self, channelname=None):
        '''Return all transforms matching the channelname, or all transforms if channelname is None'''

        transform_paths = []
        for section, channelmap in self.transform_path_map.items():
            for channel in GetChannels(channelmap, channelname):
                yield channel

        return


class VolumeRegisteredChannel(object):

    @property
    def Name(self):
        return self._channelModel.Name

    @property
    def Transform(self):
        return self._transform

    @property
    def Scale(self):
        return self._channelModel.Scale

    def GetTilesPath(self, filtername, level):
        filterObj = self._channelModel.Filters[filtername]
        level = filterObj.TilePyramid.Levels.get(level, None)
        if level is None:
            raise Exception("Missing level " + str(level))

        return level.FullPath


    def __init__(self, channelModel=None):

        self._channelModel = channelModel
        self._transform = VolumeRegisteredChannel._FindTransform(channelModel, transformName=None)


        if self._transform is None:
            raise Exception('No channel to volume transform found')

    @classmethod
    def _FindTransform(cls, channelModel, transformName=None):
        if transformName is None:
            transformName = 'ChannelToVolume'

        return channelModel.Transforms.get(transformName, None)


class Scale(object):
    @property
    def X(self):
        return self._scale_model.X.UnitsPerPixel

    @property
    def Y(self):
        return self._scale_model.Y.UnitsPerPixel

    @property
    def Z(self):
        return self._scale_model.Z.UnitsPerPixel

    def __init__(self, scale_model=None):
        if scale_model is None:
            self._scale_model = Scale()
        else:
            self._scale_model = scale_model

    def __str__(self, *args, **kwargs):
        out_str = ""
        for axis_name in self._scale_model.AxisNames:
            axis_data = self._scale_model.GetAxis(axis_name)
            out_str += " %s : %g %s " % (axis_name, axis_data.UnitsPerPixel, axis_data.UnitsOfMeasure)

        return out_str


    @classmethod
    def MinAxisScales(self, scale_model_A, scale_model_B):
        '''Given two scale models, return a scale object describing the highest resolution available for each axis'''

        axis_list = list(scale_model_A.AxisNames)
        axis_list.extend(scale_model_B.AxisNames)

        output_scale_model = nornir_volumemodel.Scale()

        # use the unique axis names
        axis_name_set = set(axis_list)

        for axis_name in axis_name_set:
            A = scale_model_A.GetAxis(axis_name)
            B = scale_model_B.GetAxis(axis_name)

            if A is None and B is None:
                raise Exception("Could not find expected scale: %s" % axis_name)
            elif A and B:
                MinUnitsPerPixel = min(A.UnitsPerPixel, B.UnitsPerPixel)

                if A.UnitsOfMeasure != B.UnitsOfMeasure:
                    raise Exception("No support for different units of measure in scales yet")

                output_scale_model.SetAxis(axis_name, MinUnitsPerPixel, A.UnitsOfMeasure)
            elif A:
                output_scale_model.SetAxis(axis_name, A.UnitsPerPixel, A.UnitsOfMeasure)
            elif B:
                output_scale_model.SetAxis(axis_name, B.UnitsPerPixel, B.UnitsOfMeasure)

        return output_scale_model


def GetChannels(channelmap, channelnames):
    if channelnames:
        for channel_name in channelnames:
            if channel_name in channelmap:
                yield channelmap[channel_name]
    else:
        for channel in channelmap.values():
            yield channel
