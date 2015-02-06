from django import forms
from django.conf import settings

from eveonline.models import EveCorporationInfo
from services.managers.eve_api_manager import EveApiManager
from eveonline.managers import EveManager


class HRApplicationForm(forms.Form):
	allchoices = []
	for corp in EveCorporationInfo.objects.all():
		if corp.alliance is not None:
			if corp.alliance.alliance_id == settings.ALLIANCE_ID:
				allchoices.append((str(corp.corporation_id), str(corp.corporation_name)))

	character_name = forms.CharField(max_length=254, required=True, label="Character Who is Applying")
	full_api_id = forms.CharField(max_length=254, required=True, label="API ID")
	full_api_key = forms.CharField(max_length=254, required=True, label="API Verification Code")
	corp = forms.ChoiceField(choices=[(settings.CORPORATION_ID, settings.CORPORATION_NAME)], required=True, label="Corp")
	is_a_spi = forms.ChoiceField(choices=[('Yes', 'Yes'), ('No', 'No')], required=True, label='Are you a spy?')
	about = forms.CharField(widget=forms.Textarea, required=False, label="About You")
	extra = forms.CharField(widget=forms.Textarea, required=False, label="Extra Application Info")

	def clean(self):
		if not EveApiManager.check_api_is_type_account(self.cleaned_data['full_api_id'], self.cleaned_data['full_api_key']):
			raise forms.ValidationError(u'API not of type account')

		if not EveApiManager.check_api_is_full(self.cleaned_data['full_api_id'], self.cleaned_data['full_api_key']):
			raise forms.ValidationError(u'API supplied is not a full api key')

		return self.cleaned_data


class HRApplicationCommentForm(forms.Form):
	app_id = forms.CharField(widget=forms.TextInput(attrs={'readonly': 'True'}))
	comment = forms.CharField(widget=forms.Textarea, required=False, label="Comment", max_length=254)


class HRApplicationSearchForm(forms.Form):
	search_string = forms.CharField(max_length=254, required=True, label="Search String")