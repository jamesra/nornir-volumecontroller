import nornir_volumecontroller
import nornir_volumexml
import nornir_imageregistration

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
                            boundsXY[nornir_imageregistration.spatial.iRect.MinY],
                            boundsXY[nornir_imageregistration.spatial.iRect.MinX],
                            maxZ,
                            boundsXY[nornir_imageregistration.spatial.iRect.MaxY],
                            boundsXY[nornir_imageregistration.spatial.iRect.MaxX]]
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

    def GetData(self, region, resolution, channel_names):
        '''Return data for the specified region
           :param ndarray region: (minZ, minY, minX, maxZ, maxY, maxX)
           :param float resolution: resolution of output data
           :param list channels: channels to include in output
           :returns: list of ndarray images
        '''
        boundingbox = nornir_imageregistration.BoundingBox.CreateFromBounds(region)
        StartSection = region[nornir_imageregistration.iBox.MinZ]
        EndSection = region[nornir_imageregistration.iBox.MaxZ]

        rect = boundingbox.RectangleXY
        images = [] 
        for sectionNumber in range(StartSection, EndSection):
            if sectionNumber in self.transform_path_map:
                channelmap = self.transform_path_map[sectionNumber]
                
                mosaic_files = GetChannels(channelmap, channel_names)
                
                for mosaic_file in mosaic_files:
                    mosaic = nornir_imageregistration.Mosaic.LoadFromMosaicFile(mosaic_file)
                    mosaic.AssembleTiles(tilesPath, rect, usecluster=True)
                    

        pass

    ##########Non interface methods##############
    
    def MatchingSectionChannels(self, section):
        for section, channelmap in self.transform_path_map.items():
            

    def Calculate2DBoundingBox(self):
        transforms = []
        for t in self._TransformPaths(channelname=None):
            transform = nornir_imageregistration.Mosaic.LoadFromMosaicFile(t)
            transforms.append(transform)

        return nornir_imageregistration.transforms.utils.FixedBoundingBox(transforms)

    def _TransformPaths(self, channelname=None):
        '''Return all transforms matching the channelname, or all transforms if channelname is None'''

        transform_paths = []
        for section, channelmap in self.transform_path_map.items():
            channel = GetChannels(channelmap, channelname)
            if channel:
                yield channel

        return

def GetChannels(channelmap, channelname):
    if channelname:
        if not channelname in channelmap:
            return None
        return channelmap[channelname]
    else:
        for channel in channelmap.values():
            return channel