Jira Tool
============

Tool for querying jira server, updating fields for specific jira issue id and creating new jira issue id.


##PIP Requirements:
-jira
-pbr

##usage

```bash
jiratool.py [-h] {create,update,get} ...

positional arguments:
  {create,update,get}  commands
    create             create new issue
    update             update existing issue
    get                get field values or issue list

optional arguments:
  -h, --help           show this help message and exit
```

##Examples:

CREATE

```bash
Options:
 -t --title bug title summary [mandatory param]
 -co --component component name [mandatory param]
 -fov --foundversion found in version [mandatory param]
 -ae --assignee ASSIGNEE
 -d --description bug description

python jiratool.py create -t "Bug Title:Test bug" -co "Tools" -fov 4.5 -ae "firstname.lastname" -d "Test bug over API"
```

UPDATE

```bash
Options:
  -i --jiraid Jira ID [mandatory param]
  -fxv --fixversion Fix Versions
  -g --gerritnum gerrit changelist number
  -b --branch branch name
  -c --comment comment
  -d --description description text

#update fix version

python jiratool.py update -i MYPROJ-24419 -fxv 4.4.2

#update bug description

python jiratool.py update -i MYPROJ-24419 -d "merged to single utility"

#update bug comment

python jiratool.py update -i MYPROJ-24419 -c "reduced variables"

#update gerrit change-list in comment section

python jiratool.py update -i MYPROJ-24419 -g 65013

#assignee bug to new owner 

python jiratool.py update -i MYPROJ-24419 -ae 'firstname.lastname'

#update jira fix summary field with commit details

python jiratool.py update -i MYPROJ-26493 -fxs -b 'featureA' -g '65013' -fxv '4.5' -cod "testuser,05-04-2018,newfix"
```


GET

```bash
Options:

  -i --jiraid Jira Id
  -f --fieldname Jira fieldname
  -tv --targetversion Target Version
  -av --affectsversion Affects Version
  -fxv --fixversion Fix Versions
  -fov --foundversion Found in version
  -m --maxResults maxResults [default,50]

#get resoultion field value

python jiratool.py get -i MYPROJ-24419 -f resolution

#get bug field status

python jiratool.py get -i MYPROJ-24419 -f status

#get bug field fixversion

python jiratool.py get -i MYPROJ-24419 -f fixversion

#get bug field target version

python jiratool.py get -i MYPROJ-24419 -f targetversion

#get bug field found in version

python jiratool.py get -i MYPROJ-24419 -f foundversion

#get bug field affected version

python jiratool.py get -i MYPROJ-24419 -f affectedversion

#get bug field assignee

python jiratool.py get -i MYPROJ-25628 -f assignee

#get bug list matching target version

python jiratool.py get -tv 4.4.1.2

#get bug list matching fix version

python jiratool.py get -fxv 4.5

#get bug list matching affects version

python jiratool.py get -av 4.5

#get bug list matching found in version

python jiratool.py get -fov 4.5

#get bug list matching the jira query string

python jiratool.py get -qs "project = MYPROJ AND summary ~ 'dummy jira bug for testing' AND status=cancelled"
```
