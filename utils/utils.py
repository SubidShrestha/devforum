from sklearn.feature_extraction.text import CountVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.neighbors import NearestNeighbors
import pandas as pd

def recommend(user,question):
    all_question = question.all()
    user_tags = user.tags.values('name')
    threshold = 0.5
    recommended_question = []
    for question in all_question:
        question_tags = question.tags.values('name')
        question_vector = [1 if tag in question_tags else 0 for tag in user_tags]
        user_vector = [1 if tag in user_tags else 0 for tag in user_tags]
        similarity_score = cosine_similarity([question_vector], [user_vector])[0][0]
        if similarity_score >= threshold:
            recommended_question.append(question.id)
    return recommended_question
    