import unittest
from sklearn.feature_extraction.text import TfidfVectorizer

class TestFeatureExtraction(unittest.TestCase):

    def test_tfidf_vector_shape(self):
        sample_texts = ["I love this!", "This is bad."]
        vectorizer = TfidfVectorizer(max_features=10)
        X = vectorizer.fit_transform(sample_texts)
        self.assertEqual(X.shape[0], 2)  # 2 documents
        self.assertEqual(X.shape[1], len(vectorizer.get_feature_names_out()))


if __name__ == "__main__":
    unittest.main()
