from wsgi import app
import os

if __name__ == '__main__':
    app.config['DEBUG'] = False
    # app.config['PROPAGATE_EXCEPTIONS'] = True
    app.run(port=int(os.getenv('PORT', 5000))) #, debug=os.getenv('DEBUG', 'True').lower() == 'true')