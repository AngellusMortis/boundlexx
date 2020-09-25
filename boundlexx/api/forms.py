from django import forms

from boundlexx.boundless.models import World

BASE_QUERY = World.objects.all()


class ForumFormatForm(forms.Form):
    username = forms.CharField(required=True, help_text="Your Boundless Username")
    world_name = forms.CharField(
        required=True, help_text="The name of your world.", label="World Name"
    )
    world_id = forms.IntegerField(
        required=False,
        help_text=(
            "The ID of your world if 'World Name' is not working. You can get "
            'your World ID from the <a href="https://forum.playboundless.com/'
            "uploads/default/original/3X/3/f/3fef2e21cedc3d4594971d6143d40110bd489686"
            '.jpeg" target="_blank">Debug Menu</a> if you are on PC'
        ),
        label="World ID",
    )
    will_renew = forms.NullBooleanField(
        required=True,
        help_text="Do you plan to renew this world?",
        label="Will Renew?",
    )
    can_visit = forms.BooleanField(
        required=False,
        help_text="Can Everyone warp/use portals to your world?",
        label="Can Visit?",
    )
    can_edit = forms.BooleanField(
        required=False,
        help_text="Can Everyone edit blocks on your world (outside of plots)?",
        label="Can Edit?",
    )
    can_claim = forms.BooleanField(
        required=False,
        help_text="Can Everyone create beacon and plot on your world?",
        label="Can Claim?",
    )
    portal_directions = forms.CharField(
        required=True,
        max_length=100,
        help_text="Directions to help players find the portal to your world",
        label="Portal Directions",
    )

    def clean(self):
        cleaned_data = super().clean()

        world_id = cleaned_data.get("world_id")
        if world_id:
            try:
                world = BASE_QUERY.get(pk=world_id)
            except World.DoesNotExist:
                self.add_error("world_id", "Could not find a world with that ID")
            else:
                cleaned_data["world"] = world
        else:
            world_name = cleaned_data.get("world_name")
            try:
                world = BASE_QUERY.get(display_name=world_name)
            except World.DoesNotExist:
                self.add_error(
                    "world_name",
                    "Could not find a world with that name. Try using World ID.",
                )
            except World.MultipleObjectsReturned:
                self.add_error(
                    "world_name", "Multiple worlds with that name. Try using World ID."
                )
            else:
                cleaned_data["world"] = world

        return cleaned_data
