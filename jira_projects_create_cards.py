#!/usr/bin/env python3
from github_common import repositories_by_topic
from authentication import jira_connection, github_connection
import click
import sys
import csv
import os
import tempfile
from subprocess import call
EDITOR = os.environ.get('EDITOR','vim')

class JiraTools:
    """Object to automate process with Jira.
    """

    def __init__(self, **kwarg):
        """Jira and github must be retrieved before in the authentication part.
        """
        # Input arg
        self.topic = kwarg.get('topic')
        self.description = kwarg.get('description')
        self.issuetype = kwarg.get('issuetype')
        self.summary = kwarg.get('summary')
        self.template = kwarg.get('template')
        self.csv_project_list = kwarg.get('csv_project_list')
        self.csv_jira_card = kwarg.get('csv_jira_card')
        self.jira = jira_connection()

        if not self.csv_project_list:
            self.github = github_connection()
        else:
            self.github = None

        self.projects_list = []
        self.projects = []

    def create_new_issue_one_github_list(self):
        """
            Global method to create a new issue.

            The topic to search all github matching repositories
            must be added by the user.
        """
        if self.csv_project_list:
            self.projects_list = self.parse_csv_jira_projects(
                self.csv_project_list
            )

        else:
            if not self.topic:
                sys.exit("Please add GitHub topic")

            self.projects_list = repositories_by_topic(self.github, self.topic)
            self.topic = False

        self.projects = self.get_jira_projets(self.jira, self.projects_list)
        self.new_issue_on_projects(self.jira, self.projects)

    def new_issue_on_projects(self, jira, projects):
        """ Create on jira a new issue on all project list

            :param jira: jira api object
            :param projects: jira project list
        """
        projects = self._check_project_list(projects)

        if self.csv_jira_card:
            list_issue_dict = self.get_csv_jira_card(self.csv_jira_card)
        else:
            issue_dict = self._check_if_existing_issue()
            list_issue_dict = [issue_dict] # only one issue

        for project in projects:
            for issue in list_issue_dict:
                issue['project'] = {'id': project.id}
                new_issue = self.jira.create_issue(fields=issue)
                print(
                    '* Issue {} create on {}'.format(
                        new_issue.key, project.name
                    )
                )

        sys.exit("Bye")

    ### Retrieve Jira projects ###
    #############################

    def parse_csv_jira_projects(self, csv_file):
        """ Retrieve jira project in the csv file.

            :param csv_file: csv file with column 'project'
            :param repo_list: repository list
            :return: jira project list
        """
        repo_list = []
        with open(csv_file, newline='') as f:
            reader = csv.DictReader(f)
            for row in reader:
                repo_list.append(row.get('projects'))
        return repo_list

    def get_jira_projets(self, jira, repo_list):
        """ Retrieve jira projects matching by repository name.

            :param jira: jira api object
            :param repo_list: repository list
            :return: jira project list
        """
        repo_list = self._format_repo_list(repo_list)
        # Get all projects viewable
        projects = jira.projects()
        match_projects = []

        for project in projects:
            project_name = self._format_project_name(project.name)
            for repo in repo_list:
                if project_name.startswith(repo):
                    match_projects.append(project)
        return match_projects

    ### Formating methods ###
    ##########################

    def _format_repo_list(self, repo_list):
        """
            Formating github repository name.

            :param repo_list: repository list
            :return: repository list formated
        """
        suffixs = ['_odoo', '_openerp']
        for repo in repo_list:
            for suffix in suffixs:
                repo = repo.replace(suffix, "")
        return repo_list

    def _format_project_name(self, project_name):
        """ Formating jira project name.

            :param project_name: jira project name
            :return: repository jira project name formated
        """
        pjct_name_no_space = project_name.replace(" ", "")
        return pjct_name_no_space.lower()

    def _check_project_list(self, projects):
        """ Edit interactively the list of projects.
            Like that we are able to remove projects and add some projects

            :param projects: jira project list
            :return: repository jira project list updated by the user

            # TODO: Maybe also output the ignored lines.
        """
        projects_names = [project.name for project in projects]
        initial_message = '\n'.join(projects_names)
        initial_message = "# Project list :\n" + \
            initial_message + \
            "\n# Remove some of them if you want"

        with tempfile.NamedTemporaryFile(suffix=".tmp") as tf:
            tf.write(initial_message.encode('ascii'))
            tf.flush()
            call([EDITOR, tf.name])

            # do the parsing with `tf` using regular File operations.
            # for instance:
            tf.seek(0)
            edited_message = tf.read()
        # Decode and remove the comment
        projects_names_updated = edited_message.decode(
            'ascii'
        ).split('\n')[1:-2]
        # Keep only the project in the name retrived before
        projects_list_updated = [
            project for project
            in projects if project.name in projects_names_updated
        ]
        return projects_list_updated

    ### Creating issue content ###
    ##############################

    def get_csv_jira_card(self, csv_file):
        """ Retrieve the different parts used to create new issues
            in the csv file.

            :param csv_file: csv file with column 'project'
            :return: lite of dict to create one issue
        """
        issues_list = []
        with open(csv_file, newline='') as f:
            reader = csv.DictReader(f)
            for row in reader:
                issues_list.append(
                    {
                        'summary': row.get('summary'),
                        'description': row.get('description'),
                        'issuetype': {'name': row.get('issuetype'),},
                    }
                )
        return issues_list

    def _retrieve_or_duplicate_issue(self):
        """ Retrieve an issue if user has duplicated an existing one OR
            created one.

            :return: jira project list
        """
        if not self.template:
            self.template = input(
                "Issue's name (ie. JRA-1330): "
            )
        not_existing_issue = True
        while not_existing_issue:
            try:
                jira_obj = self.jira.issue(self.template)
                not_existing_issue = False
            except Exception as expt:
                print(expt)
                self.template = input(
                    '\nIssus not found try again like JRA-1330 : '
                )

        issue_dict = {
            'summary': jira_obj.fields.summary or 'TODO',
            'description': jira_obj.fields.description or 'TODO',
            'issuetype': {'name': jira_obj.fields.issuetype.name or 'Task'},
        }
        return issue_dict

    def _check_if_existing_issue(self):
        """ Redirect to right method depending the user choice.
        """
        if self.template:
            return self._retrieve_or_duplicate_issue()
        if self.issuetype and self.summary and self.description:
            return self._create_new_issue_content()
        if click.confirm('Do you want to use existing issue ?'):
            return self._retrieve_or_duplicate_issue()
        else:
            return self._create_new_issue_content()

    def _create_new_issue_content(self):
        """ Retrieve the different part to create a new issue.

            :return: dict to create one issue
        """
        issuetype = self._add_issue_type()
        summary = self._add_summary()
        description = self._add_description()

        return {
        'summary': summary,
        'description': description,
        'issuetype': {'name': issuetype},
        }

    def _add_issue_type(self):
        """ Add issue type

            :return: issue type
        """
        issuetype_list = ['Bug', 'Task']
        while self.issuetype not in issuetype_list:
            print(
                'Possible issue types are: [%s]' % '; '.join(
                    map(str, issuetype_list)
                )
            )
            self.issuetype = input('Choose the issue type: ')
        return self.issuetype

    def _add_description(self):
        """ Add issue description

            :return: issue description
        """
        while not self.description:
            print("Description shouldn't be empty")
            self.description = input('Add description: ')

        self.description = self.description.replace('\\n', '\n')
        return self.description

    def _add_summary(self):
        """ Add issue summary

            :return: issue summary
        """
        while not self.summary:
            print("summary shouldn't be empty")
            self.summary = input('Add summary: ')
        return self.summary

@click.command()
@click.option('--topic', default=False, multiple=True, help='GitHub topic')
@click.option('--description', default=False, help='New jira issue description')
@click.option('--issuetype', default=False, help='New jira issue type')
@click.option('--summary', default=False, help='New jira issue summary')
@click.option('--template', default=False, help='Issue to duplicate name like JRA-1330')
@click.option('--csv_project_list', default=False, help='Give the path to your project list csv')
@click.option('--csv_jira_card', default=False, help='Give the path to your card list csv')
def main(
        topic,
        description,
        issuetype,
        summary,
        template,
        csv_project_list,
        csv_jira_card):
    """
        Create a Jira issue on project list.

        1) Project list :
        * The list can be directly provided by csv file (projects.csv) in argument
            --csv_project_list projects.csv
        * Or retrieved in GitHub by corresponding label
            --topic business,odoo-9,need-5-digits

        And the list can be edited before card creation in the shell
        interaction

        2) Card content:
        * The content can be duplicated from an existing card
            --template JRA-1330
        * Or provided by csv file (card_template.csv) in argument
            --csv_jira_card card_template.csv
        * Or provided directly in arguments
            --issuetype Task \
            --summary "My summary" \
            --description "One description\nwith multiple lines\n:-)"

        If your action corresponds to the script process, you will see
        for all your issue creation:\n
            'Issue ok for [project_name]'

        Enjoy and don't hesitate to contribute or create an issue :-)
    """

    kwargs = {
        'topic': topic,
        'description': description,
        'issuetype': issuetype,
        'summary': summary,
        'template': template,
        'csv_project_list': csv_project_list,
        'csv_jira_card': csv_jira_card,
    }
    session = JiraTools(**kwargs)
    session.create_new_issue_one_github_list()

if __name__ == "__main__":
    main()
