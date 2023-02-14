from sklearn.metrics.pairwise import cosine_similarity
from collections import defaultdict

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

def get_nearest_neighbors(user,upvote ,k=10):
    upvotes = upvote.filter(user=user)
    question_ids = upvotes.values_list('question', flat=True)
    other_upvotes = upvote.exclude(user=user).filter(question__in=question_ids)
    user_similarities = defaultdict(int)
    for upvote in other_upvotes:
        user_similarities[upvote.user] += 1
    nearest_neighbors = sorted(user_similarities.items(), key=lambda x: x[1], reverse=True)[:k]
    return nearest_neighbors

def collab_recommend(user,upvote,k=10):
    nearest_neighbors = get_nearest_neighbors(user,upvote, k)
    recommended_questions = []
    for neighbor, similarity in nearest_neighbors:
        upvotes = upvote.filter(user=neighbor)
        recommended_questions.extend(list(upvotes.values_list('question', flat=True)))
    return recommended_questions

