# JIRA bulk task creator

## Install

* Manage configuration in file [config.json](/Jira_tools/config.json)
* Add permission to be executed: `chmod +x jira_projects_create_cards.py github_common.py`

* Run `pip install -r requirements.txt --user`

**OR**

* Using virtualenv
    * `virtualenv jira_env`
    * `pip install -r requirements.txt`
    * `source jira_env/bin/activate`

**OR**

* Using [pyenv](https://amaral.northwestern.edu/resources/guides/pyenv-tutorial#VirtualEnvironments)
    * `curl -L https://raw.githubusercontent.com/yyuu/pyenv-installer/master/bin/pyenv-installer | bash`
    * `pyenv install 3.6.3`
    * `pyenv local 3.6.3`
    * `pipenv install`
    * `pipenv shell`

## Start

* List of arguments: `./jira_projects_create_cards.py --help`

* You have 3 ways to use:
    * with github topic
        * Duplicate an existing issue
        * Create new one
    * with 2 CSV files
        * project list + cards description

### Sample

* Duplicating an existing Jira card:
```
./jira_projects_create_cards.py \
--topic business,odoo-9,need-5-digits \
--existing_issue_copy JRA-1330
```

* Creating a new Jira card:
```
./jira_projects_create_cards.py \
--topic odoo-8 \
--issuetype Task \
--summary "My summary" \
--description "One description\nwith multiple lines\n:-)"
```

* Creating a new Jira card from a CSV file:
```
python jira_projects_create_cards.py \
--csv_project_list projects.csv \
--csv_jira_card card_template.csv
```

### NB

Getting help about this tool:
`./jira_projects_create_cards.py --help`
