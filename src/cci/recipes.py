import logging
import os
from typing import Optional, Iterator, List

import cci.types
from cci.recipe import Recipe
from cci.recipe_options import explode_options_without_duplicates
from cci.repository import Repository
from conans.model.ref import ConanFileReference

log = logging.getLogger(__name__)


def get_recipe_list(cci_repo: Repository,
                    cwd: cci.types.PATH,
                    draft_folder: Optional[cci.types.PATH],
                    explode_options: bool = False) -> Iterator[Recipe]:
    # Clone the repo and return recipes in it
    cci_repo.clone(base_folder=cwd)
    recipes: List[str] = []
    for recipe in cci_repo.get_recipe_list():
        recipes.append(recipe.ref.name)
        if explode_options:
            for it in explode_options_without_duplicates(recipe):
                yield it
        else:
            yield recipe

    # Go for the draft recipes (avoid duplicates)
    if draft_folder:
        for recipe in get_draft_recipes(draft_folder):
            if recipe.ref.name not in recipes:
                yield recipe
            else:
                log.warninig(f"Duplicate recipe in drafts: {recipe.ref.name}")


def get_draft_recipes(draft_folder: cci.types.PATH):
    log.info(f"Gather draft recipes from {draft_folder}")

    for recipe in os.listdir(draft_folder):
        name, _ = os.path.splitext(recipe)
        ref = ConanFileReference(name=name, version='draft', user=None, channel=None)
        conanfile = os.path.join(draft_folder, recipe)
        yield Recipe(ref=ref, conanfile=conanfile, is_draft=True)