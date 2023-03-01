def add_new_team_members(cfg, team_handle, members, role):
    for member in members:
        cfg.increase_rate_counter()
        user = cfg.gh_handle.get_user(member)
        cfg.increase_rate_counter()
        for tmp_member in team_handle.get_members():
            if tmp_member.login == member:
                # check for changes
                cfg.increase_rate_counter()
                membership = team_handle.get_team_membership(user)
                if membership.role != role:
                    # update membership
                    if not cfg.dry_run:
                        cfg.increase_rate_counter()
                        team_handle.add_membership(user, role)
                    cfg.log_change(f"{team_handle.name} {role} {member}")
                break
        else:
            # check if there is a pending invite
            invite_found = False
            for invite in team_handle.invitations():
                if user.login == invite.login:
                    invite_found = True
                    break
            if invite_found:
                continue

            # add user to team
            if not cfg.dry_run:
                cfg.increase_rate_counter()
                team_handle.add_membership(user, role)
            cfg.log_addition(f"{team_handle.name} {role} {member}")


def delete_old_team_members(cfg, team_handle, members):
    cfg.increase_rate_counter()
    for tmp_member in team_handle.get_members():
        for member in members:
            if tmp_member.login == member:
                # member found in config and online
                break
        else:
            # delete old member
            name = tmp_member.login
            cfg.increase_rate_counter()
            user = cfg.gh_handle.get_user(tmp_member.login)
            if not cfg.dry_run:
                cfg.increase_rate_counter()
                team_handle.remove_membership(user)
            cfg.log_deletion(f"{team_handle.name} {name}")


def set_team_members(cfg):
    cfg.set_log_compartment("team-member")
    for team in cfg.config['teams']:
        if "members" in cfg.config['teams'][team]:
            members = cfg.config['teams'][team]['members']
        if "maintainers" in cfg.config['teams'][team]:
            maintainers = cfg.config['teams'][team]['maintainers']
        cfg.increase_rate_counter()
        for team_id in cfg.org_handle.get_teams():
            if team_id.name == team:
                cfg.increase_rate_counter()
                team_handle = cfg.org_handle.get_team(team_id.id)
                break
        else:
            # this should never happen --- famous words
            cfg.log_critical(f"team {team} not found")

        if "members" in cfg.config['teams'][team]:
            add_new_team_members(cfg, team_handle, members, "member")
        if "maintainers" in cfg.config['teams'][team]:
            add_new_team_members(cfg, team_handle, maintainers, "maintainer")

        if cfg.config['allow_team_member_removal']:
            keep_list = []
            if "members" in cfg.config['teams'][team]:
                keep_list = keep_list + members
            if "maintainers" in cfg.config['teams'][team]:
                keep_list = keep_list + maintainers
            delete_old_team_members(cfg, team_handle, keep_list)
