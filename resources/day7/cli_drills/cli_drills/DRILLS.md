# Command-line drills

Each drill is a list of tasks. Write the command that does the task, then run it to check. The
answers are in the file Command-line drills answers (under Files); read them after you have tried the drill. Pass mark: 12 of 15 in drill 1,
12 of 15 in drill 2, 8 of 10 in drills 3 to 5, 6 of 8 in drill 6.

Practise in a **throw-away folder or container**, never on a customer machine. Read the official
pages when you are unsure: Git <https://git-scm.com/docs>, GitHub CLI <https://cli.github.com/manual/>,
Docker <https://docs.docker.com/reference/cli/docker/>, `psql` <https://www.postgresql.org/docs/current/app-psql.html>,
`curl` <https://curl.se/docs/manpage.html>, `jq` <https://jqlang.github.io/jq/manual/>,
`kubectl` <https://kubernetes.io/docs/reference/kubectl/quick-reference/>.

## Drill 1: shell, Git and uv (day 1), 15 tasks
1. Print the folder you are in.
2. List all files, including hidden ones, in long format.
3. Create a folder `lab` and move into it.
4. Create an empty file `notes.txt`.
5. Show the first 5 lines of a file `server.log`.
6. Follow the end of `server.log` as it grows.
7. Find every line containing `ERROR` in `server.log`, ignoring upper or lower case.
8. Turn the folder into a Git repository.
9. Show which files changed and which are staged.
10. Stage `notes.txt` and commit it with the message `Add notes`.
11. Create and switch to a new branch called `feature/search`.
12. Show the last 5 commits, one line each.
13. Install the project's libraries exactly as the lock file says (uv).
14. Run the tests through uv.
15. Open a pull request from the current branch using the GitHub CLI, with title `Add search` and an empty body.

## Drill 2: Docker (day 7 and day 18), 15 tasks
1. Show the Docker version.
2. Download the image `postgres` with a specific tag `<TAG>`.
3. Start it in the background, named `pg`, with the password in an environment variable, port 5432 published only on 127.0.0.1, and a named volume `pgdata` for its data.
4. List running containers.
5. List all containers, including stopped ones.
6. Follow the log of `pg`.
7. Open a shell inside `pg`.
8. Open the `psql` program inside `pg` as user `postgres`.
9. Show the details of `pg` as JSON.
10. Show only its health status.
11. Stop `pg`.
12. Remove `pg` (but keep the volume).
13. List volumes.
14. Build an image from the current folder and tag it `app:release-a`.
15. Show how much disk Docker uses.

## Drill 3: Docker Compose (day 13 and day 18), 10 tasks
1. Show the final, merged configuration.
2. Start all services in the background, building first.
3. Show the status of the services.
4. Follow the last 100 lines of the log of service `app`.
5. Run a command `ls` inside the running service `app`.
6. Restart only `app`.
7. Pull newer images.
8. Stop and remove containers but keep volumes.
9. Show which command would also delete volumes (and why you must be careful).
10. Rebuild only `app` without using the cache.

## Drill 4: psql (day 7), 10 tasks
1. Connect to database `shop` on host `localhost`, port 5432, as user `alice`.
2. List databases.
3. Switch to database `analytics`.
4. List tables.
5. Describe table `orders`.
6. Turn on expanded output.
7. Run a script file `setup.sql`.
8. Run one query from the shell without opening the prompt.
9. Show the help for backslash commands from the shell.
10. Quit.

## Drill 5: curl and jq (day 4), 10 tasks
1. Fetch a URL and show the response headers too.
2. Fetch quietly (no progress bar) and pretty-print JSON.
3. Send a JSON body with POST.
4. Send an `Authorization` header with a token held in the variable `$TOKEN`.
5. Save the response to a file.
6. Show only the HTTP status code.
7. With `jq`: print the field `name` of each item in `.items`.
8. With `jq`: keep only the items whose `status` is `active`.
9. With `jq`: count the items.
10. Retry up to 3 times if the call fails.

## Drill 6: kubectl and Azure CLI (days 31 and 32), 8 tasks
1. Show which cluster context you are using.
2. List pods in the namespace `lab`.
3. Describe the pod `web-1`.
4. Show the log of `web-1`.
5. Apply the file `deploy.yaml` after a client-side dry run.
6. Watch the roll-out of deployment `web` finish.
7. Undo the last roll-out of `web`.
8. Azure: show which subscription you are signed in to; list resource groups; show a private endpoint named `pe-lab` in resource group `rg-lab`.
