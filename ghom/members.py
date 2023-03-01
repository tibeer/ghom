def add_new_owners(cfg):
    for owner in cfg.config['owners']:
        cfg.increase_rate_counter()
        user = cfg.gh_handle.get_user(owner)
        cfg.increase_rate_counter()
        if not cfg.org_handle.has_in_members(user):
            cfg.increase_rate_counter()
            cfg.org_handle.add_to_members(user, role="admin")
            cfg.log_addition(f"{owner}")
        else:
            cfg.increase_rate_counter()
            for tmp_owner in cfg.org_handle.get_members(role="admin"):
                if owner == tmp_owner.login:
                    # nothing to do
                    break
            else:
                if not cfg.dry_run:
                    cfg.increase_rate_counter()
                    cfg.org_handle.add_to_members(user, role="admin")
                cfg.log_change(f"{owner}")


def add_new_members(cfg):
    for member in cfg.config['members']:
        cfg.increase_rate_counter()
        user = cfg.gh_handle.get_user(member)
        cfg.increase_rate_counter()
        if not cfg.org_handle.has_in_members(user):
            if not cfg.dry_run:
                cfg.increase_rate_counter()
                cfg.org_handle.add_to_members(user, role="member")
            cfg.log_addition(f"{member}")
        else:
            cfg.increase_rate_counter()
            for tmp_member in cfg.org_handle.get_members(role="member"):
                if member == tmp_member.login:
                    # nothing to do
                    break
            else:
                if not cfg.dry_run:
                    cfg.increase_rate_counter()
                    cfg.org_handle.add_to_members(user, role="member")
                cfg.log_change(f"{member}")


def delete_old_members(cfg):
    cfg.increase_rate_counter()
    for member in cfg.org_handle.get_members():
        if member.login not in (cfg.config['owners'] + cfg.config['members']):
            cfg.increase_rate_counter()
            if member.login in cfg.org_handle.get_members(role="member"):
                helper = "member"
            else:
                helper = "owner"

            name = member.login
            cfg.increase_rate_counter()
            user = cfg.gh_handle.get_user(member.login)
            if not cfg.dry_run:
                cfg.increase_rate_counter()
                cfg.org_handle.remove_from_members(user)
            cfg.set_log_compartment(helper)
            cfg.log_deletion(f"{helper} {name}")


def set_members(cfg):
    cfg.set_log_compartment("owner")
    add_new_owners(cfg)
    cfg.set_log_compartment("member")
    add_new_members(cfg)
    if cfg.config['allow_member_removal']:
        delete_old_members(cfg)
