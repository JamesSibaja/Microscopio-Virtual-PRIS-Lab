from django.forms import ModelForm, Textarea, Form,FileField
# from crispy_forms.helper import FormHelper
# from crispy_forms.layout import Submit
from microscope.models import Slide
from django import forms

# class FileUploadForm(forms.Form):
#     file = forms.FileField(label='Selecciona un archivo')
#     name = forms.CharField(label='Nombre de slide')
#     decription = forms.CharField(label='Descripcion del slide')

#     def __init__(self, *args, **kwargs):
#         super().__init__(*args, **kwargs)
#         self.helper = FormHelper()
#         self.helper.form_id = 'file-upload-form'
#         self.helper.form_method = 'post'
#         self.helper.form_class = 'form-horizontal'
#         self.helper.add_input(Submit('submit', 'Subir'))
class UploadFileForm(forms.Form):
    name = forms.CharField(max_length=100, label='Nombre')
    description = forms.CharField(widget=forms.Textarea, label='Descripción')

class SlideForm(ModelForm):
    # file = FileField(label='Selecciona un archivo')
    class Meta:
        model = Slide
        fields = ['name','description']
        labels = {'name':'Titulo','description':'Descripción'}

    def __init__(self, *args, **kwargs):
        super(SlideForm,self).__init__( *args, **kwargs)
        self.fields['name'].widget.attrs['class'] = 'form-control'
        self.fields['name'].widget.attrs['placeholder'] = 'Titulo del slide'
        self.fields['description'].widget.attrs['class'] = 'form-control'
        self.fields['description'].widget.attrs['placeholder'] = 'Descripción del slide'