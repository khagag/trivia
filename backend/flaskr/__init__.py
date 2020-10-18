import os
from flask import Flask, request, abort, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS ,cross_origin
import random

from models import setup_db, Question, Category,db

QUESTIONS_PER_PAGE = 10


def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__)
    setup_db(app)
    '''
  @TODO: Set up CORS. Allow '*' for origins. Delete the sample route after completing the TODOs
  '''
    CORS(app, resources={'*': {'origins': '*'}})

    '''
  @TODO: Use the after_request decorator to set Access-Control-Allow
  '''
    @app.after_request
    def after_request(response):
        # pass
        response.headers.add('Access-Control-Allow-Headers',
                             'Content-Type,Authorization,true')
        response.headers.add('Access-Control-Allow-Methods',
                             'GET,PUT,POST,DELETE,OPTIONS')
        return response

    # utility for paginating questions
    def paginate_questions(request, selection):
        page = request.args.get('page', 1, type=int)
        start = (page - 1) * QUESTIONS_PER_PAGE
        end = start + QUESTIONS_PER_PAGE

        questions = [question.format() for question in selection]
        current_questions = questions[start:end]

        return current_questions

    def paginate(req, data):
        p = req.args.get('page', 1, type=int)
        s = (p-1) * QUESTIONS_PER_PAGE
        data = [s, s + QUESTIONS_PER_PAGE]
        return data
    '''
  @TODO:
  Create an endpoint to handle GET requests
  for all available categories.
  '''

    @app.route('/categories')
    def retrive_categories():
        categories = Category.query.all()
        return jsonify({
            'success':True,
            'categories': {i.id: i.type for i in categories},
            'total_categories':len(categories)
        })
    '''
  @TODO:
  Create an endpoint to handle GET requests for questions,
  including pagination (every 10 questions).
  This endpoint should return a list of questions,
  number of total questions, current category, categories.
  '''
    @app.route('/questions')
    def get_question():
        selection = Question.query.all()
        ques = paginate_questions(request, selection)
        if len(ques) == 0:
            abort(404)
        return jsonify({
            'success': True,
            'categories': {i.id: i.type for i in Category.query.all()},
            'total_questions': len(Category.query.all()),
            'current_category': Category.query.first().format(),
            "questions": ques})
    '''
  TEST: At this point, when you start the application
  you should see questions and categories generated,
  ten questions per page and pagination at the bottom of the screen for three pages.
  Clicking on the page numbers should update the questions.
  '''

    '''
  @TODO:
  Create an endpoint to DELETE question using a question ID.

  TEST: When you click the trash icon next to a question, the question will be removed.
  This removal will persist in the database and when you refresh the page.
  '''
    @app.route('/questions/<int:question_id>',methods=['DELETE'])
    def delete_question(question_id):
        try:
            q=Question.query.get(question_id)
            if q is None:
                abort(404)
            db.session.delete(q)
            db.session.commit()
        except:
            abort(500)
        return jsonify({
            "success":True
        })

    '''
  @TODO:
  Create an endpoint to POST a new question,
  which will require the question and answer text,
  category, and difficulty score.

  TEST: When you submit a question on the "Add" tab,
  the form will clear and the question will appear at the end of the last page
  of the questions list in the "List" tab.
  '''
    @cross_origin()
    @app.route('/questions', methods=['POST'])
    def add():
        '''
        Handles POST requests for creating new questions and searching questions.
        '''
        # load the request body
        body = request.get_json()

        # if search term is present
        if (body.get('searchTerm')):
            search_term = body.get('searchTerm')

            # query the database using search term
            selection = Question.query.filter(
                Question.question.ilike(f'%{search_term}%')).all()

            # 404 if no results found
            if (len(selection) == 0):
                abort(404)

            # paginate the results
            paginated = paginate_questions(request, selection)

            # return results
            return jsonify({
                'success': True,
                'questions': paginated,
                'total_questions': len(Question.query.all())
            })
        # if no search term, create new question
        else:
            # load data from body
            new_question = body.get('question')
            new_answer = body.get('answer')
            new_difficulty = body.get('difficulty')
            new_category = body.get('category')

            # ensure all fields have data
            if ((new_question is None) or (new_answer is None)
                    or (new_difficulty is None) or (new_category is None)):
                abort(422)

            try:
                # create and insert new question
                question = Question(question=new_question, answer=new_answer,
                                    difficulty=new_difficulty, category=new_category)
                question.insert()

                # get all questions and paginate
                selection = Question.query.order_by(Question.id).all()
                current_questions = paginate_questions(request, selection)

                # return data to view
                return jsonify({
                    'success': True,
                    'created': question.id,
                    'question_created': question.question,
                    'questions': current_questions,
                    'total_questions': len(Question.query.all())
                })

            except:
                # abort unprocessable if exception
                abort(422)

    '''
  @TODO:
  Create a POST endpoint to get questions based on a search term.
  It should return any questions for whom the search term
  is a substring of the question.

  TEST: Search by any phrase. The questions list will update to include
  only question that include that string within their question.
  Try using the word "title" to start.
  '''
    # @app.route('/questions', methods=['POST'])
    # @cross_origin(origin=r'*/^')
    # def search():
    #     # print("data is"+request.args.get('searchTerm'))
    #     question = "%{}%".format(request.get_json()['searchTerm'])
    #     return jsonify({
    #       'questions': [i.format() for i in Question.query.filter(Question.question.like(question)).all()]
    #   })
    '''
  @TODO:
  Create a GET endpoint to get questions based on category.

  TEST: In the "List" tab / main screen, clicking on one of the
  categories in the left column will cause only questions of that
  category to be shown.
  '''
    @app.route("/categories/<int:cat>/questions")
    def category_questions(cat):
        return jsonify({
            'questions': [i.format() for i in Question.query.filter_by(category=cat).all()]
        })
    '''
  @TODO:
  Create a POST endpoint to get questions to play the quiz.
  This endpoint should take category and previous question parameters
  and return a random questions within the given category,
  if provided, and that is not one of the previous questions.

  TEST: In the "Play" tab, after a user selects "All" or a category,
  one question at a time is displayed, the user is allowed to answer
  and shown whether they were correct or not.
  '''
    @app.route('/quizzes', methods=['POST'])
    def quiz():
        return jsonify({'question': Question.query.first().format()})
    '''
  @TODO:
  Create error handlers for all expected errors
  including 404 and 422.
  '''
    @app.errorhandler(404)
    def not_found(error):
        return jsonify({
            "success": False,
            "error": 404,
            "message": "Not found"
            }), 404
    @app.errorhandler(422)
    def not_found(error):
        return jsonify({
            "success": False,
            "error": 422,
            "message": "Unprocessed Entity"
            }), 422
    return app
