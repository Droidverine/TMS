import webapp2
import jinja2
import time
from google.appengine.ext import ndb
from google.appengine.api import users
import uuid 
import os


JINJA_ENVIRONMENT = jinja2.Environment(loader=jinja2.FileSystemLoader(os.path.dirname(__file__)+"/"))

#User Model class
class MyUser(ndb.Model):
#Email address of this user
  email_address = ndb.StringProperty()

#EV Model class
class TaskBoard(ndb.Model):
  TaskBoard_Owner=ndb.StringProperty()
  TaskBoard_name=ndb.StringProperty()
  TaskBoard_uid=ndb.StringProperty()
  TaskBoard_members=ndb.StringProperty(repeated=True)

class Tasks(ndb.Model) :
    Task_name=ndb.StringProperty() 
    Task_boardname=ndb.StringProperty()




#Landing page does the authentication
class LoginPage(webapp2.RequestHandler):
    def get(self):
        url = ''
        url_string = ''
        welcome = 'Welcome back'
        myuser = None
        result= None

        user = users.get_current_user()

        if user:
            #if user succesfully logged in
            url = users.create_logout_url('/')
            url_string = 'logout'
            myuser_key = ndb.Key('MyUser', user.user_id())
            myuser = myuser_key.get()
            template = JINJA_ENVIRONMENT.get_template('Home.html')
            q=TaskBoard.query()
            searchq=q.filter(TaskBoard.TaskBoard_Owner==user.email())
            result=searchq.fetch()
            q1=TaskBoard.query()


			#q=TaskBoard.query()
			#searchq = q.filter(TaskBoard.TaskBoard_Owner==user.email())
			#result = searchq.fetch()       
                      

            if myuser == None:
                #if user info not in database insert.
                welcome = 'Welcome to the application'
                myuser = MyUser(id=user.email(), email_address=user.email())
                myuser.email_address = user.email()
                myuser.put()
              

        else:
            #if user not logged in.
            url = users.create_login_url(self.request.uri)
            url_string = 'login'
            template = JINJA_ENVIRONMENT.get_template('Login.html')

    
        template_values = {
            'url' : url,
            'url_string' : url_string,
            'user' : user,
            'welcome' : welcome,
            'myuser' : myuser,
            'result':result
        }
        self.response.write(template.render(template_values))

class TaskBoard_Create(webapp2.RequestHandler):
    def get(self):

      
    #If does'nt exists
        id = uuid.uuid1() 
        av=str(id)
        user = users.get_current_user()
	
        q=TaskBoard.query()
        searchq = q.filter(TaskBoard.TaskBoard_name==self.request.get('TaskBoard_name'),TaskBoard.TaskBoard_Owner==user.email())
        result = searchq.fetch()
        if len(result)<1:
        	taskboardmodel=TaskBoard(id=av)
        	taskboardmodel.TaskBoard_name=self.request.get('TaskBoard_name')
        	taskboardmodel.TaskBoard_Owner=user.email()
        	taskboardmodel.TaskBoard_members=[self.request.get('TaskBoard_members')]
        	taskboardmodel.TaskBoard_uid=av       
        	taskboardmodel.put()
        	self.response.headers['Content-Type'] = 'text/html'
        	self.response.write('Successfully entered')
        else:
        	self.response.headers['Content-Type'] = 'text/html'
        	self.response.write('Oops seems like taskboard already exists')

class TaskBoardAddMembers(webapp2.RequestHandler):
    def get(self):
        if self.request.get('View'):
            q=TaskBoard.query()
            searchq = q.filter(TaskBoard.TaskBoard_name==self.request.get('TaskBoard_name'),TaskBoard.TaskBoard_Owner==user.email())
            result = searchq.fetch()

            template_values = {
            'result':result
             }

            template = JINJA_ENVIRONMENT.get_template('AddMember.html')
            self.response.write(template.render(template_values))
        if self.request.get('AddMember'):
            Tb=ndb.Key(TaskBoard,self.request.get('TaskBoard_uid'))
            q=TaskBoard.query()
            searchq = q.filter(TaskBoard.TaskBoard_name==self.request.get('TaskBoard_name'),TaskBoard.TaskBoard_Owner==user.email())
            result = searchq.fetch()
            Tb.TaskBoard_members=result.append(self.request.get('TaskBoard_members'))	

class AddTask(webapp2.RequestHandler):
    def get(self):
        if self.request.get('ViewTask'):
            q=Tasks.query()
            searchq=q.filter(Tasks.Task_boardname==self.request.get('Task_boardname'))
            result=searchq.fetch()
            template_values = {
            'result':result,
            'Task_boardname':self.request.get('Task_boardname')

             }

            template = JINJA_ENVIRONMENT.get_template('TaskBoard.html')
            self.response.write(template.render(template_values))


        if self.request.get('submit'):
             tk=Tasks()
             tk.Task_name=self.request.get('Task_name')
             tk.Task_boardname=self.request.get('Task_boardname')
             tk.put()

app = webapp2.WSGIApplication([
    ('/', LoginPage),('/TaskBoard_Create',TaskBoard_Create),('/TaskBoardAddMembers',TaskBoardAddMembers),('/AddTask',AddTask)
], debug=True)
