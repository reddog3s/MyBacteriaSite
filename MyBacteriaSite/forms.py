from django import forms
from django.contrib.auth.forms import UserCreationForm
from django_countries.fields import CountryField

from django.forms.widgets import ClearableFileInput


from MyBacteriaSite.models import MicrobePost, Microbe
from django.forms import ModelForm, Form
from django.contrib.auth.models import User




class DateInput(forms.DateInput):
    input_type = 'date'


class NewUserForm(UserCreationForm):
	email = forms.EmailField(required=True)
	birthdate = forms.DateField(widget=DateInput, help_text='Birthday date', required= False)
	country = CountryField(blank=True).formfield()

	class Meta:
		model = User
		fields = ["username", "password1", "password2", "email", "birthdate", "country"]

 
	def save(self, commit=True):
		user = super(NewUserForm, self).save(commit=False)
		user.email = self.cleaned_data['email']
		if commit:
			user.save()
		return user



class NewPostFrom(ModelForm):
	image = forms.ImageField(widget=ClearableFileInput(attrs={'class': 'dropzone', 'accept': 'image/*'}))


	class Meta:
		model = MicrobePost
		fields = ["title", "longitude", "latitude", "image", "microbe", "text"]


	


class NewMicrobeFrom(ModelForm):

	class Meta:
		model = Microbe
		fields = '__all__'

class CSV_form(Form):
	csv_file = forms.FileField(label = "Microbes as csv")


class MicrobeFilter(Form): 
	def create_choices(field):
		temp = Microbe.objects.order_by().values_list(field).distinct()
		temp = list(temp)
		choices = []
		for choice in temp:
			choices.append((choice[0], choice[0]))
		choices.append((None, '-------'))
		return choices

	Phylum = forms.ChoiceField(choices = create_choices('MicrobePhylum'), label='Phylum', required= False)

	Class = forms.ChoiceField(choices = create_choices('MicrobeClass'),label='Class', required= False)

	Order = forms.ChoiceField(choices = create_choices('MicrobeOrder'),label='Order', required= False)

	Family = forms.ChoiceField(choices = create_choices('MicrobeFamily'),label='Family', required= False)

	Genus = forms.ChoiceField(choices = create_choices('MicrobeGenus'),label='Genus', required= False)

	Species = forms.CharField(label='Species', required= False)

	num_of_posts_high_th = forms.IntegerField(label='Number of likes higher than', required= False)
	num_of_posts_low_th = forms.IntegerField(label='Number of likes lower than', required= False)


class PostFilter(Form):
    author = forms.CharField(label='Author', required= False)
    title = forms.CharField(label='Title', required= False)
    microbe = forms.CharField(label='Microbe', required= False)
    created_date_high_th = forms.DateTimeField(widget=DateInput, label='Date published later than', required= False)
    created_date_low_th = forms.DateTimeField(widget=DateInput, label='Date published earlier than', required= False)
    num_of_likes_high_th = forms.IntegerField(label='Number of likes higher than', required= False)
    num_of_likes_low_th = forms.IntegerField(label='Number of likes lower than', required= False)


