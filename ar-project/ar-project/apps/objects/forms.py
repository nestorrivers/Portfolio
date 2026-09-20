from django import forms
from .models import ARTextObjectTemplate, ARTextObject



class ARTextObjectTemplateForm(forms.ModelForm):
    SHAPE_CHOICES = [
        ('plane', 'Plane'),
        ('box', 'Box'),
        ('circle', 'Circle'),
        ('sphere', 'Sphere'),
        ('cylinder', 'Cylinder'),
        ('cone', 'Cone'),
        ('torus', 'Torus'),
        # ('custom_model', 'Custom Model (GLTF)'),
    ]


    name = forms.CharField(max_length=120)
    description = forms.CharField(widget=forms.Textarea, required=False)
    is_active = forms.BooleanField(required=False)
    shape = forms.ChoiceField(choices=SHAPE_CHOICES)
    width = forms.FloatField(required=False)
    height = forms.FloatField(required=False)
    depth = forms.FloatField(required=False)
    radius = forms.FloatField(required=False)
    radius_top = forms.FloatField(required=False)
    radius_bottom = forms.FloatField(required=False)
    model_url = forms.URLField(required=False)
    rotation_x = forms.FloatField(required=False)
    rotation_y = forms.FloatField(required=False)
    rotation_z = forms.FloatField(required=False)
    billboard = forms.BooleanField(required=False)
    material_opacity = forms.FloatField(required=False)
    material_transparent = forms.BooleanField(required=False)
    material_metalness = forms.FloatField(required=False)
    material_roughness = forms.FloatField(required=False)
    texture_url = forms.URLField(required=False)
    texture_repeat_x = forms.FloatField(required=False)
    texture_repeat_y = forms.FloatField(required=False)
    cast_shadow = forms.BooleanField(required=False)
    receive_shadow = forms.BooleanField(required=False)
    clickable = forms.BooleanField(required=False)
    hover_enabled = forms.BooleanField(required=False)
    dwell_time_ms = forms.IntegerField(required=False)
    scale_on_hover = forms.FloatField(required=False)
    animation_enabled = forms.BooleanField(required=False)
    animation_type = forms.CharField(max_length=50, required=False)

    class Meta:
        model = ARTextObjectTemplate
        fields = [
            'name', 'description', 'is_active', 'shape', 'width', 'height', 
            'depth', 'radius', 'radius_top', 'radius_bottom', 'model_url', 
            'rotation_x', 'rotation_y', 'rotation_z', 'billboard', 
            'material_opacity', 'material_transparent', 'material_metalness', 
            'material_roughness', 'texture_url', 'texture_repeat_x', 
            'texture_repeat_y', 'cast_shadow', 'receive_shadow', 'clickable', 
            'hover_enabled', 'dwell_time_ms', 'scale_on_hover', 
            'animation_enabled', 'animation_type'
        ]


class ARTextObjectForm(forms.ModelForm):
    VISIBILITY_CHOICES = [
        ('Public', 'Public'),
        ('Unlisted', 'Unlisted'),
        ('Private', 'Private'),
    ]

    COLOURS = [
        ('Black', 'Black'),
        ('White', 'White'),
        ('Red', 'Red'),
        ('Green', 'Green'),
        ('Blue', 'Blue'),
        ('Yellow', 'Yellow'),
        ('Purple', 'Purple'),
        ('Orange', 'Orange'),
        ('Gray', 'Gray'),
    ]

    FONT_CHOICES = [
        ('Default', 'Default'),
        ('MozillaVR', 'Mozilla VR'),
        ('AileronSemibold', 'Aileron Semibold'),
    ]

    TEXT_ALIGN_CHOICES = [
        ('left', 'Left'),
        ('center', 'Center'),
        ('right', 'Right'),
    ]

    SHAPE_CHOICES = [
        ('plane', 'Plane'),
        ('box', 'Box'),
        ('circle', 'Circle'),
        ('sphere', 'Sphere'),
        ('cylinder', 'Cylinder'),
        ('cone', 'Cone'),
        ('torus', 'Torus'),
        ('custom_model', 'Custom Model (GLTF)'),
    ]

    title = forms.CharField(max_length=200)
    description = forms.CharField(widget=forms.Textarea, required=False)
    text_content = forms.CharField(widget=forms.Textarea, required=False)
    # font = forms.ChoiceField(choices=FONT_CHOICES, required=False)
    font_size = forms.FloatField(required=False)
    text_wrap_count = forms.IntegerField(required=False)
    text_align = forms.ChoiceField(choices=TEXT_ALIGN_CHOICES, required=False)
    text_width = forms.FloatField(required=False)
    text_opacity = forms.FloatField(required=False)
    text_colour = forms.ChoiceField(choices=COLOURS, required=False)
    object_colour = forms.ChoiceField(choices=COLOURS, required=False)
    text_offset_x = forms.FloatField(required=False)
    text_offset_y = forms.FloatField(required=False)
    text_offset_z = forms.FloatField(required=False)
    latitude = forms.FloatField()
    longitude = forms.FloatField()
    altitude = forms.FloatField(required=False)
    template = forms.ModelChoiceField(queryset=ARTextObjectTemplate.objects.all(), required=False)
    visibility = forms.ChoiceField(choices=VISIBILITY_CHOICES)

    description = forms.CharField(widget=forms.Textarea, required=False)
    is_active = forms.BooleanField(required=False)
    shape = forms.ChoiceField(choices=SHAPE_CHOICES)
    width = forms.FloatField(required=False)
    height = forms.FloatField(required=False)
    depth = forms.FloatField(required=False)
    radius = forms.FloatField(required=False)
    radius_top = forms.FloatField(required=False)
    radius_bottom = forms.FloatField(required=False)
    model_url = forms.URLField(required=False)
    rotation_x = forms.FloatField(required=False)
    rotation_y = forms.FloatField(required=False)
    rotation_z = forms.FloatField(required=False)
    billboard = forms.BooleanField(required=False)
    material_opacity = forms.FloatField(required=False)
    material_transparent = forms.BooleanField(required=False)
    material_metalness = forms.FloatField(required=False)
    material_roughness = forms.FloatField(required=False)
    texture_url = forms.URLField(required=False)
    texture_repeat_x = forms.FloatField(required=False)
    texture_repeat_y = forms.FloatField(required=False)
    cast_shadow = forms.BooleanField(required=False)
    receive_shadow = forms.BooleanField(required=False)
    clickable = forms.BooleanField(required=False)
    hover_enabled = forms.BooleanField(required=False)
    dwell_time_ms = forms.IntegerField(required=False)
    scale_on_hover = forms.FloatField(required=False)
    animation_enabled = forms.BooleanField(required=False)
    animation_type = forms.CharField(max_length=50, required=False)

    class Meta:
        model = ARTextObject
        fields = [
            'title', 'description', 'text_content',
            'font_size', 'text_wrap_count', 'text_align', 'text_width',
            'text_opacity', 'text_colour', 'object_colour',
            'text_offset_x', 'text_offset_y', 'text_offset_z',
            'latitude', 'longitude', 'altitude', 'template', 'visibility'
            # 'font',
        ]


class SuspendObjectForm(forms.Form):
    reason = forms.CharField(widget=forms.Textarea, required=True)
    ban_user = forms.BooleanField(required=False)
    ban_user_duration_days = forms.IntegerField(required=False)



