Here's a clean refresher on **GitHub basics from the shell**, nothing
fancy.

**1. Create a new repo on GitHub**

Do this on the GitHub website:

-   Click **New repository**

-   Give it a name (e.g., python-sandbox)

-   Leave it empty (no README) --- makes shell setup simpler

-   Copy the repo URL (HTTPS is easiest)

Example URL:

https://github.com/yourname/python-sandbox.git

**2. Make a local folder**

In your filesystem:

mkdir python-sandbox

cd python-sandbox

**3. Initialize Git**

git init

**4. Add the remote**

git remote add origin https://github.com/yourname/python-sandbox.git

**5. Add your Python files**

Put your .py files in the folder.

Then:

git add .

git commit -m \"initial commit\"

git push -u origin main

If GitHub created a master branch instead of main, use:

git push -u origin master

**6. Pull changes back down**

If you change something on GitHub:

git pull

**7. Clone an existing repo**

If you want to bring a repo down fresh:

git clone https://github.com/yourname/python-sandbox.git

That's it --- you now have a local copy.

**That's the entire basic workflow**

-   git init

-   git add

-   git commit

-   git push

-   git pull

-   git clone

To tell Git who you are, you only need **two commands**.\
Run these in **MSYS2**:

git config \--global user.name \"Brian\"

git config \--global user.email \"your_email@example.com\"

Check them:

git config \--global \--list

You should see:

user.name=Brian

user.email=your_email@example.com

To tell Git who you are, you only need **two commands**.\
Run these in **MSYS2**:

git config \--global user.name \"Brian\"

git config \--global user.email \"your_email@example.com\"

Check them:

git config \--global \--list

You should see:

user.name=Brian

user.email=your_email@example.com

**2. Start the SSH agent**

eval \"\$(ssh-agent -s)\"

**3. Add your key to the agent**

ssh-add \~/.ssh/id_ed25519

**4. Copy the public key**

cat \~/.ssh/id_ed25519.pub

Copy the entire line that starts with:

ssh-ed25519

**5. Add it to GitHub**

On GitHub:

-   Settings

-   SSH and GPG keys

-   New SSH key

-   Paste the key

-   Save

**6. Test the connection**

ssh -T git@github.com

Expected output:

Hi Brian! You\'ve successfully authenticated\...

**7. Use SSH URLs instead of HTTPS**

When adding a remote:

git remote add origin git@github.com:yourname/yourrepo.git

Or when cloning:

git clone git@github.com:yourname/yourrepo.git
