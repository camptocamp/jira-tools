#!/usr/bin/env python3
import github3

def repositories_by_topic(github, topic):
    """
        Retrieve all commits with a precise topic.

        :param github: the github object
        :param topic: name of the topic that needs to be match for
        :return: repository list
    """
    repos = []
    topic_text =  _format_topic(topic)
    for repo in github.search_repositories(f"topic:{topic_text}"):
        repos.append(repo.repository.name)
    return repos

def _format_topic(topic_tuple):
    """ Format to render topic in a proper domain string for GitHub

        cause 'tuple' object has no attribute 'replace'
    """
    topic_text =  ' '.join(topic_tuple)
    return ' '.join(topic_text.split(','))
