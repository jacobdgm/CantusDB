import json
import unittest
from unittest.mock import Mock, patch
from django.test import TestCase
from typing import Union, Optional
from main_app.models import (
    Chant,
    Source,
)
from main_app.tests.make_fakes import (
    make_fake_chant,
    make_fake_source,
)
from main_app.management.commands import update_cached_concordances
from main_app.signals import generate_incipit
from cantusindex import get_json_from_ci_api, get_expected_fulltext

DATA_FOR_CID_001008: str = """
    {
        "info": {
            "field_ah_item": null,
            "field_ah_volume": null,
            "field_cao": "1008",
            "field_cao_concordances": "D",
            "field_feast": "Exaltatio Crucis",
            "field_full_text": "Adoremus deum quia ipse redemit nos",
            "field_fulltext_source": "CAO (1968), Vol. 3, p. 2;",
            "field_genre": "I",
            "field_language": null,
            "field_notes": null,
            "field_related_chant_id": null,
            "field_similar_chant_id": null,
            "field_troped_chant_id": null
        },
        "chants": {
            "1": {
                "siglum": "F-Pn : Lat. 17296",
                "srclink": "http://musmed.eu/source/13486",
                "chantlink": "http://musmed.eu/chant/190422",
                "folio": "213v",
                "sequence": "1",
                "incipit": "Adoremus deum quia ipse redemit nos",
                "feast": "Exaltatio Crucis",
                "office": "M",
                "genre": "I",
                "position": "",
                "image": "https://gallica.bnf.fr/ark:/12148/btv1b6000532c/f438.item",
                "mode": "4",
                "fulltext": "Adoremus deum quia ipse redemit nos",
                "melody": "",
                "db": "MMMO"
            },
            "2": {
                "siglum": "F-Pn Lat. 15182",
                "srclink": "http://cantusdatabase.org/source/123632",
                "chantlink": "http://cantusdatabase.org/chant/415291",
                "folio": "355v",
                "sequence": "3",
                "incipit": "Adoremus dominum quia ipse",
                "feast": "Exaltatio Crucis",
                "office": "M",
                "genre": "I",
                "position": "",
                "image": "http://gallica.bnf.fr/ark:/12148/btv1b8447769r/f712.image",
                "mode": "6T",
                "fulltext": "",
                "melody": "",
                "db": "CD"
            },
            "0": {
                "siglum": "F-Pn Lat. 15182",
                "srclink": "https://cantusdatabase.org/source/123632/",
                "chantlink": "https://cantusdatabase.org/chant/415291/",
                "folio": "355v",
                "sequence": "3",
                "incipit": "Adoremus dominum quia ipse",
                "feast": "Exaltatio Crucis",
                "office": "M",
                "genre": "I",
                "position": null,
                "image": "http://gallica.bnf.fr/ark:/12148/btv1b8447769r/f712.image",
                "mode": "6T",
                "fulltext": null,
                "melody": null,
                "db": "CD"
            }
        }
    }
"""
BYTES_FOR_CID_001008: bytes = bytes(DATA_FOR_CID_001008, encoding="utf-8-sig")
JSON_FOR_CID_001008: dict = json.loads(DATA_FOR_CID_001008)


# run with `python -Wa manage.py test main_app.tests.test_functions`
# the -Wa flag tells Python to display deprecation warnings


class UpdateCachedConcordancesCommandTest(TestCase):
    def test_concordances_structure(self):
        chant: Chant = make_fake_chant(cantus_id="123456")
        concordances: list = update_cached_concordances.get_concordances()

        with self.subTest(test="Ensure get_concordances returns list"):
            self.assertIsInstance(concordances, list)

        single_concordance = concordances[0]
        with self.subTest(test="Ensure each concordance is a dict"):
            self.assertIsInstance(single_concordance, dict)

        expected_keys = (
            "siglum",
            "srclink",
            "chantlink",
            "folio",
            "sequence",
            "incipit",
            "feast",
            "genre",
            "office",
            "position",
            "cantus_id",
            "image",
            "mode",
            "full_text",
            "melody",
            "db",
        )
        concordance_keys = single_concordance.keys()
        for key in expected_keys:
            with self.subTest(key=key):
                self.assertIn(key, concordance_keys)
        with self.subTest(test="Ensure no unexpected keys present"):
            self.assertEqual(len(concordance_keys), len(expected_keys))

    def test_published_vs_unpublished(self):
        published_source: Source = make_fake_source(published=True)
        published_chant: Chant = make_fake_chant(
            source=published_source,
            manuscript_full_text_std_spelling="chant in a published source",
        )
        unpublished_source: Source = make_fake_source(published=False)
        unpublished_chant: Chant = make_fake_chant(
            source=unpublished_source,
            manuscript_full_text_std_spelling="chant in an unpublished source",
        )

        concordances: list = update_cached_concordances.get_concordances()
        self.assertEqual(len(concordances), 1)

        single_concordance: dict = concordances[0]
        expected_fulltext: str = published_chant.manuscript_full_text_std_spelling
        observed_fulltext: str = single_concordance["full_text"]
        self.assertEqual(expected_fulltext, observed_fulltext)

    def test_concordances_values(self):
        chant: Chant = make_fake_chant()

        concordances: list = update_cached_concordances.get_concordances()
        single_concordance: dict = concordances[0]

        expected_items: tuple = (
            ("siglum", chant.source.siglum),
            ("srclink", f"https://cantusdatabase.org/source/{chant.source.id}/"),
            ("chantlink", f"https://cantusdatabase.org/chant/{chant.id}/"),
            ("folio", chant.folio),
            ("sequence", chant.c_sequence),
            ("incipit", chant.incipit),
            ("feast", chant.feast.name),
            ("genre", chant.genre.name),
            ("office", chant.office.name),
            ("position", chant.position),
            ("cantus_id", chant.cantus_id),
            ("image", chant.image_link),
            ("mode", chant.mode),
            ("full_text", chant.manuscript_full_text_std_spelling),
            ("melody", chant.volpiano),
            ("db", "CD"),
        )

        for key, value in expected_items:
            observed_value: Union[str, int, None] = single_concordance[key]
            with self.subTest(key=key):
                self.assertEqual(observed_value, value)


class IncipitSignalTest(TestCase):
    # testing an edge case in generate_incipit, within main_app/signals.py.
    # Some other tests involving this function can be found
    # in ChantModelTest and SequenceModelTest.
    def test_generate_incipit(self):
        complete_fulltext: str = "one two three four five six seven"
        expected_incipit_1: str = "one two three four five"
        observed_incipit_1: str = generate_incipit(complete_fulltext)
        with self.subTest(test="full-length fulltext"):
            self.assertEqual(observed_incipit_1, expected_incipit_1)
        short_fulltext: str = "one*"
        expected_incipit_2 = "one*"
        observed_incipit_2 = generate_incipit(short_fulltext)
        with self.subTest(test="fulltext that's already a short incipit"):
            self.assertEqual(observed_incipit_2, expected_incipit_2)


class CantusIndexFunctionsTest(TestCase):
    def test_get_json_from_ci_api(self):
        expected_json: dict = JSON_FOR_CID_001008

        # When running the tests, we create a mock copy of requests.get
        # that will replace (i.e., patch) the call to requests.get within
        # get_json_from_ci_api. This way, instead of testing
        # get_json_from_ci_api AND requests.get AND the state of the Cantus Index
        # database, we can test get_json_from_ci_api alone, on a known value returned
        # by requests.get.
        class MockResponse:
            def __init__(self, content: bytes):
                self.content = content

            def content(self):
                return self.content

        def mock_requests_get(url: str, timeout: Optional[int] = None):
            return MockResponse(BYTES_FOR_CID_001008)

        with patch("requests.get", mock_requests_get):
            observed_json = get_json_from_ci_api("/json-cid/001008")
            self.assertEqual(observed_json, expected_json)

    def test_get_expected_fulltext(self):
        json_from_ci: dict = json.loads(DATA_FOR_CID_001008)
        expected_fulltext: str = json_from_ci["info"]["field_full_text"]

        # patch get_json_from_ci_api to return a known value, in order to test
        # get_expected_fulltext only.
        def mock_get_json_from_ci_api(path: str, timeout: Optional[int] = 2):
            return JSON_FOR_CID_001008

        with patch(
            "cantusindex.get_json_from_ci_api",
            mock_get_json_from_ci_api,
        ):
            observed_fulltext = get_expected_fulltext("001008")
            print(f"{observed_fulltext=}")

        self.assertEqual(observed_fulltext, expected_fulltext)
