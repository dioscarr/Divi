import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from cli import search_index, searchable_metadata, features


class LibraryBuilderSearchTests(unittest.TestCase):
    def setUp(self):
        markup = '<!-- wp:divi/text --><h1>Dark mobile hero</h1><!-- /wp:divi/text --><!-- wp:divi/image /--><!-- wp:divi/button /-->'
        metadata_features = features(markup)
        data = searchable_metadata('Dark mobile hero', 'hero', markup, metadata_features)
        self.index = {'components': [{
            'id': 'hero-dark', 'category': 'hero', 'label': 'Dark mobile hero',
            'features': metadata_features, **data,
        }, {
            'id': 'faq-light', 'category': 'faq', 'label': 'FAQ',
            'features': {'has_image': False}, 'modules': ['accordion'],
            'signals': {'visual': [], 'content': ['responsive']},
            'search_terms': ['faq', 'responsive'],
        }]}

    def test_synonyms_rank_relevant_component(self):
        results = search_index(self.index, 'dark phone banner with action')
        self.assertEqual(results[0]['id'], 'hero-dark')
        self.assertIn('hero', results[0]['matched_terms'])

    def test_filters_are_supported(self):
        results = search_index(self.index, 'category:hero feature:image')
        self.assertEqual([item['id'] for item in results], ['hero-dark'])


if __name__ == '__main__':
    unittest.main()
