import gettext
import locale

locale = locale.setlocale(locale.LC_ALL, locale.getlocale())
translation = gettext.translation(f"counter", "po", fallback=True)
transcode = gettext.translation("domain", "po", fallback=True)
_, ngettext = translation.gettext, translation.ngettext
_2, ngettext2 = transcode.gettext, transcode.ngettext


while str := input(_("Write some worsds: ")):
    N = len(str.split())
    print(ngettext("You entered {} word", "You entered {} words", N).format(N))
    print(ngettext2("You entered {} word", "You entered {} words", N).format(N))
