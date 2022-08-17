from main_app.models import Chant
from collections import Counter


def next_chants(cantus_id, display_unpublished=False):
    """find instances of the chant with the given cantus_id
    in all manuscripts, gather a list of other chants that follow the
    specified chant in those manuscripts, and count how often each
    following chant occurs.

    Returns:
        list of duples, each representing a cantusID-count pair
    """
    concordances = Chant.objects.filter(cantus_id=cantus_id).only(
        "source", "folio", "sequence_number"
    )
    # if not display_unpublished:
    #     concordances = concordances.filter(source__published=True)
    
    next_chants = [chant.next_chant
            for chant
            in concordances
            if chant.next_chant is not None
        ]
    if not display_unpublished:
        next_chants = [chant
            for chant
            in next_chants
            if chant.source.published
        ]

    ids = [chant.cantus_id
        for chant
        in next_chants
        if chant.cantus_id is not None]   # chant would be None if .get_next_chant() returned None,
                                                                # i.e. if the chant in concordances was the last in the manuscript
    counts = Counter(ids)
    ids_and_counts = [item for item in counts.items()] # each item is an id-count key-value pair
    
    return ids_and_counts