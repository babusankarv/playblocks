#!/usr/bin/env python
"""list of functions to interact with Jira Server
Supports creating jira issue
Supports updating specific fields in Jira for a given issue id
Get field values for specific jira id as well as search list of issues"""

from jira import JIRA
from jira.exceptions import JIRAError


class JiraUtils(object):
    """List of functions to interact with Jira Server."""

    def __init__(self, jiraserver, jirauser, jiraapitoken):
        """Initialize Jira Server connection parameters."""
        self.jiraserver = jiraserver
        self.jirauser = jirauser
        self.jiraapitoken = jiraapitoken

    def Connect(self):
        """Connection to Jira Server."""
        try:
            jira_site = JIRA(basic_auth=(self.jirauser, self.jiraapitoken),
                             options={'server': self.jiraserver})
        except JIRAError:
            print 'connection failed'
            return None
        return jira_site

    def GetBugDetails(self, site, bug_id):
        """Get field details for specified bug."""
        myjira_site = site
        issue_id = bug_id
        try:
            issue = myjira_site.issue(issue_id)
        except JIRAError as e:
            print e
            return None
        return issue

    def UpdateFix(self, issue, fixversion):
        """Update fix version for specified bug."""
        curfixlist = []
        newfixvers = fixversion
        if issue is not None:
            for fix in issue.fields.fixVersions:
                curfixlist.append({"name": fix.name})
            if ({"name": newfixvers}) not in curfixlist:
                curfixlist.append({"name": newfixvers})
            else:
                return 'SKIPPED'
            try:
                issue.update(fields={"fixVersions": curfixlist})
            except JIRAError as e:
                print e
                return None
        return 'SUCCESS'

    def UpdateFixSummary(self, issue, fixsummary):
        """Update fix version for specified bug."""
        current_text = ""
        table_header = "||Branch||REL||Date||Author||Subject||Link||\r"
        if issue is not None:
            current_text = issue.fields.customfield_13188
            if current_text is None:
                current_text = table_header+fixsummary
            else:
                current_text = current_text+fixsummary
            try:
                issue.update(fields={"customfield_13188": current_text})
            except JIRAError as e:
                print e
                return None
        return 'SUCCESS'

    def UpdateComments(self, site, issue, commentstring):
        """Update comment for a specified bug."""
        myjira_site = site
        if myjira_site is not None:
            try:
                myjira_site.add_comment(issue, commentstring)
            except JIRAError as e:
                print e
                return None
        return 'SUCCESS'

    def UpdateAssignee(self, issue, assigneename):
        """Update assigneename for a specified bug."""
        if issue is not None:
            try:
                issue.update(assignee={'name': assigneename})
            except JIRAError as e:
                print e
                return None
        return 'SUCCESS'

    def UpdateDescription(self, issue, newdescription):
        """Update description for a specified bug."""
        if issue is not None:
            try:
                issue.update(fields={'description': newdescription})
            except JIRAError as e:
                print e
                return None
        return 'SUCCESS'

    def UpdateGerritLink(self, site, issue, gerrit_num):
        """Update gerrit link for a specified bug."""
        myjira_site = site
        if issue is not None:
            localcommentstring = "http://mygerrit:8080/#/c/%s" % gerrit_num
            try:
                myjira_site.add_comment(issue, localcommentstring)
            except JIRAError as e:
                print e
                return None
        return 'SUCCESS'

    def CreateNewIssue(self, site, **issue_data):
        """Create new Jira issue."""
        myjira_site = site
        try:
            new_issue = myjira_site.create_issue(fields=issue_data)
        except JIRAError as e:
            print e
            return None
        return new_issue

    def GetBugTargetVersions(self, issue):
        """Get target version for a bug.Jira fieldname is customfield_13167."""
        mytargetversions = []
        if hasattr(issue.fields, "customfield_13167"):
            if issue.fields.customfield_13167 is not None:
                for item in issue.fields.customfield_13167:
                    mytargetversions.append(item.value)
        return mytargetversions

    def GetBugAffectedVersions(self, issue):
        """Get Affected versions for a bug."""
        myaffectedversions = []
        if hasattr(issue.fields, "versions"):
            if issue.fields.versions is not None:
                for item in issue.fields.versions:
                    myaffectedversions.append(item.name)
        return myaffectedversions

    def GetBugfixVersions(self, issue):
        """Get Fix Versions for a bug."""
        myfixversions = []
        if hasattr(issue.fields, "fixVersions"):
            if issue.fields.fixVersions is not None:
                for item in issue.fields.fixVersions:
                    myfixversions.append(item.name)
        return myfixversions

    def GetBugfoundVersions(self, issue):
        """Get Found Versions for a bug,jira fieldname is customfield_13149."""
        myfoundversions = []
        if hasattr(issue.fields, "customfield_13149"):
            if issue.fields.customfield_13149 is not None:
                myfoundversions.append(issue.fields.customfield_13149.value)
        return myfoundversions

    def GetBugStatus(self, issue):
        """Get status for a bug."""
        mystatus = ''
        if hasattr(issue.fields, "status"):
            if issue.fields.status is not None:
                mystatus = issue.fields.status
        return mystatus

    def GetBugResolution(self, issue):
        """Get Resolution status for a bug."""
        mystatus = ''
        if hasattr(issue.fields, "resolution"):
            if issue.fields.resolution is not None:
                mystatus = issue.fields.resolution
        return mystatus

    def GetBugAssignee(self, issue):
        """Get assignee name for a bug."""
        myname = ''
        if hasattr(issue.fields, "assignee"):
            if issue.fields.assignee is not None:
                myname = issue.fields.assignee
        return myname

    def GetTargetVersionBugs(self, jira_site, targetversion, max_results):
        """Get list of bugs matching target version."""
        myissue_list = []
        if targetversion is not None:
            jql_query = """project=MYPROJ and "Target Version/s" in (%s) and \
                        status=open""" % targetversion
            try:
                myissue_list = jira_site.search_issues(jql_query,
                                                       maxResults=max_results)
            except JIRAError as e:
                print e
                return None
        return myissue_list

    def GetAffectsVersionBugs(self, jira_site, affectsversion, max_results):
        """Get list of bugs matching affected version."""
        myissue_list = []
        if affectsversion is not None:
            jql_query = """project=MYPROJ and affectedVersion in (%s) \
                        and status=open""" % affectsversion
            try:
                myissue_list = jira_site.search_issues(jql_query,
                                                       maxResults=max_results)
            except JIRAError as e:
                print e
                return None
        return myissue_list

    def GetFixVersionBugs(self, jira_site, fixversion, max_results):
        """Get list of bugs matching fix version."""
        myissue_list = []
        if fixversion is not None:
            jql_query = 'project=MYPROJ and fixversion in (%s)' % fixversion
            try:
                myissue_list = jira_site.search_issues(jql_query,
                                                       maxResults=max_results)
            except JIRAError as e:
                print e
                return None
        return myissue_list

    def GetFoundVersionBugs(self, jira_site, foundversion, max_results):
        """Get list of bugs matching found version."""
        myissue_list = []
        if foundversion is not None:
            jql_query = """project=MYPROJ and "Found-In Version"=%s""" \
                        % foundversion
            try:
                myissue_list = jira_site.search_issues(jql_query,
                                                       maxResults=max_results)
            except JIRAError as e:
                print e
                return None
        return myissue_list

    def GetBugsAdvSearch(self, jira_site, jql_query, max_results):
        """Get list of bugs matching search string."""
        myissue_list = []
        print jql_query
        try:
            myissue_list = jira_site.search_issues(jql_query,
                                                   maxResults=max_results)
        except JIRAError as e:
            print e
            return None
        return myissue_list

    def ShowIssues(self, issue_list):
        """Display list of issues from the list."""
        if issue_list:
            for issue in issue_list:
                print issue.key
