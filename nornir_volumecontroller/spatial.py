import nornir_imageregistration
import nornir_volumecontroller

def BuildSectionChannelMap(section):

    SectionToChannelTransforms = {}

    for channel in section.Channels:
        if 'ChannelToVolume' in channel.Transforms:
            SectionToChannelTransforms[channel.Name] = nornir_volumecontroller.base_objects.VolumeRegisteredChannel(channel)

    return SectionToChannelTransforms

def BuildVolumeTransformMap(volume):
    '''Returns {SectionNumber : {ChannelName : transform}}'''

    Sections = {}

    for block in volume.Blocks:
        for section in block.Sections:
            ChannelToVolumeMapping = BuildSectionChannelMap(section)
            if len(ChannelToVolumeMapping.keys()) > 0:
                Sections[section.Number] = ChannelToVolumeMapping

    return Sections


def SectionsInBoundingBox(boundingbox):
    StartSection = boundingbox.BoundingBox[nornir_imageregistration.iBox.MinZ]
    EndSection = boundingbox.BoundingBox[nornir_imageregistration.iBox.MaxZ]

    for sectionNumber in range(int(StartSection), int(EndSection)+1):
        yield sectionNumber
