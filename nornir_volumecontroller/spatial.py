# import nornir_imageregistration


def BuildSectionChannelMap(section):

    SectionToChannelTransforms = {}

    for channel in section.Channels:
        for transform in channel.Transforms:
            if transform.Name == 'ChannelToVolume':
                SectionToChannelTransforms[channel.Name] = transform.FullPath

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