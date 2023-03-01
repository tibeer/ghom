# GHOM - GitHub Organization Manager

Ghom is a tool to manage your GitHub organisation by a simple YAML file. Users, teams, repos, labels, primary branch protections and even team per repo access! You have private repos and don't want to expose them? Just use another private repo with an additional ghom config file.

## How to use

In any case you need to change the settings in your organization to allow changes from actions. Head over to <https://github.com/organizations/YOUR_ORG/settings/actions>, scroll down to _Workflow permissions_ and select __Read and write permissions__. Otherwise github actions cannot change settings on your organization.

Additionally, you'll need a GHP for your account (or for your bot account). Head over to <https://github.com/settings/tokens>, generate a new "classic" token and tick `repo`, `admin:org` and `delete_repo`.

### Automated (recommended)

1. Create a fresh new GitHub organization. You may use ghom also on an existing org, but I will not guarantee for flawless integration. In any case: Use with caution.
2. Create a repository containing a `ghom.yaml` file.
3. Create a workflow like shown [here](.github/workflows/ghom_workflow.yml.example) in the same repository.
4. Create a secret inside your github repository (Settings > Secrets and variables > Actions > New repository secret). Name it __GHOM_TOKEN__ and insert your GHP.
5. Trigger the workflow it by either merging a PR to main (containing a change in `ghom.yaml`) or by manual execution.

### Manual

```sh
export GITHUB_REPOSITORY_OWNER=ghomtest
export INPUT_GHOM_CONFIG=ghom.yaml
export INPUT_GHOM_TOKEN=ghp_XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
export INPUT_GHOM_DRY=False
python3 -m ghom.main
```

## FAQ

Q: How to deal with private repositories?\
A: Look [here](docs/private_repositories.md)

Q: Why do you have to use a GHP token?\
A: A GitHub app would require a running server. I could provide one, but this would have the drawback, that the rate limit would affect all users simultaniously. Either we "gain" more possible requests than needed. Or a user with a humoungus organization size installs the app and will block the app for all users...

Q: How to deal with my large organization that is too large to fit into 5000 api requests per hour?\
A: Switch back to manual adjustment or split the ghom file into multiple parts. The principle is basically the same as if you would use [private repositories](docs/private_repositories.md). If you have another (elegant) solution, let me know!

Q: Why do repositories have to be initialized with the default README.md file?\
A: Otherwise branch protections cannot be set.

Q: Why is the code so redundant?\
A: To keep it simple. If you have a solution, that removes redundant code while keeping it easy to maintain and understand, feel free to create a pull request.

Q: Why is there no script to generate a `ghom.yaml` file from an existing org?\
A: I had no interest in creating one yet. Chances are low that I find the motivation in the future :)

Q: Why is the ghom called _ghom-ghom_ in the GitHub marketplace?\
A: _ghom_ was taken already or is too short. Therefore the name _ghom-ghom_.

## Known issues

Branch protection rules are a bit flanky. You can only delete them, if default rules are set. Leaving them empty would result in keeping the current rules.

If you create a new team, the owner of the organization will be added automatically to this team. Therefore you'll see first the creation of the and and second the deletion of a team member. This behavior is due to GitHub internal handeling of these API requests and cannot be changed.
