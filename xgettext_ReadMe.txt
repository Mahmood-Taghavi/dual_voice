Download link:
http://gnuwin32.sourceforge.net/downlinks/gettext.php
Usage:
1. Put list of files with their full path in an txt file for example namely "xgettext_filesfrom.txt".
2. Run cmd and change the working directory to location of "xgettext_filesfrom.txt".
3. Create pot file template which have translatable text extracted from the code files:
xgettext --files-from=xgettext_filesfrom.txt -o nvda.pot --package-name="Dual Voice for NVDA"
4. You need to create an empty folder namely "LC_MESSAGES" at addon/locale/xx/ where xx is language code.
5. Create language specific po file. where xx is language code in both of the local and output parameters:
msginit --input=nvda.pot --locale=xx --output=addon/locale/xx/LC_MESSAGES/nvda.po
