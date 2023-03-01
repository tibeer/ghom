def build_attributes(cfg, repo_handle):
    # get all default labels
    default_labels = cfg.config['labels']
    # get all new repo labels
    new_repo_labels = []
    if cfg.config['repositories'][repo_handle.name]:
        if "labels" in cfg.config['repositories'][repo_handle.name]:
            new_repo_labels = cfg.config['repositories'][repo_handle.name]['labels']

    # combine them
    result_labels = default_labels
    add_counter = 0
    for new_repo_label in new_repo_labels:
        for default_label in default_labels:
            # if label found in defaults and new labels
            if new_repo_label['name'] == default_label['name']:
                # replace default label in favor of new label config
                replace_counter = 0
                for result_label in result_labels:
                    if result_label['name'] == default_label['name']:
                        result_labels[replace_counter] = new_repo_labels[add_counter]
                        break
                    replace_counter = replace_counter + 1
                break
        else:
            # add new label
            result_labels.append(new_repo_labels[add_counter])
        add_counter = add_counter + 1

    return result_labels


def add_new_labels(cfg, repo_handle):

    new_labels = build_attributes(cfg, repo_handle)

    for new_label in new_labels:
        cfg.increase_rate_counter()
        for old_label in repo_handle.get_labels():
            # check if label already exists
            if old_label.name == new_label['name']:
                # check if update is required
                if old_label.color != new_label['color'] or \
                   old_label.description != new_label['description']:
                    cfg.increase_rate_counter()
                    label = repo_handle.get_label(old_label.name)
                    if not cfg.dry_run:
                        cfg.increase_rate_counter()
                        label.edit(
                            name=old_label.name,
                            color=new_label['color'],
                            description=new_label['description']
                        )
                    cfg.log_change(f"{old_label.name} repo {repo_handle.name}")
                break
        else:
            # else create new label
            if not cfg.dry_run:
                cfg.increase_rate_counter()
                repo_handle.create_label(
                    name=new_label['name'],
                    color=new_label['color'],
                    description=new_label['description']
                )
            cfg.log_addition(f"{new_label['name']} repo {repo_handle.name}")


def delete_old_labels(cfg, repo_handle):
    cfg.increase_rate_counter()
    for old_labels in repo_handle.get_labels():
        new_labels = build_attributes(cfg, repo_handle)
        for new_label in new_labels:
            if old_labels.name == new_label['name']:
                # label found in config and online
                break
        else:
            # delete old label
            name = old_labels.name
            cfg.increase_rate_counter()
            label = repo_handle.get_label(name)
            if not cfg.dry_run:
                cfg.increase_rate_counter()
                label.delete()
            cfg.log_deletion(f"{name} repo {repo_handle.name}")


def set_labels(cfg):
    cfg.set_log_compartment("label")
    for repo in cfg.config['repositories']:
        cfg.increase_rate_counter()
        repo_handle = cfg.org_handle.get_repo(repo)
        add_new_labels(cfg, repo_handle)
        if cfg.config['allow_label_removal']:
            delete_old_labels(cfg, repo_handle)
