# Git drill (45 minutes on day 3, 30 minutes on day 17)

Learn the commands by using them on a throw-away repository. Build it first:

```bash
python make_git_drill.py ../../git_drill_repo      # any new, empty folder
cd ../../git_drill_repo
git log --oneline --all --graph                    # look at the shape
```

References: the Pro Git book <https://git-scm.com/book/en/v2>, the interactive
<https://learngitbranching.js.org/> (practise branching in the browser), GitHub flow
<https://docs.github.com/en/get-started/using-github/github-flow>, and resolving a conflict from the
command line <https://docs.github.com/en/pull-requests/collaborating-with-pull-requests/addressing-merge-conflicts/resolving-a-merge-conflict-using-the-command-line>.

## The picture in your head
```
working folder  --git add-->  staging area  --git commit-->  your repository  --git push-->  GitHub
      ^                                                           |
      +------------------------- git restore / git switch --------+
```

## Part 1: branches and a merge conflict (day 3)
1. `git switch feature/a` then `git merge feature/b`. Git stops: **CONFLICT**. That is normal, not an error to fear.
2. `git status` tells you which file is in conflict. Open `policy.txt`. You will see:
   ```
   <<<<<<< HEAD
   A member may keep a book for 28 days.
   =======
   A member may keep a book for 14 days.
   >>>>>>> feature/b
   ```
   The top is your branch, the bottom is the other branch.
3. **Decide with a person**: which rule is right? Edit the file to the final text and delete the three marker lines.
   (Never choose "ours" or "theirs" without reading, Playbook VC-13.)
4. `git add policy.txt` then `git commit` (Git suggests a message). Run the tests of your project if it has any.
5. `git log --oneline --graph --all` and draw what happened.

## Part 2: rebase (day 3)
1. `git switch -c practice main`, make a commit, then on `main` make another commit.
2. On `practice` run `git rebase main`. Compare the history with a merge. Which is easier to read?
3. **Rule:** never rebase or force-push a branch that other people use (VC-12).

## Part 3: undo mistakes (day 3)
| Situation | Command |
|---|---|
| Throw away edits to a file that is not staged | `git restore <file>` |
| Unstage a file | `git restore --staged <file>` |
| Undo the last commit but keep the changes | `git reset --soft HEAD~1` |
| Undo a commit that is already shared, safely | `git revert <commit>` |
| "I lost a commit!" | `git reflog` shows where HEAD has been; `git switch -c rescue <hash>` |

Practise each once. Then run `git reflog` and find a commit you "lost".

## Part 4: the leaked secret (day 17)
The branch `oops` has a fake key in `settings.txt`.
1. Find it with the secret scanner your project uses (`gitleaks`).
2. **Rotate first.** For a real key this is step one, because anyone who cloned it already has it. (GitHub's own page says the same:
   <https://docs.github.com/en/authentication/keeping-your-account-and-data-secure/removing-sensitive-data-from-a-repository>.)
3. Only if the secret is still needed in history: rewrite history with `git filter-repo` (follow the GitHub page: version requirements, the `--invert-paths` or `--replace-text` options, then a forced push).
4. Tell everyone to **re-clone**: old clones and forks can bring the secret back.
5. Write the five steps you would give a team.

## Part 5: the GitHub flow with your own repository (day 1 and every day)
1. `git switch -c feature/short-name`
2. Small commits with clear messages (`git add -p` lets you pick parts).
3. `git push -u origin feature/short-name`
4. Open a pull request (`gh pr create` or the web page) using the template.
5. Respond to review comments with more commits; the pull request updates by itself.
6. Merge when approved and checks pass; delete the branch.

## Check yourself
- Can you explain the difference between `merge` and `rebase` in two sentences?
- Which command rescued your "lost" commit?
- What are the first two things you do when a secret is committed?
