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
    Task_status=ndb.StringProperty()
    Task_uid=ndb.StringProperty()




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
            'result':result,
            'TaskBoard_uid':self.request.get('TaskBoard_uid')
             }

            template = JINJA_ENVIRONMENT.get_template('AddMember.html')
            self.response.write(template.render(template_values))
        if self.request.get('AddMemberView'):
            user = users.get_current_user()

            q=TaskBoard.query()
            searchq = q.filter(TaskBoard.TaskBoard_name==self.request.get('TaskBoard_name'),TaskBoard.TaskBoard_Owner==user.email())
            result = searchq.fetch()

            template_values = {
            'result':result,
            'TaskBoard_uid':self.request.get('TaskBoard_uid')
             }

            template = JINJA_ENVIRONMENT.get_template('AddMember.html')
            self.response.write(template.render(template_values))	
        if self.request.get('AddMember'):
            user = users.get_current_user()
            print('ghghghghgh')
            print(self.request.get('TaskBoard_uid'))
            Tb=ndb.Key(TaskBoard,self.request.get('TaskBoard_uid')).get()
            q=TaskBoard.query()
            searchq = q.filter(TaskBoard.TaskBoard_uid==self.request.get('TaskBoard_uid'))
            result = searchq.fetch()
            print('shivraj')
            kbc=result[0]
            kk=kbc.TaskBoard_members
            fin=list(kbc.TaskBoard_members)
            nl=[self.request.get('TaskBoard_members')]
            for f in fin:
                nl.append(f)
            print(nl)

            Tb.TaskBoard_members=nl
            Tb.put()
            self.redirect('/')	            


#For viewing and creating Task
class AddTask(webapp2.RequestHandler):
    def get(self):
        if self.request.get('ViewTask'):
            q=Tasks.query()
            searchq=q.filter(Tasks.Task_boardname==self.request.get('Task_boardname'))
            result=searchq.fetch()
            template_values = {
            'result':result,
            'Task_boardname':self.request.get('Task_boardname'),
            'TaskBoard_uid':self.request.get('TaskBoard_uid')

             }

            template = JINJA_ENVIRONMENT.get_template('ViewTask.html')
            self.response.write(template.render(template_values))

        if self.request.get('View'):
            print("addview")
            template_values = {
            'Task_boardname':self.request.get('Task_boardname'),
            'TaskBoard_uid':self.request.get('TaskBoard_uid')
             }

            template = JINJA_ENVIRONMENT.get_template('AddTask.html')
            self.response.write(template.render(template_values))

        if self.request.get('submit'):
             q=Tasks.query().filter(Tasks.Task_name==self.request.get('Task_name'),Tasks.Task_boardname==self.request.get('Task_boardname'))
             result=list(q.fetch())
             if len(result)<1:
             	id = uuid.uuid1() 
                av=str(id)
                tk=Tasks(id=av)
                tk.Task_uid=av
                tk.Task_name=self.request.get('Task_name')
                tk.Task_boardname=self.request.get('Task_boardname')
                tk.Task_due=self.request.get('Task_due')
                tk.Task_owner=self.request.get('Task_owner')
                tk.Task_status="False"
                tk.put()
                time.sleep(1)
                self.redirect('/AddTask?ViewTask=True&Task_boardname='+self.request.get('Task_boardname'))

            
             else:
                self.response.headers['Content-Type'] = 'text/html'
                self.response.write('Oops..!!! Seems like task already exists in this task board. ')
             	   
class EditTask(webapp2.RequestHandler):
    def get(self):
        if self.request.get('EditStatus'):
           iad=self.request.get('Task_uid')
           es = ndb.Key('Tasks',iad).get()
           print(es)
           es.Task_status='True'
           #es.Task_status="True"
           es.put()
           q=Tasks.query()
           searchq=q.filter(Tasks.Task_boardname==self.request.get('Task_boardname'))
           result=searchq.fetch()
           template_values = {
           'result':result,
           'Task_boardname':self.request.get('Task_boardname')


            }

           template = JINJA_ENVIRONMENT.get_template('ViewTask.html')
           self.response.write(template.render(template_values))

        if self.request.get('EditView'):
           q=Tasks.query()
           searchq=q.filter(Tasks.Task_uid==self.request.get('Task_uid'))
           rst=list(searchq.fetch())
           #To get the taskboard members
           q1=TaskBoard.query()
           searchq1=q1.filter(TaskBoard.TaskBoard_uid==self.request.get('TaskBoard_uid'))
           rst1=searchq1.fetch()
           rst1=rst1[0]
           membersarray=rst1.TaskBoard_members
           result=rst[0]
           print("editview")
           print(result)
           template_values = {
           'Task_name':self.request.get('Task_name'),
           'Task_boardname':self.request.get('Task_boardname'),
           'result':result,
           'Taskboard':rst1,
           'TaskBoard_members': membersarray,
           'TaskBoard_uid':self.request.get('TaskBoard_uid')

            }

           template = JINJA_ENVIRONMENT.get_template('TaskEditView.html')
           self.response.write(template.render(template_values))

        if self.request.get('EditTask'):

           q=Tasks.query()
           searchq=q.filter(Tasks.Task_boardname==self.request.get('Task_boardname'),Tasks.Task_name==self.request.get('Task_name'))
           rst=list(searchq.fetch())
           if(len(rst)>0):
                self.response.headers['Content-Type'] = 'text/html'
                self.response.write('Oops..!!! Seems like task already exists in this task board. ')


           else:
            print('bhadva')
            print(self.request.get('TaskBoard_uid'))
            iad=self.request.get('Task_uid')
            es=ndb.Key('Tasks',iad).get()
            print(es)
            if(self.request.get('Task_name')):
                es.Task_name=self.request.get('Task_name')
            if(self.request.get('Task_owner')):    
                es.Task_owner=self.request.get('Task_owner')
            if(self.request.get('Task_due')):    
                es.Task_due=self.request.get('Task_due')
                    
                #es.Task_status="True" 
            es.put()
            q=Tasks.query()
            searchq=q.filter(Tasks.Task_boardname==self.request.get('Task_boardname'))
            result=searchq.fetch()
            
            time.sleep(1)
            self.redirect('/AddTask?ViewTask=true&Task_boardname='+self.request.get('Task_boardname')+"&TaskBoard_uid="+self.request.get('TaskBoard_uid'))



app = webapp2.WSGIApplication([
    ('/', LoginPage),('/TaskBoard_Create',TaskBoard_Create),('/TaskBoardAddMembers',TaskBoardAddMembers),('/AddTask',AddTask),
    ('/EditTask',EditTask)
], debug=True)
