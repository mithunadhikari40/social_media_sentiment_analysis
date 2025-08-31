
import unittest
import matplotlib.pyplot as plt
from backend.chart_generator import create_sentiment_distribution_chart

class TestVisualization(unittest.TestCase):

    def test_plot_generation(self):

        sample_data = [
            {"sentiment": "positive", "count": 13},
            {"sentiment": "negative", "count": 8},
            {"sentiment": "neutral", "count": 3}
        ]
        fig,_ = create_sentiment_distribution_chart(sample_data, save_path="plots/sentiment_chart_test.png")
        self.assertIsNotNone(fig)


if __name__ == "__main__":
    unittest.main()


