from recommendation.recommender import Recommender


recommender = Recommender()

recommendations = recommender.recommend(0)

for product in recommendations:
    print(product)
