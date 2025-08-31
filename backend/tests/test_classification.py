import unittest
import numpy as np
from sklearn.naive_bayes import MultinomialNB
from sklearn.svm import SVC

class TestClassification(unittest.TestCase):

    def test_naive_bayes_prediction(self):
        X_train = np.array([[1,0],[0,1]])
        y_train = np.array([0,1])
        model = MultinomialNB()
        model.fit(X_train, y_train)
        pred = model.predict(X_train)
        self.assertListEqual(list(pred), [0,1])

    def test_svc_prediction(self):
        X_train = np.array([[1,0],[0,1]])
        y_train = np.array([0,1])
        model = SVC()
        model.fit(X_train, y_train)
        pred = model.predict(X_train)
        self.assertListEqual(list(pred), [0,1])


if __name__ == "__main__":
    unittest.main()
