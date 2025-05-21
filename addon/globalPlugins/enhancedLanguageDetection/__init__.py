# coding: utf-8
# Copyright 2025 Emil-18
# An add-on that detects languages based on the spoken text itself
# This add-on is licensed under the same license as NVDA. See the copying.txt file for more information

import addonHandler
addonHandler.initTranslation()
import config
import globalPluginHandler
import gui
import languageHandler
import os
import speech
import wx
from scriptHandler import script
from speech.commands import LangChangeCommand
from speech.extensions import filter_speechSequence
from . import langdetect
profilePath = os.path.join(os.path.dirname(__file__), "langdetect", "profiles")
languages = os.listdir(profilePath)

confspec = {
	"languageDetection": "integer(default=1)"
}
for i in languages:
	confspec.update({i: "boolean(default=False)"})
config.conf.spec["enhancedLanguageDetection"] = confspec
class EnhancedLanguageDetectionSettingsPanel(gui.SettingsPanel):
	# Translators: The title for the settings panel
	title = _("Enhanced Language Detection")
	def makeSettings(self, settingsSizer):
		settings = gui.guiHelper.BoxSizerHelper(self, sizer = settingsSizer)
		comboBoxValues = [
			# Translators: An option in a combo box
			_("always interpret"),
			# Translators: An option in a combo box
			_("only interpret if the text doesn't instruct NVDA to change language"),
			# Translators: An option in a combo box
			_("never interpret (NVDA's default behavior)")
		]
		# Translators: The label for a combo box
		label = _("Language interpretation:")
		self.languageDetection = settings.addLabeledControl(label, wx.Choice, choices = comboBoxValues)
		self.languageDetection.SetSelection(config.conf["enhancedLanguageDetection"]["languageDetection"])
		# Translators: The label for a checkable list box
		label = _("Languages to interpret")
		choices = []
		for i in languages:
			description = languageHandler.getLanguageDescription(i)
			if description:
				choices.append(description)
			else:
				choices.append(i)
		self.languages = settings.addLabeledControl(label, gui.nvdaControls.CustomCheckListBox, choices = choices)
		self.languages.SetSelection(0)
		checked = []
		for i in range(len(languages)):
			if config.conf["enhancedLanguageDetection"][languages[i]]:
				checked.append(i)
		self.languages.SetCheckedItems(checked)
	def onSave(self):
		config.conf["enhancedLanguageDetection"]["languageDetection"] = self.languageDetection.GetSelection()
		checked = self.languages.GetCheckedItems()
		for i in range(len(languages)):
			config.conf["enhancedLanguageDetection"][languages[i]] = i in checked
allowedLanguages = ["no", "en"]
def detectLanguage(text):
	try:
		languages = langdetect.detect_langs(text)
	except:
		languages = None
		return
	if not languages:
		return
	lang = None
	for language in languages:
		if config.conf["enhancedLanguageDetection"][language.lang]:
			lang = language.lang
			return(lang)
def speechSequenceFilter(speechSequence, *args, **kwargs):
	if config.conf["enhancedLanguageDetection"]["languageDetection"] == 2 or not config.conf["speech"]["autoLanguageSwitching"]:
		return(speechSequence)
	newSequence = []
	shouldInterpret = True
	for i in speechSequence:
		if  isinstance(i, LangChangeCommand) and config.conf["enhancedLanguageDetection"]["languageDetection"] == 0:
			continue
		if isinstance(i, LangChangeCommand):
			shouldInterpret = not i.lang
		if isinstance(i, str):
			if shouldInterpret:
				language = detectLanguage(i)
				languageCommand = LangChangeCommand(language)
				newSequence.append(languageCommand)
			else:
				newSequence.append(i)
				continue

		newSequence.append(i)
	return(newSequence)

class GlobalPlugin(globalPluginHandler.GlobalPlugin):
	def __init__(self, *args, **kwargs):
		super(GlobalPlugin, self).__init__(*args, **kwargs)
		gui.settingsDialogs.NVDASettingsDialog.categoryClasses.append(EnhancedLanguageDetectionSettingsPanel)
		filter_speechSequence.register(speechSequenceFilter)
	def terminate(self, *args, **kwargs):
		filter_speechSequence.unRegister(speechSequenceFilter)
		gui.settingsDialogs.NVDASettingsDialog.categoryClasses.remove