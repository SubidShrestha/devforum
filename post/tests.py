from django.test import TestCase
from .models import *
from account.models import User
from .recommender import HybridRecommender, SearchEngine
from taggit.models import Tag

class RecommenderTest(TestCase):
    def setUp(self):
        self.tag1 = Tag.objects.create(name = 'tag1',slug = 'tag1')
        self.tag2 = Tag.objects.create(name = 'tag2',slug = 'tag2')
        self.tag3 = Tag.objects.create(name = 'tag3',slug = 'tag3')
        self.tag4 = Tag.objects.create(name = 'tag4',slug = 'tag4')
        self.tag5 = Tag.objects.create(name = 'tag5',slug = 'tag5')
        self.tag6 = Tag.objects.create(name = 'tag6',slug = 'tag6')
        
        self.user1 = User.objects.create(username='user1',password ="testus@12",email="testuser1@gmail.com")
        self.user1.tags.add(self.tag1,self.tag2)
        self.user2 = User.objects.create(username='user2',password ="testus@12",email="testuser2@gmail.com")
        self.user2.tags.add(self.tag3,self.tag4)
        
        self.user3 = User.objects.create(username='user3',password ="testus@12",email="testuser3@gmail.com")
        self.user3.tags.add(self.tag1,self.tag2)
        self.user4 = User.objects.create(username='user4',password ="testus@12",email="testuser4@gmail.com")
        self.user4.tags.add(self.tag3,self.tag4)
        self.user5 = User.objects.create(username='user5',password ="testus@12",email="testuser5@gmail.com")
        self.user5.tags.add(self.tag3)

        self.item1 = Question.objects.create(title='Item 1',author = self.user1)
        self.item1.tags.add(self.tag1,self.tag2)
        self.item2 = Question.objects.create(title='Item 2',author = self.user2)
        self.item2.tags.add(self.tag1,self.tag2)
        
        self.item3 = Question.objects.create(title='Item 3',author = self.user1)
        self.item3.tags.add(self.tag1,self.tag2)
        self.item4 = Question.objects.create(title='Item 4',author = self.user2)
        self.item4.tags.add(self.tag1,self.tag2)
        
        self.item5 = Question.objects.create(title='Item 5',author = self.user1)
        self.item5.tags.add(self.tag1,self.tag2)
        self.item6 = Question.objects.create(title='Item 6',author = self.user2)
        self.item6.tags.add(self.tag1,self.tag2)
        
        self.item7 = Question.objects.create(title='Item 7',author = self.user1)
        self.item7.tags.add(self.tag1,self.tag2)
        self.item8 = Question.objects.create(title='Item 8',author = self.user2)
        self.item8.tags.add(self.tag1,self.tag2)
        
        self.item9 = Question.objects.create(title='Item 9',author = self.user2)
        self.item9.tags.add(self.tag1,self.tag2)
        self.item10 = Question.objects.create(title='Item 10',author = self.user2)
        self.item10.tags.add(self.tag1,self.tag2)
        
        self.item11 = Question.objects.create(title='Item 11',author = self.user5)
        self.item11.tags.add(self.tag5,self.tag6)
        self.item12 = Question.objects.create(title='Item 12',author = self.user2)
        self.item12.tags.add(self.tag5)
        
        self.item13 = Question.objects.create(title='Item 13',author = self.user2)
        self.item13.tags.add(self.tag3,self.tag4)
        self.item14 = Question.objects.create(title='Item 14',author = self.user2)
        self.item14.tags.add(self.tag3,self.tag4)
        
        self.item15 = Question.objects.create(title='Item 15',author = self.user2)
        self.item15.tags.add(self.tag3,self.tag4)
        self.item16 = Question.objects.create(title='Item 16',author = self.user2)
        self.item16.tags.add(self.tag2,self.tag4)
        
        self.item17 = Question.objects.create(title='Item 17',author = self.user2)
        self.item17.tags.add(self.tag3,self.tag1)
        self.item18 = Question.objects.create(title='Item 18',author = self.user2)
        self.item18.tags.add(self.tag5,self.tag6)
        
        self.item19 = Question.objects.create(title='Item 19',author = self.user2)
        self.item19.tags.add(self.tag4)
        self.item20 = Question.objects.create(title='Item 20',author = self.user2)
        self.item20.tags.add(self.tag3)
        
        self.item21 = Question.objects.create(title='Item 21',author = self.user2)
        self.item21.tags.add(self.tag3,self.tag4)

        UpvoteQuestion.objects.create(user=self.user3, question=self.item1)
        UpvoteQuestion.objects.create(user=self.user3, question=self.item2)
        UpvoteQuestion.objects.create(user = self.user5, question = self.item18)
        UpvoteQuestion.objects.create(user = self.user5, question = self.item11)
        UpvoteQuestion.objects.create(user=self.user4, question=self.item18)
        UpvoteQuestion.objects.create(user=self.user4, question=self.item21)

    def test_hybrid_recommender(self):
        recommender = HybridRecommender()
        recommendation_user3 = recommender.get_recommendations(user=self.user3)
        recommendation_user4 = recommender.get_recommendations(user=self.user4)

        recommend_items_for_user3 = [self.item1,self.item2,self.item3,self.item4,self.item5,self.item6,self.item7,self.item8,self.item9,self.item10]
        recommend_items_for_user4 = [self.item11,self.item13,self.item14,self.item15,self.item16,self.item17,self.item18,self.item19,self.item20,self.item21]
        try:
            self.assertEqual(list(recommendation_user3),recommend_items_for_user3)
            self.assertEqual(list(recommendation_user4),recommend_items_for_user4)
        except AssertionError as e:
            print(e)
    
    def test_search_engine(self):
        search_engine = SearchEngine()
        keywords = [
            {
                'tag5':[self.item11,self.item12,self.item18]
            },
            {
                'tag1' : [self.item1, self.item2, self.item3, self.item4, self.item5]
            },
            {
                'tag2' : [self.item1, self.item2, self.item3, self.item4, self.item5]
            },
            {
                'tag3' : [self.item13, self.item14, self.item15, self.item17,self.item21]
            },
            {
                'tag4' : [self.item13, self.item14, self.item16, self.item17, self.item19,self.item21]
            },
            {
                'non exist': []
            },
            {
                'Item' : [self.item1, self.item2, self.item3, self.item4, self.item5]
            },
            {
                'Item9' : [self.item9]
            }]
        accuracy = []
        for keyword in keywords:
            val = next(iter(keyword))
            result = search_engine.search(val)
            result = result[:5]
            relevant_result = [j for j in result if j in keyword[val]]
            if len(relevant_result) == len(val):
                accuracy.append(1)
            elif len(relevant_result) == 0:
                accuracy.append(0)
            else:
                accuracy.append(len(relevant_result)/len(val))
        avg_accuracy = sum(accuracy)/len(accuracy)
        print(avg_accuracy)
        