from __future__ import annotations

from datetime import timedelta
from typing import Any, Dict, List, Optional, Tuple

from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.humanize.templatetags.humanize import intcomma, naturaltime
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.template.loader import render_to_string
from django.utils import timezone
from django_celery_results.models import TaskResult
from polymorphic.models import PolymorphicManager, PolymorphicModel

from boundlexx.api.utils import get_base_url
from boundlexx.notifications.tasks import send_discord_webhook

User = get_user_model()

FORUM_LOOKUP_IMAGES = {
    "atmosphere": {
        "Normal": "upload://zQPL2iTQyNRjnveK1pbaFUcg4i4.png",
        "Potent": "upload://linnMQpEPnT5pRqJIWFHTMdeLPx.png",
        "Caustic": "upload://2x7uv24VIfWgkNDTqFVx5Gk2gIR.png",
        "Volatile": "upload://d5YyGKl5Yen386685JSv4ImOL5u.png",
    },
    "world_image": "upload://eS8DcCKkoJlt7y92Nt2TevbKjgb.png",
    "tier": "upload://zQPL2iTQyNRjnveK1pbaFUcg4i4.png",
    "name": "upload://bzts4NY6U0qkkIqMKTj0KkZC84J.png",
    "type": {
        "METAL": "upload://c3dr1zplLt6oZDgzlZomOZueAlo.png",
        "LUSH": "upload://f354Yvp4oXkXaxyg7xjm2zmGmaE.png",
        "COAL": "upload://g5p1MqEsw28PO6r9urF7qgtJzPv.png",
        "BURN": "upload://22vHpbbakPNllMvweQdPYDtWehI.png",
        "BLAST": "upload://fnB3eiyIpVaBQt352s6OWrro79T.png",
        "CHILL": "upload://ocqxUujgpad17Qd5EMzyLLot9sI.png",
        "SHOCK": "upload://pIXkMl6LS39GAvrN2VoosVefLQn.png",
        "TOXIC": "upload://u0a11C8AsRwGmTtTnKsTxPBhIcD.png",
        "CORROSIVE": "upload://gDaVjwVAXO0HoeXAxMuzxf7KNjK.png",
        "DARKMATTER": "upload://bdqxtxS4nyezAXOA9WDFq8uFDnh.png",
        "RIFT": "upload://bMQ6ivM8A7OQ5gOX6UeOO5scLn3.png",
        "BLINK": "upload://xpjPdoHtk5xxkvCf7pS6NPlX7jf.png",
    },
    "liquid": "upload://58uDj8uNmp52zqscy8PBW6k4alj.png",
    "server": "upload://zIT1kP3jGkZWWDAPCVcPknxsCSB.png",
    "lifetime": "upload://sKrov0t6oQapS2LKHlx7WkGYyx8.png",
    "blinksec": "upload://3rARAhHkZrnva4hiOeZRhXoSZO4.png",
    "warpcost": "upload://9dzMQi3rgBh0OJyl88r7mSNedwR.png",
    "exo_color": "upload://ya3ST9IB6OehJNYg6jY559ku9PH.png",
    "exo_color_new": "upload://lr0si60hUaEwkOP3UIsJFR7l0Lw.png",
    "by_recipe": "upload://xFrZpq1fBHP9zGCYGSZMyX3SfLo.png",
    "timelapse": "upload://oHqrS83ax0p0hsCLuR2mJnaoW6K.png",
    "owner": "upload://8UfHjxV1950IdfuKNcDumg9equG.png",
    "permissions": "upload://zbesXUQO9RZUEP7TNiHA24EVT9w.png",
    "portal": "upload://2GR4nUcRGOaMMDzj452JuqxVMWr.png",
    "perm_color": "upload://hRlPcEQgOBNrB5q38AT7n1cPleB.png",
    "colors": {
        0: "upload://pLWvEwsdJfVxylVUaST7zDfJnnP.png",
        1: "upload://l3M345enn9ycGBw61qecq1a8DLm.png",
        2: "upload://pBGbZZO7kGOGHC4iE5ygrggWAks.png",
        3: "upload://7SqZ3YzE0jKD43uh9HfGzMLlqiR.png",
        4: "upload://ko5MEqa4H6KNzdT4VFs2hfffIpv.png",
        5: "upload://m2z1sI7OwYrAlYI5ScaIabhAqcg.png",
        6: "upload://tWzEZcKVn0gArZtE7YijJoqvYGc.png",
        7: "upload://h8xKCYH9OEKYuoqz2CYoBojt545.png",
        8: "upload://q2dwFh2GUhYc51fxbbQCdrFnxkl.png",
        9: "upload://yPjRwFg65Qg0R7wNhPzHuyZKZho.png",
        10: "upload://7T2A5e4wWpeyj4AunXBZOlQxpY7.png",
        11: "upload://2xF5zByeA0Ec5HyNxkHC08Y9aZk.png",
        12: "upload://ykaqBC7dT9DmILigtG7nkGEyKB6.png",
        13: "upload://uim2KaEgQfNlx40gdWtPVttz0G3.png",
        14: "upload://uyaTEBXYEPEbOMDEt8CsnE7Tezg.png",
        15: "upload://jxKBgJBRlwIH945LCzSRuiBteA.png",
        16: "upload://wdzBpVuaqcQgEnnUcD12PeJemhW.png",
        17: "upload://wU9nOcvmWNnAZwKwzrRxn1Zbjce.png",
        18: "upload://mXEMuzGaAU3McsDPXjqfavzL9BZ.png",
        19: "upload://gUOnnrg1I4TApRbmHkxkHmaluUg.png",
        20: "upload://jp2jO8OunOg7xBSnFvlTx5Bes6I.png",
        21: "upload://qkHstPWWWh0GOsfwLlypogi1bEA.png",
        22: "upload://7WsNTMFAIWI5NI8aolGx78R9OEp.png",
        23: "upload://5QwCHh1STECYrNShxo4iIGKYlZb.png",
        24: "upload://b5XxybJbzxxcdGD8BFUAHeNRib3.png",
        25: "upload://t7XZMrHxp9iy4yG6cKmspMR2wck.png",
        26: "upload://jbohh3QIXCFB0ylJN3L7OJVUkJK.png",
        27: "upload://a5sUcAyCaXKBVdAmkAgguPHGTW2.png",
        28: "upload://q9bImhsSGQQdtEgOfdZUlFJWRKD.png",
        29: "upload://c920ghqZ3ZDQDx127O8dOAD56yw.png",
        30: "upload://jzHvSBlOOaopLQ99Ed6eHeQYsTu.png",
        31: "upload://5Lrx3lIEN8fJaKBP1RVdH04q0om.png",
        32: "upload://t2rL9dP0JTbTiu9Ss0iZFAZh8hS.png",
        33: "upload://nFmIz9OBwM1V7g2FJhUsfcwR6jj.png",
        34: "upload://aN8lpNfJaRTbtAlEOoZaOio7TKr.png",
        35: "upload://mwDrtpL4oQHhyda5xU3hvU1nNgy.png",
        36: "upload://t2IRTVwyVe5sstaQXLIo1aBKafu.png",
        37: "upload://cAUY4ntNCIR0mcFrT8uMefhhH9D.png",
        38: "upload://ct0pv3SqggVdB0ZOBaqJJth9S9I.png",
        39: "upload://p28rfMCIz6R2Yh35xxW0oI8oqJ0.png",
        40: "upload://jVdhUkOYeaHTS7V8HfVdKk3Oas4.png",
        41: "upload://41aBgL6DwmgPSACCY5LrA6Lq08i.png",
        42: "upload://fD3Dzr1fdTFWNnWG8egWptBEcLX.png",
        43: "upload://htfUZFia5CaeAzV2bufWEL2viyH.png",
        44: "upload://59HvYqkqixphIu6Lhyi2brReh7U.png",
        45: "upload://21RzzeAjkBH0Uco2ffNp1eW1nHj.png",
        46: "upload://y0gplIQH22pBojOTS8lG3ATypq3.png",
        47: "upload://p365JDgF6AZdNy0vJU4KUfnXSxW.png",
        48: "upload://sOhIq8pV9AMKG36DOIhw0B58WKo.png",
        49: "upload://4YbHej98WTHd9S7ugmJRxqdfxL6.png",
        50: "upload://5KCRezrwUQeXFDl0kYZFWVZ869y.png",
        51: "upload://raYrLwnTgAR67dNJSYVqdw6kfQH.png",
        52: "upload://70znWMqFW63QFRAHLzQIQhS9aNR.png",
        53: "upload://jaJxcjKbfgbaxLIuit662VDfEgz.png",
        54: "upload://uk6aZvmT2dhq1f4ulwObdS9XB0G.png",
        55: "upload://bepZIOS8HNBkM7IdSkapWNFcqya.png",
        56: "upload://cHWwiM6lyii1vkBOwTB7AWzx6vx.png",
        57: "upload://yxtXFu4Rbo1NBFkmWaRdnbZSRVg.png",
        58: "upload://gUnZw3fmxm359dtX6hd3KkZ8nAS.png",
        59: "upload://hlgsqtNzmn008xMrEF3HXB5R1lo.png",
        60: "upload://4413zcbyKEHbHPR77U6W7zCXHHC.png",
        61: "upload://4mySufEp1YT65rFQBiKSUEZni1I.png",
        62: "upload://5cdK8AJt3SeoEAtKDMzKUYKhddn.png",
        63: "upload://lRbWdPVAihIarG4AvtQVL4vNYSK.png",
        64: "upload://6wj5dw3J3nQzyqdTGZVwxOP5fCu.png",
        65: "upload://mPuQARDxEq3PdopVo2Ui2c6y51R.png",
        66: "upload://11kCngULAo7vEFZQSlr7XRlysRo.png",
        67: "upload://zqBhRIXiSWThaxb7bqcSIXEXgIR.png",
        68: "upload://vbDBLU6YIglj8Z6jeSqb345Gk5z.png",
        69: "upload://2aCe9vpxFywy2xQDsINYcECpjZx.png",
        70: "upload://yz9O2Rte4z4ww4z3LtehNcl6SIk.png",
        71: "upload://aFkRzzjFyUf3kwMSmQVqJDJ1aeE.png",
        72: "upload://cgHBLl6TZbzZ5jzSSX8psfZKmTg.png",
        73: "upload://ubwt0z5w9ZogZ9iDpcp5LqIgfya.png",
        74: "upload://vzqrgFk0yK9eGP9Bl9E3hCGgg05.png",
        75: "upload://rqA5JjoH8PRKwZzk9PkGu0kCROg.png",
        76: "upload://sOfdNhQT1idtzCZU2wUSeSmuNxC.png",
        77: "upload://djU2lN9KA3WE2keEZU768hlmKW5.png",
        78: "upload://9HSwt1MuilOF0Ec58EXcQtca8Xi.png",
        79: "upload://4UTZmweP00q7sbe9hZHgKQZf0fR.png",
        80: "upload://dnh1qFLdvbqsrxfm3zeKk4x9LOp.png",
        81: "upload://nSD3fBnu4ThMzfrNUbMuiUHzhU.png",
        82: "upload://u41c99IA867b0oOe2TZhqR87o3U.png",
        83: "upload://c58LLTmTLZguVGeygoHj73N2fNA.png",
        84: "upload://txexaMkXMOzpF8aVmCHESr6vZyS.png",
        85: "upload://nVMHJXF6KLJ7wdTsNsxN7yDZ4rt.png",
        86: "upload://6nZ3pXt35xluNkGzo7TPqgxV6SR.png",
        87: "upload://jsI3LOBAL9k6ptPxXEsH536qu7U.png",
        88: "upload://d10mYkvqU3vIAhpnwxFoKSUWBOm.png",
        89: "upload://eijdXIEX8wGuLkqgCnBpBxx61RE.png",
        90: "upload://4yPIm1ytz0lJUp8BNDacdfHEhvr.png",
        91: "upload://l2cqKddDoJi2eyTe14ve3C7zEC8.png",
        92: "upload://jkOtaGJPH3t5G1h8X89RgRMYCsI.png",
        93: "upload://lRSFiyygl1cZ1NiFZVxRgmXBbzh.png",
        94: "upload://oKmnAUn3UgZeZDLsp8woaqKRxBf.png",
        95: "upload://lRWHSfFCRUjfovFj2hhuxVCTt8.png",
        96: "upload://kc1qgQNOS55Yw5HrLVo0dLAhu7y.png",
        97: "upload://jY0SjKsmBFjJAsgoiCAXIQaRi5g.png",
        98: "upload://3RTonhAtlGiFc9DNiHS8vNwRnvJ.png",
        99: "upload://k3Rnp7Jv3ramKZFymZg469qaQa2.png",
        100: "upload://kVJXX90yJJKqidERhusRUHvd441.png",
        101: "upload://1iJ5bFwbcgDB6CdqW4v4f7N9oaj.png",
        102: "upload://t1ceFnAdRJ1nmLuA7gje23Ru8Vu.png",
        103: "upload://ju4W7Njtn8QgSeS3zYWoOEI7mID.png",
        104: "upload://4a0QVdxqokiJETQDvWk7XCObU5L.png",
        105: "upload://iVQLy2DX8C4AwZ6tsFkFINAKx0r.png",
        106: "upload://7rVZacGeqgCHvAsu51QSTjR1MsQ.png",
        107: "upload://6By0LuyDxHFgN1RcaBeM7G10zNC.png",
        108: "upload://ci6xGG3UPy352KMbHQvo0ae4E4B.png",
        109: "upload://bjshr5u5hBdvzZ8tQGj0iMeWtzz.png",
        110: "upload://2e1nPfLTHhHMWUD8jUvAwsdPcJU.png",
        111: "upload://mBMkB2imxvfdrt6C6Yr9rMS1iXh.png",
        112: "upload://gfIyiKuRJTvpP8QHSH5F6XSkID6.png",
        113: "upload://5o5BBb7BxYwxGLyCA2F58CJcV86.png",
        114: "upload://sHrKKnqgwzVXRJKzo3rekkZNOe.png",
        115: "upload://fLLyC2FoCTkZUiaBoAvAKoXz46t.png",
        116: "upload://k6AVw5MSFyAaVqVAANAbMpvzrqv.png",
        117: "upload://sD5R7y8FX6fYhnnfKpDm32vN8Mx.png",
        118: "upload://75Yd6XpG6EgHAqCbuFmm9jxDdvM.png",
        119: "upload://A245TqwzAyuA9FMpItPjZz5KOEI.png",
        120: "upload://yPWc3FJVfUH4qJc7Oyt2mNeiz7p.png",
        121: "upload://tcKTMBStp5oU50AJzr6PRczAZaB.png",
        122: "upload://5OLbT6p15r7GXqZLA0kNajOTzBw.png",
        123: "upload://hPfEuu27Ok39wqGUhGLJ6D4BJlT.png",
        124: "upload://uWpdYa0EboOhffHwhShzF89CNc9.png",
        125: "upload://r6BISeEmzRtJKGaIwYUpuY4WZ3e.png",
        126: "upload://mAfGgYnrgQVktQu3YW1iWa7Bqc0.png",
        127: "upload://wYwIQRCYp0RkJ09fxBtMv407f3z.png",
        128: "upload://4hFqDNK1GKavDeBY518C6PS1PGn.png",
        129: "upload://n7oo64sZE2JL2k1AGQCEkBlLasl.png",
        130: "upload://onRZz8VopTc2e0uTHKPVJAtdQ64.png",
        131: "upload://2nTyOzSaFm1OZnhak1RPEmCOJG.png",
        132: "upload://k6t7e1XGI9GjGNjItsIwerpCEsl.png",
        133: "upload://1CdVMGRst2dsjdf8CG6ky48IRvQ.png",
        134: "upload://8COqnnKUFsPeWdYRnUDd2QQeXQg.png",
        135: "upload://m9WXlS9HpKZOHRA7kfMzdEuFyXp.png",
        136: "upload://hh7lxIWGTjY4C7uYEMnyoVi8ZXb.png",
        137: "upload://rfegBAH1PLCkIkzWUyBu0uYcbuK.png",
        138: "upload://dUP4uUTjsQOeOxfXduwbMbDUm6w.png",
        139: "upload://vciNYshN4aFHmtrAA8QSLd7rtOZ.png",
        140: "upload://83Lj2neuUOEwkAh1k84P0Hczkyl.png",
        141: "upload://gSccoOwvDUZPJ34PGjD5ZMAQ0mI.png",
        142: "upload://6KIBBTHcIue3WPxM8byP6vFPwJt.png",
        143: "upload://AncUrojYTA5I5DiBEK7FZgVqBCT.png",
        144: "upload://23ZejD12y2MkhNsuayGGDX6hmfP.png",
        145: "upload://qBbrhhEjBTHblQYzsBDhHrbKzY6.png",
        146: "upload://whqsngoky9WztXQm3UaSK5MyiWu.png",
        147: "upload://8ZjK7Yt1j67wcaLalJ2sHlXnI6d.png",
        148: "upload://fn0rrpCI26spI4ZrN0AGlbf4a0S.png",
        149: "upload://5J0jRTECpEUdPMH1BaymOG1XSmc.png",
        150: "upload://z2cTyIscpXCPnPdgzEOfzcnCmfk.png",
        151: "upload://dj8bJwkUuKb4eNUHhIRokM8qTdb.png",
        152: "upload://7NNtClogvQGEGC6cA2jlFX7v19V.png",
        153: "upload://zXeoT30RIoJXZrcBYzAod7T5oFw.png",
        154: "upload://iDnHyUrvrJeHNXldUBJ14JhLWm5.png",
        155: "upload://eE2iyU5ZUeuEFO449DNjj4P9T4Q.png",
        156: "upload://2QGmzuStxa9XkcxdhEwOqkGtUYv.png",
        157: "upload://mO892oz3fFGi97uiavo4PwRy3Q3.png",
        158: "upload://fZMSB24oX0S1yrKqDeWDPJk9Tmb.png",
        159: "upload://aqqrzPgqXtcaXcMfLmYpXiHeRib.png",
        160: "upload://4ZBNVsnRQw8HYcqnqXNNGyZ04LV.png",
        161: "upload://kgWil10NgdQeVuEhVlOW83BNkQJ.png",
        162: "upload://pnSvTSe5EKdaplsykYx8a4Fi2gS.png",
        163: "upload://v9VsUJyxSN0hA0vivvv0ZZawqlN.png",
        164: "upload://cEBhtrh6wcv0GVRLRpufSziKd10.png",
        165: "upload://3Alo3YTwBZMkDITIvNoIjNgk8aC.png",
        166: "upload://gWg37eJP66TE1ROwgTPp7hQYZWI.png",
        167: "upload://rmGI5d4xVtWGrGFSR3HvrZegXeu.png",
        168: "upload://7T8fz7XQR6IimRPsVlrE36p1PvO.png",
        169: "upload://rWi4dLpNyJswalnMHCjicFY4ei0.png",
        170: "upload://e8gYYE8VI3q1Pzl6w0qa1KWIqe6.png",
        171: "upload://dJMKxiAEImGT3kq1r7pzbwc6Qh8.png",
        172: "upload://wozOEJ2RlpFGaPruImbgrrSF4Xe.png",
        173: "upload://yJDwEpimZRWAMi2M7K6ufQlncdW.png",
        174: "upload://rP1ckSAAkwu0fT2h27Tct66iJVo.png",
        175: "upload://7V3OiMHFH1Kolu7Tqsd3Dtozmru.png",
        176: "upload://qcAWLb8uxsfxQi17wCgMwBVZ8P5.png",
        177: "upload://elT0xrnvyePYXsKknSLY56Fhsp4.png",
        178: "upload://nE4vCCAmOgzzyYTMWbIKhceykr5.png",
        179: "upload://tOMQtHWjzhILzvGZqrJsQNe3pIx.png",
        180: "upload://fdRtET83xc3LYqAyYgS7PABGfYS.png",
        181: "upload://pUQZApa1m8as6jgAgTpHzpeGe9i.png",
        182: "upload://ikqiwqnEgn0PLCD1mvLC8u1b25E.png",
        183: "upload://AuJos9oNHZ8bzWtJgFQj7rUA9yk.png",
        184: "upload://45I8KFNWLMl2itPFB8u2CAhgGa0.png",
        185: "upload://hyCeQoCl8b5Yrh7Z9H7ZoLv2vdA.png",
        186: "upload://fsNDn51XCodHQo1tztrCWzVXkZx.png",
        187: "upload://dLsLmTopuV2Dq1jQRnWAIOWHew0.png",
        188: "upload://6bGeMyfDDgv7nWw4RCU2FnGfjGv.png",
        189: "upload://7gihV7VppYN1l0Ol6Twcj8ARlt3.png",
        190: "upload://w1FF14THykFI1n4aOj5MIruwyvE.png",
        191: "upload://zoRmjoKlXaGtJFoYsPfFZIehv1P.png",
        192: "upload://h8FKJ2RLYNL2wok9hpGataB1x3U.png",
        193: "upload://mLrabn0nEQYpOW3XfLPUBCIUTj9.png",
        194: "upload://yfO1TDmJjPiAstRqSu3hxRxV1t7.png",
        195: "upload://atHm4aMSJ75fR4RsMWHRtAxOeYt.png",
        196: "upload://sN6MHH4HPcSXicaOBvnLaVyFPFx.png",
        197: "upload://wMeBkkTnldEw5lPuGytZOmNAqA8.png",
        198: "upload://rcOSktYvRvQcXx84Z0hgjeucpA2.png",
        199: "upload://2Q4LS1GIQomo2JjgL3AbKJA4b2U.png",
        200: "upload://4FjmdqzVMsf7OY43Z0tG4wfCNuq.png",
        201: "upload://il782JiimbskBrXESuNZeaZtZP.png",
        202: "upload://tKHVDTWol8PVYLOlGE43M2hv7Ek.png",
        203: "upload://im4i3t00FXHCdSLi1qZ6gyDbhIn.png",
        204: "upload://whxkeZLRi9TU6H9V0kyE0QyBu2u.png",
        205: "upload://5aza09ODcMhenIGkMgPYC2CXXE6.png",
        206: "upload://b3GSpnQaxU2Dud7QWN9mlfYDONL.png",
        207: "upload://cx5IsAJbaySzkAJAiS15aUeGAYd.png",
        208: "upload://yzyZISrARIXIab3PMpsna0dxmCa.png",
        209: "upload://kcmii9qt8Juwnq47GdXHoLY1py.png",
        210: "upload://2AWhN9o8SRte7UTo31xeo6rCEYe.png",
        211: "upload://sHzBGSpOkPe4bHuxELI39sOTspF.png",
        212: "upload://4jdOpSqNRo3GYfCmkRLneAxIMyg.png",
        213: "upload://j2GRKxFh3LeejXNukKDGqxw2h60.png",
        214: "upload://6YTIN2GxCB602vhM08uFNOMTyWH.png",
        215: "upload://gN3LWjwx3eSicSpeFr5ngArrQIk.png",
        216: "upload://9lyLiK4QHQIa4WCuSCmBQ7ApQs5.png",
        217: "upload://h1GRGaUyDxMm191LONy5kmLvITD.png",
        218: "upload://62EmT0dmK2IRmfhBYOhOHAwdL6m.png",
        219: "upload://gHDDdlNxh6ViZp4olhxs1WYaE5K.png",
        220: "upload://qFpNPNIkOIv4gxYcqEB58offxph.png",
        221: "upload://qK45aSykzF6b8h7sTmGpG1vEYey.png",
        222: "upload://4NGvzxDx23e9QtsO8YkA5TiBizh.png",
        223: "upload://nNL7VpaeM8UtatS6pHOLm454hgk.png",
        224: "upload://8oj2YRjGt1r9WWjmbgZcWGSqiPn.png",
        225: "upload://z9AAIZHgv2cTbYksZ3HYV8rCsQ5.png",
        226: "upload://2QPPfgQPIW9EvSn0hQoJAatxyv0.png",
        227: "upload://d2pqXGGgADVTnGnFSHesKXBT4o6.png",
        228: "upload://l97qw2RxrK2ifKcoOuLvaaf1lvi.png",
        229: "upload://gC7sgLY8kbeGKrTTe6ukDehhKmT.png",
        230: "upload://lLuyJB8FckJNfBAgDsnxmppuK4i.png",
        231: "upload://vZTyn6n5itOQNyqQNjOYYpju11p.png",
        232: "upload://7Qk270dBzyWCvEI7XsiXTMvjOcA.png",
        233: "upload://QBzqZRD9APNVb8OhRyokkMD8Am.png",
        234: "upload://gUbp8proVwEMga9wygCykO4Hz4K.png",
        235: "upload://k3d98C18NFWB0Ao6tdqVcpjPDxR.png",
        236: "upload://nGYtZth0NnBqTiIZgAMQ5MbAuFY.png",
        237: "upload://sdVjGoPWGMoF8hPa7Rdvu9efPZh.png",
        238: "upload://3sHWDmk4f0KeTTIr8rQxRZmRrVM.png",
        239: "upload://jckjJwGF8aKoQSxpxN7pH436sic.png",
        240: "upload://e0qtyColCYoK2QBkhQmSltKQcIO.png",
        241: "upload://G3nEw6aRx1l2zSgjblQHsvltXE.png",
        242: "upload://pNemsPrX8mAwDEMR6adXKRRURGq.png",
        243: "upload://yBj7xAmxSbq8HNg3CAV1stjJNEk.png",
        244: "upload://bLWxQSMuRiJ12Bxkg4RPkUuOFdj.png",
        245: "upload://1rwu2oxxKE0pj49ZO1pQ6GLOJvU.png",
        246: "upload://387AgU2sXuqkAH8gyN50cPgFtkp.png",
        247: "upload://sQerjRrKfFSu4bhTDYEQna2h5EY.png",
        248: "upload://s41agDenSK95Z7rqrEkRnJ2yfnv.png",
        249: "upload://jgEqA7yS7GubfNI1AsON3g2Hkng.png",
        250: "upload://yID4BDatVT3DYdsfHDnz8WeDdGS.png",
        251: "upload://e5QOLrIuhkgwrjkrVDTPoXxqCst.png",
        252: "upload://1u1FJa8shwxMueoBwuIaSuhguzb.png",
        253: "upload://tIC3N83ie8NYcoWOBrJR9VQy0g6.png",
        254: "upload://rakfKVysJH00oCVzgtyRWz4OFrK.png",
        255: "upload://vA17uae1fZRg3mPQsLcXKbdzq55.png",
    },
    "homeworld": {
        1: "upload://vCbNVAN8mpRumL7qbH9XBESPkZO.png",
        2: "upload://76B7oFjBkbTmjHPZVdU8eyo7eFs.png",
        3: "upload://vSfkYZetUaDnS9FeJusYqvL3Lgc.png",
        4: "upload://h3Od69m3W4ZAAv7qsHIuHwI6pzA.png",
        5: "upload://uSSWHxoRgMTxZuEWi8LsYJBdxPQ.png",
        6: "upload://yxhgJI5MZlS5vVocopBuIjp3dHL.png",
        7: "upload://akOhETwRzQIXfPdAGbFwJqIj7Pj.png",
        8: "upload://1dgOvXf3DVSpRTtAtmKJZVgbDwJ.png",
        9: "upload://z1mdrKPqY2zDElpjxIx8El4zxeI.png",
        10: "upload://etEGdmxFZaYNMFvAJQ89kjQMULf.png",
        11: "upload://b6jKdaM9RQuxD9nzHmIu2i3x06S.png",
        12: "upload://hBezkN6fc7qeHBbrnuqZo6u8iOU.png",
        13: "upload://jlaw1hiEflhfNFEFjy2KW1sBsdx.png",
        14: "upload://gxt7SY2UR5PJxejqqkhquYovEME.png",
        15: "upload://u6hasjYVrg4sJtKiKB4jAjal2t7.png",
        16: "upload://p5UqLCgfrLVQ8DqouN6hYviPh8m.png",
        17: "upload://52hBHLRo3YFEp6nzCIwIG1O8UVW.png",
        18: "upload://bjaqhPXi4pQv5rjDh2DCSMv0jh.png",
        19: "upload://2DU9kvCt2six9xG3NNrJFRWWl7p.png",
        20: "upload://gVZBHYhKGz7SwvbI5M48Co5IO7T.png",
        21: "upload://wcbLv8Pdadqh4w2AX4DGcqQX31Q.png",
        22: "upload://9vwOmVHBunNG8MuzaxHiTZwzs2g.png",
        23: "upload://jYL8MoHWE21fzXtHGDgWhyZqjoR.png",
        24: "upload://bu13pInzTg8kp1oRIEtF8hsyRUB.png",
        25: "upload://sylxZJgclCwEdwKu0NgU4bd23Jr.png",
        26: "upload://4uUhpreWqLIVt9YfSvdHpawIkOR.png",
        27: "upload://f6uyp7MC33Mp69URS0B6TsTSJuQ.png",
        28: "upload://2N50kTR9zkz4kJu0ktkn18PVV5Z.png",
        29: "upload://9JK249eagZIPdFTYVBpLBxmiGaY.png",
        30: "upload://scIHOJwg5GZA4olQlfUqfzYQvug.png",
        31: "upload://m7q5vPRUwHYRAJumvKLnUvcZjDA.png",
        32: "upload://hOcY97pg3Mhtv982WorNImOQj0U.png",
        33: "upload://8CG9K06TCjsm5CWdNe8oiXcfMwj.png",
        34: "upload://cwifUp1AFZJr85qn3Eb8aZrGyqd.png",
        35: "upload://kWhRmVKdTzBxgHgWnEh1YZxYXAO.png",
        36: "upload://tyTZD49DGLMPOZNZgPF6RcQF6UL.png",
        37: "upload://8Pognll0lrw8lUyYqjnevaZl0tf.png",
        38: "upload://A3264cvkIhFbf9EgzYkxR41LWSK.png",
        39: "upload://zp3Mus4859PtgLLWXGzROpIrepj.png",
        40: "upload://uIEz1nsW2qveBU7HXQv1ebZQYYx.png",
        41: "upload://miJJHWTmdQkxpzuI3FPURiLIISV.png",
        42: "upload://uPIL6rJAH6e8m8Mt2nkwRuxCq5R.png",
        43: "upload://lng3kk19dL9oe3q3MaXKNdmF01y.png",
        44: "upload://8Ld4qvLFr8UDzGpD2iGuJ4dA2oz.png",
        45: "upload://xfzqBLcqQtyP79VQqkqfdXyB8Of.png",
        46: "upload://57K5AxGCyNNUlcL6S0JKij07vjF.png",
        47: "upload://8PtPCOf2WQtIOkfgy5HvUe1U8C8.png",
        48: "upload://bRdEOb2CxQ7hkG8qJydssJX0xoH.png",
        49: "upload://7A22yg3KWrBDspfH0m57veqLP1U.png",
        50: "upload://ac991J9KkizDooVBI5VJOaGyzVm.png",
    },
}


class SubscriptionBase(PolymorphicModel):
    owner = models.ForeignKey(User, on_delete=models.CASCADE, blank=True, null=True)
    name = models.CharField(max_length=32, blank=True, null=True)

    def send(self, **kwargs):
        raise NotImplementedError()


class DiscordWebhookSubscription(SubscriptionBase):
    webhook_url = models.CharField(max_length=256)
    roles = models.TextField(blank=True, null=True)
    users = models.TextField(blank=True, null=True)

    def __str__(self):
        if self.owner is None:
            return f"{self.id}: {self.name}"
        return f"{self.id} ({self.owner}): {self.name}"

    def _add_meantions_to_data(self, data, key, value):
        if value is not None:
            meantions = []
            for m in value.split(","):
                if len(m.strip()) > 0:
                    meantions.append(m.strip())

            if len(meantions) > 0:
                meantions_prefix = ""
                for meantion in meantions:
                    if key == "roles":
                        meantions_prefix = f"<@&{meantion}> {meantions_prefix}"
                    else:
                        meantions_prefix = f"<@{meantion}> {meantions_prefix}"

                data["content"] = f'{meantions_prefix.strip()}\n{data["content"]}'

        return data

    def send(
        self, embed=None, files=None, markdown=None
    ):  # pylint: disable=arguments-differ
        if embed is None and markdown is None:
            raise ValueError("embed or markdown required")

        data_list = []
        if embed is not None:
            data = {"embeds": embed, "content": ""}
            data = self._add_meantions_to_data(data, "roles", self.roles)
            data = self._add_meantions_to_data(data, "users", self.users)

            data_list.append(data)
        else:
            messages = markdown.split("%SPLIT_MESSAGE%")
            send_meantions = False
            data_list = []
            for m in messages:
                if len(m.strip()) == 0:
                    continue

                data = {"content": m}

                if not send_meantions:
                    data = self._add_meantions_to_data(data, "roles", self.roles)
                    data = self._add_meantions_to_data(data, "users", self.users)
                    send_meantions = True

                data_list.append(data)

        send_discord_webhook.delay(self.webhook_url, data_list, files)


class NotificationBase(PolymorphicModel):
    subscription = models.ForeignKey(SubscriptionBase, on_delete=models.CASCADE)
    active = models.BooleanField(default=True)
    name = models.CharField(max_length=16, blank=True, null=True)

    def __str__(self):
        return f"{self.__class__.__name__}: {self.name}"

    def markdown(self, *args, **kwargs):
        return None

    def embed(self, *args, **kwargs):
        return None, None

    def forum(self, *args, **kwargs):
        return None, None

    def _markdown_replace(self, message):
        return (
            message.replace("\xa0", " ")
            .replace("&#x27;", "'")
            .replace("&quot;", "'")
            .replace("&quot;", "'")
            .replace("&lt;", "<")
            .replace("&gt;", ">")
        )


class BaseNotificationManager(PolymorphicManager):
    def send_notification(self, message):
        notifications = self.filter(active=True)

        for notification in notifications:
            notification.subscription.send(message)


class PolymorphicNotificationManager(PolymorphicManager):
    def send_notification(self, *args):
        notifications = self.filter(active=True)

        for notification in notifications:
            embed, files = notification.embed(*args)
            markdown = notification.markdown(*args)

            notification.subscription.send(embed=embed, files=files, markdown=markdown)


class NewWorldNotificationManager(PolymorphicNotificationManager):
    def send_new_notification(self, world_poll):
        world = world_poll.world

        if world.is_exo:
            ExoworldNotification.objects.send_notification(world, world_poll.resources)
        elif world.is_creative:
            CreativeWorldNotification.objects.send_notification(
                world, world_poll.resources
            )
        elif world.is_sovereign:
            SovereignWorldNotification.objects.send_notification(
                world, world_poll.resources
            )
        else:
            HomeworldNotification.objects.send_notification(world, world_poll.resources)

        if (
            world.image.name
            and world.forum_id
            and world.worldblockcolor_set.count() > 0
        ):
            world.notification_sent = True
        else:
            world.notification_sent = False

            world.save()

    def send_update_notification(self, world):
        send_update = (
            world.address is not None
            and world.notification_sent is False
            and (
                (world.forum_id and world.image.name)
                or timezone.now() > world.start + timedelta(days=1)
                or not world.is_exo
            )
        )

        if send_update:
            # no sovereign/creative worlds
            # Block Colors change over time
            if world.is_exo:
                ExoworldNotification.objects.send_notification(world)
            elif world.is_perm:
                HomeworldNotification.objects.send_notification(world)

            world.notification_sent = True
            world.save()


class WorldNotification(NotificationBase):
    objects = NewWorldNotificationManager()

    _context = None
    _world_type = "world"

    def _get_colors(self, world, default=False):
        # never get colors for Creative worlds
        if world.is_creative:
            colors = None
        else:
            kwargs = {"active": True}
            if default:
                kwargs = {"is_default": True}

            colors = (
                world.worldblockcolor_set.filter(**kwargs)
                .order_by("item__game_id", "-time")
                .distinct("item__game_id")
            )
            if colors.count() == 0:
                colors = None

        color_groups: Dict[str, list] = {}
        if colors is not None:
            for group_name in settings.BOUNDLESS_WORLD_POLL_GROUP_ORDER:
                color_groups[group_name] = []

            for color in colors:
                item_id = color.item.game_id
                group_name = settings.BOUNDLESS_WORLD_POLL_COLOR_GROUPINGS[item_id]

                order_index = list(
                    settings.BOUNDLESS_WORLD_POLL_GROUP_ORDER[group_name]
                ).index(item_id)
                color_group: List[Tuple[int, str]] = color_groups[group_name]
                color_group.append((order_index, color))
                color_groups[group_name] = color_group

            for group_name in list(color_groups.keys()):
                if len(color_groups[group_name]) == 0:
                    del color_groups[group_name]
                    continue

                color_groups[group_name] = [
                    c[1] for c in sorted(color_groups[group_name], key=lambda g: g[0])
                ]

        return color_groups

    def _get_context(self, world, resources=None):
        if self._context is not None:
            return self._context

        color_groups = self._get_colors(world)
        default_color_groups = None
        if world.is_sovereign:
            default_color_groups = self._get_colors(world, default=True)

            if len(default_color_groups) == 0:
                default_color_groups = None

        context = {
            "world": world,
            "color_groups": color_groups,
            "default_color_groups": default_color_groups,
            "icons": FORUM_LOOKUP_IMAGES,
        }
        if resources is not None and not world.is_creative:
            embedded_resources = []
            surface_resources = []

            for resource in resources.order_by("-count"):
                if resource.is_embedded:
                    embedded_resources.append(resource)
                else:
                    surface_resources.append(resource)

            context["embedded_resources"] = embedded_resources
            context["surface_resources"] = surface_resources

        self._context = context
        return self._context

    def _template(self, world, template, resources=None, extra=None):
        context = self._get_context(world, resources)
        if extra is not None:
            context.update(extra)

        message = ""

        message = render_to_string(
            template,
            context,
        )

        return self._markdown_replace(message)

    def forum(self, world, resources, extra=None):  # pylint: disable=arguments-differ
        world_class = "Homeworld"

        if world.is_exo:
            world_class = "Exoworld"
        elif world.is_creative:
            world_class = "Creative World"
        elif world.is_sovereign:
            world_class = "Sovereign World"

        title = (
            f"[{world.display_name}] "
            f"--[T{world.tier + 1} - {world.tier_name} "
            f"{world.get_world_type_display()} {world_class}]-- "
            f"[{'Active' if world.active else 'Inactive'}]"
        )

        return title, self._template(
            world, "boundlexx/notifications/forum.md", resources=resources, extra=extra
        )

    def _main_embed(self, world, is_update=False):
        files: Optional[Dict[str, str]] = None

        main_embed: Dict[str, Any] = {
            "fields": [
                {
                    "name": "🌍 World Details",
                    "value": (
                        f"\n\n**ID**: {world.id}\n"
                        f"**Type**: {world.get_world_type_display()}\n"
                        f"**Tier**: {world.get_tier_display()}\n"
                        f"**Atmosphere**: {world.protection or 'Normal'}\n"
                        f"**Size**: {world.display_size}\n"
                        f"**Liquid**: ▲ {world.surface_liquid} | "
                        f"▼ {world.core_liquid}\n"
                        f"**Region**: {world.get_region_display()}\n"
                    ),
                }
            ]
        }
        main_embed["title"] = world.display_name

        if is_update:
            main_embed[
                "description"
            ] = f"New information is avaiable for this {self._world_type}!"
        else:
            main_embed["description"] = f"A new {self._world_type} has appeared!"

        if world.forum_url:
            main_embed["url"] = world.forum_url

        if world.image.name:
            main_embed["thumbnail"] = {"url": f"attachment://{world.image.name}"}

            files = {world.image.name: world.image.url}

        if world.assignment is not None:
            main_embed["fields"].append(
                {
                    "name": "🧭 Distance Details",
                    "value": (
                        f"**{world.assignment_distance} blinksecs** from "
                        f"**{world.assignment}** (cost: **{world.assignment_cost}c**)"
                    ),
                }
            )

        if world.start is not None:
            timestring = (
                f"Appeared {naturaltime(world.start)} ({world.start.isoformat()})"
            )
            if world.end is not None:
                timestring += (
                    f"\nLast until {naturaltime(world.end)} ({world.end.isoformat()})"
                )

            main_embed["fields"].append(
                {
                    "name": "⏱ Time Details",
                    "value": timestring,
                },
            )

        return main_embed, files

    def _resource_embed(self, embedded_resources, surface_resources):
        resource_embed: dict = {"title": "World Resources"}
        fields: List[Dict[str, str]] = []

        resource_groups = (
            (embedded_resources, "Embedded Resources"),
            (surface_resources, "Surface Resources"),
        )
        for resources, title in resource_groups:
            values = [""]
            for index, resource in enumerate(resources):
                rank = index + 1
                value = values[-1]

                new_value = (
                    f"\n#{rank} **{resource.item.english}**: "
                    f"_{resource.percentage}% ({intcomma(resource.count)})_"
                )

                value += new_value
                if len(value) > 1024:
                    values.append(new_value)
                else:
                    values[-1] = value

            if len(values[0]) > 0:
                for index, value in enumerate(values):
                    if index > 0:
                        title += " (cont.)"
                    fields.append(
                        {
                            "name": title,
                            "value": value,
                        }
                    )

        if len(fields) == 0:
            return None

        resource_embed["fields"] = fields
        return resource_embed

    def _color_embed(self, world, color_groups):
        color_embed: dict = {"title": "Block Colors"}
        fields: List[Dict[str, str]] = []
        for group_name, color_group in color_groups.items():
            value = ""
            for color in color_group:
                value += (
                    f"\n* **{color.item.english}**: "
                    f"_{color.color.default_name} ({color.color.game_id})_"
                )

                extra = []
                if world.is_exo:
                    if color.is_new_exo:
                        extra.append("**NEW**")
                    else:
                        if color.transform_first_world is not None:
                            extra.append("**TRANS**")
                        if color.transform_last_exo is not None:
                            extra.append("**EXOTRANS**")
                        if color.days_since_exo:
                            extra.append(f"**Days: {color.days_since_exo}**")
                elif world.is_sovereign and not world.is_creative:
                    if color.is_new:
                        extra.append("**NEW**")

                value += f" {' | '.join(extra)}"

            fields.append(
                {"name": group_name.title() or "Gleam", "value": value.strip()}
            )

        if len(fields) == 0:
            return None

        color_embed["fields"] = fields
        return color_embed

    def embed(self, world, resources=None):  # pylint: disable=arguments-differ
        context = self._get_context(world, resources)

        embeds = []
        main_embed, files = self._main_embed(world, resources is None)
        embeds.append(main_embed)

        if not world.is_creative and resources is not None:
            resource_embed = self._resource_embed(
                context["embedded_resources"], context["surface_resources"]
            )
            if resource_embed is not None:
                embeds.append(resource_embed)

        color_embed = self._color_embed(world, context["color_groups"])
        if color_embed is not None:
            embeds.append(color_embed)

        return embeds, files


class ExoworldNotification(WorldNotification):
    _world_type = "exoworld"


class SovereignWorldNotification(WorldNotification):
    _world_type = "sovereign world"


class CreativeWorldNotification(WorldNotification):
    _world_type = "creative world"


class HomeworldNotification(WorldNotification):
    _world_type = "homeworld"


class SovereignColorNotification(NotificationBase):
    objects = PolymorphicNotificationManager()

    def embed(self, item, colors, new_ids):  # pylint: disable=arguments-differ
        lines = []
        fields = []

        title = "Color Details"
        colors = sorted(colors, key=lambda c: c.game_id)
        for color in colors:
            line = f"_{color.default_name} ({color.game_id})_"

            if color.game_id in new_ids:
                line += " **NEW**"
            lines.append(line)

            if len(lines) == 40:
                fields.append(
                    {
                        "name": title,
                        "value": "\n".join(lines),
                    }
                )

                title = "cont'd"
                lines = []

        fields.append(
            {
                "name": title,
                "value": "\n".join(lines),
            }
        )

        main_embed: Dict[str, Any] = {
            "title": item.english,
            "description": "New Sovereign selectable colors found!",
            "fields": fields,
        }

        return [main_embed], None


class FailedTaskNotification(NotificationBase):
    objects = PolymorphicNotificationManager()

    def markdown(self, task):  # pylint: disable=arguments-differ
        output = ""
        if task.traceback is not None:
            output = task.traceback.split("\n")

        messages = []
        message: List[str] = []
        for line in output:
            if len("\n".join(message) + line) >= 1750:
                messages.append(message)
                message = []
            message.append(line)
        messages.append(message)

        return self._markdown_replace(
            render_to_string(
                "boundlexx/notifications/failed_task.md",
                {
                    "task": task,
                    "messages": messages,
                    "base_url": get_base_url(admin=True),
                },
            )
        )


@receiver(post_save, sender=TaskResult)
def task_failure_handler(sender, instance, **kwargs):
    if (
        instance.status == "FAILURE"
        and instance.task_name != "boundlexx.notifications.tasks.send_discord_webhook"
    ):
        FailedTaskNotification.objects.send_notification(instance)
