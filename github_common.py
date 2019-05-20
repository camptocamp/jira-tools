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
    topic_text =  ' '.join(topic[0].split(','))
    for repo in github.search_repositories(f"topic:{topic_text}"):
        repos.append(repo.repository.name)
    return repos
