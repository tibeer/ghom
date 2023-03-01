def set_permission(cfg, team, repo, permission):
    cfg.increase_rate_counter()
    team_handle = cfg.org_handle.get_team_by_slug(team)
    cfg.increase_rate_counter()
    repo_handle = cfg.org_handle.get_repo(repo)

    # check if team is already added to repo
    tmp_list = []
    cfg.increase_rate_counter()
    for tmp_handle in team_handle.get_repos():
        tmp_list.append(tmp_handle.name)

    # team has to be added to the repo
    if repo not in tmp_list:
        if not cfg.dry_run:
            cfg.increase_rate_counter()
            team_handle.update_team_repository(repo_handle, permission)
        cfg.log_addition(f"{team} repo {repo} permission {permission}")

    # team is already added
    else:
        # check for possible changes (yes, I have to do it this way)
        cfg.increase_rate_counter()
        old_permission = team_handle.get_repo_permission(repo_handle)
        if not cfg.dry_run:
            cfg.increase_rate_counter()
            team_handle.update_team_repository(repo_handle, permission)
        cfg.increase_rate_counter()
        new_permission = team_handle.get_repo_permission(repo_handle)

        permissions_are_equal = False
        if old_permission.triage == new_permission.triage and \
           old_permission.push == new_permission.push and \
           old_permission.pull == new_permission.pull and  \
           old_permission.maintain == new_permission.maintain and \
           old_permission.admin == new_permission.admin:
            permissions_are_equal = True

        if not permissions_are_equal:
            cfg.log_change(f"{team} repo {repo} permission {permission}")


def set_teams_permissions(cfg, repo, teams):
    for team in teams:
        permission = teams[team]
        set_permission(cfg, team, repo, permission)


def add_new_default_repo_teams(cfg):
    if "default_teams" in cfg.config['repository_defaults']:
        for repo in cfg.config['repositories']:
            set_teams_permissions(cfg, repo, cfg.config['repository_defaults']['default_teams'])


def add_new_repo_teams(cfg):
    for repo in cfg.config['repositories']:
        repo_values = cfg.config['repositories'][repo]

        # check if something repo specific needs to be done
        if repo_values:
            if "teams" in repo_values:
                set_teams_permissions(cfg, repo, repo_values['teams'])


def delete_old_repo_teams(cfg):
    # check each team in the org
    cfg.increase_rate_counter()
    for team in cfg.org_handle.get_teams():

        # check if the team in defaults
        if "default_teams" in cfg.config['repository_defaults']:
            if team.slug in cfg.config['repository_defaults']['default_teams'].keys():
                # team is in default, nothing has to be done
                continue

        # loop each repo to check for possible team settings
        for repo in cfg.config['repositories']:
            cfg.increase_rate_counter()
            repo_handle = cfg.org_handle.get_repo(repo)
            repo_values = cfg.config['repositories'][repo]

            if repo_values:
                if "teams" in repo_values:
                    if team.slug not in repo_values['teams'].keys():
                        # check if team has to be removed repo
                        for tmp_repo in team.get_repos():
                            if not cfg.dry_run:
                                cfg.increase_rate_counter()
                                team.remove_from_repos(repo_handle)
                            cfg.log_deletion(f"{team.slug} repo {repo}")
            else:
                # check if team has to be removed repo
                for tmp_repo in team.get_repos():
                    if tmp_repo.name == repo:
                        if not cfg.dry_run:
                            cfg.increase_rate_counter()
                            team.remove_from_repos(repo_handle)
                        cfg.log_deletion(f"{team.slug} repo {repo}")


def set_team_repos(cfg):
    cfg.set_log_compartment("team-repo")
    add_new_default_repo_teams(cfg)
    add_new_repo_teams(cfg)
    if cfg.config['allow_team_repo_removal']:
        delete_old_repo_teams(cfg)
