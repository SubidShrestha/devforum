from sklearn.metrics.pairwise import cosine_similarity
from collections import defaultdict
import re

def remove_emoji(string):
    emoji_pattern = re.compile("["
                           u"\U0001F600-\U0001F64F"  # emoticons
                           u"\U0001F300-\U0001F5FF"  # symbols & pictographs
                           u"\U0001F680-\U0001F6FF"  # transport & map symbols
                           u"\U0001F1E0-\U0001F1FF"  # flags (iOS)
                           u"\U00002702-\U000027B0"
                           u"\U000024C2-\U0001F251"
                           "]+", flags=re.UNICODE)
    return emoji_pattern.sub(r'', string)

def preprocess(content):
    preprocess_data = []
    for text in content:
        text['name'] = text['name'].lower()
        text['name'] = remove_emoji(text['name'])
        preprocess_data.append(text)
    return preprocess_data
        
def content_recommend(user,question):
    all_question = question.all()
    user_tags = preprocess(user.tags.values('name'))
    scores = {}
    for question in all_question:
        question_tags = question.tags.values('name')
        question_vector = [1 if tag in question_tags else 0 for tag in user_tags]
        user_vector = [1 if tag in user_tags else 0 for tag in user_tags]
        similarity_score = cosine_similarity([question_vector], [user_vector])[0][0]
        scores[question.id] = similarity_score
    return scores

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
    scores = {}
    for neighbor, similarity in nearest_neighbors:
        upvotes = upvote.filter(user=neighbor)
        for items in upvotes:
            scores[items.question.id] = similarity
    return scores

def get_recommendations(user,questions,upvotes):
    # Get content-based recommendations
    content_based_recs = content_recommend(user,questions)
    
    # Get collaborative filtering recommendations
    collaborative_recs = collab_recommend(user,upvotes)
    
    # Combine the results using a weighted hybrid approach
    combined_recs = {}
    for item in content_based_recs:
        if item in collaborative_recs:
            combined_recs[item] = (0.6 * content_based_recs[item]) + (0.4 * collaborative_recs[item])
        else:
            combined_recs[item] = content_based_recs[item]
    
    for item in collaborative_recs:
        if item not in combined_recs:
            combined_recs[item] = collaborative_recs[item] * 0.4
    
    # Sort the recommendations by the combined score
    sorted_recs = sorted(combined_recs.items(), key=lambda x: x[1], reverse=True)
    
    # Return the top 10 recommendations
    top_recs = [item[0] for item in sorted_recs][:10]
    return top_recs

