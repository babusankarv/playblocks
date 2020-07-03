#!/usr/bin/env python
"""Script to interact with Jira
Supports creating jira issue
Supports updating specific fields in Jira for a given issue id
Get field values for specific jira id as well as search list of issues"""

import argparse
import sys
import jiraUtils as js


def ParseCmd(argv):
    """Parse command line arguments."""
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers(help='commands', dest='command')

    # create parser
    create_parser = subparsers.add_parser('create', help='create new issue')
    create_parser.add_argument('-t', '--title', help='bug title summary',
                               required=True)
    create_parser.add_argument('-co', '--component', help='component name',
                               required=True)
    create_parser.add_argument('-fov', '--foundversion',
                               help='found in version', required=True)
    create_parser.add_argument('-ae', '--assignee', help='assignee name')
    create_parser.add_argument('-pri', '--priority', help='P0 or P1 or P2',
                               default='P2')

    # update parser
    update_parser = subparsers.add_parser('update',
                                          help='update existing issue')
    update_parser.add_argument('-i', '--jiraid',
                               help='Jira ID', required=True)
    update_parser.add_argument('-fxv', '--fixversion', help='Fix Versions')
    update_parser.add_argument('-g', '--gerritnum',
                               help='gerrit changelist number')
    update_parser.add_argument('-b', '--branch', help='branch name')
    update_parser.add_argument('-ae', '--assignee', help='assignee name')
    update_parser.add_argument('-cod', '--commitdetails',
                               help='commit author,commit date,commit subject')
    update_parser.add_argument('-fxs', '--fixsummary', help='flag option',
                               default=False, action="store_true")

    # get parser
    get_parser = subparsers.add_parser('get',
                                       help='get field values or issue list')
    get_parser.add_argument('-i', '--jiraid', help='Jira ID')
    get_parser.add_argument('-f', '--fieldname',
                            help='Jira fieldname', default='')
    get_parser.add_argument('-tv', '--targetversion', help='Target Versions')
    get_parser.add_argument('-av', '--affectsversion', help='Affect Versions')
    get_parser.add_argument('-fxv', '--fixversion', help='Fix Versions')
    get_parser.add_argument('-fov', '--foundversion', help='found in version')
    get_parser.add_argument('-qs', '--querystring', help='jql query string')
    get_parser.add_argument('-m', '--maxResults',
                            help='maxResults', default=50)

    # common arguments to all parsers
    for cmdparser in [create_parser, update_parser, get_parser]:
        cmdparser.add_argument('-s', '--server',
                               default='https://siteurl.com',
                               help='Jira server url')
        cmdparser.add_argument('-u', '--user',
                               help='Jira username', default='user@abc.com')
        cmdparser.add_argument('-to', '--token',
                               help='api token', default='xxxxxxxx')
        cmdparser.add_argument('-c', '--comment', help='comment')
        cmdparser.add_argument('-d', '--description', help='description text')
    return parser.parse_args(argv[1:])


if __name__ == "__main__":
    # Process Command line Arguments
    args = ParseCmd(sys.argv)
    jiraserver = args.server
    jirauser = args.user
    jiraapitoken = args.token
    new_comment = args.comment
    descriptiontext = args.description

    # Connecting to Jira Site
    ju = js.JiraUtils(jiraserver, jirauser, jiraapitoken)
    jira_site = ju.Connect()
    if jira_site is None:
        print 'jira server connection failed.Check connectivity and credential'
        sys.exit(-1)

    # For jira bug create  option
    if args.command == 'create':
        myissue_data = {
          'project': {'key': 'MYPROJ'},
          'summary': args.title,
          'components': [{'name': args.component}],
          'customfield_13149': {'value': args.foundversion},
          'priority': {'name': args.priority},
          'assignee': {'name': args.assignee},
          'description': descriptiontext,
          'issuetype': {'name': 'Bug'},
          }
        new_issue = ju.CreateNewIssue(jira_site, **myissue_data)
        if new_issue is not None:
            print new_issue
        else:
            print 'create issue failed'
            sys.exit(-1)
    # For jira bug update option
    elif args.command == 'update':
        gerritnum = args.gerritnum
        branchname = args.branch
        # Get Bug details
        myissue = ju.GetBugDetails(jira_site, args.jiraid)
        if myissue is None:
            print '%s issue not found' % args.jiraid
            sys.exit(-1)
        # Update Fix Version
        if args.fixversion is not None and args.fixsummary is False:
            mystatus = ju.UpdateFix(myissue, args.fixversion)
            if mystatus == 'SUCCESS':
                ju.UpdateComments(jira_site,
                                  args.jiraid,
                                  'Updated Fix version ' + args.fixversion)
            elif mystatus == 'SKIPPED':
                print 'fix version already present for %s' % args.jiraid
            else:
                print 'fix version update failed for %s' % args.jiraid

        # Update gerrit link if specified
        if args.gerritnum is not None and args.fixsummary is False:
            mystatus = ju.UpdateGerritLink(jira_site, myissue, args.gerritnum)
            if mystatus != 'SUCCESS':
                print 'gerrit link update failed for %s' % args.jiraid

        # Update comments
        if new_comment is not None:
            mystatus = ju.UpdateComments(jira_site, myissue, new_comment)
            if mystatus != 'SUCCESS':
                print 'comment update failed for %s' % args.jiraid

        # Update description
        if descriptiontext is not None:
            mystatus = ju.UpdateDescription(myissue, descriptiontext)
            if mystatus != 'SUCCESS':
                print 'Description update failed for %s' % args.jiraid

        # Update assignee name
        if args.assignee is not None:
            mystatus = ju.UpdateAssignee(myissue, args.assignee)
            if mystatus != 'SUCCESS':
                print 'Assignee update failed for %s' % args.jiraid

        # Update  fix summary
        if args.fixsummary is True and args.commitdetails is not None:
            if args.gerritnum == 'cimerge':
                gerrit_link = "[cimerge|http://mothership:8080/#/c/%s]" \
                              % args.gerritnum
            else:
                gerrit_link = "[%s|http://mothership:8080/#/c/%s]" \
                              % (args.gerritnum, args.gerritnum)
            commit_data = args.commitdetails.split(",")
            fix_details = [branchname, args.fixversion, commit_data[1],
                           commit_data[0], commit_data[2], gerrit_link]
            fixsummary_str = "|".join(fix_details)
            fixsummary_str = "|"+fixsummary_str+"|\r"
            mystatus = ju.UpdateFixSummary(myissue, fixsummary_str)
            if mystatus != 'SUCCESS':
                print 'Fix summary update failed for %s' % args.fixsummary
    elif args.command == 'get':
        max_results = args.maxResults
        issue_list = ''

        # Get target version list for the specified bug
        if args.jiraid is not None and "targetversion" in args.fieldname:
            targetversions = []
            myissue = ju.GetBugDetails(jira_site, args.jiraid)
            if myissue is not None:
                targetversions = ju.GetBugTargetVersions(myissue)
                targetversions_str = ",".join(targetversions)
                print targetversions_str
            else:
                print '%s issue not found' % args.jiraid
                sys.exit(-1)

        # Get affected version list for the specified bug
        if args.jiraid is not None and "affectedversion" in args.fieldname:
            affectedtversions = []
            myissue = ju.GetBugDetails(jira_site, args.jiraid)
            if myissue is not None:
                affectedversions = ju.GetBugAffectedVersions(myissue)
                print affectedversions
            else:
                print '%s issue not found' % args.jiraid
                sys.exit(-1)

        # Get fix version list for the specified bug
        if args.jiraid is not None and "fixversion" in args.fieldname:
            fixversions = []
            myissue = ju.GetBugDetails(jira_site, args.jiraid)
            if myissue is not None:
                fixversions = ju.GetBugfixVersions(myissue)
                print fixversions
            else:
                print '%s issue not found' % args.jiraid
                sys.exit(-1)
        # Get fix version list for the specified bug
        if args.jiraid is not None and "foundversion" in args.fieldname:
            foundversions = []
            myissue = ju.GetBugDetails(jira_site, args.jiraid)
            if myissue is not None:
                foundversions = ju.GetBugfoundVersions(myissue)
                print foundversions
            else:
                print '%s issue not found' % args.jiraid
                sys.exit(-1)

        # Get status for the specified bug
        if args.jiraid is not None and "status" in args.fieldname:
            myissue = ju.GetBugDetails(jira_site, args.jiraid)
            if myissue is not None:
                mystatus = ju.GetBugStatus(myissue)
                print mystatus
            else:
                print '%s issue not found' % args.jiraid
                sys.exit(-1)

        # Get resolution status for the specified bug
        if args.jiraid is not None and "resolution" in args.fieldname:
            myissue = ju.GetBugDetails(jira_site, args.jiraid)
            if myissue is not None:
                mystatus = ju.GetBugResolution(myissue)
                print mystatus
            else:
                print '%s issue not found' % args.jiraid
                sys.exit(-1)

        # Get assignee for the specified bug
        if args.jiraid is not None and "assignee" in args.fieldname:
            myissue = ju.GetBugDetails(jira_site, args.jiraid)
            if myissue is not None:
                mystatus = ju.GetBugAssignee(myissue)
                print mystatus
            else:
                print '%s issue not found' % args.jiraid
                sys.exit(-1)

        # Get bug list for target version
        if args.targetversion is not None:
            issue_list = ju.GetTargetVersionBugs(jira_site, args.targetversion,
                                                 max_results)
            ju.ShowIssues(issue_list)

        # Get bug list for affected version
        if args.affectsversion is not None:
            issue_list = ju.GetAffectsVersionBugs(jira_site,
                                                  args.affectsversion,
                                                  max_results)
            ju.ShowIssues(issue_list)

        # Get bug list for fix version
        if args.fixversion is not None:
            issue_list = ju.GetFixVersionBugs(jira_site, args.fixversion,
                                              max_results)
            ju.ShowIssues(issue_list)

        # Get bug list for found in  version
        if args.foundversion is not None:
            issue_list = ju.GetFoundVersionBugs(jira_site, args.foundversion,
                                                max_results)
            ju.ShowIssues(issue_list)

        # Get bug list for advance query string
        if args.querystring is not None:
            issue_list = ju.GetBugsAdvSearch(jira_site, args.querystring,
                                             max_results)
            ju.ShowIssues(issue_list)
