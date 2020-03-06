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

#Taskboard Model class
class TaskBoard(ndb.Model):
  TaskBoard_Owner=ndb.StringProperty()
  TaskBoard_name=ndb.StringProperty()
  TaskBoard_uid=ndb.StringProperty()
  TaskBoard_members=ndb.StringProperty(repeated=True)

#Task Model class
class Tasks(ndb.Model) :
    Task_name=ndb.StringProperty() 
    Task_boardname=ndb.StringProperty()
    Task_due=ndb.StringProperty()
    Task_owner=ndb.StringProperty()




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
            #members
            members=TaskBoard.query()
            searchm=members.fetch()
            print("members")
            for i in searchm:
                temp=i.TaskBoard_members
                if user.email() in temp:
                	result.append(i)


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

#To create TaskBoard
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

#For viwing and creating taskboard
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

#For viewing and creating Task
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

            template = JINJA_ENVIRONMENT.get_template('ViewTask.html')
            self.response.write(template.render(template_values))

        if self.request.get('View'):
            print("addview")
            template_values = {
            'Task_boardname':self.request.get('Task_boardname')
             }

            template = JINJA_ENVIRONMENT.get_template('AddTask.html')
            self.response.write(template.render(template_values))

        if self.request.get('submit'):
             q=Tasks.query().filter(Tasks.Task_name==self.request.get('Task_name'),Tasks.Task_boardname==self.request.get('Task_boardname'))
             result=list(q.fetch())
             if len(result)<1:
                tk=Tasks(id=self.request.get('Task_name')+""+self.request.get('Task_boardname'))
                tk.Task_name=self.request.get('Task_name')
                tk.Task_boardname=self.request.get('Task_boardname')
                tk.Task_due=self.request.get('Task_due')
                tk.Task_owner=self.request.get('Task_owner')
                tk.put()
                time.sleep(1)
                self.redirect('/AddTask?ViewTask=True&Task_boardname='+self.request.get('Task_boardname'))

            
             else:
                self.response.headers['Content-Type'] = 'text/html'
                self.response.write('Oops..!!! Seems like task already exists in this task board. ')
             	   

app = webapp2.WSGIApplication([
    ('/', LoginPage),('/TaskBoard_Create',TaskBoard_Create),('/TaskBoardAddMembers',TaskBoardAddMembers),('/AddTask',AddTask)
], debug=True)
