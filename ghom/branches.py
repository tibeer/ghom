from github.GithubException import GithubException


def differences_found(old_protection, new_protection):
    if old_protection == {}:
        return True
    if old_protection['enforce_admins'] != new_protection['enforce_admins']:
        return True
    if old_protection['required_pull_request_owner_review'] != new_protection['required_pull_request_owner_review']:
        return True
    if old_protection['required_pull_request_review_count'] != new_protection['required_pull_request_review_count']:
        return True
    return False


def set_default_branch_protection(cfg, repo, protection_rules):
    cfg.increase_rate_counter()
    repo_handle = cfg.org_handle.get_repo(repo)
    cfg.increase_rate_counter()
    branch = repo_handle.get_branch(protection_rules['branch_name'])

    # check if the branch has protections (no, there is no nicer way of doing this currently!)
    branch_is_protected = True
    old_protection = {}
    try:
        cfg.increase_rate_counter()
        protection = branch.get_protection()
        old_protection['enforce_admins'] = protection.enforce_admins
        old_protection['required_pull_request_owner_review'] = protection.required_pull_request_reviews.require_code_owner_reviews
        old_protection['required_pull_request_review_count'] = protection.required_pull_request_reviews.required_approving_review_count
    except GithubException:
        branch_is_protected = False

    if protection_rules['active']:

        if differences_found(old_protection, protection_rules):
            if not cfg.dry_run:
                cfg.increase_rate_counter()
                branch.edit_protection(
                    enforce_admins=protection_rules['enforce_admins'],
                    dismiss_stale_reviews=True,
                    require_code_owner_reviews=protection_rules['required_pull_request_owner_review'],
                    required_approving_review_count=protection_rules['required_pull_request_review_count'],
                )

            if old_protection == {}:
                cfg.log_addition(f"{repo} branch {protection_rules['branch_name']}")
            else:
                cfg.log_change(f"{repo} branch {protection_rules['branch_name']}")
    else:
        if branch_is_protected:
            if not cfg.dry_run:
                cfg.increase_rate_counter()
                branch.remove_protection()
            cfg.log_deletion(f"{repo} branch {protection_rules['branch_name']}")


def set_branches(cfg):
    cfg.set_log_compartment("branch-protection")
    for repo in cfg.config['repositories']:
        repo_values = cfg.config['repositories'][repo]
        protection_rules = {
            "active": False
        }

        # start with default protection rules
        if "default_branch_protection" in cfg.config['repository_defaults']:
            default_protection_rules = cfg.config['repository_defaults']['default_branch_protection']
            protection_rules['branch_name'] = default_protection_rules['branch_name']
            if default_protection_rules['active']:
                protection_rules['active'] = default_protection_rules['active']
                protection_rules['required_pull_request_review_count'] = default_protection_rules['required_pull_request_review_count']
                protection_rules['required_pull_request_owner_review'] = default_protection_rules['required_pull_request_owner_review']
                protection_rules['enforce_admins'] = default_protection_rules['enforce_admins']

        # check if something repo specific needs to be done
        if repo_values:
            if "default_branch_protection" in repo_values:
                # repo sepcific rule disables branch protection
                if not repo_values['default_branch_protection']['active']:
                    protection_rules['active'] = False
                # otherwise check for a values
                else:
                    custom_rules = repo_values['default_branch_protection']
                    if "branch_name" in custom_rules:
                        protection_rules['branch_name'] = custom_rules['branch_name']
                    if "required_pull_request_review_count" in custom_rules:
                        protection_rules['required_pull_request_review_count'] = custom_rules['required_pull_request_review_count']
                    if "required_pull_request_owner_review" in custom_rules:
                        protection_rules['required_pull_request_owner_review'] = custom_rules['required_pull_request_owner_review']
                    if "enforce_admins" in custom_rules:
                        protection_rules['enforce_admins'] = custom_rules['enforce_admins']

        set_default_branch_protection(cfg, repo, protection_rules)
