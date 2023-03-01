import copy


def build_attributes(cfg, new_repo):
    # combine repository_defaults with individual values
    # need to do a copy, otherwise python will think it has
    # to work on the original "config" variable
    default_rules = copy.copy(cfg.config['repository_defaults'])

    repo_rules = {}
    if cfg.config['repositories'][new_repo]:
        for new_attribute in cfg.config['repositories'][new_repo]:
            # labels are handles seperately, so we can skip them
            if new_attribute == "labels":
                continue
            repo_rules[new_attribute] = cfg.config['repositories'][new_repo][new_attribute]

    result_rules = default_rules
    for repo_rule in repo_rules:
        for default_rule in default_rules:
            # if rule found in defaults and new repo rules
            if repo_rule == default_rule:
                # replace default rule in favor of new rule config
                result_rules[repo_rule] = repo_rules[repo_rule]
        else:
            # add new repo rules
            result_rules[repo_rule] = repo_rules[repo_rule]

    return result_rules


def add_new_repos(cfg):
    for new_repo in cfg.config['repositories']:
        attributes = build_attributes(cfg, new_repo)
        cfg.increase_rate_counter()
        for old_repo in cfg.org_handle.get_repos():
            # check if repo already exists
            if old_repo.name == new_repo:
                # helper for description since the stupid api replies with None instead of an empty string
                helper_description = old_repo.description
                if helper_description is None:
                    helper_description = ""

                if "archived" not in attributes:
                    helper_archived = False
                else:
                    helper_archived = attributes['archived']

                # STUPID: There seems to be some internal logic when accessing one or more of the following four attributes.
                # And yes, the counter only needs to be increased by one. It seems that python starts a dedicated request in
                # the background for the first attribute and caches the result for the remaining three, so no more requests.
                cfg.increase_rate_counter()
                helper_allow_squash_merge = old_repo.allow_squash_merge != attributes['allow_squash_merge']
                helper_allow_merge_commit = old_repo.allow_merge_commit != attributes['allow_merge_commit']
                helper_allow_rebase_merge = old_repo.allow_rebase_merge != attributes['allow_rebase_merge']
                helper_delete_branch_on_merge = old_repo.delete_branch_on_merge != attributes['delete_branch_on_merge']

                # check if update is required
                if helper_description != attributes['description'] or \
                   old_repo.homepage != attributes['homepage'] or \
                   old_repo.private != attributes['private'] or \
                   old_repo.has_issues != attributes['has_issues'] or \
                   old_repo.has_wiki != attributes['has_wiki'] or \
                   old_repo.has_downloads != attributes['has_downloads'] or \
                   old_repo.has_projects != attributes['has_projects'] or \
                   helper_allow_squash_merge or \
                   helper_allow_merge_commit or \
                   helper_allow_rebase_merge or \
                   helper_delete_branch_on_merge or \
                   old_repo.archived != helper_archived:
                    cfg.increase_rate_counter()
                    repo = cfg.org_handle.get_repo(old_repo.name)
                    if helper_archived:
                        if not cfg.dry_run:
                            cfg.increase_rate_counter()
                            repo.edit(
                                name=new_repo,
                                description=attributes['description'],
                                homepage=attributes['homepage'],
                                private=attributes['private'],
                                has_issues=attributes['has_issues'],
                                has_wiki=attributes['has_wiki'],
                                has_downloads=attributes['has_downloads'],
                                has_projects=attributes['has_projects'],
                                allow_squash_merge=attributes['allow_squash_merge'],
                                allow_merge_commit=attributes['allow_merge_commit'],
                                allow_rebase_merge=attributes['allow_rebase_merge'],
                                delete_branch_on_merge=attributes['delete_branch_on_merge'],
                                archived=helper_archived
                            )
                    else:
                        if not cfg.dry_run:
                            cfg.increase_rate_counter()
                            repo.edit(
                                name=new_repo,
                                description=attributes['description'],
                                homepage=attributes['homepage'],
                                private=attributes['private'],
                                has_issues=attributes['has_issues'],
                                has_wiki=attributes['has_wiki'],
                                has_downloads=attributes['has_downloads'],
                                has_projects=attributes['has_projects'],
                                allow_squash_merge=attributes['allow_squash_merge'],
                                allow_merge_commit=attributes['allow_merge_commit'],
                                allow_rebase_merge=attributes['allow_rebase_merge'],
                                delete_branch_on_merge=attributes['delete_branch_on_merge']
                            )
                    cfg.log_change(f"{new_repo}")
                break
        else:
            if "archived" in attributes:
                if attributes['archived']:
                    cfg.log_critical(f"cannot create new repo {new_repo}: marked as archived")
                    continue

            # create new repository
            if not cfg.dry_run:
                cfg.increase_rate_counter()
                cfg.org_handle.create_repo(
                    name=new_repo,
                    description=attributes['description'],
                    homepage=attributes['homepage'],
                    private=attributes['private'],
                    has_issues=attributes['has_issues'],
                    has_wiki=attributes['has_wiki'],
                    has_downloads=attributes['has_downloads'],
                    has_projects=attributes['has_projects'],
                    auto_init=True,
                    allow_squash_merge=attributes['allow_squash_merge'],
                    allow_merge_commit=attributes['allow_merge_commit'],
                    allow_rebase_merge=attributes['allow_rebase_merge'],
                    delete_branch_on_merge=attributes['delete_branch_on_merge'],
                )
            cfg.log_addition(f"{new_repo}")


def delete_old_repos(cfg):
    cfg.increase_rate_counter()
    for old_repo in cfg.org_handle.get_repos():
        for new_repo in cfg.config['repositories']:
            if old_repo.name == new_repo:
                # repo found in config and online
                break
        else:
            # delete old repo
            name = old_repo.name
            cfg.increase_rate_counter()
            repo = cfg.org_handle.get_repo(name)
            if not cfg.dry_run:
                cfg.increase_rate_counter()
                repo.delete()
            cfg.log_deletion(f"{name}")


def set_repositories(cfg):
    cfg.set_log_compartment("repo")
    add_new_repos(cfg)
    if cfg.config['allow_repository_removal']:
        delete_old_repos(cfg)
