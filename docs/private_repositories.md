# Private repositories

You can split `ghom.yaml` files into multiple parts or even across different repositories.
Both methods have in common that you require more than one workflow.

Because of this, one workflow might interfer with the other one, especially when it comes to deletion.
Let's assume the following scenario:

- Workflow A takes care of public repositories
- Workflow B takes care of private repositories and also teams (only global teams, not repo specific ones), because they should be kept private

If workflow A has `allow_team_removal` set to __true__, it will most likely happen that all your teams managed by workflow B will be deleted. This is not a flaw in the code but rather originates from the design conzept. Ghom indends to be idempotent, so it works as expected.

Rather use multiple ghom files, all with e.g. `allow_team_removal` all set to __false__ except for one file. This file should then also contain all teams.

By using this method you can A) hide sensitive content in private repositories and B) can bypass API rate limits. Though, you might need multiple bot accounts with seperate GHP tokens.
