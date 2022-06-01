from yaml import SafeLoader
import shutil
import glob
import os
import yaml


class ReposLoader:
    name = "repos"

    def __init__(self, deb):
        self.deb = deb

    async def load(self):
        repos = await self.get_repos()
        for r in repos:
            await self.load_repo(Repo(r))

    async def get_repos(self):
        repos = []
        for path in glob.glob(
            os.path.join(self.deb.paths["os"], "repos/**/*.yaml"), recursive=True
        ):
            with open(path) as f:
                data = yaml.load(f, Loader=SafeLoader)
                repos += data
        return repos

    async def load_repo(self, repo):
        if not os.path.exists(
            os.path.join(
                self.deb.paths["lb"],
                "config-overrides/archives",
            )
        ):
            os.makedirs(
                os.path.join(
                    self.deb.paths["lb"],
                    "config-overrides/archives",
                )
            )
        if repo.live:
            # list.chroot key.chroot
            with open(
                os.path.join(
                    self.deb.paths["lb"],
                    "config-overrides/archives",
                    repo.name + ".list.chroot",
                ),
                "w",
            ) as f:
                f.write(repo.repo + "\n")
            if repo.key:
                with open(
                    os.path.join(
                        self.deb.paths["lb"],
                        "config-overrides/archives",
                        repo.name + ".key.chroot",
                    ),
                    "w",
                ) as f:
                    f.write(repo.key + "\n")
            elif os.path.exists(
                os.path.join(self.deb.paths["os"], "repos", repo.name + ".key")
            ):
                shutil.copyfile(
                    os.path.join(self.deb.paths["os"], "repos", repo.name + ".key"),
                    os.path.join(
                        self.deb.paths["lb"],
                        "config-overrides/archives",
                        repo.name + ".key.chroot",
                    ),
                )
        if repo.installed:
            pass
        if repo.binary:
            with open(
                os.path.join(
                    self.deb.paths["lb"],
                    "config-overrides/archives",
                    repo.name + ".list.binary",
                ),
                "w",
            ) as f:
                f.write(repo.repo + "\n")
            if repo.key:
                with open(
                    os.path.join(
                        self.deb.paths["lb"],
                        "config-overrides/archives",
                        repo.name + ".key.binary",
                    ),
                    "w",
                ) as f:
                    f.write(repo.key + "\n")
            elif os.path.exists(
                os.path.join(self.deb.paths["os"], "repos", repo.name + ".key")
            ):
                shutil.copyfile(
                    os.path.join(self.deb.paths["os"], "repos", repo.name + ".key"),
                    os.path.join(
                        self.deb.paths["lb"],
                        "config-overrides/archives",
                        repo.name + ".key.binary",
                    ),
                )


class Repo:
    def __init__(self, repo):
        self.live = repo["live"] if "live" in repo else True
        self.installed = repo["installed"] if "installed" in repo else True
        self.binary = repo["binary"] if "binary" in repo else False
        self.name = repo["name"].strip()
        self.repo = repo["repo"].strip()
        self.key = repo["key"].strip() if "key" in repo else None
