import importlib

class Translator:
    def __init__(self, lang="en"):
        self.translations = {}
        self.load(lang)

    def load(self, lang):
        try:
            mod = importlib.import_module(f"gfd.i18n.{lang}")
            self.translations = getattr(mod, "translations", {})
        except ModuleNotFoundError:
            # fallback to Spanish
            mod = importlib.import_module("gfd.i18n.es")
            self.translations = getattr(mod, "translations", {})

    def __call__(self, key):
        return self.translations.get(key, key)
