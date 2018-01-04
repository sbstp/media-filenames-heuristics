QUALITY = frozenset((
    "2160p",
    "1080p",
    "720p",
    "480p",
    "360p",
))

SOURCE = frozenset((
    "cam",
    "camrip",
    "ts",
    "hdts",
    "telesync",
    "tc",
    "hdtc",
    "telecine",
    "ppv",
    "ppvrip",
    "scr",
    "screener",
    "dvdscr",
    "dvdscreener",
    "bdscr",
    "ddc",
    "r5",
    "dvdrip",
    "dvdmux",
    "dvdr",
    "dvd-full",
    "dsr",
    "dsrip",
    "satrip",
    "dthrip",
    "dvbrip",
    "hdtv",
    "pdtv",
    "tvrip",
    "hdtvrip",
    "vodrip",
    "vodr",
    "webdl"
    "web-dl",
    "hdrip",
    "web-dlrip",
    "webrip",
    "web-rip",
    "bluray",
    "blu-ray",
    "bdrip",
    "brrip",
    "bdr",
    "bd5",
    "bd9",
))

VIDEO_FORMAT = frozenset((
    "xvid",
    "divx",
    "h264",
    "x264",
    "h265",
    "x265",
    "10bit",
))

AUDIO_FORMAT = frozenset((
    "ac3",
    "aac",
    "aac2",
    "dd5",
    "dd2",
))

LANGUAGE = frozenset((
    "french",
))

OTHERS = frozenset((
    "director",
    "directors",
    "director's",
    "dc",
    "extended",
    "theatrical",
    "uncut",
))

ALL = frozenset(
    QUALITY |
    SOURCE |
    VIDEO_FORMAT |
    AUDIO_FORMAT |
    LANGUAGE |
    OTHERS
)

ALL_WITHOUT_LANGUAGES = ALL - LANGUAGE
