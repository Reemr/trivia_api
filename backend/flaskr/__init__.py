import os
from flask import Flask, request, abort, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
import random

from models import setup_db, Question, Category

QUESTIONS_PER_PAGE = 10

def paginate_questions(request, selection):
  page = request.args.get('page', 1, type=int)
  start = (page - 1) * QUESTIONS_PER_PAGE
  end = start + QUESTIONS_PER_PAGE

  questions = [question.format() for question in selection]
  current_questions = questions[start:end]

  return current_questions

def create_app(test_config=None):
  # create and configure the app
  app = Flask(__name__)
  setup_db(app)
  
  '''
  @TODO: Set up CORS. Allow '*' for origins. Delete the sample route after completing the TODOs
  '''
  CORS(app, resources={r"/api/*": {'origins': '*'}})
  '''
  @TODO: Use the after_request decorator to set Access-Control-Allow
  '''
  @app.after_request
  def after_request(response):
    response.headers.add('Access-Control-Allow-Headers', 'Contente-Type, Authorization')
    response.headers.add('Access-control-Allow-Methods', 'GET, POST, PATCH, DELETE, OPTIONS')
    return response

  '''
  @TODO: 
  Create an endpoint to handle GET requests 
  for all available categories.
  '''
  @app.route('/categories')
  def get_categories():

    selection = Category.query.order_by(Category.id).all()
    # create a dictionary with id as a key and type as a value
    # this format matchs the frontend setup
    categories = {cat.id: cat.type for cat in selection}

    if len(categories) == 0:
      abort(404)

    return jsonify({
        'success': True,
        'categories': categories
    })

  '''
  @TODO: 
  Create an endpoint to handle GET requests for questions, 
  including pagination (every 10 questions). 
  This endpoint should return a list of questions, 
  number of total questions, current category, categories. 

  TEST: At this point, when you start the application
  you should see questions and categories generated,
  ten questions per page and pagination at the bottom of the screen for three pages.
  Clicking on the page numbers should update the questions. 
  '''
  @app.route('/questions')
  def get_questions():
    selection = Question.query.order_by(Question.category).all()
    current_questions = paginate_questions(request, selection) # paginate questions list

    if len(current_questions) == 0:
      abort(404)

    return jsonify({
        'success': True,
        'questions': current_questions,
        'total_questions': len(selection),
        'current_category': Category.query.get(selection[0].category).type,
        'categories': {cat.id: cat.type for cat in Category.query.all()}
    })


  '''
  @TODO: 
  Create an endpoint to DELETE question using a question ID. 

  TEST: When you click the trash icon next to a question, the question will be removed.
  This removal will persist in the database and when you refresh the page. 
  '''
  @app.route('/questions/<int:question_id>', methods=['DELETE'])
  def delete_question(question_id):
    try:
      # filter questions by id
      question = Question.query.filter(Question.id == question_id).one_or_none()
      
      question.delete()

      return jsonify({
          'success': True,
          'deleted': question.id,
      })
      
    except:
      abort(404)

  '''
  @TODO: 
  Create an endpoint to POST a new question, 
  which will require the question and answer text, 
  category, and difficulty score.

  TEST: When you submit a question on the "Add" tab, 
  the form will clear and the question will appear at the end of the last page
  of the questions list in the "List" tab.  
  '''

  '''
  @TODO: 
  Create a POST endpoint to get questions based on a search term. 
  It should return any questions for whom the search term 
  is a substring of the question. 

  TEST: Search by any phrase. The questions list will update to include 
  only question that include that string within their question. 
  Try using the word "title" to start. 
  '''

  @app.route('/questions', methods=['POST'])
  def create_question():

    body = request.get_json()

    new_question = body.get('question', None)
    new_answer = body.get('answer', None)
    new_category = body.get('category', None)
    new_difficulty_score = body.get('difficulty', None)
    search = body.get('searchTerm', None)

    # if search term is true then the method is to search for a word
    # else the method is to create a question

    if search:
      selection = Question.query.order_by(Question.id).filter(Question.question.ilike('%{}%'.format(search))).all()

      return jsonify({
        'success': True,
        'questions': [question.format() for question in selection],
        'total_questions': len(selection),
        'current_category': Category.query.get(selection[0].category).type
      })

    elif new_question:

      question = Question(question=new_question, answer=new_answer, category=new_category, difficulty=new_difficulty_score)
      question.insert()
          
      return jsonify({
          'success': True
      })
    else:
      abort(400)

  '''
  @TODO: 
  Create a GET endpoint to get questions based on category. 

  TEST: In the "List" tab / main screen, clicking on one of the 
  categories in the left column will cause only questions of that 
  category to be shown. 
  '''

  @app.route('/categories/<int:category_id>/questions')
  def get_questions_category(category_id):

    try:
      selection = Question.query.filter(Question.category == str(category_id)).all()
      questions = [question.format() for question in selection]

      return jsonify({
          'success': True,
          'questions': questions,
          'total_questions': len(questions),
          'current_category': Category.query.get(category_id).type
      })

    except:
      abort(404)


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
  def play_quiz():

    body = request.get_json()

    previous_questions = body.get('previous_questions', None)
    quiz_category = body.get('quiz_category', None)
    

    if quiz_category['type'] == 'click': # when clicking ALL in frontend it sends type click 
      questions = Question.query.order_by(Question.id).all()
    else:
      # add one to category id because frontend sends ids starting from 0
      # the table Category has categories id starting from 1
      cat_id = int(quiz_category['id'])
      questions = Question.query.filter(Question.category == str(cat_id)).all()

    question_ids = [qi.id for qi in questions]
    choices = list(set(question_ids).difference(previous_questions)) # remove previous questions from the list of choices

    if choices: # if there are ids in choices select random id from them
      random_question = random.choice(choices) 
      question = Question.query.get(random_question)
    else:
      abort(422)

    return jsonify({
        'success': True,
        'question': question.format()
    })


  '''
  @TODO: 
  Create error handlers for all expected errors 
  including 404 and 422. 
  '''

  @app.errorhandler(422)
  def unporocessable(error):
    return jsonify({
        'success': False,
        'error': 422,
        'message': 'unprocessable'
    }), 422

  @app.errorhandler(404)
  def not_found(error):
    return jsonify({
        'success': False,
        'error': 404,
        'message': 'resources not found'
    }), 404
  
  @app.errorhandler(400)
  def bas_request(error):
    return jsonify({
        'success': False,
        'error': 400,
        'message': 'bad request'
    }), 400

  @app.errorhandler(405)
  def method_not_allowed(error):
    return jsonify({
        'success': False,
        'error': 405,
        'message': 'method not allowed'
      }), 405

  @app.errorhandler(500)
  def internal_server_error(error):
    return jsonify({
        'success': False,
        'error': 500,
        'message': 'internal server error'
      }), 500
  
  return app

    