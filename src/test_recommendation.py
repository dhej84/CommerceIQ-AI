from src.recommendation.recommender import Recommender


recommender = Recommender()

sample_title = "Saucony Men's Kinvara 13 Running Shoe"
recommendations = recommender.recommend(sample_title)

print(f"Recommendations for: {sample_title}")
for product in recommendations:
    print(product)
