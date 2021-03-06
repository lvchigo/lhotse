from functools import reduce
from itertools import chain
from operator import add
from typing import Iterable, Optional, TypeVar

from lhotse.audio import Recording, RecordingSet
from lhotse.cut import Cut, CutSet, MixedCut
from lhotse.features import FeatureSet, Features
from lhotse.supervision import SupervisionSegment, SupervisionSet
from lhotse.utils import Pathlike, load_yaml

ManifestItem = TypeVar('ManifestItem', Recording, SupervisionSegment, Features, Cut, MixedCut)
Manifest = TypeVar('Manifest', RecordingSet, SupervisionSet, FeatureSet, CutSet)


def combine(*manifests: Manifest) -> Manifest:
    """Combine multiple manifests of the same type into one."""
    return reduce(add, manifests)


def to_manifest(items: Iterable[ManifestItem]) -> Optional[Manifest]:
    """
    Take an iterable of data types in Lhotse such as Recording, SupervisonSegment or Cut, and create the manifest of the
    corresponding type. When the iterable is empty, returns None.
    """
    items = iter(items)
    try:
        first_item = next(items)
    except StopIteration:
        return None
    items = chain([first_item], items)

    if isinstance(first_item, Recording):
        return RecordingSet.from_recordings(items)
    if isinstance(first_item, SupervisionSegment):
        return SupervisionSet.from_segments(items)
    if isinstance(first_item, (Cut, MixedCut)):
        return CutSet.from_cuts(items)
    if isinstance(first_item, Features):
        raise ValueError("FeatureSet generic construction from iterable is not possible, as the config information "
                         "would have been lost. Call FeatureSet.from_features() directly instead.")

    raise ValueError(f"Unknown type of manifest item: {first_item}")


def load_manifest(path: Pathlike) -> Manifest:
    """Generic utility for reading an arbitrary manifest."""
    raw_data = load_yaml(path)
    data_set = None
    for manifest_type in [RecordingSet, SupervisionSet, FeatureSet, CutSet]:
        try:
            data_set = manifest_type.from_dicts(raw_data)
        except Exception:
            pass
    if data_set is None:
        raise ValueError(f'Unknown type of manifest: {path}')
    return data_set
