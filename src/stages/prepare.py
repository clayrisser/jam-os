from deb import Deb
from loaders import loaders
from overlay import Overlay
from util import merge_dir, import_module
import os
import shutil


class PrepareStage:
    def __init__(self, deb: Deb):
        self.deb = deb

    async def run(self):
        await self.load_overlays()
        await self.deb.hooks.trigger("before_prepare")
        await self.initialize_build()
        await self.initialize_lb()
        await self.initialize_os()
        await self.initialize_overlays()
        await self.apply_loaders()
        await self.deb.hooks.trigger("after_prepare")

    async def load_overlays(self):
        overlay: Overlay
        for overlay_name, overlay in self.deb.overlays.items():
            overlay_module = None
            if os.path.exists(os.path.join(overlay.path, "overlay.py")):
                overlay_module = import_module(
                    "overlay_" + overlay_name, os.path.join(overlay.path, "overlay.py")
                )
            overlay_hooks = None
            if hasattr(overlay_module, "OverlayHooks"):
                overlay_hooks = overlay_module.OverlayHooks(self.deb)
            for method_name in dir(overlay_hooks):
                if len(method_name) <= 0:
                    continue
                if method_name[0] == "_":
                    continue
                if not hasattr(overlay_hooks, method_name):
                    continue
                if not callable(getattr(overlay_hooks, method_name)):
                    continue
                overlay_hook_name = method_name
                overlay_hook = getattr(overlay_hooks, method_name)
                self.deb.hooks.listen(
                    overlay_hook_name, lambda *args: overlay_hook(*args)
                )

    async def initialize_build(self):
        if not os.path.exists(self.deb.paths["build"]):
            os.makedirs(self.deb.paths["build"])
        shutil.copyfile(
            os.path.join(self.deb.paths["root"], "mkpm.mk"),
            os.path.join(self.deb.paths["build"], "mkpm.mk"),
        )
        if os.path.exists(
            os.path.join(self.deb.paths["root"], ".mkpm")
        ) and not os.path.exists(os.path.join(self.deb.paths["build"], ".mkpm")):
            shutil.copytree(
                os.path.join(self.deb.paths["root"], ".mkpm"),
                os.path.join(self.deb.paths["build"], ".mkpm"),
            )
        os.chdir(self.deb.paths["build"])

    async def initialize_lb(self):
        if os.path.exists(self.deb.paths["lb"]):
            shutil.rmtree(self.deb.paths["lb"])
        shutil.copytree(
            os.path.join(self.deb.paths["root"], "lb"), self.deb.paths["lb"]
        )

    async def initialize_os(self):
        if os.path.exists(self.deb.paths["os"]):
            shutil.rmtree(self.deb.paths["os"])
        shutil.copytree(
            os.path.join(self.deb.paths["root"], "os"), self.deb.paths["os"]
        )

    async def initialize_overlays(self):
        for _overlay_name, overlay in self.deb.overlays.items():
            await merge_dir(overlay.path, self.deb.paths["os"])

    async def apply_loaders(self):
        for Loader in loaders:
            loader = Loader(self.deb)
            await self.deb.hooks.trigger("before_" + loader.name)
            await loader.load()
            await self.deb.hooks.trigger("after_" + loader.name)
