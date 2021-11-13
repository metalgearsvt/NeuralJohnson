Plop the entire repo into 
> /home/ubuntu/markov/code

If that doesn't work for you, edit installUser.sh

Run `installUser.sh` from within its own directory.

Folders will be made next to the code directory with links to keep code synced.

Deployment means just changing the code in /code/

After running the script you will need to still setup conf.py and initializeDatabase.py and run initializeDatabase.py.

Then you will need to restart the daemon which will be the username.