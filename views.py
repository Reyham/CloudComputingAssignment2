

matchsa2_economy = ('function (doc) {\n  index("default", doc._id); '
                        'if (doc._id) {index("name", doc.filename, '
                        '{"store": true}); }\n}')
