from utility.main import check, pret, show, hrange
from dataclasses import dataclass, field

@dataclass
class Adjuster:
    dst_start: int
    src_start: int
    length: int

    def does_cover(self, num: int):
        return num >= self.src_start and num < (self.src_start + self.length)

    def adjust(self, num: int):
        if not self.does_cover(num):
            raise Exception(f"{num} not in range for {self}")
        return num - self.src_start + self.dst_start

    def does_cover_backwards(self, num: int):
        return num >= self.dst_start and num < (self.dst_start + self.length)

    def adjust_backwards(self, num: int):
        if not self.does_cover_backwards(num):
            raise Exception(f"{num} not in backwards range for {self}")
        return num - self.dst_start + self.src_start

my_adjuster = Adjuster(50, 98, 2)
check(my_adjuster.does_cover(79), False)
check(my_adjuster.does_cover(97), False)
check(my_adjuster.does_cover(98), True)
check(my_adjuster.does_cover(99), True)
check(my_adjuster.does_cover(100), False)
my_adjuster_2 = Adjuster(52, 50, 48)
check(my_adjuster_2.does_cover(79), True)

check(my_adjuster.adjust(98), 50)
check(my_adjuster.adjust_backwards(50), 98)
check(my_adjuster.adjust(99), 51)
check(my_adjuster.adjust_backwards(51), 99)

@dataclass
class Translation:
    frm: str
    to: str
    adjusters: list[Adjuster] = field(default_factory=list)

    def translate(self, num: int):
        for adj in self.adjusters:
            if adj.does_cover(num):
                return adj.adjust(num)
        return num

    def translate_backwards(self, num: int):
        for adj in self.adjusters:
            if adj.does_cover_backwards(num):
                return adj.adjust_backwards(num)
        return num

my_translation = Translation("seed", "soil", [my_adjuster, my_adjuster_2])
check(my_translation.translate(98), 50)
check(my_translation.translate(79), 81)
check(my_translation.translate(105), 105)
check(my_translation.translate_backwards(50), 98)
check(my_translation.translate_backwards(81), 79)
check(my_translation.translate_backwards(105), 105)

def translate_seed(seed, translations):
    current = seed
    for tl in translations:
        current = tl.translate(current)
    return current

def translate_seed_backwards(seed, translations):
    current = seed
    for tl in translations[::-1]:
        current = tl.translate_backwards(current)
    return current

def expand_seeds(seeds):
    expanded = set()
    for point in hrange(0, (len(seeds) // 2) - 1, len(seeds) // 2):
        idx = point * 2
        seed_start = seeds[idx]
        seed_length = seeds[idx + 1]
        expanded.update(range(seed_start, seed_start + seed_length))
    return expanded

def is_seed(seed, valid_seeds):
    for point in hrange(0, (len(valid_seeds) // 2) - 1, len(valid_seeds) // 2):
        idx = point * 2
        seed_start = valid_seeds[idx]
        seed_length = valid_seeds[idx + 1]
        if seed >= seed_start and seed < (seed_start + seed_length):
            return True
    return False

def find_lowest_seed(seeds, translations):
    candidate = 0
    while True:
        show(f"Trying: {candidate}")
        translated = translate_seed_backwards(candidate, translations)
        if is_seed(translated, seeds):
            return candidate
        candidate += 1

check(len(expand_seeds([79, 14, 55, 13])), 27)
check(is_seed(79, [79, 14, 55, 13]), True)
check(is_seed(92, [79, 14, 55, 13]), True)
check(is_seed(93, [79, 14, 55, 13]), False)

trial_seeds = [79, 14, 55, 13]
trial_translations = [
    Translation("seed", "soil", [
        Adjuster(50, 98, 2),
        Adjuster(52, 50, 48),
    ]),
    Translation("soil", "fertilizer", [
        Adjuster(0, 15, 37),
        Adjuster(37, 52, 2),
        Adjuster(39, 0, 15),
    ]),
    Translation("fertilizer", "water", [
        Adjuster(49, 53, 8),
        Adjuster(0, 11, 42),
        Adjuster(42, 0, 7),
        Adjuster(57, 7, 4),
    ]),
    Translation("water", "light", [
        Adjuster(88, 18, 7),
        Adjuster(18, 25, 70),
    ]),
    Translation("light", "temperature", [
        Adjuster(45, 77, 23),
        Adjuster(81, 45, 19),
        Adjuster(68, 64, 13),
    ]),
    Translation("temperature", "humidity", [
        Adjuster(0, 69, 1),
        Adjuster(1, 0, 69),
    ]),
    Translation("humidity", "location", [
        Adjuster(60, 56, 37),
        Adjuster(56, 93, 4),
    ]),
]

check(translate_seed(79, trial_translations), 82)
check(translate_seed_backwards(82, trial_translations), 79)
pret("Trial result:", find_lowest_seed(trial_seeds, trial_translations))

def translate_seeds(seeds, translations):
    return [
        translate_seed(seed, translations)
        for seed in seeds
    ]

def translate_seeds_backwards(seeds, translations):
    return [
        translate_seed_backwards(seed, translations)
        for seed in seeds
    ]

check(translate_seeds_backwards(translate_seeds(trial_seeds, trial_translations), trial_translations), trial_seeds)

input_seeds = [432986705, 28073546, 1364097901, 88338513, 2733524843, 234912494, 3151642679, 224376393, 485709676, 344068331, 1560394266, 911616092, 3819746175, 87998136, 892394515, 435690182, 4218056486, 23868437, 848725444, 8940450]

input_translations = [
Translation("seed", "soil", [
    Adjuster(748585809, 2125564114, 88980459),
    Adjuster(1317392128, 775565564, 217595062),
    Adjuster(1218610825, 676784261, 98781303),
    Adjuster(954230685, 2235762425, 141777617),
    Adjuster(2920242079, 4081180892, 51765553),
    Adjuster(2972007632, 3159586797, 16102841),
    Adjuster(0, 2377540042, 17565155),
    Adjuster(2834452876, 3712797875, 58062179),
    Adjuster(2892515055, 2917079842, 6424918),
    Adjuster(3327351062, 3175689638, 162608005),
    Adjuster(673338549, 647264576, 29519685),
    Adjuster(1197392973, 2214544573, 21217852),
    Adjuster(738232750, 116664417, 10353059),
    Adjuster(2988110473, 2429807442, 71556277),
    Adjuster(17565155, 334379348, 277510712),
    Adjuster(1700771639, 228674051, 105705297),
    Adjuster(3059666750, 4132946445, 162020851),
    Adjuster(1806476936, 993160626, 588628261),
    Adjuster(1096008302, 127289380, 101384671),
    Adjuster(622123656, 1908836676, 50942989),
    Adjuster(3221687601, 3338297643, 28028532),
    Adjuster(2408505336, 3770860054, 310320838),
    Adjuster(4175210607, 3039830108, 119756689),
    Adjuster(3326652416, 3039131462, 698646),
    Adjuster(2898939973, 2408505336, 21302106),
    Adjuster(673066645, 127017476, 271904),
    Adjuster(3489959067, 3382623558, 330174317),
    Adjuster(702858234, 611890060, 35374516),
    Adjuster(4086270124, 2562002619, 88940483),
    Adjuster(837566268, 0, 116664417),
    Adjuster(1534987190, 1959779665, 165784449),
    Adjuster(2718826174, 2923504760, 115626702),
    Adjuster(3249716133, 3366326175, 16297383),
    Adjuster(3820133384, 2650943102, 266136740),
    Adjuster(3266013516, 2501363719, 60638900),
    Adjuster(295075867, 1581788887, 327047789),

]),
Translation("soil", "fertilizer", [
    Adjuster(2018515973, 2192795257, 82329405),
    Adjuster(3722326327, 3015971185, 249665840),
    Adjuster(3046459770, 3689390318, 25519185),
    Adjuster(3971992167, 3265637025, 40217941),
    Adjuster(3071978955, 3453653215, 203407731),
    Adjuster(0, 443504340, 17965088),
    Adjuster(584437096, 1722124969, 470670288),
    Adjuster(1055107384, 744431503, 164966659),
    Adjuster(1489299099, 461469428, 282962075),
    Adjuster(2321848831, 2380372526, 153650776),
    Adjuster(2100845378, 269225056, 174279284),
    Adjuster(3487660258, 2648616968, 234666069),
    Adjuster(3275386686, 3305854966, 147798249),
    Adjuster(1772261174, 1172578553, 246254799),
    Adjuster(4012210108, 2883283037, 132688148),
    Adjuster(3423184935, 4138946628, 64475323),
    Adjuster(4144898256, 2321848831, 58523695),
    Adjuster(538253726, 1418833352, 46183370),
    Adjuster(1220074043, 0, 269225056),
    Adjuster(17965088, 909398162, 263180391),
    Adjuster(2590093273, 3657060946, 32329372),
    Adjuster(281145479, 1465016722, 257108247),
    Adjuster(2622422645, 3714909503, 424037125),
    Adjuster(2475499607, 2534023302, 114593666),

]),
Translation("fertilizer", "water", [
    Adjuster(3731805434, 353192162, 37567806),
    Adjuster(926873139, 889685769, 255250442),
    Adjuster(3170336676, 695153543, 194532226),
    Adjuster(679924479, 451681440, 193671776),
    Adjuster(3009343704, 3081959489, 160992972),
    Adjuster(1242360754, 3579359343, 278026518),
    Adjuster(1861131448, 2500688596, 20068354),
    Adjuster(4028837903, 4006213119, 266129393),
    Adjuster(1182123581, 3242952461, 60237173),
    Adjuster(3877550443, 645353216, 49800327),
    Adjuster(2223776164, 1371077033, 341527178),
    Adjuster(3364868902, 2566566565, 36440100),
    Adjuster(1773121333, 0, 76664401),
    Adjuster(264823995, 2444756861, 55931735),
    Adjuster(3929841219, 3857385861, 27802851),
    Adjuster(2166799431, 1712604211, 56976733),
    Adjuster(873596255, 1769580944, 53276884),
    Adjuster(645696746, 3047731756, 34227733),
    Adjuster(3927350770, 3955153621, 2490449),
    Adjuster(3769373240, 177937131, 108177203),
    Adjuster(0, 3314535348, 264823995),
    Adjuster(1942121274, 3885188712, 69964909),
    Adjuster(1881199802, 390759968, 60921472),
    Adjuster(1849785734, 3303189634, 11345714),
    Adjuster(3401309002, 2855740726, 104355610),
    Adjuster(2079164011, 2960096336, 87635420),
    Adjuster(544424016, 76664401, 101272730),
    Adjuster(2565303342, 2520756950, 45809615),
    Adjuster(1520387272, 2603006665, 252734061),
    Adjuster(2012086183, 286114334, 67077828),
    Adjuster(2611112957, 1822857828, 398230747),
    Adjuster(320755730, 2221088575, 223668286),
    Adjuster(3505664612, 1144936211, 226140822),
    Adjuster(4006213119, 4272342512, 22624784),

]),
Translation("water", "light", [
    Adjuster(62780592, 544346201, 30115959),
    Adjuster(2740764032, 1352944740, 34082945),
    Adjuster(377487729, 807592920, 35446631),
    Adjuster(1316419610, 1454554942, 34907962),
    Adjuster(986581913, 756881718, 50711202),
    Adjuster(4167758628, 3240047125, 127208668),
    Adjuster(818809239, 1222506283, 58684750),
    Adjuster(3649838514, 2036598113, 6212644),
    Adjuster(127663629, 0, 10715051),
    Adjuster(3023280854, 1435387310, 19167632),
    Adjuster(663070842, 10715051, 124076893),
    Adjuster(2774846977, 2422700597, 37614763),
    Adjuster(1812617371, 2460315360, 5121443),
    Adjuster(1640337506, 1864318248, 172279865),
    Adjuster(2986755724, 1316419610, 36525130),
    Adjuster(2023334670, 2467203928, 540327060),
    Adjuster(1159184084, 248462172, 14557802),
    Adjuster(1037293115, 152894449, 95567723),
    Adjuster(0, 134791944, 18102505),
    Adjuster(18102505, 712203631, 44678087),
    Adjuster(465375803, 972369801, 197695039),
    Adjuster(2576394916, 3007530988, 65274194),
    Adjuster(92896551, 1281191033, 34767078),
    Adjuster(3656051158, 4289142647, 5824649),
    Adjuster(412934360, 1170064840, 52441443),
    Adjuster(3417303830, 3873138614, 84580361),
    Adjuster(787147735, 263019974, 31661504),
    Adjuster(1817738814, 2042810757, 205595856),
    Adjuster(1285160111, 843039551, 30798000),
    Adjuster(2563661730, 3123136764, 12733186),
    Adjuster(138378680, 305237152, 239109049),
    Adjuster(3648071389, 2465436803, 1767125),
    Adjuster(1132860838, 574462160, 26323246),
    Adjuster(888049663, 873837551, 98532250),
    Adjuster(3626039273, 3072805182, 22032116),
    Adjuster(3530183657, 4193287031, 95855616),
    Adjuster(1404769450, 3957718975, 235568056),
    Adjuster(3042448486, 1489462904, 374855344),
    Adjuster(2641669110, 1387027685, 48359625),
    Adjuster(877493989, 294681478, 10555674),
    Adjuster(3501884191, 3094837298, 28299466),
    Adjuster(1351327572, 3186605247, 53441878),
    Adjuster(2690028735, 3135869950, 50735297),
    Adjuster(2812461740, 2248406613, 174293984),
    Adjuster(3661875807, 3367255793, 505882821),
    Adjuster(1173741886, 600785406, 111418225),

]),
Translation("light", "temperature", [
    Adjuster(964570004, 989608620, 226759942),
    Adjuster(2204148775, 2545437438, 20646474),
    Adjuster(233260112, 338444213, 39032265),
    Adjuster(958191857, 332066066, 6378147),
    Adjuster(2318799855, 914518254, 75090366),
    Adjuster(4247140372, 3146297568, 47826924),
    Adjuster(2224795249, 1216368562, 94004606),
    Adjuster(2871022952, 1310373168, 80313918),
    Adjuster(1400254919, 233260112, 98805954),
    Adjuster(445493256, 487550555, 149554087),
    Adjuster(2576473348, 3962746668, 294549604),
    Adjuster(3535295748, 2775008885, 371288683),
    Adjuster(1499060873, 377476478, 110074077),
    Adjuster(272292377, 2215619580, 173200879),
    Adjuster(3347481948, 1867953550, 157067409),
    Adjuster(4161267146, 3794452372, 85873226),
    Adjuster(3504549357, 2184873189, 30746391),
    Adjuster(1759636962, 1780717197, 87236353),
    Adjuster(2951336870, 2388820459, 6114967),
    Adjuster(1191329946, 2566083912, 208924973),
    Adjuster(1884544339, 3880325598, 82421070),
    Adjuster(595047343, 3431307858, 363144514),
    Adjuster(2393890221, 731935127, 182583127),
    Adjuster(4001414916, 2025020959, 159852230),
    Adjuster(2957451837, 1390687086, 390030111),
    Adjuster(1846873315, 4257296272, 37671024),
    Adjuster(1966965409, 3194124492, 237183366),
    Adjuster(1609134950, 2394935426, 150502012),
    Adjuster(3906584431, 637104642, 94830485),

]),
Translation("temperature", "humidity", [
    Adjuster(1406768592, 2335526312, 13344484),
    Adjuster(666958498, 1862550129, 472976183),
    Adjuster(558853371, 843618476, 74696086),
    Adjuster(1168798622, 129171378, 168640618),
    Adjuster(1713291209, 297811996, 183431863),
    Adjuster(1993628008, 635748116, 152317885),
    Adjuster(2560263686, 2849350774, 11516524),
    Adjuster(32266442, 1212766321, 287276323),
    Adjuster(2571780210, 3319898101, 11192927),
    Adjuster(375095240, 995599149, 183758131),
    Adjuster(2661986290, 2353962919, 50829838),
    Adjuster(3252020768, 4280298713, 14668583),
    Adjuster(1337439240, 1793220777, 69329352),
    Adjuster(3419718116, 3502299739, 574454544),
    Adjuster(2353962919, 2650392505, 198958269),
    Adjuster(633549457, 1179357280, 33409041),
    Adjuster(2582973137, 4076754283, 50515665),
    Adjuster(319542765, 788066001, 55552475),
    Adjuster(1896723072, 32266442, 96904936),
    Adjuster(1420113076, 1500042644, 293178133),
    Adjuster(3006421020, 2404792757, 245599748),
    Adjuster(2842554807, 3331091028, 163866213),
    Adjuster(2633488802, 2990605977, 28497488),
    Adjuster(2300450150, 947178503, 48420646),
    Adjuster(3266689351, 4127269948, 153028765),
    Adjuster(2145945893, 481243859, 154504257),
    Adjuster(3994172660, 3019103465, 300794636),
    Adjuster(1139934681, 918314562, 28863941),
    Adjuster(2712816128, 2860867298, 129738679),
    Adjuster(2552921188, 3494957241, 7342498),

]),
Translation("humidity", "location", [
    Adjuster(897459980, 3171885613, 268595078),
    Adjuster(506368722, 1864971513, 13322696),
    Adjuster(1166055058, 2803961444, 53745388),
    Adjuster(2572095034, 667166679, 114420176),
    Adjuster(687118932, 1725187165, 139784348),
    Adjuster(2478398695, 0, 14138781),
    Adjuster(3427672233, 370325921, 251085897),
    Adjuster(3888215738, 3612891343, 82449665),
    Adjuster(1674720770, 1530101168, 79955344),
    Adjuster(3970665403, 925512154, 2812137),
    Adjuster(519691418, 2452425610, 167427514),
    Adjuster(3884704963, 3168374838, 3510775),
    Adjuster(826903280, 2381868910, 70556700),
    Adjuster(2399774019, 349568762, 20757159),
    Adjuster(2972099388, 3465151802, 147739541),
    Adjuster(1754676114, 131614075, 217954687),
    Adjuster(2865104023, 3440480691, 24671111),
    Adjuster(2206760431, 932309368, 77882935),
    Adjuster(2284643366, 1610056512, 115130653),
    Adjuster(2492537476, 14138781, 35151040),
    Adjuster(2527688516, 3695341008, 44406518),
    Adjuster(3119838929, 781586855, 143925299),
    Adjuster(2732270071, 2857706832, 132833952),
    Adjuster(1599442846, 2728683520, 75277924),
    Adjuster(3263764228, 3995626854, 27783181),
    Adjuster(0, 2990540784, 177834054),
    Adjuster(2686515210, 621411818, 45754861),
    Adjuster(2420531178, 2670816003, 57867517),
    Adjuster(1219800446, 1010192303, 191374197),
    Adjuster(3678758130, 3789680021, 205946833),
    Adjuster(3973477540, 3739747526, 49932495),
    Adjuster(1972630801, 2014419033, 234129630),
    Adjuster(3291547409, 1878294209, 136124824),
    Adjuster(2889775134, 49289821, 82324254),
    Adjuster(1411174643, 2619853124, 50962879),
    Adjuster(1466122599, 2248548663, 133320247),
    Adjuster(177834054, 1201566500, 328534668),
    Adjuster(1462137522, 928324291, 3985077),
]),
]

# show(len(expand_seeds(input_seeds)))
# pret("Result:", compute(input_seeds, input_translations))
pret("Input result:", find_lowest_seed(input_seeds, input_translations))

# Got half way through implementing bisect and then it completed XD
