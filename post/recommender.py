from .models import *
from account.models import User
from sklearn.metrics.pairwise import cosine_similarity
from collections import defaultdict
from sklearn.feature_extraction.text import CountVectorizer
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

def preprocess(text):
    text = text.lower()
    text = text.strip()
    text = remove_emoji(text)
    return text

class SearchEngine:
    def search(self,query):
        query = preprocess(query)
        questions = Question.objects.all()
        question_titles = [question.title for question in questions]
        question_tags = [question.tags.values('name') for question in questions]
        question_tag_list = []
        for tags in question_tags:
            tag_list = []
            for tag in tags:
                tag_list.append(tag['name'])
            question_tag_list.append(tag_list)
        combined_inputs = [f"{title} {' '.join(tags)}" for title, tags in zip(question_titles, question_tag_list)]
        
        vectorizer = CountVectorizer()

        # Vectorize the combined inputs
        question_matrix = vectorizer.fit_transform(combined_inputs)
        query_vector = vectorizer.transform([query])
        similarities = cosine_similarity(question_matrix, query_vector)

        # Sort questions by similarity scores in descending order
        sorted_questions = sorted(zip(questions, similarities), key=lambda x: x[1], reverse=True)
        
        top_similar_question = []
        threshold = 0.3
        for question, similarity in sorted_questions:
            if(similarity[0] >= threshold):
                top_similar_question.append(question.id)
        query = Question.objects.filter(pk__in = top_similar_question).distinct()
        return query
        
class HybridRecommender:
    def content_recommend(self,user):
        all_question = Question.objects.all()
        user_tags = user.tags.values('name')
        scores = {}
        for question in all_question:
            question_tags = question.tags.values('name')
            question_vector = [1 if tag in question_tags else 0 for tag in user_tags]
            user_vector = [1 if tag in user_tags else 0 for tag in user_tags]
            similarity_score = cosine_similarity([question_vector], [user_vector])[0][0]
            scores[question.id] = similarity_score
        return scores

    def get_nearest_neighbors(self,user, k=10):
        upvotes = UpvoteQuestion.objects.filter(user=user)
        question_ids = upvotes.values_list('question', flat=True)
        other_upvotes = UpvoteQuestion.objects.all().exclude(user=user).filter(question__in=question_ids)
        user_similarities = defaultdict(int)
        for upvote in other_upvotes:
            user_similarities[upvote.user] += 1
        nearest_neighbors = sorted(user_similarities.items(), key=lambda x: x[1], reverse=True)[:k]
        return nearest_neighbors

    def collab_recommend(self,user,k=10):
        nearest_neighbors = self.get_nearest_neighbors(user, k)
        scores = {}
        for neighbor, similarity in nearest_neighbors:
            upvotes = UpvoteQuestion.objects.filter(user=neighbor)
            for items in upvotes:
                scores[items.question.id] = similarity
        return scores

    def get_recommendations(self,user):
        # Get content-based recommendations
        content_based_recs = self.content_recommend(user)
        
        # Get collaborative filtering recommendations
        collaborative_recs = self.collab_recommend(user)
        
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
        query = Question.objects.filter(pk__in=top_recs)
        return query
