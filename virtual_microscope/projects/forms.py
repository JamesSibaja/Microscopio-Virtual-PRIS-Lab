from django.forms import ModelForm, Textarea, Form
from django import forms
from projects.models import ProjectSlide, Notes, Project, User
from django.contrib.admin.widgets import FilteredSelectMultiple
from django.contrib import admin


class ProjectForm(forms.ModelForm):
    class Meta:
        model = Project
        fields = '__all__'
        widgets = {
            'sharedUsers': FilteredSelectMultiple("sharedUsers", is_stacked=False),
            'invitedUsers': FilteredSelectMultiple("invitedUsers", is_stacked=False),
        }


class ProjectAdmin(admin.ModelAdmin):
    form = ProjectForm

class MensajeForm(forms.Form):
    contenido = forms.CharField(widget=forms.Textarea)
    class Meta:
        model = Notes
        fields = ['user','project','contenido']
        labels = {'name':'Texto','description':'Detalles Adicionales'}
        exclude = ['user','project','contenido']

class SearchForm(forms.Form):
    titulo = forms.CharField()
    def __init__(self, *args, **kwargs):
        super(SearchForm,self).__init__( *args, **kwargs)
        self.fields['titulo'].widget.attrs['class'] = 'form-control'
        self.fields['titulo'].widget.attrs['placeholder'] = 'Titulo del Proyecto'

class NoteForm(ModelForm):
    class Meta:
        model = Notes
        fields = ['project','name','description','xUnoPos','yUnoPos','xDosPos','yDosPos','geojson_data']
        labels = {'name':'Texto','description':'Detalles Adicionales'}
        exclude = ['project','xUnoPos','yUnoPos','xDosPos','yDosPos','geojson_data']
        widgets = {
          'description': Textarea(attrs={'rows':3, 'cols':80}),
        }
    def __init__(self, *args, **kwargs):
        super(NoteForm,self).__init__( *args, **kwargs)
        self.fields['name'].widget.attrs['class'] = 'form-control'
        self.fields['name'].widget.attrs['placeholder'] = 'Contenido de la nota'
        self.fields['description'].widget.attrs['class'] = 'form-control'
        self.fields['description'].widget.attrs['placeholder'] = 'Detalles adicionales de la nota'

class ProjectForm(ModelForm):
    class Meta:
        model = Project
        fields = ['name','user','description']
        labels = {'name':'Titulo','description':'Descripción'}
        exclude = ['user']

    def __init__(self, *args, **kwargs):
        super(ProjectForm,self).__init__( *args, **kwargs)
        self.fields['name'].widget.attrs['class'] = 'form-control'
        self.fields['name'].widget.attrs['placeholder'] = 'Titulo del proyecto'
        self.fields['description'].widget.attrs['class'] = 'form-control'
        self.fields['description'].widget.attrs['placeholder'] = 'Descripción del proyecto'

    
class ProjectSlideForm(ModelForm,Form):
    class Meta:
        model = ProjectSlide
        fields = ['name','project','description','slide']
        labels = {'name':'Titulo','description':'Descripción'}
        exclude = ['project','slide']

    def __init__(self, *args, **kwargs):
        argumento = kwargs.pop('name', None)
        super(ProjectSlideForm,self).__init__( *args, **kwargs)
        self.fields['name'].widget.attrs['class'] = 'form-control'
        # self.fields['name'].widget.attrs['placeholder'] = kwargs['instanceName']
        self.fields['description'].widget.attrs['class'] = 'form-control'
        

