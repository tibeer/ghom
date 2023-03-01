from ghom import conf, teams, team_members, members, repositories, branches, labels, team_repos


def main():
    cfg = conf.Conf()
    teams.set_teams(cfg)
    team_members.set_team_members(cfg)
    members.set_members(cfg)
    repositories.set_repositories(cfg)
    branches.set_branches(cfg)
    labels.set_labels(cfg)
    team_repos.set_team_repos(cfg)
    cfg.print_end_message()


if __name__ == "__main__":
    main()
