import urllib.request
import getpass
import json      
import base64
import os
import hvac

class BBForkStarterPack(object):
    
    def __init__(self):

        while True:
            self.username = input("Stash Username:")
            self.password = getpass.getpass("Password for " + self.username + ":")
            self.project = input("Project Name (Ex. ProjectTest):")
            self.project_key = input("Short Key for project name (Ex. TST):")
            self.project_desc = input("Project Description:")
            if self.username == "" or self.password == "" or self.project == "" or self.project_key == "":
                print("Sorry, none of the values above can be empty.")
                continue
            else:
                break
        
        create_project = self.create_project()
        if create_project == 201:
            print ("Project " + self.project + " created :)")
            fork_starter_pack = self.fork_starter_pack()
            if fork_starter_pack == 201:
                print ("Fork Starter Pack executed")
        else:
            print ("Project already exist")
            pass
        set_permission = self.project_permission()
        if set_permission == 204:
            print ("Permissions configured")
        create_webhook = self.create_webhook()
        if create_webhook == 201:
            print ("Atlantis Webhook configured")

    def make_request(self, body, url, method=None):
        userpass = self.username + ':' + self.password
        str_bytes = str.encode(userpass)
        b64Val = (base64.b64encode(str_bytes)).decode('utf-8')
    
        if method == 'PUT':
            req = urllib.request.Request(url, method=method)
        else:
            req = urllib.request.Request(url)
        req.add_header('Content-Type', 'application/json; charset=utf-8')
        req.add_header('Authorization', 'Basic %s' % b64Val)
    
        jsondata = json.dumps(body)
        jsondataasbytes = jsondata.encode('utf-8')
   
        try:
            if method == 'PUT':
                response = urllib.request.urlopen(req)
            else:
                response = urllib.request.urlopen(req, jsondataasbytes)
            with response as f:
                pass
            return f.status
        except urllib.error.HTTPError:
            pass
       
    def create_project(self):
        body = { 'key': self.project_key, 'name': self.project, 'description': self.project_desc }
        url = "https://bitbucket.repo.domain/rest/api/1.0/projects/"
        request = self.make_request(body, url)
    
        return request
    
    def fork_starter_pack(self):
        body = {'name': 'Infrastructure', 'project': {'key': self.project_key}}
        url = "https://bitbucket.repo.domain/rest/api/1.0/projects/<Project-To-Fork-From>/repos/<Repo-To-Fork-From>"
        request = self.make_request(body, url)
    
        return request
    
    def project_permission(self):
        body = {}
        method = 'PUT'
        users = ['user1', 'user2', 'user3']
        urls = []
        for user in users:
            user_url = 'https://bitbucket.repo.domain/rest/api/1.0/projects/' + self.project_key + '/repos/<repositoryslug>/permissions/users?name=' + user + '&permission=REPO_WRITE'
            urls.append(user_url)
    
        repo_group_access_url = 'https://bitbucket.repo.domain/rest/api/1.0/projects/' + self.project_key + '/repos/<repositoryslug>/permissions/groups?name=<randon_user1>&permission=REPO_ADMIN'
        urls.append(repo_group_access_url)
    
        project_group_access_url = 'https://bitbucket.repo.domain/rest/api/1.0/projects/' + self.project_key + '/permissions/groups?name=<randon_user2>&permission=PROJECT_ADMIN'
        urls.append(project_group_access_url)
    
        for url in urls:
            request = self.make_request(body, url, method)
            return request
    
    def create_webhook(self):
        client = hvac.Client()
        client = hvac.Client(url=os.environ['VAULT_ADDR'])
        client.auth_userpass(self.username, self.password)
        result = client.read('<vault-secret-path>')
        atlantis_pwd = result.get('data').get('<atlantis-pwd-key>')
    
        body = {'name':'Atlantis','events':['pr:deleted','pr:modified','pr:opened','repo:refs_changed','pr:comment:added','pr:declined','pr:merged'],'configuration':{'secret':atlantis_pwd},'url':'https://atlantis.domain/events','active': True}
        url = 'https://bitbucket.repo.domain/rest/api/1.0/projects/' + self.project_key + '/repos/<repositoryslug>/webhooks'
        request = self.make_request(body, url)
    
        return request
    
BBForkStarterPack()
