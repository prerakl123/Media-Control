# WINDOWS KEY CODES ::= https://learn.microsoft.com/uk-ua/windows/win32/inputdev/virtual-key-codes
# ICON BASE64 DATA  ::=  https://icons8.com/

# IMPORT LIBRARIES
from ctypes import cast, POINTER
from comtypes import CLSCTX_ALL
from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume
import win32api
import base64
import io
from win32con import VK_MEDIA_PLAY_PAUSE, VK_MEDIA_PREV_TRACK, VK_MEDIA_NEXT_TRACK,\
    VK_VOLUME_MUTE, VK_VOLUME_DOWN, VK_VOLUME_UP, KEYEVENTF_EXTENDEDKEY
import asyncio
import winrt.windows.media.control as wmc
from PIL import Image, ImageTk
from tkinter import Tk, Frame, Canvas, Label, X, Y, BOTH, TOP, BOTTOM, RIGHT, LEFT,\
    SUNKEN, FLAT, NW

# CONSTANTS
PLAYING = 'PLAYING'
PAUSED = 'PAUSED'

# BASE64 ENCODED IMAGE DATA
SLIDER_CIRCLE_IMG_DATA = b'iVBORw0KGgoAAAANSUhEUgAAAKUAAAClCAYAAAA9Kz3aAAAAAXNSR0IArs4c6QAAB9BJREFUeF7t\n3Wly20gMBWD' \
                         b'7JjnqHDU3mSlVhrFELQS6sT3g5VeqQnVj+YImmdj+/uIvYQV+/yu88MNlv7731+i/\nAov00GMLeKtoCPao3HCUmQi' \
                         b'v8M5FOgxlZYREOmhSIkN8B7X3FG06KTtCnAO0EcpJEF8B7TM9G6Cc\njrEfUGCUxHj1aPT1hTk9AVES4zXG8xVYOI' \
                         b'FQZmP8R2/h6RMWa+yEgYETBGUkyAw4kXvWh1kcZQTG\nSBDSKRcRU12cRVF6YoxouBSf9DrPmOvhLIjSA6RnU6WwrK' \
                         b'7zyKUWzGIorUF6NNAKl8U6lvnVgVkE\npSVGy0ZZwIlYwzLnfJwFUFqBtGxMBCSPPaxqkAszGaUFSKtGeCDJWtOiJn' \
                         b'kwk1ASYwxXTJwJKAky\nBuSxCx7MYJS7IC0KHEuizm67tYs7zgNR7oDcLWgdGvmR7NQyBmYQSoLMx3gfQW2YASgJsh' \
                         b'ZIi3tN\n34npjHIV5M7f5JoE6ka1Wms/mI4oCbIuxHNktWA6oSRIHJC7x7n9xHRASZB4IGvBNEZJkLggd5/O\n7SZ' \
                         b'mMsrVe5kera+dhbY3JVFqp6Q26dot7Bmdtkc2MI0mJUH2RHnLKh6mAUotyJVE+7YcI7NYmAko\ntQlitK13lNqe7R' \
                         b'3jmyi1U1KbXO9WY2Wn7d06zA2UBImFyiLaGJiLKAnSosWYa/jDDECpTQKzVbOi\n1vRUf4wvoNRMSU3ws9qKn62mt' \
                         b'zqYRImvIymDMig5JZMEFN3WB6ZiUhJkURnJYdnDJMrkluJvn4aS\nUxIfj2cGtjCFk1KKUhOcZ5G4dnwFpL2/fhIX' \
                         b'oJSC5H+0iIdQaUcpylvMn2EaotQEVamYjMWuAlID\nWyg5Je0aNmElKcrP0/JiUkpRaoKZ0JzJOUotvJ+WRDnZj0v' \
                         b'uUpTvp+UHlJySLj0bsagU5utpSZQj\nkEQn6YKSUzK6jf32W4f5ZlISZT8k0RmloJRuGl0M7lenAhIjz/eVLyYlp2' \
                         b'SdpqJHIkH5/BROlOh9\nLx1/KErpZqUrxuBCKiCx8niEnyYlj+6QPo3aRILy8QgnylFAspKVwPyZlgsoJRtkJc99a' \
                         b'1ZAYoYo\na/aubVTLKHk/2dZEemISlD/3lXfHtwSldPH0KjCAchWQ2PlzhBNlueZ1DYgou3YWOC81SsnRfauH\nZG' \
                         b'HgujF0xwpI7fz6/v/4lqCULuqYF5cGr4DEEFGCNxktfKJE69iAeIlyQJPRUiRKtI4NiJcoBzQZ\nLUUxSj55o7UWO' \
                         b'95rmN9fX0SJ3WS06IkSrWMD4iXKAU1GS5Eo0To2IF6iHNBktBSJEq1jA+IlygFN\nRkuRKNE6NiBeohzQZLQUiRKt' \
                         b'YwPiJcoBTUZLkSjROjYgXqIc0GS0FIkSrWMD4iXKAU1GS5Eo0To2\nIF4Rylsd+H8qB2gokOI1yNsPE+XXfRdo1Zw' \
                         b'QiHJOr2EyJUqYVs0JlCjn9BomU6KEadWcQM1R3kon\nWXROiZmppgJSO3+fvvlaSFNeXrtSAQlKfifflcryM8sVIM' \
                         b'rl0vGDXhVwQ8n7Sq+W9V5XAvJWgafj\nm/eVvWFkZidByR/ulNmhgXu7o+QRPlDVZspEuVlAfty2AhKQP/eTt98t/' \
                         b'hB66Ua26XE1xApIrHz8\ned/Shx0e4Yg84mOWgHyckhuTkijjG4y4oxlK6bSUbohYTMZsUwGJkcej+82klKLktLRp' \
                         b'XNdVJCCf\nj26i7OqhRF7mKDktS/QVNoh1kB8mJVHCeigReDpK3luWcFAmCCnI1/eTF5OS07JMn6ECkaJ8fuo+\n0' \
                         b'nzxLzr3FZB8k4LjemkwUBVmsKoKaAwso+S0VPVk/MVSlO9BCo5vDUreW842KQX5/l5SeHwfl0mP\ncU1gs1vYL3tp' \
                         b'7z9PSeGk5LTsB8g6IynI6ympQEmY1m3ss54tSKLsIyMxk1SUnJaJnS+6tT1I5aTU\nPvTwabyoJKOwfEASpVF7Zi5T' \
                         b'CiWP8ZkI77P2A7k4KbUoeYz3QqwBKXsFdK7Pxb99fyqn9IX6sYY2\nmV6t7JGNtofXL8pf1WUDJSdmD2jSLGJAbhzf' \
                         b'94lwYkrbin0dUWL3r130cSCNJiWP8XYGHxKKBWmI\nkjB7wowHaYySMHvB1IJce/3j8PR9XlL70MN3mDUh54F0mJQr' \
                         b'05LvMWvBzAXphJIwayGTRrOC0e7I\nvo9y8+X5p4RXjnIe51JCttfVAek4KY+SEaYtHo/VaoEMQLlzlHNqehB8XLMe' \
                         b'yCCUhOmPS7vDKkaf\ne8hz9I73lBavi/hkruV2fX1tkIGTcvcekzivsV1dsYMxZkIeGQROSiuYvNe84vf85zggEyYl' \
                         b'YepB\n7XxiF2PshEyclJYwOTVfk7XAmAMycVLel3L1Xea5HVaN2JlM2Z+1qsHalzFYZZ9wT/kqdCuYUyen\nFca86X' \
                         b'ivoghK6yN9Ck5LjDVAFjm+z5PTcmoea1s3z+qgWlnHI5fc4/pchWKT0mNidrj39IB41KUW\nyKKT0uMh6N1E8mz2y' \
                         b'hS8/4x3bPUwFnglpGmax5H+an9vCJ9yjtq7LkYwlLdwo2B6TtUoeO9yqA8S\n4Pj2fn2kmdbI12JgBJyUEU/pyPBe' \
                         b'xY6FsQHKiCd1VKSYGBuhJM6fvzrYGBuijHyVVGmC9oB4X9Gi\nL88tm5791G6Zy7FWP4jDUHaZoL0hDkaJ9AQ/B+G5' \
                         b'KwOOb83xmXnUz0VIlBqjD9dagCU8Sfn/A7e+\n2YQGJkDMAAAAAElFTkSuQmCC\n'
PLAY_BUTTON_IMG_DATA = b'iVBORw0KGgoAAAANSUhEUgAAADIAAAAyCAYAAAAeP4ixAAAABmJLR0QA/wD/AP+gvaeTAAABP0lEQVRoge2Zu20CQRR' \
                       b'Fj42ME8hISSjADbgDF0ELBLgAWiAkJXTqBmjAFODYqTMShGAcPQmtgP29mbcPz5Fufo+AnbsDZDKZTIF3oG9dQoMAfA' \
                       b'Nv1kXaEs7yCUxs6zQnFLIHlsDQslQTiiKSH2AKPNhVq8c1EckGeDFrV4MykQAcgTUwMupYiSoikl9gBvRMmpZQR0SyB' \
                       b'V4tyt6iiUgATsAHME5f+TJNRSQ7YAE8py5epK2IxHwdaImYrwNtkYDROoghIkm6DmKKSJKsgxQiATgAKyKug1Qikmjr' \
                       b'ILWIRH0dWIkEKqyDR0VRN1h9Gl84/2q5/7HfxePX/YHofqLIaBykEBC0JdzPePcvVu5fde/i8kH9VNagjoD7C7rop7I' \
                       b'GZRLuL7Hd/61gcipr0IlTWYNOnMoazIEn6xKZTOaf8wf43HVcgMUNewAAAABJRU5ErkJggg=='
PAUSE_BUTTON_IMG_DATA = b'iVBORw0KGgoAAAANSUhEUgAAADIAAAAyCAYAAAAeP4ixAAAABmJLR0QA/wD/AP+gvaeTAAAAUklEQVRoge3PsQ3AIB' \
                        b'AEQXD/PUMDTgzJypqJ/17aMQDg3DzYrMvft/tXz5fjMiE1QmqE1AipEVIjpEZIjZAaITVCaoTUCKkRUiOkRkiNEAD4' \
                        b'kw2niAJE1VFArgAAAABJRU5ErkJggg=='
NEXT_BUTTON_IMG_DATA = b'iVBORw0KGgoAAAANSUhEUgAAADIAAAAyCAYAAAAeP4ixAAAABmJLR0QA/wD/AP+gvaeTAAABtklEQVRoge2asU7DMBC' \
                       b'GP8qAxMDAgNqysLAx8QaspCsbM09QYKcMfQVegSdgKWJjAPECTDAyMBCQCkKE4Ry1ggRsx0ldy59kWVHufP+1qXPJFS' \
                       b'KRiC09YAS8AtmMR6q0JKZJnHogvmwMdJPoKYcx0Ac6pp9CDXSAQ0RThuY3c6mM+/XpsuYI0TbSMU6VcbtORZa0EW0vO' \
                       b'sb5tegrhfpaMxBSCzER34iJlHACLDle05oqu1YG3AM77uQUxtDSVzWRDPgCzoAVy3V0Yrgz/MP3Q82PSMnjkkYT2QKu' \
                       b'p47PgTXLNctiuDP8x7cFHCDlRAY8q+MFy7WN9blKJGcDuJg6dwVsWq5fFqOaoaHvHvCkzr8Bx8Ci4xh2hha+q8hultv' \
                       b'dAduOY5gbVvDdBR6Y7HBD9G+kXiUCsIwk8InZjTTsMr6IeGlp+AbxY5/77Xfub4hBlCjBFI3BlPFBPFgF8ajbxMuHRh' \
                       b'JpgrBrrZiIbwSdSKpmH1puP1lX869GT1EiN2rer02OPbmmWx3jBNnexkjPrluTKBO6SNn/jmjTblMPmOzXvg3t9nROg' \
                       b'nRP8+boLIf1HwYikYjwDSt9ZhC7EO7hAAAAAElFTkSuQmCC'
PREVIOUS_BUTTON_IMG_DATA = b'iVBORw0KGgoAAAANSUhEUgAAADIAAAAyCAYAAAAeP4ixAAAABmJLR0QA/wD/AP+gvaeTAAABsElEQVRoge2aPU7' \
                           b'DMBiGH4oQEgMDA2rLwsLGxMgVkoWBjZkTFNgpA1fgCpyApYiNAcTGBRgYGBgoSAUhwmBHWCVI/okbx/iRLKuS7e' \
                           b'99W9f53K+QSCRsyYER8AoUDbex1JKZmjgJQPxfbahrIpcTJsAA6Jm+Cx7oAQcITQWan8ylHDzwp8uaQ4S2kc7gs' \
                           b'Rzc9anIki5C24vO4HIvhkqlvk4DQryQjIRGMuLIInDsO4jvU2sbuHeIoa3Pl5El4BT4dIzRqJEceJDrfjjGaMTI' \
                           b'CnCmrHkHbDnGmLmRXeBJrvUGHAHzNcSYmZF14EJZ5wrYqDGGdyMdYB+R0BXAs3w9V2MMo7k2QTaBa2XuObBacwz' \
                           b'juSZBFhB7v7zwPAI7Ncewnqs7UH2wfSFOp+W6xejOjSbXquLfbS2V1n/ZVaI4flVa/0CcpvUpikoUSaNK69N4lS' \
                           b'guViqtv+qquPz4EJQRF+LOtZKR0IjayFj2IZTcplmT/a9CT5WRG9nveZNjT6npVmdwhjjeJoiaXd+TKBP6iKTzH' \
                           b'aFNu0w95Oe8Dq1pl6dLMkT1tCyONtms/zCQSCQE3/UPZcACYRBYAAAAAElFTkSuQmCC'
VOLUP_BUTTON_IMG_DATA = b'iVBORw0KGgoAAAANSUhEUgAAADIAAAAyCAYAAAAeP4ixAAAABmJLR0QA/wD/AP+gvaeTAAAECklEQVRoge2aWWsUQR' \
                        b'DHf9HorsRrN65ZfFIU8ULjk4IH5kFNjEgUFOLxpuiLB+qr+h2EgJ9DEDGg0RjFeMQExBweL2qIggiKMRJlfahqetzs' \
                        b'bqZnejcR/MMwy1Z39b+mu6trqgb+Y3qhyqOuNLAd2AKsAZYDi4EalX8HPgJvgZdAF9AJfPHIITKSwDGgHfgN5ByvX8' \
                        b'At4CiQqDB3AOYAF4DhAKkx4A5wCWgBVgMpYJZeKf2vBbgMdGgf0/8DcB55OBVBM/AmQOAJcBxYEEHXQuAE8DSg7zXQ' \
                        b'5IVpESSBa4EBnwG7POpvBJ4H9LdRhtnJIsRzyKY9Dcz0PYjqPAuMYme7zpfyZch054B+YJ0vxSWwHhjUMV8ph1jIBB' \
                        b'Q+BhbFVeiAFOKic8iezEZVlMQup4fY86CSqAEeYZdZpD1jNnY/cthNFWqxq6LNtXMzdmNXYk9MhvVYB9AYttMc7Dlx' \
                        b'ujy8IuEcdvOHWmIXsedEOVxsVFQDvQi3c5M1TiChQg7YWV5ekbAH4TbMJLNyFOshpiOqsJ70cKmG7drouKeBs0gc1U' \
                        b'uMcyAPJxGON4s1SCNh9RjRAsB8ZBHXbWKnfvwYkwJ+AuMU4dmiA97xMFjQiP683z6Muav69pk/ZgSEW/XeEXOQrOpY' \
                        b'BQwADXoN6H8dxDfmrt63FhLeIM/KCKgDXqieAWBJQLY4IBvMk7liv+q5Xkg4pMLVEZXnL6dCTz1MmzBYi31YE/BZhV' \
                        b'HiqlIzkQ8fM7NI+38qJPypwtmOSl2MMIhrTAKbJ5iAKIZEMcIgjjElDXFdWnGMMIhqTIYSS8t1s/fh52wIOoDekH0m' \
                        b'bPbgOTKk95UhlY3pwA3ASMg+hTCiOvooslQKwHA0nP8yxFi3IaSyTcBG4hlhMALUA5tDtjccC85Il953xOdVdjTovb' \
                        b'OQMIUNGhdWilEEpLFB43zzZ3BGvgC3Edd2sKLU3HAIOSLaga/FGh1BvMHTCpFyRRXQg3BsLdUwAbzXhrvLz8sZexFu' \
                        b'7whRhjivjXuYfskHc3adCdMhic31ni0fL2eYBzyIQ1GoSTuNIsmxqUY98APh5FzKaMM+gVq/vJyQQZJyOeBqFAVJJC' \
                        b'2UQxLJU5HEngt0K4duYtQZM0gYYMoKGR/sQiINPMCW42IXfJZhp3aQ8LFYHNQHxhwClvpSXIddZqNI7rXal/IAqhHv' \
                        b'ZDZ2N/LO4hVJrAMw7w6+qq9VSCnDnBNmY5e19t6InXaTtT+JBJ2uSAOnsGGHWUo+q8UlkUSWlwlnckhEeg+4guSd1i' \
                        b'Jue7ZetUjR6IC2uYfNE5iw4wxT9AVEAsmK30ReAVw/4RhHEoOtxDTA50c1C5CParYh7/0rEHc9T+XfkGTBa8Sl30dm' \
                        b'pWgo/h//Mv4AHo5GD7a4m+MAAAAASUVORK5CYII='
VOLDOWN_BUTTON_IMG_DATA = b'iVBORw0KGgoAAAANSUhEUgAAADIAAAAyCAYAAAAeP4ixAAAABmJLR0QA/wD/AP+gvaeTAAAECklEQVRoge3az29V' \
                          b'RRQH8E+10kdQoS2ljSuJxgQhyJ6gLvxRRGN1h+IOghuEoFvlfzBp4t9hogSNVvwVUURrjFBENyiJJIaoEWnQPBdn' \
                          b'bu4VX1/vve++1y74Ji/zcufMme+5M2fmzJnLTawuDDWoawwPYifuxz3YhHWp/k/8gh/xHT7Gh7jSIIfaaOEFvIN/' \
                          b'0K74+xsnsA8jA+YO1uJlXCqQuob38SpmsAWjuC39RtOzGbyGudQma/8zjoqXMxDswQ8FAl9gP9bX0LUBB3C6oO8C' \
                          b'djfCdAm08Eahwy/xWIP6p/FVQf+sPozOlCDeFk57CLc23UnSeRhX5aM92ZTyzWK42ziLbU0p7oLtWEh9fp849ISJ' \
                          b'gsLPsbFXhRUwKpbotvDJqbqKWvLp9Kl8Pxgk1uEz+TSr5TOZY58Vm91KYVw+K2arNt4jd+xB+MRy2C5fAKbLNlor' \
                          b'3ycO9YdXLRyRO3+pKfaKfJ/oxxJbF8P4WnA7spzwiAgV2ni0v7xq4QnB7ZJlRmWffIVYjRiSr6TPdRN8NwntHwCp' \
                          b'ujgoOB5fSmBMhNXX1AsAB4VRLOK6As9bCgIPCef+BL8NlFo1XBGb5LA4yOG/huxM5QcDJFUXc6nclT0oGrIlld+U' \
                          b'VHYmydaOgQqYwjxOlZSfT+WWTpXnhRN1rFxCWRbC9GLMVNLRFueRMtia5M91qvw1VZaNqzbh29RmAXeVbFfEZEHH' \
                          b'uQo6NqY2lztVLqbKNRWI9GJMXSOIjTvLE/wPdQyhnjG9GMEyhlSdWkVUMaZXI4gD35JTq6qz34ii0y61AJSRKYOu' \
                          b'zv5Wqny6pnK6j0wTI5Hh2aTnzexBcR85m8oHeujgMh4RRO/De+KtT4mNdmuqe1hEsHWxPZUdR2RGWDnXqbIibpxC' \
                          b'TUynIk4mfU91qhyVB40bGuisaEyTRozJg8Y7lxI6kTo90ECH5KHHvGaMgBcFx7e7CT2fhE431GnTGBIxXht7uwmO' \
                          b'4Kck+Hj/eVXGk4LbRSWuIY4m4TNWX/IhC1RfKtOgJc/1Hu4fr8rIXvCCCpdCu1Ojq/I1eyWxA38JTpWvMmblb2C8' \
                          b'WV6VMCGScm28XkdBS6SF2uKMvBJJ7NvFqbGdytr3jBMiDMiuFSaaYFcSYyIRkl3H9Xzhs1k+tAt6i8XKYkehz/O4' \
                          b'uynFk/JpdlXkXoebUl7AsFidMsc+JSLqRtGSLwBtkVBu6vZ1SFxlZPtE5th9vXuflg97lrU/KILOqhgTsVMWdmRT' \
                          b'qcnb4q5oiemVhTNtEZGexDE8I84e4yIHsCb93yYORceS7GKh/UWxY6/IFxAjIit+XBwBqn7CcV2cTPfq0YAmP6pZ' \
                          b'L3Kxu8S5/16xXN+R6v8QJ8gLYkn/SIzK7w1yuIlVg38BWf5E1m2tG+IAAAAASUVORK5CYII='
# MUTE_BUTTON_IMG_DATA = b'iVBORw0KGgoAAAANSUhEUgAAADIAAAAyCAYAAAAeP4ixAAAABmJLR0QA/wD/AP+gvaeTAAADu0lEQVRogd2aS0hUUR' \
#                        b'jHf9qkY0WGERmiRI9NDzBa9FyE0KKiRSBUiyKCCNoVvRYFFVhQlBgJQVCUWEQFFQVuWtXCVRgWWErRU6iUyMjSbFrc' \
#                        b'7zDX6zkz5957ZmT6wyw8/+989/w8z3tmAM4Bb4HFFLCKgVKgBnhEgcNMAFqBFPCZAodJALdwB1MM7AdeAv1AM5CMmd' \
#                        b'NarmBKgLuSx/856aCN1oo7zEwQKeCVu2baKWrPlAD30EOkgJEQbSgDVkhbYiksTDYI9bHVbonvAFaGabhOtjC2EGFA' \
#                        b'FskzU8Bf4DwwMTSBT9nmTKY5EQcEYBrQBAxL3SdAZRQIJRNMWIiwIEqrgV6p3w3MipgHGDvMlmI/nOKCgHfy6JQcz4' \
#                        b'CKGLlGwYxkaGxUkCvAdaDa4Ffi9UgKaAOKoqOMhnEJkgA+SMwAsN0QNxvok7i9USEmA1NiwmRSNXDfF9tgiKsX/xcw' \
#                        b'JwpIG/A4JoyNDpMeukcMMTfEb/EXJoFG0iuD6eHq7zgwttpDeg/ZoPHnAkN4wAtVYaPlw/1lUWHCqEnq9OLtKUFdEr' \
#                        b'9RFZh6IhNIVBilcrzT8E5gkgEkCXRJvRMaf7kPNKFroC1IFBilVb6y90CdAUZN7G8a4CKgR/w1cUHCwvgbsQVol/Ih' \
#                        b'YJ0GpAh4IzGbNX6zeIdcgISB0TW0QbyvwAxNzCnxWzTeDvHuuAKxhTGpTfxjGm+9eF0ar1a8TpcgNjAm1Yn/VONViz' \
#                        b'fM2GNJlXgfXYNkgzGpQvwfGq/MV7/c4A3mAiQTjOnlbKb4fRqv1Fc/uJ8kpfxnrkBMMKY3zU3it2s8NXz+4F0z6f4B' \
#                        b'vbkEsYVJkF6G92lA1mKe7EvE68g1SDaYJHCV9IQNzgHwTgAp9MvvNvFa8wGSCUbtzIN4R46gin0xWzX+BfEO5gtEwc' \
#                        b'DYBaAHbz/QaaPE9KM/k6ldvxbgU55A/LlsFoAS4IXE6F6ylon3Dtlfzo4DiA3MGfF6gakakGviH1cFSYEx9UyuQDLB' \
#                        b'7MJ7qTK9WM0HfuMdNqs0fkbFuXQwgehgTgtACjhqqKOuoprCQgQf6BLElNv0NYRacvuA6VFAXMDY5h5AvwAsAL5LTH' \
#                        b'1UCN0DXYIEcwcXgBq8FSoFXIwLoeS/D3YJEsytYOaRvmV8gIPvTfzK5XVQsGfU7eJDzJcVsZTL66Bg7ts47omgwgyz' \
#                        b'OLnz8tW5LUzc3HmByTbMBh3lHneY5w5z5w3mJmNBDjjKnVeYYrzbv27gC95Fs6sVJ+8wudR//UOgglYCuAy8/gcrSK' \
#                        b'krq/oFoAAAAABJRU5ErkJggg=='
# UNMUTE_BUTTON_IMG_DATA = b'iVBORw0KGgoAAAANSUhEUgAAADIAAAAyCAYAAAAeP4ixAAAABmJLR0QA/wD/AP+gvaeTAAAC50lEQVRoge2ZO2tU' \
#                          b'QRiGn1w2WS2UiBhXRYL4C1RQULHQykYEsYqaws4qYLykFxWUWCn+AS28xBgjWgsiBvGOhYqIGEHFBCzUaHYt5pvN' \
#                          b'8u2c7LnlnAnsC4dh329mzvfs2TlzWWiqqQWlFqAfeANMApeARblmFEMF4DpQUdfZPJOKqgJwk3qICvA2x7wiqQAM' \
#                          b'44aoADP5pRZejSDs5bXCQngNEgXCW5AO4BbhIeKA7ALWpJFskOJARAXpBr5j5qH9qWStFBciDsiYtCsDx1LIvaoO' \
#                          b'YMSR4HyOkQEMSAU4kSD3qpJCJBnsBzDzUJkUfmZJIcKAtAJ9QLsjNiB9TBHwAigCQ8CXBjdPChEG5KjUewSUHPFR' \
#                          b'iY+6Gg+FvHkWIBuAZ1L3vQOmBPyU+BbdOOhJ5AECsBi4K/UfYybdWp2W2IhuGPbmWYGA2bs8lzYnVawb+AtMA8t8' \
#                          b'AukB9jj8jZi31CSwVMXuSX99voC0AQ8kdhGzs6zVHYkdVn6/+Jd9AemUpKZxfMNAr/jDyt8m/rgvIFb2tftS+evF' \
#                          b'/6D8VeJ/9g1khcRnMPOaVVH8X6p+nd86R+dZyo4NDWvzKzfyfQE5KOVr4HeNb5ciX1X9LimnrOFa02SpTuAIcEo+' \
#                          b'6yOjrVI+Vf46KSeskfcT+Qfsxcze54ArKt4r5ZjyN0n5pNbMe7D3ALsd/g5pMwksUbH7OF7XeYO41IVZNFaAQRUr' \
#                          b'YZ7kH9QSZcIzkOXAQ6k/Tv2i8YzE9CTJeY9AtgOfpO5HYLWK1y7jN+vGRYEJejJZggxKvRfAWkfcrr1uh+grUDcS' \
#                          b'QoQBaceclrj+gjjO7OBPdNZVIDlMXB3CzOIzwL4E/VSVFCaqWjBHQPY4KNWzrSQwUbSS2S1vGbNCTl1xYaLIHpn+' \
#                          b'IKWfU5DiwETVTub5ENuqDbjK/A/2TBQFxnuFhVkQajRm9HbVa80F8yrHvGKpAFyjHiTVySwrtWJm5HfAN+AC+W+r' \
#                          b'm2oqjv4DXPTe4pS6rrgAAAAASUVORK5CYII='


# CUSTOMISED SLIDER CLASS FOR VOLUME
class CustomScale(Frame):
    def __init__(self, master, root, **kwargs):
        Frame.__init__(self, master, **kwargs)
        self.root = root

        # SLIDER CIRCLE IMAGE SETTING
        slider_img = Image.open(io.BytesIO(base64.b64decode(SLIDER_CIRCLE_IMG_DATA)))
        slider_dimen = slider_img.resize((15, 15), Image.ANTIALIAS)
        self.slider_img = ImageTk.PhotoImage(slider_dimen)

        # MUTE BUTTON IMAGE SETTING
        # mute_img = Image.open(io.BytesIO(base64.b64decode(MUTE_BUTTON_IMG_DATA)))
        # mute_dimen = mute_img.resize((30, 30), Image.ANTIALIAS)
        # self.mute_img = ImageTk.PhotoImage(mute_dimen)

        # UNMUTE BUTTON IMAGE SETTING
        # unmute_img = Image.open(io.BytesIO(base64.b64decode(UNMUTE_BUTTON_IMG_DATA)))
        # unmute_dimen = unmute_img.resize((30, 30), Image.ANTIALIAS)
        # self.unmute_img = ImageTk.PhotoImage(unmute_dimen)

        # SETTING UP SLIDER
        self.slider_canvas = Canvas(self, width=115, height=20, bg='#2e60ab', highlightthickness=0)
        self.canvas_slider_line = self.round_rectangle(10, 10, 110, 15, tags='slider_line', fill="#6969ff")
        self.canvas_slider_img = self.slider_canvas.create_image((5, 5), anchor=NW, image=self.slider_img,
                                                                 tags='slider_circle')
        self.volume_lbl = Label(self, text=self.root.volume, font=('Courier', 10), bg='#2e6000')

        # PACKINGS
        self.slider_canvas.pack(side=LEFT, fill=Y)
        self.volume_lbl.pack(side=RIGHT, padx=10)

        # SLIDER KEY BINDING
        self.slider_canvas.bind("<Enter>", self.on_enter)
        self.slider_canvas.bind('<Button-1>', self.on_click)
        self.slider_canvas.bind('<B1-Motion>', self.move_slider)
        self.slider_canvas.bind('<MouseWheel>', lambda _=None: [self.vol_up() if _.delta == 120 else self.vol_down()])
        self.slider_canvas.bind('<Button-2>', self.on_mid_mouse_btn)

        # KEY BINDINGS
        self.bind_all('<Any-Key>', self.refresh)
        self.bind_all('<MouseWheel>', self.refresh)
        self.bind_all('<1>', self.refresh)
        self.bind_all('<2>', self.refresh)
        self.bind_all('<3>', self.refresh)
        self.bind_all('<Motion>', self.refresh)

    def round_rectangle(self, x1, y1, x2, y2, radius=5, **kwargs):
        points = [x1 + radius, y1, x1 + radius, y1,
                  x2 - radius, y1, x2 - radius, y1,
                  x2, y1,
                  x2, y1 + radius, x2, y1 + radius,
                  x2, y2 - radius, x2, y2 - radius,
                  x2, y2,
                  x2 - radius, y2, x2 - radius, y2,
                  x1 + radius, y2, x1 + radius, y2,
                  x1, y2,
                  x1, y2 - radius, x1, y2 - radius,
                  x1, y1 + radius, x1, y1 + radius,
                  x1, y1]

        return self.slider_canvas.create_polygon(points, **kwargs, smooth=True)

    def refresh(self, event=None):
        self.slider_canvas.coords(self.canvas_slider_img, int(volume.GetMasterVolumeLevelScalar()*100), 5)
        self.root.volume = f'{int(round(volume.GetMasterVolumeLevelScalar(), 2) * 100)}%'
        self.volume_lbl.config(text=self.root.volume)

    def on_enter(self, event=None):
        self.slider_canvas.config(cursor='hand2')

    def on_mid_mouse_btn(self, event=None):
        win32api.keybd_event(VK_VOLUME_MUTE, 0, KEYEVENTF_EXTENDEDKEY, 0)
        self.refresh()
        self.slider_canvas.coords(self.canvas_slider_img, 5, 5)

    def on_click(self, event=None):
        if event.x <= 10:
            volume.SetMasterVolumeLevelScalar(0, None)
            self.slider_canvas.coords(self.canvas_slider_img, 5, 5)
        elif event.x >= 110:
            volume.SetMasterVolumeLevelScalar(1, None)
            self.slider_canvas.coords(self.canvas_slider_img, 100, 5)
        else:
            volume.SetMasterVolumeLevelScalar(round(1 - (110 - event.x)/100, 2), None)
            self.slider_canvas.coords(self.canvas_slider_img, event.x, 5)
        self.root.volume = f'{int(round(volume.GetMasterVolumeLevelScalar(), 2) * 100)}%'

    def move_slider(self, event):
        """ Updates volume, volume label and slider position on slider movement. """
        # LINE:   (10, 10)::(110, 15)
        # SLIDER: (05, 05)::( 95, 05)

        if event.x_root < self.root.x + 5:
            self.slider_canvas.coords(self.canvas_slider_img, 5, 5)
        elif event.x_root > self.root.x + 100:
            self.slider_canvas.coords(self.canvas_slider_img, 100, 5)
        else:
            self.slider_canvas.coords(self.canvas_slider_img, event.x_root - self.root.x - 5, 5)
        try:
            volume.SetMasterVolumeLevelScalar(round(1 - (110 - self.slider_canvas.bbox(
                'slider_circle')[0]) / 100, 2), None)
        except Exception:
            pass

    def vol_up(self, event=None):
        """ Updates on volume up event. """
        if float(volume.GetMasterVolumeLevelScalar()) + float(0.01) >= 1.0:
            volume.SetMasterVolumeLevelScalar(1.0, None)
            return
        volume.SetMasterVolumeLevelScalar(round(float(volume.GetMasterVolumeLevelScalar()), 2) + float(0.01), None)
        self.refresh()

    def vol_down(self, event=None):
        """ Updates on volume down event. """
        if float(volume.GetMasterVolumeLevelScalar()) - float(0.01) <= 0.0:
            volume.SetMasterVolumeLevelScalar(0.01, None)
            return
        volume.SetMasterVolumeLevelScalar(round(float(volume.GetMasterVolumeLevelScalar()), 2) - float(0.01), None)
        self.refresh()


# CUSTOMISED PLAY/PAUSE MEDIA BUTTON
class PlayPauseButton(Label):
    def __init__(self, master, root, **kwargs):
        Label.__init__(self, master, **kwargs)
        self.root = root

        # PLAY MEDIA BUTTON IMAGE SETTING
        play_img = Image.open(io.BytesIO(base64.b64decode(PLAY_BUTTON_IMG_DATA)))
        play_img_dimen = play_img.resize((30, 30), Image.ANTIALIAS)
        self.play_img = ImageTk.PhotoImage(play_img_dimen)

        # PAUSE MEDIA BUTTON IMAGE SETTING
        pause_img = Image.open(io.BytesIO(base64.b64decode(PAUSE_BUTTON_IMG_DATA)))
        pause_img_dimen = pause_img.resize((30, 30), Image.ANTIALIAS)
        self.pause_img = ImageTk.PhotoImage(pause_img_dimen)

        # SET STATE
        self.state = PLAYING if ismedia(PLAYING) else PAUSED
        self.refresh()

        # KEY BINDINGS
        self.bind('<Button-1>', lambda _=None: [self.on_btn_1(_), self.refresh(_)])
        self.bind('<Any-Key>', self.refresh)
        self.bind('<MouseWheel>', self.refresh)
        self.bind('<2>', self.refresh)
        self.bind('<3>', self.refresh)
        self.bind('<B1-Motion>', self.refresh)
        self.bind('<Enter>', lambda _=None: [self.refresh(_), self.config(bg='#28707d')])
        self.bind('<Motion>', self.refresh)
        self.bind('<Leave>', lambda _=None: [self.refresh(_), self.config(bg='#2e60ab')])

    def on_btn_1(self, event=None):
        """ Mouse click <Button-1> event function"""
        win32api.keybd_event(VK_MEDIA_PLAY_PAUSE, 0, KEYEVENTF_EXTENDEDKEY, 0)
        self.refresh()

    def refresh(self, event=None):
        """ Refreshes the current media state. """
        self.state = PLAYING if ismedia(PLAYING) else PAUSED
        if self.state == PLAYING:
            self.config(image=self.pause_img)
        else:
            self.config(image=self.play_img)


# CUSTOMISED MEDIA-NEXT BUTTON
class NextMediaButton(Label):
    def __init__(self, master, root, **kwargs):
        Label.__init__(self, master, **kwargs)
        self.root = root

        # NEXT MEDIA BUTTON IMAGE SETTING
        next_img = Image.open(io.BytesIO(base64.b64decode(NEXT_BUTTON_IMG_DATA)))
        next_dimen = next_img.resize((30, 30), Image.ANTIALIAS)
        self.next_img = ImageTk.PhotoImage(next_dimen)
        self.config(image=self.next_img)

        #  KEY BINDINGS
        self.bind('<Button-1>', lambda _=None: [
            win32api.keybd_event(VK_MEDIA_NEXT_TRACK, 0, KEYEVENTF_EXTENDEDKEY, 0),
            self.root.scale.refresh(_)
        ])
        self.bind('<Enter>', lambda _=None: self.config(bg='#28707d'))
        self.bind('<Leave>', lambda _=None: self.config(bg='#2e60ab'))


# CUSTOMISED MEDIA-PREVIOUS BUTTON
class PreviousMediaButton(Label):
    def __init__(self, master, root, **kwargs):
        Label.__init__(self, master, **kwargs)
        self.root = root

        # PREVIOUS MEDIA BUTTON IMAGE SETTING
        previous_img = Image.open(io.BytesIO(base64.b64decode(PREVIOUS_BUTTON_IMG_DATA)))
        previous_dimen = previous_img.resize((30, 30), Image.ANTIALIAS)
        self.previous_img = ImageTk.PhotoImage(previous_dimen)
        self.config(image=self.previous_img)

        # KEY BINDINGS
        self.bind('<Button-1>', lambda _=None: [
            win32api.keybd_event(VK_MEDIA_PREV_TRACK, 0, KEYEVENTF_EXTENDEDKEY, 0),
            self.root.scale.refresh(_)
        ])
        self.bind('<Enter>', lambda _=None: self.config(bg='#28707d'))
        self.bind('<Leave>', lambda _=None: self.config(bg='#2e60ab'))


# CUSTOMISED VOLUME-UP BUTTON
class VolumeUpButton(Label):
    def __init__(self, master, root, **kwargs):
        Label.__init__(self, master, **kwargs)
        self.root = root

        # VOLUME UP IMAGE SETTING
        volup_img = Image.open(io.BytesIO(base64.b64decode(VOLUP_BUTTON_IMG_DATA)))
        volup_dimen = volup_img.resize((15, 15), Image.ANTIALIAS)
        self.volup_img = ImageTk.PhotoImage(volup_dimen)
        self.config(image=self.volup_img)

        # KEY BINDINGS
        self.bind('<Button-1>', lambda _=None: [
            win32api.keybd_event(VK_VOLUME_UP, 0, KEYEVENTF_EXTENDEDKEY, 0),
            self.root.scale.refresh(_)
        ])
        self.bind('<Enter>', lambda _=None: self.config(bg='#28707d'))
        self.bind('<Leave>', lambda _=None: self.config(bg='#2e60ab'))


# CUSTOMISED VOLUME-DOWN BUTTON
class VolumeDownButton(Label):
    def __init__(self, master, root, **kwargs):
        Label.__init__(self, master, **kwargs)
        self.root = root

        # VOLUME DOWN IMAGE SETTING
        voldown_img = Image.open(io.BytesIO(base64.b64decode(VOLDOWN_BUTTON_IMG_DATA)))
        voldown_dimen = voldown_img.resize((15, 15), Image.ANTIALIAS)
        self.voldown_img = ImageTk.PhotoImage(voldown_dimen)
        self.config(image=self.voldown_img)

        # KEY BINDINGS
        self.bind('<Button-1>', lambda _=None: [
            win32api.keybd_event(VK_VOLUME_DOWN, 0, KEYEVENTF_EXTENDEDKEY, 0),
            self.root.scale.refresh(_)
        ])
        self.bind('<Enter>', lambda _=None: self.config(bg='#28707d'))
        self.bind('<Leave>', lambda _=None: self.config(bg='#2e60ab'))


# MAIN WINDOW
class FloatingWindow(Tk):
    def __init__(self, **kwargs):
        Tk.__init__(self, **kwargs)
        self.overrideredirect(True)
        self.update_idletasks()
        self.x = self.winfo_rootx()
        self.y = self.winfo_rooty()
        self.volume = f'{int(round(volume.GetMasterVolumeLevelScalar(), 2) * 100)}%'
        self.screen_width = self.winfo_screenwidth()
        self.screen_height = self.winfo_screenheight()

        # TITLE FRAME
        self.title_frame = Frame(self, bg='#2e60ff')
        self.grip = Label(self.title_frame, bitmap="gray25", bg='#2e60ff')
        self.close = Label(self.title_frame, text='❌', bg='#2e60ff', fg="white")

        # TITLE FRAME - PACKINGS
        self.grip.pack(side=LEFT, fill=Y)
        self.close.pack(side=RIGHT, fill=Y)
        self.title_frame.pack(side=TOP, fill=X)

        # TITLE FRAME - BINDINGS
        self.grip.bind("<ButtonPress-1>", lambda _=None: [self.start_move(_), self.grip.config(cursor='fleur')])
        self.grip.bind("<ButtonRelease-1>", lambda _=None: [self.stop_move(_), self.grip.config(cursor='arrow')])
        self.grip.bind("<B1-Motion>", self.do_move)
        self.title_frame.bind("<ButtonPress-1>", lambda _=None: [self.start_move(_), self.grip.config(cursor='fleur')])
        self.title_frame.bind("<ButtonRelease-1>", lambda _=None: [self.stop_move(_), self.grip.config(cursor='arrow')])
        self.title_frame.bind("<B1-Motion>", self.do_move)
        self.close.bind("<Enter>", lambda _=None: self.close.config(bg="maroon", fg="grey28"))
        self.close.bind("<Leave>", lambda _=None: self.close.config(bg='#2e60ff', fg="white"))
        self.close.bind("<ButtonPress-1>", lambda _=None: self.close.config(relief=SUNKEN))
        self.close.bind("ButtonRelease-1>", lambda _=None: [self.close.config(relief=FLAT), self.close_window(_)])

        # MAIN FRAME
        self.main_frame = Frame(self, bg='#2e60ab')

        # # MAIN FRAME - VOLUME FRAME
        self.volume_frame = Frame(self.main_frame, bg='#2e60ab')
        self.scale = CustomScale(self.volume_frame, root=self, bg='#2e60ab')

        # # MAIN FRAME - MEDIA BUTTONS FRAME
        self.media_frame = Frame(self.main_frame, bg='#2e60ab')
        self.previous_button = PreviousMediaButton(self.media_frame, self, bg='#2e60ab')
        self.playpause_button = PlayPauseButton(self.media_frame, self, bg='#2e60ab')
        self.next_button = NextMediaButton(self.media_frame, self, bg='#2e60ab')
        self.volup_button = VolumeUpButton(self.media_frame, self, bg='#2e60ab')
        self.voldown_button = VolumeDownButton(self.media_frame, self, bg='#2e60ab')

        # MAIN FRAME - PACKINGS
        self.volume_frame.pack(side=TOP, fill=BOTH)
        self.scale.pack(side=LEFT)
        self.media_frame.pack(side=BOTTOM, fill=BOTH)
        self.previous_button.grid(column=0, row=0, rowspan=2)
        self.playpause_button.grid(column=1, row=0, rowspan=2)
        self.next_button.grid(column=2, row=0, rowspan=2)
        self.volup_button.grid(column=3, row=0, padx=25)
        self.voldown_button.grid(column=3, row=1, padx=10)
        self.main_frame.pack(side=TOP, fill=X)

        self.bind('<Enter>', self.on_enter)
        self.bind('<Leave>', self.on_leave)

    # CLASS FUNCTIONS
    def start_move(self, event):
        """Updates x and y coords in the class for window movement"""
        self.x = event.x
        self.y = event.y

    def stop_move(self, event):
        """Sets x and y coords to None after window movement stops"""
        self.x = self.winfo_rootx()
        self.y = self.winfo_rooty()

    def do_move(self, event):
        """Moves window according to the movement of drag and drop by mouse pointer"""
        deltax = event.x - self.x
        deltay = event.y - self.y
        x = self.winfo_x() + deltax
        y = self.winfo_y() + deltay
        self.geometry(f"+{x}+{y}")

    def on_enter(self, event=None):
        self.wm_attributes('-alpha', 1)

    def on_leave(self, event=None):
        self.wm_attributes('-alpha', 0.2)

    def close_window(self, event):
        self.destroy()


# win32api.keybd_event(VK_MEDIA_PREV_TRACK, 0, KEYEVENTF_EXTENDEDKEY, 0)
async def get_media_session():
    sessions = await wmc.GlobalSystemMediaTransportControlsSessionManager.request_async()
    session = sessions.get_current_session()
    return session


def ismedia(state) -> bool:
    session = asyncio.run(get_media_session())
    if session is None:
        return False
    return bool(int(wmc.GlobalSystemMediaTransportControlsSessionPlaybackStatus[state]) ==
                session.get_playback_info().playback_status)


# def get_media_info():
#     session = asyncio.run(get_media_session())
#     if session is None:
#         return None
#     for i in list(wmc.GlobalSystemMediaTransportControlsSessionMediaProperties.keys()):
#         print(i, wmc.GlobalSystemMediaTransportControlsSessionMediaProperties[i])


if __name__ == '__main__':
    devices = AudioUtilities.GetSpeakers()
    interface = devices.Activate(IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
    volume = cast(interface, POINTER(IAudioEndpointVolume))
    app = FloatingWindow()
    app.geometry("160x85")
    app.attributes('-topmost', True)
    app.geometry('+20+900')
    app.config(bg='#2e60ab')
    app.mainloop()
