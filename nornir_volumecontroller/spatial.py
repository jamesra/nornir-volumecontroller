import nornir_imageregistration
import nornir_volumecontroller


def BuildSectionChannelMap(section):
    """Build a mapping from channel name to :class:`VolumeRegisteredChannel` for one section.

    Only channels that have a ``ChannelToVolume`` transform are included.

    :param section: A :class:`~nornir_volumemodel.model.section.Section` model object.
    :returns: ``{channel_name: VolumeRegisteredChannel}``
    :rtype: dict
    """

    SectionToChannelTransforms = {}

    for channel in section.Channels:
        if 'ChannelToVolume' in channel.Transforms:
            SectionToChannelTransforms[channel.Name] = nornir_volumecontroller.base_objects.VolumeRegisteredChannel(channel)

    return SectionToChannelTransforms


def BuildVolumeTransformMap(volume):
    """Build a two-level map from section number → channel name → :class:`VolumeRegisteredChannel`.

    Only sections that contain at least one channel with a ``ChannelToVolume`` transform are
    included.

    :param volume: A :class:`~nornir_volumemodel.model.volume.Volume` model object.
    :returns: ``{section_number: {channel_name: VolumeRegisteredChannel}}``
    :rtype: dict
    """

    Sections = {}

    for block in volume.Blocks:
        for section in block.Sections:
            ChannelToVolumeMapping = BuildSectionChannelMap(section)
            if len(ChannelToVolumeMapping.keys()) > 0:
                Sections[section.Number] = ChannelToVolumeMapping

    return Sections


def SectionsInBoundingBox(boundingbox):
    """Yield every integer section number whose Z-coordinate falls within *boundingbox*.

    :param boundingbox: A bounding-box object with a ``BoundingBox`` attribute indexed
        by :data:`nornir_imageregistration.iBox` constants.
    :yields: int — section numbers from ``MinZ`` to ``MaxZ`` inclusive.
    """
    StartSection = boundingbox.BoundingBox[nornir_imageregistration.iBox.MinZ]
    EndSection = boundingbox.BoundingBox[nornir_imageregistration.iBox.MaxZ]

    for sectionNumber in range(int(StartSection), int(EndSection) + 1):
        yield sectionNumber
