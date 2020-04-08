import webapp2
import jinja2
import time
from google.appengine.ext import ndb
from google.appengine.api import users
import uuid
import os
from urlparse import urlparse, parse_qs

JINJA_ENVIRONMENT = jinja2.Environment(loader=jinja2.FileSystemLoader(os.path.dirname(__file__)+"/"))

#User Model class
class Users(ndb.Model):
#Email address of this user
  email_address = ndb.StringProperty()
  users_taskboardslist=ndb.StringProperty(repeated=True)

#Taskboard Model class
class TaskBoard(ndb.Model):
  TaskBoard_Owner=ndb.StringProperty()
  TaskBoard_name=ndb.StringProperty()
  TaskBoard_uid=ndb.StringProperty()
  TaskBoard_members=ndb.StringProperty(repeated=True)
  TaskBoard_tasksuidlist=ndb.StringProperty(repeated=True)

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
            myuser_key = ndb.Key('Users', user.email())
            myuser = myuser_key.get()
            template = JINJA_ENVIRONMENT.get_template('Home.html')
            userdata = ndb.Key('Users', user.email()).get()
            result=[]
            #query only to get users

            q=Users.query()
            us =q.fetch()
            usersinsystem=[]
            for i in us:
              usersinsystem.append(i.email_address)
            usersinsystem.append('')
            if(user.email() in usersinsystem):
              usersinsystem.remove(user.email())



            if myuser!=None:
                taskboardslist=userdata.users_taskboardslist
                for i in taskboardslist:
            	  if(i!='ep'):
                    taskboardslist = ndb.Key(TaskBoard,i).get()
                    result.append(taskboardslist)



            if myuser == None:
                #if user info not in database insert.
                welcome = 'Welcome to the application'
                abc=['ep']
                myuser = Users(id=user.email())
                myuser.email_address = user.email()
                myuser.users_taskboardslist=abc
                myuser.put()


        else:
            #if user not logged in.
            url = users.create_login_url(self.request.uri)
            url_string = 'login'
            template = JINJA_ENVIRONMENT.get_template('Login.html')


       
        if( myuser == None):
          template_values = {
            'url' : url,
            'url_string' : url_string,
            'user' : user,
            'welcome' : welcome,
            'myuser' : myuser,
            'result':result,

        }
        else:
          template_values = {
            'url' : url,
            'url_string' : url_string,
            'user' : user,
            'welcome' : welcome,
            'myuser' : myuser,
            'result':result,
            'usersinsystem':usersinsystem

        } 
        self.response.write(template.render(template_values))

#To create TaskBoard
class TaskBoard_Create(webapp2.RequestHandler):
    def get(self):

    #If does'nt exists
       #  av=str(id)
        user = users.get_current_user()

        taskboardchecker = ndb.Key('TaskBoard',""+self.request.get('TaskBoard_name')+""+user.email()).get()

        if taskboardchecker==None:
            taskboardmodel=TaskBoard(id=self.request.get('TaskBoard_name')+""+user.email())
            taskboardmodel.TaskBoard_name=self.request.get('TaskBoard_name')
            taskboardmodel.TaskBoard_Owner=user.email()
            taskboardmodel.TaskBoard_members=[self.request.get('TaskBoard_members')]
            taskboardmodel.TaskBoard_uid=self.request.get('TaskBoard_name')+""+user.email()
            taskboardmodel.TaskBoard_tasksuidlist=['ep']
            taskboardmodel.put()
            userid = user.email()
            userdata = ndb.Key('Users', user.email()).get()
            if(userdata.users_taskboardslist):
                ulist=list(userdata.users_taskboardslist)
                ulist.append(self.request.get('TaskBoard_name')+""+user.email())
                userdata.users_taskboardslist=ulist
            else:
            	ulist=[self.request.get('TaskBoard_name')+""+user.email()]

            userdata.put()
            print('ghe')
            print(ulist)

            self.response.headers['Content-Type'] = 'text/html'
            self.response.write('Successfully entered')
        else:
            self.response.headers['Content-Type'] = 'text/html'
            self.response.write('Oops seems like taskboard already exists')

#For viwing and creating taskboard
class TaskBoardAddMembers(webapp2.RequestHandler):
    def get(self):
        if self.request.get('View'):
          #query only to get users
            searchq = ndb.Key(self.request.get('TaskBoard_name')+""+user.email()).get
            result = searchq
            q=Users.query()
            us =q.fetch()
            usersinsystem=[]
            for i in us:
              usersinsystem.append(i.email_address)
            usersinsystem.append('')
            print('usersinsystem')        

            print(usersinsystem)    

            template_values = {
            'result':result,
            'usersinsystem':usersinsystem,
            'TaskBoard_uid':self.request.get('TaskBoard_uid')
             }

            template = JINJA_ENVIRONMENT.get_template('AddMember.html')
            self.response.write(template.render(template_values))
        if self.request.get('AddMemberView'):
            user = users.get_current_user()
            q=Users.query()
            us =q.fetch()
            usersinsystem=[]
            for i in us:
              usersinsystem.append(i.email_address)
            usersinsystem.append('')
            if user.email() in usersinsystem:
              usersinsystem.remove(user.email())
            print('usersinsystem')        

            print(usersinsystem)    
            q=TaskBoard.query()
            searchq = q.filter(TaskBoard.TaskBoard_name==self.request.get('TaskBoard_name'),TaskBoard.TaskBoard_Owner==user.email())
            result = searchq.fetch()

            template_values = {
            'result':result,
            'usersinsystem':usersinsystem,
            'TaskBoard_uid':self.request.get('TaskBoard_uid')
             }

            template = JINJA_ENVIRONMENT.get_template('AddMember.html')
            self.response.write(template.render(template_values))
        if self.request.get('AddMember'):
            user = users.get_current_user()
            print('ghghghghgh')
            print(self.request.get('TaskBoard_uid'))
            parsed_url = urlparse(self.request.get('TaskBoard_uid'))
            print(parsed_url.path)
            Tb=ndb.Key(TaskBoard,parsed_url.path).get()

            print('shivraj')
            print(Tb.TaskBoard_members)
            kk=Tb.TaskBoard_members
            fin=kk

            updatetaskboardlist = ndb.Key('Users', self.request.get('TaskBoard_members')).get()
            if updatetaskboardlist==None:
                self.response.headers['Content-Type'] = 'text/html'
                self.response.write('Oops seems like No users exists in system with this email ID')
            else:
                existingtaskboardslist=updatetaskboardlist.users_taskboardslist
                existingtaskboardslist.append(parsed_url.path)
                updatetaskboardlist.users_taskboardslist=existingtaskboardslist
                updatetaskboardlist.put()
                print('addd users')
                print(updatetaskboardlist)
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
            parsed_url = urlparse(self.request.get('TaskBoard_uid'))
            Taskslistmodel=ndb.Key(TaskBoard,self.request.get('TaskBoard_uid')).get()
            print('taskslist')
            print(Taskslistmodel.TaskBoard_tasksuidlist)
            templist=Taskslistmodel.TaskBoard_tasksuidlist
            result=[]
            for i in templist:
                if(i!='ep'):
                    taskslist = ndb.Key(Tasks,i).get()
                    result.append(taskslist)
            print(result)

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
             print('taskname')
             parsed_url = urlparse(self.request.get('TaskBoard_uid'))
             print(parsed_url.path)
             taskchecker = ndb.Key(TaskBoard,parsed_url.path).get()
             templiste=taskchecker.TaskBoard_tasksuidlist
             print("ali")
             print(templiste)


             if self.request.get('Task_name') in str(templiste):
                self.response.headers['Content-Type'] = 'text/html'
                self.response.write('Oops..!!! Seems like task already exists in this task board. ')


             else:

                tk=Tasks(id=parsed_url.path+""+self.request.get('Task_name'))
                tk.Task_uid=parsed_url.path+""+self.request.get('Task_name')
                tk.Task_name=self.request.get('Task_name')
                tk.Task_boardname=self.request.get('Task_boardname')
                tk.Task_due=self.request.get('Task_due')
                tk.Task_owner=self.request.get('Task_owner')
                tk.Task_status="False"
                tk.put()
                templist=taskchecker.TaskBoard_tasksuidlist
                print('alalalalalalal')
                print(templist)
                templist.append(parsed_url.path+""+self.request.get('Task_name'))
                taskchecker.TaskBoard_tasksuidlist=templist
                taskchecker.put()
                time.sleep(1)
                self.redirect('/AddTask?ViewTask=True&Task_boardname='+self.request.get('Task_boardname')+'&TaskBoard_uid='+self.request.get('TaskBoard_uid'))


class EditTask(webapp2.RequestHandler):
    def get(self):
        if self.request.get('EditStatus'):
           iad=self.request.get('Task_uid')
           es = ndb.Key('Tasks',iad).get()
           print(es)
           es.Task_status='True'
           es.put()
           Taskslistmodel=ndb.Key(TaskBoard,self.request.get('TaskBoard_uid')).get()
           Taskslistmodel=Taskslistmodel.TaskBoard_tasksuidlist
           result=[]
           for i in Taskslistmodel:
               Taskslistmodel=ndb.Key(Tasks,i).get()
               result.append(Taskslistmodel)
               print(i)
           template_values = {
           'result':result,
           'Task_boardname':self.request.get('Task_boardname'),
           'TaskBoard_uid':self.request.get('TaskBoard_uid')


            }

           template = JINJA_ENVIRONMENT.get_template('ViewTask.html')
           self.response.write(template.render(template_values))

        if self.request.get('EditView'):
           rst=ndb.Key(Tasks,self.request.get('Task_uid')).get()
           #Query used only to get the taskboard members
           q1=TaskBoard.query()
           searchq1=q1.filter(TaskBoard.TaskBoard_uid==self.request.get('TaskBoard_uid'))
           rst1=list(searchq1.fetch())

           rst1=rst1[0]
           membersarray=rst1.TaskBoard_members
           result=rst
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

           #q=Tasks.query()
           #searchq=q.filter(Tasks.Task_boardname==self.request.get('Task_boardname'),Tasks.Task_name==self.request.get('Task_name'))
           #rst=list(searchq.fetch())
           parsed_tkname = urlparse(self.request.get('Task_name'))
           parsed_tkboard = urlparse(self.request.get('Task_boardname'))
           parsed_tkowner=urlparse(self.request.get('Task_owner'))
           parsed_tkuid=urlparse(self.request.get('Task_uid'))
           tkname=parsed_tkname.path
           tkboardname=parsed_tkboard.path
           tkowner=parsed_tkowner.path
           tkuid=parsed_tkuid.path
           oldname=ndb.Key(Tasks,tkuid).get()
           if(oldname.Task_name!=tkname):
               print('avvv')

               rst=ndb.Key(Tasks,self.request.get('TaskBoard_uid')+""+tkname).get()
               if(rst!=None):
                    self.response.headers['Content-Type'] = 'text/html'
                    self.response.write('Oops..!!! Seems like task already exists in this task board. ')

               else:
                   print('bhadva')
                   print(self.request.get('TaskBoard_uid'))
                   iad=self.request.get('Task_uid')
                   oldtk=ndb.Key('Tasks',iad).get()
                   oldtk.key.delete()
                   tkboardupdate=ndb.Key("TaskBoard",self.request.get('TaskBoard_uid')).get()
                   tasksuidlist=tkboardupdate.TaskBoard_tasksuidlist
                   taskboardowner=tkboardupdate.TaskBoard_Owner
                   taskboardmembers=tkboardupdate.TaskBoard_members
                   taskboarduid=tkboardupdate.TaskBoard_uid
                   taskboardname=tkboardupdate.TaskBoard_name
                   print('lele')
                   tasksuidlist.remove(iad)
                   print(taskboardname)

                   es=Tasks(id=self.request.get('TaskBoard_uid')+""+tkname)
                   print(es)
                   if(self.request.get('Task_name')):
                       es.Task_name=tkname
                   if(self.request.get('Task_owner')):
                       es.Task_owner=tkowner
                   if(self.request.get('Task_due')):
                       es.Task_due=self.request.get('Task_due')

                   es.Task_status="False"
                   es.Task_boardname=taskboardname
                   es.Task_uid=self.request.get('TaskBoard_uid')+""+tkname
                   es.put()


                   tasksuidlist.append(self.request.get('TaskBoard_uid')+""+tkname)
                   tkboardupdate=TaskBoard(id=self.request.get('TaskBoard_uid'))
                   tkboardupdate.TaskBoard_tasksuidlist=tasksuidlist
                   tkboardupdate.TaskBoard_Owner=taskboardowner
                   tkboardupdate.TaskBoard_members=taskboardmembers
                   tkboardupdate.TaskBoard_uid=taskboarduid
                   tkboardupdate.TaskBoard_name=taskboardname
                   tkboardupdate.put()
               #print('avvv')



                   time.sleep(1)
                   self.redirect('/AddTask?ViewTask=true&Task_boardname='+tkboardname+'&TaskBoard_uid='+taskboarduid)
           else:
               print('avv')
               print('bhadva')
               print(self.request.get('TaskBoard_uid'))
               iad=self.request.get('Task_uid')
               oldtk=ndb.Key('Tasks',iad).get()
               oldtk.key.delete()
               tkboardupdate=ndb.Key("TaskBoard",self.request.get('TaskBoard_uid')).get()
               tasksuidlist=tkboardupdate.TaskBoard_tasksuidlist
               taskboardowner=tkboardupdate.TaskBoard_Owner
               taskboardmembers=tkboardupdate.TaskBoard_members
               taskboarduid=tkboardupdate.TaskBoard_uid
               taskboardname=tkboardupdate.TaskBoard_name
               print('lele')
               tasksuidlist.remove(iad)
               print(taskboardname)

               es=Tasks(id=self.request.get('TaskBoard_uid')+""+tkname)
               print(es)
               if(self.request.get('Task_name')):
                  es.Task_name=tkname
               if(self.request.get('Task_owner')):
                  es.Task_owner=tkowner
               if(self.request.get('Task_due')):
                  es.Task_due=self.request.get('Task_due')

               es.Task_status="False"
               es.Task_boardname=taskboardname
               es.Task_uid=self.request.get('TaskBoard_uid')+""+tkname
               es.put()


               tasksuidlist.append(self.request.get('TaskBoard_uid')+""+tkname)
               tkboardupdate=TaskBoard(id=self.request.get('TaskBoard_uid'))
               tkboardupdate.TaskBoard_tasksuidlist=tasksuidlist
               tkboardupdate.TaskBoard_Owner=taskboardowner
               tkboardupdate.TaskBoard_members=taskboardmembers
               tkboardupdate.TaskBoard_uid=taskboarduid
               tkboardupdate.TaskBoard_name=taskboardname
               tkboardupdate.put()
               print('avvv')



               time.sleep(1)
               self.redirect('/AddTask?ViewTask=true&Task_boardname='+tkboardname+'&TaskBoard_uid='+taskboarduid)



app = webapp2.WSGIApplication([
    ('/', LoginPage),('/TaskBoard_Create',TaskBoard_Create),('/TaskBoardAddMembers',TaskBoardAddMembers),('/AddTask',AddTask),
    ('/EditTask',EditTask)
], debug=True)
