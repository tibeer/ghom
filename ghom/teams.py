def get_team_parameters(cfg, name):
    result = {
        "privacy": "closed",
        "description": ""
    }

    if "private" in cfg.config['teams'][name]:
        if cfg.config['teams'][name]['private']:
            result['privacy'] = "secret"

    if "description" in cfg.config['teams'][name]:
        result['description'] = cfg.config['teams'][name]['description']

    return result


def update_team(cfg, name, team_handle):

    params = get_team_parameters(cfg, name=name)
    if team_handle.privacy != params['privacy'] or \
       team_handle.description != params['description']:
        if not cfg.dry_run:
            cfg.increase_rate_counter()
            team_handle.edit(
                name=name,
                privacy=params['privacy'],
                description=params['description']
            )
        cfg.log_change(f"{name}")


def add_new_teams(cfg):
    for new_team in cfg.config['teams']:

        # check if need to create, edit or do nothing
        cfg.increase_rate_counter()
        for old_team in cfg.org_handle.get_teams():
            # team found in config and online
            if new_team == old_team.name:
                cfg.increase_rate_counter()
                tmp_team = cfg.org_handle.get_team(old_team.id)
                update_team(cfg, name=new_team, team_handle=tmp_team)
                break
        else:
            # create new teams
            params = get_team_parameters(cfg, name=new_team)
            if not cfg.dry_run:
                cfg.increase_rate_counter()
                cfg.org_handle.create_team(
                    name=new_team,
                    privacy=params['privacy'],
                    description=params['description']
                )
            cfg.log_addition(f"{new_team}")


def remove_old_teams(cfg):
    cfg.increase_rate_counter()
    for old_team in cfg.org_handle.get_teams():
        for new_team in cfg.config['teams']:
            if old_team.name == new_team:
                # team found in config and online
                break
        else:
            # delete old teams
            name = old_team.name
            if not cfg.dry_run:
                cfg.increase_rate_counter()
                old_team.delete()
            cfg.log_deletion(f"{name}")


def set_teams(cfg):
    cfg.set_log_compartment("team")
    add_new_teams(cfg)
    if cfg.config['allow_team_removal']:
        remove_old_teams(cfg)
