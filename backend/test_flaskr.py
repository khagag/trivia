import os
import unittest
import json
from flask_sqlalchemy import SQLAlchemy

from flaskr import create_app
from models import setup_db, Question, Category


class TriviaTestCase(unittest.TestCase):
    """This class represents the trivia test case"""

    def setUp(self):
        """Define test variables and initialize app."""
        self.app = create_app()
        self.client = self.app.test_client
        self.database_name = "trivia_test"
        self.database_path = "postgres://{}/{}".format('postgres:kareem@localhost:8888', self.database_name)
        setup_db(self.app, self.database_path)

        # sample question for use in tests
        self.new_question = {
            'question': 'Which four states make up the 4 Corners region of the US?',
            'answer': 'Colorado, New Mexico, Arizona, Utah',
            'difficulty': 3,
            'category': '3'
        }

        # binds the app to the current context
        with self.app.app_context():
            self.db = SQLAlchemy()
            self.db.init_app(self.app)
            # create all tables
            self.db.create_all()

    def test_questions_get_api(self):
        """ check getting the questions & categories """
        res = self.client().get('/questions?page=300')
         # assert if the request status is successful
        self.assertEqual(res.status_code, 404)
        data = json.loads(res.data)
        # assert the payload of the response
        self.assertEqual(data['success'],False)

    def test_questions_get_api_fail(self):

        res = self.client().get('/questions')
        self.assertEqual(res.status_code, 200)
        data = json.loads(res.data)
        # assert the payload of the response
        self.assertTrue(data['total_questions'])
        self.assertTrue(len(data['questions']))
        self.assertTrue(len(data['categories']))


    def test_search_questions_faliure(self):
        """Tests search questions faliure"""

        # send post request with search term
        response = self.client().post('/questions',
                                      json={'searchTerm': 'lljlks'})

        # load response data
        data = json.loads(response.data)

        # check response status code and message
        self.assertEqual(response.status_code, 404)
        self.assertEqual(data['success'], False)


    def test_search_questions(self):
        """Tests search questions success"""

        # send post request with search term
        response = self.client().post('/questions',
                                      json={'searchTerm': 'cup'})

        # load response data
        data = json.loads(response.data)

        # check response status code and message
        self.assertEqual(response.status_code, 200)
        self.assertEqual(data['success'], True)

        # check that number of results = 2
        self.assertEqual(len(data['questions']), 2)

    def test_categories_get_api(self):
        """ check getting the categories """
        res = self.client().get('/categories')
        # assert if the request status is successful
        self.assertEqual(res.status_code, 200)
        data = json.loads(res.data)
        # assert the payload of the response
        self.assertTrue(data['total_categories'])
        self.assertTrue(len(data['categories']))

    # def test_categories_get_api_faliure(self):
    #     """ check getting the categories """
    #     res = self.client().get('/categories?page=899')
    #     # assert if the request status is successful
    #     self.assertEqual(res.status_code, 404)
    #     data = json.loads(res.data)
    #     # assert the payload of the response
    #     self.assertEqual(data['success'],False)

    def test_quizz_get(self):
        """ check getting the categories """
        res = self.client().post('/quizzes',json={
            'previous_questions':[],
            'quiz_category':{'type': 'Science', 'id': '1'}
        })
        # assert if the request status is successful
        self.assertEqual(res.status_code, 200)
        data = json.loads(res.data)
        # assert the payload of the response
        self.assertTrue(data['success'])
        self.assertTrue(data['question'])

    def test_questions_create(self):
        """ check creating new questions """

        before = len(Question.query.all())
        # create a new question to be deleted
        question = Question('','','','')
        question.question = self.new_question['question']
        question.answer = self.new_question['answer']
        question.category = self.new_question['category']
        question.difficulty = self.new_question['difficulty']
        q=question.insert()
        after = len(Question.query.all())

        # check status code and success message
        self.assertEqual(before+1,after)


    def test_404_request_beyond_valid_page(self):
        """Tests question pagination failure 404"""

        # send request with not found page/questions
        response = self.client().get('/questions?page=200')
        data = json.loads(response.data)

        # check status code and payload
        self.assertEqual(response.status_code, 404)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'Not found')

    def test_422_request_beyond_valid_page(self):
        """Tests question pagination failure 422"""

        # send request with not found page/questions

        response = self.client().post('/questions', json={})
        data = json.loads(response.data)

        # check status code and payload
        self.assertEqual(response.status_code, 422)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'Unprocessed Entity')

    def test_delete_question(self):
        """Tests question deletion success"""

        # create a new question to be deleted
        question = Question('','','','')
        question.question = self.new_question['question']
        question.answer = self.new_question['answer']
        question.category = self.new_question['category']
        question.difficulty = self.new_question['difficulty']
        question.insert()

        # get the id of the new question
        questionId = question.id

        # get number of questions before delete
        questions_before = len(Question.query.all())

        # delete the question and store response
        response = self.client().delete('/questions/{}'.format(questionId))
        data = json.loads(response.data)

        # get number of questions after delete
        questions_after = len(Question.query.all())

        # assert if the question decreased / the question is deleted
        self.assertEqual(questions_after+1,questions_before)

        # check status code and success message
        self.assertEqual(response.status_code, 200)
        self.assertEqual(data['success'], True)



    def tearDown(self):
        """Executed after reach test"""
        pass

    """
    TODO
    Write at least one test for each test for successful operation and for expected errors.
    """


# Make the tests conveniently executable
if __name__ == "__main__":
    unittest.main()
