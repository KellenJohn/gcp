# gcp 
# test ms


```bash
git remote add origin git@github.com:KellenJohn/gcp.git
git branch -M develop
git push -u origin develop
```

* Change the git url to git
```bash
git remote -v
git remote set-url origin git@github.com:KellenJohn/gcp.git
```

* Set the SSH Key
```bash
ssh-keygen -t rsa -b 4096 -C "your_email@example.com"
# check ssh-agent is workable
eval $(ssh-agent -s)
# if show this is workable
> Agent pid 59566
# add the secret to agent
ssh-add ~/.ssh/id_rsa
```
* copy secret to GitHub
* Git push

