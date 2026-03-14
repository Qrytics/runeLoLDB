-- Seed data for common champions and default rune pages

INSERT INTO champions (champion_id, name, key) VALUES
    (157, 'Yone', 'Yone'),
    (238, 'Zed', 'Zed'),
    (245, 'Ekko', 'Ekko'),
    (92,  'Riven', 'Riven'),
    (91,  'Talon', 'Talon'),
    (55,  'Katarina', 'Katarina'),
    (84,  'Akali', 'Akali'),
    (134, 'Syndra', 'Syndra'),
    (103, 'Ahri', 'Ahri'),
    (236, 'Lucian', 'Lucian'),
    (51,  'Caitlyn', 'Caitlyn'),
    (202, 'Jhin', 'Jhin'),
    (412, 'Thresh', 'Thresh'),
    (53,  'Blitzcrank', 'Blitzcrank'),
    (235, 'Senna', 'Senna'),
    (60,  'Elise', 'Elise'),
    (121, 'Khazix', 'Khazix'),
    (64,  'LeeSin', 'LeeSin'),
    (254, 'Vi', 'Vi'),
    (59,  'JarvanIV', 'JarvanIV'),
    (420, 'Illaoi', 'Illaoi'),
    (24,  'Jax', 'Jax'),
    (86,  'Garen', 'Garen'),
    (122, 'Darius', 'Darius'),
    (57,  'Maokai', 'Maokai'),
    (115, 'Ziggs', 'Ziggs'),
    (161, 'Velkoz', 'Velkoz'),
    (432, 'Bard', 'Bard'),
    (89,  'Leona', 'Leona'),
    (350, 'Yuumi', 'Yuumi'),
    (223, 'TahmKench', 'TahmKench'),
    (516, 'Ornn', 'Ornn'),
    (150, 'Gnar', 'Gnar'),
    (517, 'Sylas', 'Sylas'),
    (11,  'MasterYi', 'MasterYi'),
    (35,  'Shaco', 'Shaco'),
    (76,  'Nidalee', 'Nidalee'),
    (5,   'XinZhao', 'XinZhao'),
    (141, 'Kayn', 'Kayn'),
    (203, 'Kindred', 'Kindred'),
    (113, 'Sejuani', 'Sejuani'),
    (154, 'Zac', 'Zac'),
    (74,  'Heimerdinger', 'Heimerdinger'),
    (268, 'Azir', 'Azir'),
    (163, 'Taliyah', 'Taliyah'),
    (142, 'Zoe', 'Zoe'),
    (518, 'Neeko', 'Neeko'),
    (136, 'AurelionSol', 'AurelionSol'),
    (4,   'TwistedFate', 'TwistedFate'),
    (69,  'Cassiopeia', 'Cassiopeia'),
    (131, 'Diana', 'Diana'),
    (30,  'Karthus', 'Karthus'),
    (25,  'Morgana', 'Morgana'),
    (143, 'Zyra', 'Zyra'),
    (99,  'Lux', 'Lux'),
    (117, 'Lulu', 'Lulu'),
    (267, 'Nami', 'Nami'),
    (498, 'Xayah', 'Xayah'),
    (222, 'Jinx', 'Jinx'),
    (21,  'MissFortune', 'MissFortune'),
    (18,  'Tristana', 'Tristana'),
    (29,  'Twitch', 'Twitch'),
    (15,  'Sivir', 'Sivir'),
    (81,  'Ezreal', 'Ezreal'),
    (67,  'Vayne', 'Vayne'),
    (110, 'Varus', 'Varus'),
    (42,  'Corki', 'Corki'),
    (96,  'KogMaw', 'KogMaw'),
    (119, 'Draven', 'Draven'),
    (895, 'Nilah', 'Nilah'),
    (523, 'Aphelios', 'Aphelios')
ON CONFLICT (champion_id) DO NOTHING;

-- Default rune pages for common champions
INSERT INTO default_runes (champion_id, role, runes, patch) VALUES
(
    157, 'MID',
    '{
        "primaryPath": {
            "id": 8000,
            "name": "Precision",
            "keystone": {"id": 8010, "name": "Conqueror"},
            "slots": [
                {"id": 9111, "name": "Triumph"},
                {"id": 9104, "name": "Legend: Alacrity"},
                {"id": 8014, "name": "Last Stand"}
            ]
        },
        "secondaryPath": {
            "id": 8200,
            "name": "Domination",
            "slots": [
                {"id": 8126, "name": "Taste of Blood"},
                {"id": 8135, "name": "Treasure Hunter"}
            ]
        },
        "statShards": [
            {"id": 5008, "name": "Adaptive Force"},
            {"id": 5008, "name": "Adaptive Force"},
            {"id": 5003, "name": "Magic Resist"}
        ]
    }',
    '14.24'
),
(
    238, 'MID',
    '{
        "primaryPath": {
            "id": 8100,
            "name": "Domination",
            "keystone": {"id": 8128, "name": "Dark Harvest"},
            "slots": [
                {"id": 8126, "name": "Taste of Blood"},
                {"id": 8138, "name": "Eyeball Collection"},
                {"id": 8135, "name": "Treasure Hunter"}
            ]
        },
        "secondaryPath": {
            "id": 8300,
            "name": "Inspiration",
            "slots": [
                {"id": 8306, "name": "Magical Footwear"},
                {"id": 8347, "name": "Cosmic Insight"}
            ]
        },
        "statShards": [
            {"id": 5008, "name": "Adaptive Force"},
            {"id": 5008, "name": "Adaptive Force"},
            {"id": 5002, "name": "Armor"}
        ]
    }',
    '14.24'
),
(
    84, 'MID',
    '{
        "primaryPath": {
            "id": 8100,
            "name": "Domination",
            "keystone": {"id": 8112, "name": "Electrocute"},
            "slots": [
                {"id": 8126, "name": "Taste of Blood"},
                {"id": 8138, "name": "Eyeball Collection"},
                {"id": 8135, "name": "Treasure Hunter"}
            ]
        },
        "secondaryPath": {
            "id": 8000,
            "name": "Precision",
            "slots": [
                {"id": 9111, "name": "Triumph"},
                {"id": 9104, "name": "Legend: Alacrity"}
            ]
        },
        "statShards": [
            {"id": 5008, "name": "Adaptive Force"},
            {"id": 5008, "name": "Adaptive Force"},
            {"id": 5003, "name": "Magic Resist"}
        ]
    }',
    '14.24'
),
(
    64, 'JUNGLE',
    '{
        "primaryPath": {
            "id": 8400,
            "name": "Resolve",
            "keystone": {"id": 8439, "name": "Aftershock"},
            "slots": [
                {"id": 8446, "name": "Font of Life"},
                {"id": 8429, "name": "Bone Plating"},
                {"id": 8451, "name": "Overgrowth"}
            ]
        },
        "secondaryPath": {
            "id": 8000,
            "name": "Precision",
            "slots": [
                {"id": 9111, "name": "Triumph"},
                {"id": 9104, "name": "Legend: Alacrity"}
            ]
        },
        "statShards": [
            {"id": 5008, "name": "Adaptive Force"},
            {"id": 5002, "name": "Armor"},
            {"id": 5003, "name": "Magic Resist"}
        ]
    }',
    '14.24'
),
(
    51, 'BOTTOM',
    '{
        "primaryPath": {
            "id": 8000,
            "name": "Precision",
            "keystone": {"id": 8021, "name": "Fleet Footwork"},
            "slots": [
                {"id": 9111, "name": "Triumph"},
                {"id": 9104, "name": "Legend: Alacrity"},
                {"id": 8014, "name": "Last Stand"}
            ]
        },
        "secondaryPath": {
            "id": 8300,
            "name": "Inspiration",
            "slots": [
                {"id": 8306, "name": "Magical Footwear"},
                {"id": 8347, "name": "Cosmic Insight"}
            ]
        },
        "statShards": [
            {"id": 5008, "name": "Adaptive Force"},
            {"id": 5008, "name": "Adaptive Force"},
            {"id": 5002, "name": "Armor"}
        ]
    }',
    '14.24'
),
(
    412, 'SUPPORT',
    '{
        "primaryPath": {
            "id": 8400,
            "name": "Resolve",
            "keystone": {"id": 8439, "name": "Aftershock"},
            "slots": [
                {"id": 8446, "name": "Font of Life"},
                {"id": 8429, "name": "Bone Plating"},
                {"id": 8451, "name": "Overgrowth"}
            ]
        },
        "secondaryPath": {
            "id": 8200,
            "name": "Sorcery",
            "slots": [
                {"id": 8234, "name": "Nullifying Orb"},
                {"id": 8236, "name": "Gathering Storm"}
            ]
        },
        "statShards": [
            {"id": 5008, "name": "Adaptive Force"},
            {"id": 5002, "name": "Armor"},
            {"id": 5003, "name": "Magic Resist"}
        ]
    }',
    '14.24'
)
ON CONFLICT (champion_id, role) DO NOTHING;
